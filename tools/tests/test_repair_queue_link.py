"""Phase 3 queue regressions. Synthetic files only; no compiler/census/measurement.

Subprocesses in the existing test_repair_queue.py use only git and Python -c.
Bundle fixtures call serialization and graph analysis helpers, never real linking.
"""
import csv
import importlib
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cycle_fixture import NOW, bundle, measured_run, rehash, save_receipt
import closure_report as cr
import cycle_artifacts as ca
import eligibility
import link_cycle as lc
import publish_cycle as pc

SHARED_SERVABLE = eligibility.servable


@pytest.fixture
def rq(monkeypatch):
    monkeypatch.delenv("REPAIR_ROOT", raising=False)
    monkeypatch.delenv("REPAIR_LINK_STATUS", raising=False)
    import repair_queue
    module = importlib.reload(repair_queue)
    # Never fetch real host claims or run fleet discovery. Specific tests replace
    # this with the shared predicate's test double and assert it is called.
    monkeypatch.setattr(eligibility, "servable", lambda **kw: lambda rva: True)
    return module


def local_status(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ca.STATUS_COLUMNS)
        w.writeheader()
        for name, rva, placed, strict, size in [("ok", 0x1000, 1, 1, 100),
                                               ("far", 0x2000, 0, 1, 500),
                                               ("wire", 0x3000, 1, 0, 40)]:
            row = dict.fromkeys(ca.STATUS_COLUMNS, "0")
            row.update(name=name, kind="real", source=f"game/{name}.cpp", retail_rva=f"0x{rva:08X}",
                       size=str(size), placed=str(placed), self_strict=str(strict), failures="data-back:x",
                       placement_reason="alignment")
            w.writerow(row)
    return path


def census(rq, root):
    rq.ROOT = root
    rq.CENSUS_STATUS = "targets/game/reverse/link_status.csv"
    rq.CENSUS_HISTORY = "targets/game/reverse/link_census_history.csv"
    rev = root / "targets/game/reverse"
    rev.mkdir(parents=True)
    (rev / "link_status.csv").write_text("source,linked,unresolved\ngame/wire.cpp,no,1\ngame/ok.cpp,yes,0\n")
    (rev / "link_census_history.csv").write_text("commit,date\nabc,2026-10-22 12:00\n")
    rq.ledger.cache_clear()
    (rev / "functions.csv").write_text("name,target_rva,target_size,source,status\n"
                                       "wire,0x3000,40,game/wire.cpp,matched\n"
                                       "ok,0x1000,100,game/ok.cpp,matched\n")
    return rev


def test_bfme1_guard_removed_and_eligibility_claims_used(rq, tmp_path, monkeypatch):
    calls = []
    def servable(**kw):
        calls.append(kw)
        return lambda rva: rva != 0x2000  # shared eligibility/claims rejection
    monkeypatch.setattr(eligibility, "servable", servable)
    items, note = rq.link_items(local_status(tmp_path / "status.csv"))
    assert [i["function"] for i in items] == ["wire"]
    assert items[0]["claim_required"]
    assert items[0]["claim_command"] == "python3 tools/claims.py claim 0x00003000"
    assert items[0]["credit"] == 0  # extent is not a proven closure gain
    assert calls == [{"root": rq.ROOT}]
    assert "LOCAL DIAGNOSTIC" in note and "non-authoritative" in note


def test_local_census_fallback_and_explicit_cycle_precedence(rq, tmp_path, monkeypatch):
    census(rq, tmp_path)
    rq.LINK_STATUS = str(tmp_path / "missing.csv")
    items, note = rq.link_items()
    assert [i["function"] for i in items] == ["wire"]
    assert "committed link census" in note and "abc" in note
    assert items[0]["credit"] == 0
    # No receipt: automatic local source must be at least as new as the census.
    status = local_status(tmp_path / "status.csv")
    os.utime(status, (0, 0))
    rq.LINK_STATUS = str(status)
    assert rq.link_source()[0] == "census"
    assert "not newer" in rq.link_source()[2]
    assert rq.link_source(status)[0] == "cycle"  # explicitly named local diagnostic


