"""R1 regression tests; PASS means the defect is prevented.

Only synthetic images, artifacts and temporary git repositories. Never run a
compiler, linker, census, cycle(), Wine, or the general tools/tests suite.
Run: ~/.cache/bfme-venv/bin/python -m pytest -q -s tools/tests/test_bfme2_port_r1_regressions.py
"""
import ast
import collections
import copy
import csv
import importlib.util
import itertools
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import types

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cycle_fixture import host_stamp, NOW, measured_run, save_receipt, rehash
import closure_report as cr
import cycle_artifacts as ca
import cycle_diff as cd
import cycle_launch as launch
import cycle_stamp as stamp
import eligibility
import link_census as census
import link_cycle as lc
import link_cycle_context as ctx
import publish_cycle as pc
import repair_queue as rq

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "aef2f16877"


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def checkout(tmp_path, monkeypatch):
    """Real clean git ancestry and real rule hashing, no authority-policy mocks."""
    root = tmp_path / "checkout"
    (root / "tools").mkdir(parents=True)
    names = set(ctx.MEASUREMENT_FILES) | {
        "closure_report.py", "cycle_artifacts.py", "publish_cycle.py",
        "repair_queue.py", "cycle_diff.py", "data_back_rank.py", "cycle_stamp.py", "cycle_launch.py"}
    for name in names:
        shutil.copyfile(ROOT / "tools" / name, root / "tools" / name)
    reverse = root / "targets/game/reverse"
    reverse.mkdir(parents=True)
    for name in ("functions", "symbols", "data_rows"):
        (reverse / (name + ".csv")).write_text("synthetic ledger\n")
    (root / "game").mkdir()
    (root / "game/f.cpp").write_text("// synthetic measured source\n")
    key = stamp.keygen(tmp_path / "host-key")
    monkeypatch.setattr(stamp, "_reader_key_for_tests", key)
    (root / ".gitignore").write_text("build/\n__pycache__/\n")
    git(root, "init", "-q")
    git(root, "add", "tools", "targets", "game", ".gitignore")
    git(root, "-c", "core.hooksPath=.githooks", "-c", "user.name=R1 fixture",
        "-c", "user.email=r1@example.invalid", "commit", "-qm", "synthetic approved checkout")
    commit = git(root, "rev-parse", "HEAD")
    git(root, "update-ref", "refs/remotes/origin/master", commit)
    assert not git(root, "status", "--porcelain")
    assert ca.ancestry(commit, root)[0] is True
    monkeypatch.setattr(rq, "ROOT", root)
    monkeypatch.setattr(rq, "BFME1", True)
    # Isolate live host claims/fleet state, not bundle or graph validation.
    monkeypatch.setattr(eligibility, "servable", lambda **kw: lambda rva: True)
    return root, commit


def run_for(checkout, path, **kwargs):
    root, commit = checkout
    run, receipt = measured_run(path, commit=commit, deps=ca.local_dependencies(root), **kwargs)
    bind_evidence(run, receipt, root)
    return run, receipt


def bind_evidence(run, receipt, root):
    receipt["executed_modules"] = {n: {"origin": "tools/" + n, "sha256": ca.sha256_file(root / "tools" / n)}
                                   for n in receipt["rule_identity"]["measurement_files"]}
    import cycle_source
    import os
    audit = os.environ.get(cycle_source.AUDIT_ENV)
    receipt["runtime_modules"] = (cycle_source.audit_modules(audit, require_complete=False, runtime=True) if audit else
                                  {"sys": {"origin": "built-in:sys", "sha256":
                                           receipt["rule_identity"]["runtime"]["executable_sha256"]}})
    receipt["inputs"] = {n: ca.text_sha256(root / n) for n in ca.LEDGERS}
    receipt["snapshot"] = True
    receipt["run_options"]["snapshot"] = True
    for phase in ("start", "end"):
        receipt["checkout_" + phase].update(snapshot=True, tree_manifest="e" * 64)
    h = "e" * 64
    prov = {"build/f.obj": {"object": h, "object_canon": h, "proof": "inventory",
                            "source": "game/f.cpp", "source_sha256": ca.sha256_file(root / "game/f.cpp"),
                            "deps_sha256": h}}
    (run / ca.PROVENANCE).write_text(ca.dumps(prov))
    receipt["provenance_sha256"] = ca.sha256_file(run / ca.PROVENANCE)
    receipt["objects_digest"] = __import__("hashlib").sha256(b"build/f.obj\0" + h.encode()).hexdigest()
    receipt.update(lc.canonical_digests(prov))
    save_receipt(run, receipt)


def freeze(run, out, root, *, sign=True, **kwargs):
    manifest = pc.make_bundle(run, out, "R1 synthetic reproduction", root=root, **kwargs)
    if sign:
        manifest["execution"] = {"launcher": "cycle_launch/1", "commit": manifest["commit"], "snapshot": True,
                                 "semantic_sha256": manifest["rules"]["implementation_sha256"]}
        (out / ca.MANIFEST).write_text(ca.dumps(manifest))
        host_stamp(out, stamp.configured_keys()[0])
    return out


