"""Synthetic BFME1 cycle artifacts; never compile, census, or link a real image."""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import closure_report as cr
import cycle_artifacts as ca
import link_cycle as lc
import link_cycle_context as context
import publish_cycle as pc

NOW = 1792670400  # Fixed UTC epoch, independent of the runner's wall clock.


def measured_run(path, *, now=NOW, commit="a" * 40, name="f", deps=None, empty=False):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    rows = [] if empty else [[name, "real", "game/f.cpp", 0x1000, 10, "unit:1", 1, 1]]
    graph = {"schema": context.GRAPH_SCHEMA, "rules": context.RULES,
             "bad_targets": list(context.BAD_TARGETS),
             "nodes": {} if empty else {"unit:1": {"kind": "unit", "ok": True, "name": name,
                                                 "rva": 0x1000, "source": "game/f.cpp", "failures": []}},
             "edges": {}, "rows": rows}
    lc.write_closure_graph(path / ca.CLOSURE_GRAPH, graph)
    with (path / "link_status.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ca.STATUS_COLUMNS)
        w.writeheader()
        if rows:
            row = dict.fromkeys(ca.STATUS_COLUMNS, "0")
            row.update(name=name, kind="real", source="game/f.cpp", retail_rva="0x00001000", size="10",
                       linked_rva="0x00001000", placed="1", self_strict="1", closed_strict="1", failures="")
            w.writerow(row)
    deps = context.tool_dependencies() if deps is None else deps
    h = "e" * 64
    receipt = {"tool": "link_cycle", "commit": commit, "rules": context.RULES,
               "rule_identity": context.rule_identity(deps), "tool_dependencies": deps,
               "tool_digest": context.digest(deps), "target": {"sha256": h, "machine": 0x14c,
                                                                "image_base": 0x400000, "size_of_image": 0xA00000},
               "retail_sha256": h, "inputs": dict.fromkeys(ca.LEDGERS, h), "objects_digest": h,
               "provenance_sha256": h, "objects_canon_digest": h, "provenance_canon_sha256": h,
               "canon_rules": lc.CANON_RULES, "objects": 1, "objects_missing": 0,
               "authoritative": True, "snapshot": False, "dirty": False, "allow_dirty": False,
               "compile_failed": [], "warm_start": {"stale": False},
               "checkout_start": {"commit": commit, "snapshot": False, "dirty": False},
               "checkout_end": {"commit": commit, "snapshot": False, "dirty": False},
               "run_options": dict.fromkeys(context.RUN_OPTIONS, False), "submodules": {}, "tree_manifest": h,
               "date_utc": ca.iso_utc(now), "measured_end_ns": int(now * 1e9), "seconds": {"total": 10},
               "closure_graph_sha256": ca.sha256_file(path / ca.CLOSURE_GRAPH),
               "series": {"credit_unique_bytes": 0 if empty else 10,
                          "link_status_sha256": ca.sha256_file(path / "link_status.csv"),
                          "closure_graph_sha256": ca.sha256_file(path / ca.CLOSURE_GRAPH)}}
    save_receipt(path, receipt)
    return path, receipt


def save_receipt(path, receipt):
    lc.stamp_cores(receipt)
    (Path(path) / ca.RECEIPT).write_text(ca.dumps(receipt))


def bundle(path, *, run=None, first=False, **kwargs):
    run, _ = measured_run(path / "run") if run is None else (run, None)
    dest = path / "bundle"
    pc.make_bundle(run, dest, "synthetic-bfme1-test", first=first, **kwargs)
    return dest


def rewrite_manifest(directory, fn):
    path = directory / ca.MANIFEST
    doc = ca.read_json(path)
    fn(doc)
    path.write_text(ca.dumps(doc))


def rehash(directory, name):
    rewrite_manifest(directory, lambda m: m["members"].update({name: ca.member_meta(directory / name)}))


# Existing serializer/queue unit tests use deliberately invented commits. Their
# execution evidence is stubbed explicitly; real Git/host-bound checks live in
# test_bfme2_port_r1_regressions.py and do not use this fixture.
import pytest


@pytest.fixture(autouse=True)
def synthetic_host(tmp_path, monkeypatch):
    import cycle_stamp
    key = cycle_stamp.keygen(tmp_path / "host-key")
    monkeypatch.setenv("BFME_CYCLE_KEYS", str(key))
    monkeypatch.setattr(ca, "run_evidence_failure", lambda *a: None)
    original = pc.make_bundle

    def signed(*args, **kwargs):
        result = original(*args, **kwargs)
        host_stamp(Path(args[1]), key)
        return result
    monkeypatch.setattr(pc, "make_bundle", signed)


def host_stamp(directory, key):
    """Simulate a trusted measuring host, only for synthetic tests."""
    import hashlib
    import hmac
    import cycle_stamp
    secret = cycle_stamp.read_key(key)
    digest = ca.sha256_file(directory / ca.MANIFEST)
    (directory / cycle_stamp.STAMP).write_text(ca.dumps({
        "schema": cycle_stamp.SCHEMA, "manifest_sha256": digest,
        "key_id": hashlib.sha256(secret).hexdigest(),
        "hmac_sha256": hmac.new(secret, bytes.fromhex(digest), hashlib.sha256).hexdigest()}))