def test_gzip_status_and_passing_rows_excluded(rq, tmp_path):
    plain = local_status(tmp_path / "status.csv")
    compressed = tmp_path / "status.csv.gz"
    pc.gzip_bytes(plain.read_bytes(), compressed)
    assert [i["function"] for i in rq.cycle_items(compressed)] == ["wire", "far"]


def failed_bundle(tmp_path, *, eh=False, only_joint=False):
    """Two failing roots, one single-root beneficiary, one joint-only and one passing row."""
    run, receipt = measured_run(tmp_path / "run")
    specs = [(1, 0x1000, 20, False, True), (2, 0x2000, 10, False, True),
             (3, 0x3000, 30, True, True), (4, 0x4000, 100, True, True),
             (5, 0x5000, 8, True, True), (6, 0x6000, 1000, True, False)]
    nodes = {f"unit:{i}": {"kind": "unit", "ok": strict, "name": f"f{i}", "rva": rva,
                            "source": f"game/f{i}.cpp", "failures": [] if strict else ["data-back:x"]}
             for i, rva, size, strict, placed in specs}
    if eh:
        nodes["eh:40960"] = {"kind": "eh", "ok": False, "failures": ["shift"]}
    # A joint-only graph still contains the failing roots as measured nodes,
    # but no authored/placed own rows to give them individual credit.
    if only_joint:
        specs = [s for s in specs if s[0] not in (1, 2, 3)]
    doc = {"schema": ca.context.GRAPH_SCHEMA, "rules": ca.context.RULES,
           "bad_targets": list(ca.context.BAD_TARGETS), "nodes": nodes,
           "edges": {"unit:3": ["unit:1"], "unit:4": ["unit:1", "unit:2"],
                     **({"unit:5": ["eh:40960"]} if eh else {})},
           "rows": [[f"f{i}", "real", f"game/f{i}.cpp", rva, size, f"unit:{i}", int(placed), int(strict)]
                    for i, rva, size, strict, placed in specs]}
    lc.write_closure_graph(run / ca.CLOSURE_GRAPH, doc)
    graph = cr.graph_from_doc(doc)
    closed = cr.reference_closure(graph[0], graph[1])
    with (run / "link_status.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ca.STATUS_COLUMNS)
        w.writeheader()
        for i, rva, size, strict, placed in specs:
            row = dict.fromkeys(ca.STATUS_COLUMNS, "0")
            row.update(name=f"f{i}", kind="real", source=f"game/f{i}.cpp", retail_rva=f"0x{rva:08X}",
                       size=str(size), placed=str(int(placed)), self_strict=str(int(strict)),
                       linked_rva=f"0x{rva:08X}",
                       closed_strict=str(int(strict and ("unit", f"unit:{i}") in closed)),
                       failures="" if strict else "data-back:x", placement_reason="" if placed else "alignment")
            w.writerow(row)
    receipt["closure_graph_sha256"] = ca.sha256_file(run / ca.CLOSURE_GRAPH)
    receipt["series"].update(closure_graph_sha256=receipt["closure_graph_sha256"],
                             link_status_sha256=ca.sha256_file(run / "link_status.csv"),
                             credit_unique_bytes=cr.credit_of(*graph[:3]))
    save_receipt(run, receipt)
    return bundle(tmp_path, run=run)


@pytest.fixture
def failing(tmp_path, monkeypatch):
    monkeypatch.setattr(ca.time, "time", lambda: NOW)
    return failed_bundle(tmp_path)


@pytest.mark.parametrize("reason,route,code", [
    ("corrupt", "tooling seat", 1), ("unavailable", "use another work lane", 2),
    ("empty", "use another work lane", 3), ("stale", "use another work lane", 4),
    ("incompatible-rules", "tooling seat / human review", 5), ("unauthenticated", "refuse", 6),
    ("no-closure-report", "ordinary link queue, no closure ranking", 7)])
def test_reason_router_api_and_json_exit(rq, monkeypatch, capsys, reason, route, code):
    assert rq.failure_route(reason) == {"reason": reason, "route": route, "exit_code": code}
    assert ca.EXIT[reason] == code
    calls = []
    def serve(*args, **kwargs):
        calls.append(kwargs)
        raise ca.Refused("synthetic rejection", reason)
    monkeypatch.setattr(ca, "serve", serve)
    def forbidden(*args, **kw):
        pytest.fail("explicit bundle failure fell back to local/census files")
    monkeypatch.setattr(rq, "link_source", forbidden)
    assert rq.main(["link", "--bundle", "current", "--closure", "--route", "--json"]) == code
    got = json.loads(capsys.readouterr().out)
    assert got["reason"] == reason and got["route"] == route and got["exit_code"] == code
    assert got["items"] == [] and got["closure_ranking"] is False
    assert calls[0]["allow_stale"] is False and len(calls) == 1


def test_default_empty_allowlist_refuses_real_bundle_and_router(rq, failing, capsys):
    assert ca.PUBLISHERS == () and ca.DEFAULT_REPO is None
    result = rq.route_link_queue(failing, now=NOW)
    assert result["reason"] == "unauthenticated" and result["exit_code"] == 6
    assert not result["items"]
    assert rq.main(["link", "--bundle", str(failing), "--json"]) == 6
    assert json.loads(capsys.readouterr().out)["route"] == "refuse"


@pytest.mark.parametrize("closure", [False, True])
def test_local_unpublished_inspection_is_labelled_but_never_routed(rq, failing, capsys, closure):
    result = rq.link_queue(failing, local_unpublished=True, closure=closure, now=NOW)
    assert result["exit_code"] == 0 and result["route"] is None
    assert result["diagnostic"] and not result["authoritative"]
    assert all(i["diagnostic"] and not i["authoritative"] for i in result["items"])
    assert "never routed" in result["notes"][0] and "UNAUTHENTICATED" in result["notes"][0]
    routed = rq.route_link_queue(failing, local_unpublished=True, closure=closure, now=NOW)
    assert routed["reason"] == "unauthenticated" and routed["items"] == []
    flags = ["--closure"] if closure else []
    assert rq.main(["link", "--bundle", str(failing), "--local-unpublished", "--route", "--json", *flags]) == 6
    assert json.loads(capsys.readouterr().out)["items"] == []


def test_closure_ranking_order_joint_separation_and_passing_rows(rq, failing, capsys):
    result = rq.link_queue(failing, closure=True, local_unpublished=True, now=NOW)
    assert [(i["function"], i["conditional_gain_bytes"]) for i in result["items"]] == [("f1", 50), ("f2", 10)]
    assert result["joint_only"]["candidate_unique_bytes"] == 100
    assert result["joint_only"]["non_additive"] is True
    assert all(i["non_additive"] and i["credit"] == i["conditional_gain_bytes"] for i in result["items"])
    assert "total_gain" not in result  # no additive aggregate, including across --limit
    ordinary = rq.link_queue(failing, local_unpublished=True, now=NOW)
    assert [i["function"] for i in ordinary["items"]] == ["f1", "f2", "f6"]
    assert all(i["credit"] == 0 for i in ordinary["items"])
    assert rq.main(["link", "--bundle", str(failing), "--closure", "--local-unpublished", "--json", "--limit", "1"]) == 0
    got = json.loads(capsys.readouterr().out)
    assert len(got["items"]) == 1 and got["items"][0]["credit"] == 50
    assert got["joint_only"]["candidate_unique_bytes"] == 100
    assert rq.main(["link", "--bundle", str(failing), "--closure", "--local-unpublished", "--limit", "1"]) == 0
    text = capsys.readouterr().out
    assert "JOINT-ONLY" in text and "do not add them" in text and "never included" in text


def test_bundle_eligibility_applies_after_ranking(rq, failing, monkeypatch):
    seen = []
    def shared(**kwargs):
        assert kwargs == {"root": rq.ROOT}
        def ok(rva):
            seen.append(rva)
            return rva != 0x1000
        return ok
    monkeypatch.setattr(eligibility, "servable", shared)
    result = rq.link_queue(failing, local_unpublished=True, closure=True, now=NOW)
    assert [i["function"] for i in result["items"]] == ["f2"]
    assert set(seen) == {0x1000, 0x2000}
    assert result["items"][0]["claim_required"]


def test_current_alias_uses_cycle_store_without_local_fallback(rq, failing, tmp_path, monkeypatch):
    store = tmp_path / "store"
    ca.install_local(failing, store, local_unpublished=True, now=NOW)
    monkeypatch.setattr(ca, "DEFAULT_STORE", store)
    assert rq.link_queue("current", now=NOW)["reason"] == "unauthenticated"
    result = rq.link_queue("current", local_unpublished=True, closure=True, now=NOW)
    assert result["exit_code"] == 0 and result["items"][0]["credit"] == 50


@pytest.mark.parametrize("closure", [False, True])
def test_stale_never_auto_overridden_and_explicit_override_recorded(rq, failing, monkeypatch, capsys, closure):
    monkeypatch.setattr(ca.time, "time", lambda: NOW + 25 * 3600)
    flags = ["--closure"] if closure else []
    args = ["link", "--bundle", str(failing), "--local-unpublished", "--json", *flags]
    assert rq.main(args) == 4
    got = json.loads(capsys.readouterr().out)
    assert got["reason"] == "stale" and got["allow_stale"] is False and got["items"] == []
    assert rq.main([*args, "--allow-stale"]) == 0
    got = json.loads(capsys.readouterr().out)
    assert got["allow_stale"] is True and got["freshness"]["stale"] is True
    assert "allow_stale=True" in got["notes"][0]
    # Human freshness override does not authenticate a bundle for a router.
    assert rq.route_link_queue(failing, allow_stale=True)["reason"] == "unauthenticated"


def test_missing_empty_corrupt_and_incompatible_bundle_failures(rq, failing, tmp_path, monkeypatch):
    assert rq.link_queue(tmp_path / "absent")["reason"] == "unavailable"
    empty = tmp_path / "empty"
    empty.mkdir()
    assert rq.link_queue(empty)["reason"] == "empty"
    other_root = tmp_path / "other-checkout"
    other_root.mkdir()
    monkeypatch.setattr(rq, "ROOT", other_root)
    assert rq.link_queue(failing, local_unpublished=True, now=NOW)["reason"] == "incompatible-rules"
    # Incompatibility/future checks cannot be bypassed with a freshness override.
    assert rq.link_queue(failing, local_unpublished=True, allow_stale=True, now=NOW)["reason"] == "incompatible-rules"
    (failing / ca.LINK_STATUS).write_bytes(b"broken gzip")
    assert rq.link_queue(failing, local_unpublished=True, now=NOW)["reason"] == "corrupt"


def test_future_not_overridden(rq, failing):
    result = rq.link_queue(failing, local_unpublished=True, allow_stale=True, now=NOW - 601)
    assert result["reason"] == "corrupt" and result["items"] == []


def test_no_closure_report_routes_ordinary_queue_without_local_fallback(rq, failing, monkeypatch):
    # Current BFME1 profile requires the report pair; this tests the explicit
    # missing-report routing signal, not admission of a reduced bundle profile.
    from cycle_fixture import rewrite_manifest
    rewrite_manifest(failing, lambda m: m["members"].pop(ca.CLOSURE_ROOTS))
    monkeypatch.setattr(rq, "link_source", lambda *a: pytest.fail("no bundle fallback allowed"))
    result = rq.link_queue(failing, closure=True, local_unpublished=True, now=NOW)
    assert result["reason"] == "no-closure-report" and result["exit_code"] == 7
    assert result["route"] == "ordinary link queue, no closure ranking" and result["items"] == []


@pytest.mark.parametrize("field", ["gain", "summary", "nodes", "extra-root"])
def test_forged_report_claims_rejected_even_after_manifest_rehash(rq, failing, field):
    doc = ca.read_json(failing / ca.CLOSURE_ROOTS)
    if field == "gain":
        doc["roots"][0]["conditional_gain_bytes"] += 10000
    elif field == "summary":
        doc["summary"]["joint_only"]["candidate_unique_bytes"] += 10000
    elif field == "nodes":
        # Masquerade as a passing beneficiary row while keeping the score.
        doc["roots"][0]["nodes"][0].update(name="f3", source="game/f3.cpp", retail_rva="0x00003000")
    else:
        doc["roots"].append(dict(doc["roots"][0], root="0x00005000"))
    pc.gzip_bytes(ca.dumps(doc).encode(), failing / ca.CLOSURE_ROOTS)
    rehash(failing, ca.CLOSURE_ROOTS)
    result = rq.link_queue(failing, closure=True, local_unpublished=True, now=NOW)
    assert result["reason"] == "corrupt" and result["items"] == []


def test_all_passing_bundle_is_empty_and_flags_need_explicit_bundle(rq, tmp_path, monkeypatch):
    monkeypatch.setattr(ca.time, "time", lambda: NOW)
    passing = bundle(tmp_path)
    assert rq.link_queue(passing, local_unpublished=True, now=NOW)["reason"] == "empty"
    assert rq.link_queue(passing, closure=True, local_unpublished=True, now=NOW)["reason"] == "empty"
    for flags in ({"closure": True}, {"allow_stale": True}, {"local_unpublished": True}):
        assert rq.link_queue(**flags)["reason"] == "unavailable"


def test_real_shared_eligibility_includes_claims(rq, failing, monkeypatch):
    import claims
    import fleet_run
    calls = []
    def active(root):
        calls.append(root)
        return {0x1000: {"owner": "another-seat"}}
    monkeypatch.setenv("BFME_CLAIMS", "on")
    monkeypatch.setattr(eligibility, "servable", SHARED_SERVABLE)
    monkeypatch.setattr(claims, "active", active)
    monkeypatch.setattr(fleet_run, "active_rvas", lambda root: set())
    monkeypatch.setattr(eligibility, "legacy_busy_tokens", lambda *a: set())
    monkeypatch.setattr(eligibility, "recent_run_rvas", lambda *a: set())
    monkeypatch.setattr(eligibility, "latest_verdicts", lambda: {})
    monkeypatch.setattr(eligibility.re_log, "latest_records", lambda: {})
    monkeypatch.setattr(eligibility, "attempt_counts", lambda: {})
    monkeypatch.setattr(eligibility, "unlocked_rvas", lambda: set())
    result = rq.link_queue(failing, closure=True, local_unpublished=True, now=NOW)
    assert result["exit_code"] == 0
    assert [i["function"] for i in result["items"]] == ["f2"]
    assert calls == [rq.ROOT]


def test_roots_without_retail_address_are_reported_but_not_claimed(rq, tmp_path, monkeypatch):
    monkeypatch.setattr(ca.time, "time", lambda: NOW)
    result = rq.link_queue(failed_bundle(tmp_path, eh=True), closure=True, local_unpublished=True, now=NOW)
    assert result["exit_code"] == 0
    assert [i["function"] for i in result["items"]] == ["f1", "f2"]
    assert any("no retail address" in n and "eh:0x0000A000" in n for n in result["notes"])


def test_joint_only_candidates_remain_visible_when_no_single_root_can_be_served(rq, tmp_path, monkeypatch):
    monkeypatch.setattr(ca.time, "time", lambda: NOW)
    result = rq.link_queue(failed_bundle(tmp_path, only_joint=True), closure=True, local_unpublished=True, now=NOW)
    assert result["reason"] == "empty" and result["exit_code"] == 3
    assert result["items"] == [] and result["joint_only"]["candidate_unique_bytes"] == 100
    assert result["joint_only"]["non_additive"] is True