def change_row(run, receipt, **changes):
    path = run / "link_status.csv"
    rows = cr.status_rows(path)
    rows[0].update({k: str(v) for k, v in changes.items()})
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ca.STATUS_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    receipt["series"]["link_status_sha256"] = ca.sha256_file(path)


def save_graph(run, receipt, doc):
    lc.write_closure_graph(run / ca.CLOSURE_GRAPH, doc)
    receipt["closure_graph_sha256"] = ca.sha256_file(run / ca.CLOSURE_GRAPH)
    receipt["series"]["closure_graph_sha256"] = receipt["closure_graph_sha256"]
    save_receipt(run, receipt)


def test_r3_shift_only_failure_is_dropped_from_both_queues(checkout, tmp_path):
    root, _ = checkout
    run, receipt = run_for(checkout, tmp_path / "run")
    doc = ca.read_json(run / ca.CLOSURE_GRAPH)
    doc["nodes"]["unit:1"].update(ok=False, failures=["shift:hardcoded address"])
    change_row(run, receipt, closed_strict=0, hardcoded=1, failure_count=1,
               failures="shift:hardcoded address")
    receipt["series"]["credit_unique_bytes"] = 0
    save_graph(run, receipt, doc)
    out = freeze(run, tmp_path / "bundle", root)
    roots = ca.read_json(out / ca.CLOSURE_ROOTS)["roots"]
    assert roots[0]["conditional_gain_bytes"] == 10
    assert roots[0]["failures"] == ["shift:hardcoded address"]
    ordinary = rq.route_link_queue(out, now=NOW)
    closure = rq.route_link_queue(out, closure=True, now=NOW)
    assert ordinary["status"] == closure["status"] == "ok"
    assert ordinary["items"][0]["function"] == closure["items"][0]["function"] == "f"


def census_fixture(tmp_path, monkeypatch, data_only=False):
    root = tmp_path / "census-checkout"
    rev = root / "targets/game/reverse"
    rev.mkdir(parents=True)
    (rev / "functions.csv").write_text(
        "name,target_rva,target_size,source,status\n"
        "f,0x00001000,10,game/f.cpp,matched\n")
    (rev / "data_rows.csv").write_text(
        "name,address,address_kind,size,source,status\n"
        "_datum,0x00900000,va,4,game/Data.cpp,matched\n")
    (rev / "link_status.csv").write_text(
        "source,linked,unresolved,duplicates,comdat_losers,addresses,wrong_selected,alias_target,alias_unknown\n"
        + ("game/Data.cpp,no,1,0,0,0,0,0,0\n" if data_only else
           "game/f.cpp,no,0,0,0,0,0,1,1\n"))
    (rev / "link_census_history.csv").write_text("commit,date\nabc,2026-10-22 12:00\n")
    monkeypatch.setattr(rq, "ROOT", root)
    monkeypatch.setattr(rq, "BFME1", True)
    monkeypatch.setattr(rq, "LEDGER", "targets/game/reverse/functions.csv")
    monkeypatch.setattr(rq, "CENSUS_STATUS", "targets/game/reverse/link_status.csv")
    monkeypatch.setattr(rq, "CENSUS_HISTORY", "targets/game/reverse/link_census_history.csv")
    monkeypatch.setattr(rq, "LINK_STATUS", str(root / "build/link_cycle/link_status.csv"))
    monkeypatch.setattr(eligibility, "servable", lambda **kw: lambda rva: True)
    rq.ledger.cache_clear()
    git(root, "init", "-q")
    git(root, "add", "targets")
    git(root, "-c", "core.hooksPath=.githooks", "-c", "user.name=R1 fixture",
        "-c", "user.email=r1@example.invalid", "commit", "-qm", "synthetic census")
    return rev


def test_r4_bfme1_alias_blockers_are_not_counted(tmp_path, monkeypatch):
    rev = census_fixture(tmp_path, monkeypatch)
    try:
        [item] = rq.census_items(rev / "link_status.csv")
        assert item["blockers"] == 2
        assert "alias_target 1" in item["why"] and "alias_unknown 1" in item["why"]
    finally:
        rq.ledger.cache_clear()


def test_r5_data_only_census_repairs_disappear(tmp_path, monkeypatch):
    census_fixture(tmp_path, monkeypatch, data_only=True)
    try:
        result = rq.route_link_queue()
        assert result["status"] == "ok"
        [item] = result["items"]
        assert item["provider_kind"] == "data" and item["target_rva"] == "0x00500000"
        assert item["size"] == item["credit"] == 0
    finally:
        rq.ledger.cache_clear()


