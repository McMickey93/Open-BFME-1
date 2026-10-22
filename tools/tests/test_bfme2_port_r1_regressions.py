"""R1 regression tests; PASS means the defect is prevented.

Only synthetic images, artifacts and temporary git repositories. Never run a
compiler, linker, census, cycle(), Wine, or the general tools/tests suite.
Run: ~/.cache/bfme-venv/bin/python -m pytest -q -s tools/tests/test_bfme2_port_review_r1.py
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
from cycle_fixture import NOW, measured_run, save_receipt, rehash
import closure_report as cr
import cycle_artifacts as ca
import cycle_diff as cd
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
        "repair_queue.py", "cycle_diff.py", "data_back_rank.py"}
    for name in names:
        shutil.copyfile(ROOT / "tools" / name, root / "tools" / name)
    reverse = root / "targets/game/reverse"
    reverse.mkdir(parents=True)
    for name in ("functions", "symbols", "data_rows"):
        (reverse / (name + ".csv")).write_text("synthetic ledger\n")
    (root / ".gitignore").write_text("build/\n__pycache__/\n")
    git(root, "init", "-q")
    git(root, "add", "tools", "targets", ".gitignore")
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
    return measured_run(path, commit=commit, deps=ca.local_dependencies(root), **kwargs)


def freeze(run, out, root, **kwargs):
    pc.make_bundle(run, out, "R1 synthetic reproduction", root=root, **kwargs)
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
    print("F3 shift-only root: gain=10; ordinary=empty; closure=empty")


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
        print("F4 census alias_target=1 alias_unknown=1 -> blockers=0; reason=" + item["why"])
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
        print("F5 data-only provider: linked=no unresolved=1; router=empty")
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
        print("F11 dirty census: invented blockers=12345; label=committed link census; router=ordinary link queue")
    finally:
        rq.ledger.cache_clear()




def test_r9_publisher_replaces_destination_created_during_validation(checkout, tmp_path, monkeypatch):
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
    print("F9 publication race: pre-existing destination inode replaced=True")


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
    print("F10 malformed closure score table: serve(need_closure=True) authoritative=True; repair queue alone detects corrupt")


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
    print("F8 unchanged predecessor identity: actual gain=0; accepted gain=10; authoritative=True")


def test_r8_missing_historical_evidence_never_counts(tmp_path):
    a, _ = measured_run(tmp_path / "a")
    b, _ = measured_run(tmp_path / "b", now=NOW + 1)
    doc = cd.compare(a, b)
    doc.pop("evidence")
    with pytest.raises(cd.CycleDiffError):
        cd.check_report(doc)
    doc.update(comparison_verified=False, totals=None, gained=None, lost=None)
    cd.check_report(doc)
