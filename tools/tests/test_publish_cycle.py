"""Local BFME1 bundle-building lifecycle and machine-readable CLI outcomes."""
import os
import sys
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cycle_fixture import NOW, bundle, measured_run, save_receipt
import closure_report as cr
import cycle_artifacts as ca
import link_cycle_context as context
import publish_cycle as pc


def test_cli_build_install_and_inspect(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(ca, "ancestry", lambda *a: (True, 0, "synthetic ancestor"))
    monkeypatch.setattr(ca.time, "time", lambda: NOW)
    run, _ = measured_run(tmp_path / "run")
    out, store = tmp_path / "out", tmp_path / "store"
    assert pc.main(["validate", str(run)]) == 0
    assert "consistent local measurement" in capsys.readouterr().out
    assert pc.main(["bundle", str(run), "--out", str(out), "--producer", "bfme1-synthetic",
                    "--first", "--install", str(store)]) == 0
    assert "authority is recomputed" in capsys.readouterr().out
    assert ca.main(["validate", str(store)]) == 0
    assert "AUTHORITATIVE: clean local run" in capsys.readouterr().out
    assert ca.main(["validate", str(out)]) == 0


def test_precomputed_report_pair_cannot_be_from_another_measurement(tmp_path):
    a, _ = measured_run(tmp_path / "a")
    b, _ = measured_run(tmp_path / "b", now=NOW + 60)
    roots, table, _ = cr.from_graph(a)
    closure = tmp_path / "closure"
    closure.mkdir()
    (closure / cr.ROOTS).write_bytes(roots)
    (closure / cr.BLOCKERS).write_bytes(table)
    with pytest.raises(ca.BundleError, match="closure report receipt_sha256"):
        pc.make_bundle(b, tmp_path / "out", "test", closure=closure)
    assert not (tmp_path / "out").exists()
    assert not list(tmp_path.glob(".out.partial-*"))


def test_receipt_repetition_and_rerun_identity(tmp_path):
    a, ra = measured_run(tmp_path / "a")
    b, rb = measured_run(tmp_path / "b", now=NOW + 60)
    assert ra["core_sha256"] == rb["core_sha256"]
    assert ca.tag_for((a / ca.RECEIPT).read_bytes()) != ca.tag_for((b / ca.RECEIPT).read_bytes())
    assert ca.bundle_id(ca.tag_for((a / ca.RECEIPT).read_bytes())) != ca.bundle_id(
        ca.tag_for((b / ca.RECEIPT).read_bytes()))


def test_current_ledgers_never_substituted_for_frozen_inputs(tmp_path, monkeypatch):
    run, receipt = measured_run(tmp_path / "run")
    def forbidden(*a, **kw):
        pytest.fail("bundle construction must not substitute today's ledger contents")
    monkeypatch.setattr(context, "input_hashes", forbidden)
    m = pc.make_bundle(run, tmp_path / "out", "test")
    assert m["binding"]["inputs"] == receipt["inputs"]


@pytest.mark.parametrize("attack", ["receipt", "status", "graph", "header", "rejected", "moved", "no-graph"])
def test_refuse_invalid_or_superseded_run(tmp_path, attack):
    run, receipt = measured_run(tmp_path / "run")
    if attack == "receipt":
        (run / ca.RECEIPT).write_text("not JSON")
    elif attack == "status":
        (run / "link_status.csv").write_text("bad")
    elif attack == "header":
        (run / "link_status.csv").write_text("source,verdict\nf.cpp,LINKED\n")
        receipt["series"]["link_status_sha256"] = ca.sha256_file(run / "link_status.csv")
        save_receipt(run, receipt)
    elif attack == "graph":
        (run / ca.CLOSURE_GRAPH).write_text("bad")
    elif attack == "no-graph":
        receipt.pop("closure_graph_sha256")
        save_receipt(run, receipt)
    elif attack == "rejected":
        rejected = run / "receipt.rejected.json"
        rejected.write_text("{}")
        ns = (run / ca.RECEIPT).stat().st_mtime_ns + 1000000
        os.utime(rejected, ns=(ns, ns))
    else:
        receipt["moved_during_run"] = ["inputs"]
        save_receipt(run, receipt)
    with pytest.raises(ca.Problem):
        pc.make_bundle(run, tmp_path / "out", "test")
    assert not (tmp_path / "out").exists()


def test_no_partial_bundle_on_copy_failure(tmp_path, monkeypatch):
    run, _ = measured_run(tmp_path / "run")
    def fail(*a, **kw):
        raise OSError("copy failed")
    monkeypatch.setattr(pc.shutil, "copyfile", fail)
    with pytest.raises(ca.Unavailable, match="copy failed"):
        pc.make_bundle(run, tmp_path / "out", "test")
    assert not (tmp_path / "out").exists()
    assert not list(tmp_path.glob(".out.partial-*"))


def test_destination_is_never_replaced_even_when_empty(tmp_path):
    run, _ = measured_run(tmp_path / "run")
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(pc.RunError, match="never replaced"):
        pc.make_bundle(run, out, "test")


def test_missing_closure_source_has_routing_reason(tmp_path):
    run, _ = measured_run(tmp_path / "run")
    with pytest.raises(ca.Refused) as e:
        pc.make_bundle(run, tmp_path / "out", "test", closure=tmp_path / "missing")
    assert e.value.reason == "no-closure-report"