def test_r11_dirty_census_is_routed_as_committed(tmp_path, monkeypatch):
    rev = census_fixture(tmp_path, monkeypatch)
    root = rev.parents[2]
    measured_commit = git(root, "rev-parse", "HEAD")
    (rev / "link_census_history.csv").write_text("commit,date\n" + measured_commit + ",2026-10-22 12:00\n")
    git(root, "add", "targets/game/reverse/link_census_history.csv")
    git(root, "-c", "core.hooksPath=.githooks", "-c", "user.name=R1 fixture",
        "-c", "user.email=r1@example.invalid", "commit", "-qm", "record census identity")
    git(root, "update-ref", "refs/remotes/origin/master", "HEAD")
    path = rev / "link_status.csv"
    path.write_text(path.read_text().replace(
        "game/f.cpp,no,0,0,0,0,0,1,1", "game/f.cpp,no,12345,0,0,0,0,0,0"))
    assert "link_status.csv" in git(root, "status", "--porcelain")
    try:
        result = rq.route_link_queue()
        assert result["status"] == "ok" and result["route"] == "ordinary link queue"
        assert result["items"][0]["blockers"] == 2
        assert "alias_target 1" in result["items"][0]["why"]
        assert "committed link census" in result["notes"][0]
    finally:
        rq.ledger.cache_clear()


@pytest.mark.parametrize("portable", [False, True])
def test_r9_publisher_replaces_destination_created_during_validation(checkout, tmp_path, monkeypatch, portable):
    if portable:
        monkeypatch.setattr(ca.sys, "platform", "portable-test")
    root, _ = checkout
    run, _ = run_for(checkout, tmp_path / "run")
    out = tmp_path / "published"
    validate = ca.validate
    created = []
    def race(directory, **kwargs):
        result = validate(directory, **kwargs)
        if Path(directory).name.startswith(".published.partial-"):
            out.mkdir()
            created.append(out.stat().st_ino)
        return result
    monkeypatch.setattr(ca, "validate", race)
    with pytest.raises(ca.Unavailable):
        freeze(run, out, root)
    assert created and out.stat().st_ino == created[0]
    assert list(out.iterdir()) == []


def test_r10_rehashed_closure_report_is_authoritative_before_queue_checks(checkout, tmp_path):
    root, _ = checkout
    run, _ = run_for(checkout, tmp_path / "run")
    out = freeze(run, tmp_path / "bundle", root)
    doc = ca.read_json(out / ca.CLOSURE_ROOTS)
    assert doc["roots"] == []
    doc["roots"] = [{"root": "0x00001000", "conditional_gain_bytes": 999999999}]
    pc.gzip_bytes(ca.dumps(doc).encode(), out / ca.CLOSURE_ROOTS)
    rehash(out, ca.CLOSURE_ROOTS)
    with pytest.raises(ca.BundleError, match="closure root gains"):
        ca.serve(out, root=root, now=NOW, need_closure=True)
    assert rq.route_link_queue(out, closure=True, now=NOW)["reason"] == "corrupt"


def test_r8_cycle_diff_predecessor_credit_is_unbound(checkout, tmp_path):
    root, _ = checkout
    old_run, _ = run_for(checkout, tmp_path / "old-run")
    new_run, _ = run_for(checkout, tmp_path / "new-run", now=NOW + 100)
    old = freeze(old_run, tmp_path / "old", root)
    out = freeze(new_run, tmp_path / "new", root, previous=old)
    doc = ca.read_json(out / ca.CYCLE_DIFF)
    assert doc["totals"]["gained"] == 0
    unchanged_identity = copy.deepcopy(doc["identity"])
    doc["credit"]["old"] = []
    doc["gained"] = doc["credit"]["new"]
    doc["lost"] = []
    doc["totals"] = {"old": 0, "new": 10, "gained": 10, "lost": 0, "delta": 10}
    (out / ca.CYCLE_DIFF).write_text(cd.dumps(doc))
    rehash(out, ca.CYCLE_DIFF)
    assert ca.read_json(out / ca.CYCLE_DIFF)["identity"] == unchanged_identity
    with pytest.raises(ca.BundleError, match="old credit union"):
        ca.validate(out, root=root)


def test_r8_missing_historical_evidence_never_counts(tmp_path):
    a, _ = measured_run(tmp_path / "a")
    b, _ = measured_run(tmp_path / "b", now=NOW + 1)
    doc = cd.compare(a, b)
    doc.pop("evidence")
    with pytest.raises(cd.CycleDiffError):
        cd.check_report(doc)
    doc.update(comparison_verified=False, totals=None, gained=None, lost=None)
    cd.check_report(doc)


def test_r6_diagnostic_install_masks_authoritative_current(checkout, tmp_path):
    root, _ = checkout
    good_run, _ = run_for(checkout, tmp_path / "good-run")
    good = freeze(good_run, tmp_path / "good", root)
    bad_run, receipt = run_for(checkout, tmp_path / "diagnostic-run", now=NOW + 1)
    receipt["run_options"]["allow_dirty"] = True
    save_receipt(bad_run, receipt)
    bad = freeze(bad_run, tmp_path / "diagnostic", root)
    store = tmp_path / "store"
    good_manifest, _ = ca.install_local(good, store, root=root, now=NOW + 1)
    _, pointer = ca.install_local(bad, store, root=root, now=NOW + 1)
    assert pointer["latest_measurement"] == ca.bundle_id(good_manifest["tag"])
    for closure in (False, True):
        b, fr, _ = ca.serve(store, root=root, now=NOW + 1, need_closure=closure)
        assert fr["authoritative"] and b.tag == good_manifest["tag"]


def test_r7_pointer_replay_returns_old_measurement_without_warning(checkout, tmp_path):
    root, _ = checkout
    old_run, _ = run_for(checkout, tmp_path / "old-run")
    old = freeze(old_run, tmp_path / "old", root)
    new_run, _ = run_for(checkout, tmp_path / "new-run", now=NOW + 100)
    new = freeze(new_run, tmp_path / "new", root)
    store = tmp_path / "store"
    ca.install_local(old, store, root=root, now=NOW + 100)
    saved_pointer = (store / ca.POINTER).read_bytes()
    ca.install_local(new, store, root=root, now=NOW + 100)
    assert ca.serve(store, root=root, now=NOW + 100)[0].receipt["measured_end_ns"] == (NOW + 100) * 10**9
    (store / ca.POINTER).write_bytes(saved_pointer)
    for closure in (False, True):
        b, fr, lines = ca.serve(store, root=root, now=NOW + 100, need_closure=closure)
        assert fr["authoritative"] and b.receipt["measured_end_ns"] == (NOW + 100) * 10**9
        assert any("rollback" in line for line in lines)
    historical = store / ca.bundle_id(ca.read_manifest(old)["tag"]) / "bundle"
    _, fr, notes = ca.serve(historical, root=root, now=NOW + 100)
    assert fr["authoritative"] and any("explicit historical" in line for line in notes)


def test_r1_fabricated_run_is_authoritative(checkout, tmp_path):
    root, commit = checkout
    run, receipt = measured_run(tmp_path / "fabricated", commit=commit, deps=ca.local_dependencies(root))
    # All producer evidence is invented, including image/ledger/object digests.
    # No ancestry, compatibility, freshness or integrity checker is patched.
    assert receipt["inputs"][ca.LEDGERS[0]] != ctx.text_sha256(root / ca.LEDGERS[0])
    assert not (run / "provenance.json").exists()
    out = freeze(run, tmp_path / "bundle", root, sign=False)
    ca.validate(out, root=root)
    with pytest.raises(ca.Refused) as refused:
        ca.serve(out, root=root, now=NOW)
    assert refused.value.sub_reason == "unstamped"


def test_r2_loaded_verifier_can_claim_restored_disk_rules(checkout, tmp_path, monkeypatch):
    root, commit = checkout
    driver = root / "tools/link_cycle.py"
    original = driver.read_text()
    old = "    def code(self, at, size, masked, rels):\n"
    assert old in original
    driver.write_text(original.replace(old, old + "        return None  # bad local verifier\n"))
    monkeypatch.setenv("LINK_CYCLE_ROOT", str(root))
    monkeypatch.setattr(sys, "path", list(sys.path))
    spec = importlib.util.spec_from_file_location("review_loaded_driver", driver)
    running = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(running)
    driver.write_text(original)  # checkout/rebase restores disk; imported code survives
    assert not git(root, "status", "--porcelain")
    deps = ctx.tool_dependencies(root, running.__file__)
    assert ctx.rule_identity(deps) == ca.local_rules(root)
    # Exercise the real clean-start/end observer, with inert toolchain files and
    # a minimal PE32 target. No compiler discovery/execution or policy mock.
    toolchain = root / "build/toolchain"
    (toolchain / "Vc7/bin").mkdir(parents=True)
    for name in ("cl.exe", "link.exe", "lib.exe"):
        (toolchain / "Vc7/bin" / name).write_bytes(b"inert synthetic executable")
    target = root / "build/fixture.exe"
    pe = bytearray(0x400)
    pe[:2] = b"MZ"
    struct.pack_into("<I", pe, 0x3c, 0x40)
    pe[0x40:0x44] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", pe, 0x44, 0x14c, 1, 0, 0, 0, 224, 0x102)
    struct.pack_into("<H", pe, 0x58, 0x10b)
    struct.pack_into("<I", pe, 0x58 + 28, 0x400000)
    struct.pack_into("<II", pe, 0x58 + 32, 0x1000, 0x200)
    struct.pack_into("<II", pe, 0x58 + 56, 0x2000, 0x200)
    pe[0x138:0x140] = b".text\0\0\0"
    struct.pack_into("<IIII", pe, 0x140, 0x100, 0x1000, 0x200, 0x200)
    struct.pack_into("<I", pe, 0x138 + 36, 0x60000020)
    target.write_bytes(pe)
    monkeypatch.setattr(running.build, "ROOT", root)
    monkeypatch.setattr(running.build, "MANIFEST", root / "inputs/baselines/bfme1/manifest.json")
    monkeypatch.setattr(running.build, "EXE", target)
    monkeypatch.setattr(running.build, "vc71_root", lambda: toolchain)
    start = running.input_state()
    assert not start["dirty"] and start["rule_identity"] == ca.local_rules(root)
    run, receipt = measured_run(tmp_path / "run", commit=commit, deps=deps)
    receipt.update(start)
    image = bytearray(0x3000)
    image[0x1000:0x1006] = b"\xa1" + struct.pack("<I", lc.BASE + 0x1f10) + b"\xc3"
    shifted = running.Shifted.__new__(running.Shifted)
    shifted.I = shifted.S = bytes(image)
    shifted.delta, shifted.base_s = lc.SHIFT_BASE - lc.BASE, lc.SHIFT_BASE
    shifted.lo, shifted.hi, shifted.starts = lc.BASE + 0x1f00, lc.BASE + 0x2000, set()
    shifted.why, shifted.failed = None, collections.Counter()
    assert lc.Shifted.code(shifted, 0x1000, 6, set(), []) == "hardcoded address"
    assert shifted.code(0x1000, 6, set(), []) is None
    shifted.failed.clear()
    row = {"name": "f", "kind": "real", "source": "game/f.cpp", "rva": 0x1000, "size": 6}
    unit = {"id": 1, "head": "f", "rows": [row]}
    rec = {"row": row, "unit": unit, "measured": True, "placed": 1, "linked": 0x1000, "fails": [],
           "edges": set(), "masked": set(), "rels": [], "unpinned": False}
    m = types.SimpleNamespace(run=lambda: [rec], twins={}, dnodes={}, eh=collections.Counter(),
                              import_equiv=0, ilt_routes=collections.Counter(), back={})
    (run / "base.map").write_text("")
    # Only replace the linker/PE inputs with in-memory fixtures. The modified
    # Shifted.code executes; measure writes the actual status and graph.
    with monkeypatch.context() as patch:
        patch.setattr(running, "Measure", lambda *a: m)
        patch.setattr(running, "Shifted", lambda *a: shifted)
        patch.setattr(running, "pe_view", lambda p: (None, bytes(image), {".text": (0x1000, 0x2000)}, {}))
        patch.setattr(running, "zz_names", lambda p: ({}, []))
        series = running.measure(run, [unit], [], types.SimpleNamespace(by_base={}), bytes(image),
                                 {".text": (0x1000, 0x2000)}, {}, {}, True, lc.SHIFT_BASE)
    assert series["credit_unique_bytes"] == 6
    receipt.update(series=series, closure_graph_sha256=series["closure_graph_sha256"])
    end = running.input_state(final=True)
    assert start == end
    running.record_run_evidence(receipt, start, end, types.SimpleNamespace())
    save_receipt(run, receipt)
    assert sys.modules["link_cycle"] is lc  # independent, unmodified consumer
    out = freeze(run, tmp_path / "bundle", root, sign=False)
    with pytest.raises(ca.Refused) as refused:
        ca.serve(out, root=root, now=NOW)
    assert refused.value.sub_reason == "unstamped"


@pytest.mark.parametrize("attack,reason", [
    ("functions", "input-mismatch"), ("symbols", "input-mismatch"), ("data_rows", "input-mismatch"),
    ("extra-input", "input-mismatch"),
    ("tool", "tool-mismatch"), ("missing-objects", "missing-object-evidence"),
    ("objects-digest", "bad-object-evidence"), ("object-source", "object-source-mismatch")])
def test_r1_stamped_evidence_must_match_git_and_objects(checkout, tmp_path, attack, reason):
    root, _ = checkout
    run, receipt = run_for(checkout, tmp_path / "run")
    if attack in ("functions", "symbols", "data_rows"):
        receipt["inputs"][f"targets/game/reverse/{attack}.csv"] = "f" * 64
    elif attack == "extra-input":
        receipt["inputs"]["tools/repair_queue.py"] = "f" * 64
    elif attack == "tool":
        # A broad tool hash must match Git even under equal semantic rules.
        receipt["tool_dependencies"]["repair_queue.py"] = "f" * 64
        receipt["tool_digest"] = ctx.digest(receipt["tool_dependencies"])
    elif attack == "missing-objects":
        (run / ca.PROVENANCE).unlink()
    elif attack == "objects-digest":
        receipt["objects_digest"] = "f" * 64
    else:
        prov = ca.read_json(run / ca.PROVENANCE)
        prov["build/f.obj"]["source_sha256"] = "f" * 64
        (run / ca.PROVENANCE).write_text(ca.dumps(prov))
        receipt["provenance_sha256"] = ca.sha256_file(run / ca.PROVENANCE)
    save_receipt(run, receipt)
    out = freeze(run, tmp_path / "bundle", root)
    with pytest.raises(ca.Refused) as refused:
        ca.serve(out, root=root, now=NOW)
    assert refused.value.sub_reason == reason


@pytest.mark.parametrize("attack,reason", [
    ("missing", "unstamped"), ("no-keys", "unstamped"), ("wrong-key", "bad-stamp"),
    ("mac", "bad-stamp"), ("manifest", "bad-stamp"), ("readable-key", "bad-stamp")])
def test_r1_host_stamp_required_under_reader_keys(checkout, tmp_path, monkeypatch, attack, reason):
    root, _ = checkout
    run, _ = run_for(checkout, tmp_path / "run")
    out = freeze(run, tmp_path / "bundle", root)
    assert ca.serve(out, root=root, now=NOW)[1]["authoritative"]
    if attack == "missing":
        (out / stamp.STAMP).unlink()
    elif attack == "no-keys":
        monkeypatch.setattr(stamp, "_reader_key_for_tests", tmp_path / "absent-key")
    elif attack == "wrong-key":
        monkeypatch.setattr(stamp, "_reader_key_for_tests", stamp.keygen(tmp_path / "other-key"))
    elif attack == "mac":
        doc = ca.read_json(out / stamp.STAMP)
        doc["hmac_sha256"] = "0" * 64
        (out / stamp.STAMP).write_text(ca.dumps(doc))
    elif attack == "readable-key":
        stamp.configured_keys()[0].chmod(0o640)
    else:
        manifest = ca.read_manifest(out)
        manifest["producer"] = "changed producer"
        (out / ca.MANIFEST).write_text(ca.dumps(manifest))
    with pytest.raises(ca.Refused) as refused:
        ca.serve(out, root=root, now=NOW)
    assert refused.value.sub_reason == reason
    assert ca.load_bundle(out, root=root).freshness(now=NOW)["authoritative"] is False


def test_r1_keygen_refuses_repository_keys_and_never_replaces(checkout, tmp_path):
    root, _ = checkout
    key = tmp_path / "new-key"
    assert launch.main(["keygen", "--key", str(key)]) == 0
    assert key.stat().st_mode & 0o777 == 0o600 and len(stamp.read_key(key)) == 32
    original = key.read_bytes()
    assert launch.main(["keygen", "--key", str(key)]) == 1
    assert key.read_bytes() == original
    for candidate in (root / "key", root / ".git/key"):
        assert launch.main(["keygen", "--key", str(candidate)]) == 1
        assert not candidate.exists()
    inside = root / "secret"
    inside.write_bytes(original)
    inside.chmod(0o600)
    with pytest.raises(stamp.KeyError, match="outside every"):
        stamp.read_key(inside)
    symlink = tmp_path / "key-symlink"
    symlink.symlink_to(key)
    with pytest.raises((stamp.KeyError, OSError)):
        stamp.read_key(symlink)


def synthetic_snapshot_checkout(checkout):
    """Commit an inert measurement entrypoint; the real cycle body is removed.

    Real export_snapshot/run_in_snapshot execute, followed by synthetic artifact
    serialization only. Neither a compiler nor the real cycle can be called.
    """
    import inspect
    import textwrap
    root, _ = checkout
    driver = root / "tools/link_cycle.py"
    source = driver.read_text()
    cycle = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "cycle")
    lines = source.splitlines(True)
    lines[cycle.lineno - 1:cycle.end_lineno] = []
    source = "".join(lines).replace("    cycle(args)\n", "    synthetic_measurement(args)\n")
    helper = "def synthetic_measurement(args):\n"
    # Inline only the inert artifact serializer into the declared driver. No
    # test module or bundle reader is imported as an undeclared provider.
    helper += "    import types\n    import link_cycle as lc\n"
    helper += "    NOW = " + repr(NOW) + "\n"
    helper += "    ca = types.SimpleNamespace()\n"
    helper += "    ca.LEDGERS = " + repr(ca.LEDGERS) + "\n"
    helper += "    ca.STATUS_COLUMNS = " + repr(ca.STATUS_COLUMNS) + "\n"
    helper += "    ca.RECEIPT, ca.PROVENANCE, ca.CLOSURE_GRAPH = 'receipt.json', 'provenance.json', 'closure_graph.json.gz'\n"
    helper += "    ca.dumps = lambda doc: json.dumps(doc, sort_keys=True, indent=2) + chr(10)\n"
    helper += "    ca.read_json = lambda path: json.loads(path.read_bytes())\n"
    helper += "    ca.local_dependencies = context.tool_dependencies\n"
    helper += "    ca.text_sha256, ca.sha256_file = text_sha256, sha256\n"
    helper += "    ca.iso_utc = lambda seconds: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(seconds))\n"
    helper += textwrap.indent(inspect.getsource(measured_run), "    ")
    helper += textwrap.indent(inspect.getsource(save_receipt), "    ")
    helper += textwrap.indent(inspect.getsource(bind_evidence), "    ")
    helper += '''
    meta = ca.read_json(ROOT / SNAPSHOT_MARK)
    run, receipt = measured_run(ROOT / "build/link_cycle", commit=meta["commit"], deps=ca.local_dependencies(ROOT))
    bind_evidence(run, receipt, ROOT)
    image = bytearray(0x3000)
    image[0x1000:0x1006] = b"\\xa1" + struct.pack("<I", BASE + 0x1f10) + b"\\xc3"
    sh = Shifted.__new__(Shifted)
    sh.I = sh.S = bytes(image)
    sh.delta, sh.base_s = SHIFT_BASE - BASE, SHIFT_BASE
    sh.lo, sh.hi, sh.starts = BASE + 0x1f00, BASE + 0x2000, set()
    sh.why, sh.failed = None, collections.Counter()
    result = sh.code(0x1000, 6, set(), [])
    assert result == "hardcoded address"
    receipt["synthetic_execution"] = {"pid": os.getpid(), "driver": __file__, "adapter": context.__file__, "shift": result}
    save_receipt(run, receipt)


'''
    source = source.replace('if __name__ == "__main__":', helper + 'if __name__ == "__main__":')
    assert not any(isinstance(n, ast.FunctionDef) and n.name == "cycle" for n in ast.parse(source).body)
    driver.write_text(source)
    (root / "tools/gen_case_shims.py").write_text("def ensure_case_shims(*args, **kwargs):\n    pass\n")
    git(root, "add", "tools")
    git(root, "-c", "core.hooksPath=.githooks", "-c", "user.name=R1 fixture",
        "-c", "user.email=r1@example.invalid", "commit", "-qm", "inert snapshot measurement")
    commit = git(root, "rev-parse", "HEAD")
    git(root, "update-ref", "refs/remotes/origin/master", commit)
    return root, commit


def test_r2_launcher_executes_snapshot_code_in_fresh_interpreter(checkout, tmp_path, monkeypatch):
    import os
    root, commit = synthetic_snapshot_checkout(checkout)
    # Deliberately poison the caller's already-loaded verifier. It cannot leak
    # into either subprocess, even when disk identities describe approved code.
    monkeypatch.setattr(lc.Shifted, "code", lambda *a: None)
    out = tmp_path / "launched"
    launch.measure(out, "synthetic host", root=root, key=stamp.configured_keys()[0])
    b, fr, _ = ca.serve(out, root=root, now=NOW)
    assert fr["authoritative"] and b.receipt["commit"] == commit
    executed = b.receipt["synthetic_execution"]
    assert executed["pid"] != os.getpid() and executed["shift"] == "hardcoded address"
    assert f"/s/{commit[:10]}/tools/" in executed["driver"]
    assert Path(executed["driver"]).parent == Path(executed["adapter"]).parent


def test_r2_launcher_rejects_preexecution_tool_digest_mismatch(checkout, tmp_path, monkeypatch):
    root, _ = synthetic_snapshot_checkout(checkout)
    original = launch.frozen_tools
    def mismatched(*args):
        return dict(original(*args), implementation_sha256="0" * 64)
    monkeypatch.setattr(launch, "frozen_tools", mismatched)
    out = tmp_path / "refused"
    with pytest.raises(subprocess.CalledProcessError):
        launch.measure(out, "synthetic host", root=root, key=stamp.configured_keys()[0])
    assert not out.exists()


def test_sound_differential_measurement_and_verdicts(tmp_path, monkeypatch):
    """Execute old/new measurement on identical finished records, without linking."""
    original = git(ROOT, "show", BASELINE + ":tools/link_cycle.py")
    prior = types.ModuleType("review_prior_cycle")
    prior.__file__ = str(ROOT / "tools/link_cycle.py")
    exec(compile(original, prior.__file__, "exec"), prior.__dict__)
    current_tree = ast.parse((ROOT / "tools/link_cycle.py").read_text())
    old_tree = ast.parse(original)
    old_nodes = {n.name: n for n in old_tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    new_nodes = {n.name: n for n in current_tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    # Review 2 deliberately tightens Measure/Shifted and source provenance.
    # Their refusing counterexamples live in test_cycle_review2_evidence;
    # retain differential coverage of the unaffected link setup and closure.
    for name in ("load_pins", "greatest_closure",
                 "plan_order", "filler_chunks", "read_map", "zz_objects", "object_identity"):
        assert ast.dump(old_nodes[name]) == ast.dump(new_nodes[name]), name
    # Currency now accepts caller-owned receipts and reports the proof kind.
    # Every other census node, including all verdict policy, stays identical.
    def census_policy(source):
        tree = ast.parse(source)
        tree.body = [node for node in tree.body
                     if not (isinstance(node, ast.FunctionDef)
                             and node.name in {"object_current", "stale_objects"})
                     and not (isinstance(node, ast.Assign)
                              and any(isinstance(t, ast.Name) and t.id == "_DEFAULT_RECEIPTS"
                                      for t in node.targets))]
        return ast.dump(tree)
    assert census_policy(git(ROOT, "show", BASELINE + ":tools/link_census.py")) == census_policy(
        (ROOT / "tools/link_census.py").read_text())
    # All keep-rule verdict combinations and selected-owner choices agree.
    old_census = types.ModuleType("review_prior_census")
    old_census.__file__ = str(ROOT / "tools/link_census.py")
    monkeypatch.setitem(sys.modules, old_census.__name__, old_census)
    exec(compile(git(ROOT, "show", BASELINE + ":tools/link_census.py"), old_census.__file__, "exec"), old_census.__dict__)
    for verdicts in itertools.product((None, "retail", "wrong", "unknown"), repeat=3):
        copies = [(str(i), "x" if i < 2 else "y", v) for i, v in enumerate(verdicts)]
        assert census.keep_rule(copies) == old_census.keep_rule(copies)
        for holder in (None, "0", "1", "2"):
            args = holder, {o: (d, v) for o, d, v in copies}, {"0", "1", "2"}, {"0"}, {"1"}
            assert census.judge_selected(*args) == old_census.judge_selected(*args)
    for kind, shift_failure in itertools.product(("real", "generated", "asm", "gen-alias"), (False, True)):
        results, statuses = [], []
        for module in (prior, lc):
            out = tmp_path / (module.__name__ + kind + str(shift_failure))
            out.mkdir()
            (out / "base.map").write_text("")
            rows = [{"name": "f", "kind": "real", "source": "game/f.cpp", "rva": 0x1000, "size": 4},
                    {"name": "g", "kind": kind, "source": "game/g.cpp", "rva": 0x1100, "size": 4}]
            units = [{"id": i, "head": r["name"], "rows": [r]} for i, r in enumerate(rows)]
            recs = [{"row": r, "unit": u, "measured": True, "placed": 1, "linked": r["rva"], "fails": [],
                     "edges": {("unit", 1)} if i == 0 else set(), "masked": set(), "rels": [], "unpinned": False}
                    for i, (r, u) in enumerate(zip(rows, units))]
            m = types.SimpleNamespace(run=lambda: recs, twins={}, dnodes={}, eh=collections.Counter(),
                                      import_equiv=0, ilt_routes=collections.Counter(), back={})
            sh = types.SimpleNamespace(code=lambda *a: "hardcoded address" if shift_failure else None,
                                       summary=lambda: {"checked": True})
            with monkeypatch.context() as patch:
                patch.setattr(module, "Measure", lambda *a: m)
                patch.setattr(module, "Shifted", lambda *a: sh)
                patch.setattr(module, "pe_view", lambda p: (None, bytes(0x3000), {".text": (0x1000, 0x2000)}, {}))
                patch.setattr(module, "zz_names", lambda p: ({}, []))
                result = module.measure(out, units, [], types.SimpleNamespace(by_base={}), bytes(0x3000),
                                        {".text": (0x1000, 0x2000)}, {}, {}, True, module.SHIFT_BASE)
            result.pop("data_back", None)
            result.pop("closure_graph_sha256", None)
            results.append(result)
            statuses.append((out / "link_status.csv").read_bytes())
        assert results[0] == results[1] and statuses[0] == statuses[1]
    print("SOUND old/new: 8 finished-record scenarios identical; 64 keep_rule and 256 judge_selected cases identical; link setup AST identical")


def test_r1_unstamped_bundle_has_labelled_diagnostic_cli(checkout, tmp_path, monkeypatch, capsys):
    root, _ = checkout
    run, _ = run_for(checkout, tmp_path / "run")
    out = freeze(run, tmp_path / "bundle", root, sign=False)
    original = ca.load_bundle
    monkeypatch.setattr(ca, "load_bundle", lambda path: original(path, root=root))
    monkeypatch.setattr(ca.time, "time", lambda: NOW)
    assert ca.main(["inspect", str(out)]) == 0
    assert "NOT AUTHORITATIVE: not-authoritative / unstamped" in capsys.readouterr().out


def test_r1_reader_ignores_environment_host_keys(checkout, tmp_path, monkeypatch):
    root, _ = checkout
    run, _ = run_for(checkout, tmp_path / "run")
    out = freeze(run, tmp_path / "bundle", root)
    original = stamp.configured_keys()[0]
    other = stamp.keygen(tmp_path / "second-host-key")
    monkeypatch.setenv("BFME_CYCLE_KEYS", str(other) + __import__("os").pathsep + str(original))
    assert ca.serve(out, root=root, now=NOW)[1]["authoritative"]


def test_r2_launcher_rejects_receipt_semantic_digest_mismatch(checkout, tmp_path):
    root, _ = synthetic_snapshot_checkout(checkout)
    driver = root / "tools/link_cycle.py"
    source = driver.read_text()
    needle = '    receipt["synthetic_execution"] = '
    before = source.index(needle)
    source = source[:before] + (
        '    receipt["tool_dependencies"]["link_cycle.py"] = "f" * 64\n'
        '    receipt["rule_identity"] = context.rule_identity(receipt["tool_dependencies"])\n'
        '    receipt["tool_digest"] = context.digest(receipt["tool_dependencies"])\n') + source[before:]
    driver.write_text(source)
    git(root, "add", "tools/link_cycle.py")
    git(root, "-c", "core.hooksPath=.githooks", "-c", "user.name=R1 fixture",
        "-c", "user.email=r1@example.invalid", "commit", "-qm", "inert dishonest receipt")
    git(root, "update-ref", "refs/remotes/origin/master", "HEAD")
    out = tmp_path / "refused"
    with pytest.raises(ca.BundleError, match="executed semantic dependency digest"):
        launch.measure(out, "synthetic host", root=root, key=stamp.configured_keys()[0])
    assert not out.exists()
