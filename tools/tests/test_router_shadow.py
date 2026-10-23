"""Synthetic shadow comparisons: diagnostics never route or acquire leases."""
import copy
import json
from pathlib import Path
import pickle
import subprocess
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import router_shadow as S
import link_cycle as lc
import link_cycle_context as context
from cycle_fixture import measured_run, save_receipt
from test_comdat_families import census, NAME


def status(rva=0x1000, name="root", source="game/root.cpp", passed=False):
    return {"retail_rva": f"0x{rva:08X}", "name": name, "source": source,
            "placed": "1", "self_strict": str(int(passed)), "closed_strict": str(int(passed))}


@pytest.fixture
def view():
    return {"items": [], "proof": {"0x00001000": 30}, "joint_only": {"candidate_unique_bytes": 45},
            "status": [status()], "metadata": {"authoritative": False, "reason": "not-authoritative",
                                                  "comparison_only": True, "freshness": {"stale": False}}}


def root(gain=30):
    return {"kind": "closure", "key": "0x00001000", "rva": "0x00001000", "name": "root",
            "sources": ["game/root.cpp"], "family": None, "donor_tier": None,
            "single_root_bytes": gain, "proved_single_root_bytes": 30, "identity_claimed": False,
            "edit_targets": []}


def donor(*, evidence=None):
    record = {"name": "?donor@@YAXXZ", "source": "Code/donor.cpp", "placement": "unique", "donor_names": ["?donor@@YAXXZ"]}
    hit = {"rva": 0x8000, "size": 10, "tier": "T2", "work_status": "open", "identity_evidence": evidence or [],
           "target_rows": [], "layout_disagreement": [], "exact": True, "strings": [],
           "other_identities": [], "callee_conflicts": [], "extent_conflict": False}
    hit["tier"] = S.sweep.tier_for(record, hit)
    return record, hit


def check(candidate, view, **kwargs):
    return S.invariant_violations(candidate, status=view["status"], proof=view["proof"], matched=kwargs.pop("matched", set()),
                                  eligible=kwargs.pop("eligible", True), claimable=kwargs.pop("claimable", True),
                                  routed=kwargs.pop("routed", False), authoritative=kwargs.pop("authoritative", False), **kwargs)


@pytest.mark.parametrize("passed", [False, True])
def test_already_passing_assertion(view, passed):
    view["status"] = [status(passed=passed)]
    assert ("new-already-passing" in check(root(), view)) == passed


@pytest.mark.parametrize("gain,violates", [(0, False), (30, False), (31, True), (75, True), (-1, True)])
def test_single_root_gain_never_borrows_joint_bytes(view, gain, violates):
    assert ("gain-exceeds-closure-proof" in check(root(gain), view)) == violates


def test_missing_root_cannot_claim_gain(view):
    view["proof"] = {}
    assert "gain-exceeds-closure-proof" in check(root(), view)


@pytest.mark.parametrize("claimed", [False, True])
def test_donor_placement_never_identity(view, claimed):
    item = S.donor_candidate(*donor())
    item["identity_claimed"] = claimed
    assert ("placement-upgraded-to-identity" in check(item, view)) == claimed


@pytest.mark.parametrize("evidence", [[], [{"kind": "unique-placement"}],
                                       [{"kind": "same-decorated-symbol", "name": "?donor@@YAXXZ", "rva": 0x8000, "source": "game/donor.cpp"}]])
def test_forged_t1_needs_independent_target_identity(view, evidence):
    item = S.donor_candidate(*donor(evidence=evidence))
    item["donor_tier"] = "T1"
    assert "placement-upgraded-to-identity" in check(item, view)


def test_donor_target_identity_uses_existing_provider(view, monkeypatch):
    evidence = [{"kind": "same-decorated-symbol", "name": "?donor@@YAXXZ", "rva": 0x8000, "source": "game/donor.cpp"}]
    record, hit = donor(evidence=evidence)
    hit["target_rows"] = [{"name": record["name"], "target_rva": "0x00008000", "source": "game/donor.cpp"}]
    monkeypatch.setattr(S.sweep.placement, "identity_source_keys", lambda rows: {(record["name"], "0x00008000")})
    assert check(S.donor_candidate(record, hit), view) == []


@pytest.mark.parametrize("matched", [set(), {(NAME, "wrong.cpp")}])
def test_comdat_never_edits_matched_body(view, matched):
    report = S.comdat.analyze(census(), {"wrong.cpp": [(100, 110)]})
    item = S.family_candidate(report["families"][0])
    assert item["single_root_bytes"] == 0
    assert ("comdat-changes-matched-body" in check(item, view, matched=matched)) == bool(matched)


@pytest.mark.parametrize("field", ["eligible", "claimable"])
@pytest.mark.parametrize("passed", [True, False])
def test_eligibility_and_claimability_assertions(view, field, passed):
    violations = check(root(), view, **{field: passed})
    assert (("not-eligible" if field == "eligible" else "not-claimable") in violations) == (not passed)


@pytest.mark.parametrize("authoritative,routed,violates", [(False, False, False), (False, True, True), (True, False, False)])
def test_diagnostic_never_routed(view, authoritative, routed, violates):
    assert ("diagnostic-bundle-routed" in check(root(), view, authoritative=authoritative, routed=routed)) == violates


def raw_bundle(tmp_path):
    run, receipt = measured_run(tmp_path / "run")
    graph = {"schema": context.GRAPH_SCHEMA, "rules": context.RULES, "bad_targets": list(context.BAD_TARGETS),
             "nodes": {"unit:1": {"kind": "unit", "ok": False, "name": "f", "rva": 0x1000,
                                  "source": "game/f.cpp", "failures": ["wrong-copy"]}},
             "edges": {}, "rows": [["f", "real", "game/f.cpp", 0x1000, 10, "unit:1", 1, 0]]}
    lc.write_closure_graph(run / S.closure.GRAPH_FILE, graph)
    path = run / "link_status.csv"
    import csv
    rows = list(csv.DictReader(path.read_text().splitlines()))
    rows[0].update(self_strict="0", closed_strict="0")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    receipt.update(closure_graph_sha256=S.artifacts.sha256_file(run / S.closure.GRAPH_FILE))
    receipt["series"].update(credit_unique_bytes=0, closure_graph_sha256=receipt["closure_graph_sha256"],
                              link_status_sha256=S.artifacts.sha256_file(path))
    save_receipt(run, receipt)
    roots, blockers, _ = S.closure.from_graph(run, verify=0)
    (run / "closure").mkdir()
    (run / "closure/closure_roots.json").write_bytes(roots)
    (run / "closure/closure_blockers.csv").write_bytes(blockers)
    return run


def test_raw_bundle_bound_graph_but_never_authoritative(tmp_path):
    run = raw_bundle(tmp_path)
    view = S.bundle_view(run)
    assert view["items"][0]["conditional_gain_bytes"] == 10
    assert view["metadata"]["authoritative"] is False
    assert view["metadata"]["sub_reason"] == "raw-unstamped-diagnostic"


@pytest.mark.parametrize("tamper", ["graph", "status", "gain", "joint", "receipt", "blockers"])
def test_tampered_raw_bundle_refused(tmp_path, tamper):
    run = raw_bundle(tmp_path)
    if tamper == "graph":
        (run / S.closure.GRAPH_FILE).write_bytes(b"tampered")
    elif tamper == "blockers":
        (run / "closure/closure_blockers.csv").write_bytes(b"tampered")
    elif tamper == "status":
        path = run / "link_status.csv"
        path.write_text(path.read_text().replace("game/f.cpp", "game/other.cpp"))
    else:
        path = run / "closure/closure_roots.json"
        doc = json.loads(path.read_text())
        if tamper == "gain":
            doc["roots"][0]["conditional_gain_bytes"] += 1
        elif tamper == "joint":
            doc["summary"]["joint_only"]["candidate_unique_bytes"] += 1
        else:
            doc["receipt_core_sha256"] = "wrong"
        path.write_text(json.dumps(doc))
    with pytest.raises((S.closure.ReportError, S.artifacts.Problem)):
        S.bundle_view(run)


def test_claim_inspection_never_fetches_and_unknown_markers_busy(monkeypatch):
    def read(*args):
        if args[0] == "ls-remote":
            return "a refs/claims/0x00001000\nb refs/claims/0x00002000\nc refs/claims/0x00003000"
        if args[-1] == "a":
            return json.dumps({"expires": 1})
        if args[-1] == "b":
            return json.dumps({"expires": 9999999999})
        raise subprocess.CalledProcessError(1, args)
    monkeypatch.setattr(S, "git", read)
    held, info = S.claim_snapshot()
    assert set(held) == {0x2000, 0x3000}
    assert info["unknown_markers"] == 1


def test_remote_unavailable_fail_closed(monkeypatch):
    monkeypatch.setattr(S, "git", lambda *a: (_ for _ in ()).throw(OSError("offline")))
    held, info = S.claim_snapshot()
    assert held == {} and info["status"] == "unavailable"


def test_mutation_boundaries_refuse_and_restore():
    original = S.claims.active
    with S.inspect_selectors({0x1000: {"owner": "other"}}):
        assert set(S.claims.active()) == {0x1000}
        assert S.repair_queue.repair_turn() is False
        for name in ("claim", "renew", "release", "fetch", "queue_landed"):
            with pytest.raises(RuntimeError, match="mutation"):
                getattr(S.claims, name)([])
    assert S.claims.active is original


def test_real_eligibility_predicate_respects_snapshot(monkeypatch):
    monkeypatch.setattr(S.eligibility, "recent_run_rvas", lambda *a: set())
    monkeypatch.setattr(S.eligibility, "legacy_busy_tokens", lambda *a: set())
    monkeypatch.setattr(S.eligibility, "latest_verdicts", lambda: {})
    monkeypatch.setattr(S.eligibility.re_log, "latest_records", lambda: {})
    monkeypatch.setattr(S.eligibility, "attempt_counts", lambda: {})
    monkeypatch.setattr(S.eligibility, "unlocked_rvas", lambda: set())
    import fleet_run
    monkeypatch.setattr(fleet_run, "active_rvas", lambda *a: set())
    monkeypatch.delenv("BFME_CLAIMS", raising=False)
    with S.inspect_selectors({0x1000: {"owner": "other"}}):
        ok = S.eligibility.servable()
        assert not ok(0x1000) and ok(0x2000)


@pytest.mark.parametrize("blocked", [None, "eligibility", "claim"])
def test_run_no_claim_ledger_or_rotation_writes_and_schema(tmp_path, monkeypatch, view, blocked):
    rev = tmp_path / "targets/game/reverse"
    rev.mkdir(parents=True)
    (rev / "functions.csv").write_bytes(b"name,source,status\r\nroot,game/root.cpp,matched\r\n")
    (rev / "symbols.csv").write_bytes(b"symbol,RVA\r\nroot,0x1000\r\n")
    refs = tmp_path / ".git/refs/claims"
    refs.mkdir(parents=True)
    (refs / "0x1000").write_text("lease")
    rotation = tmp_path / "build/next_work_rotation.json"
    rotation.parent.mkdir()
    rotation.write_text('{"default":7}')
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    index = census()
    index["bytes"] = {"wrong.cpp": 10}
    index_path = tmp_path / "index.pkl"
    index_path.write_bytes(pickle.dumps(index))
    view["items"] = [{"target_rva": "0x00001000", "function": "root", "source": "game/root.cpp", "conditional_gain_bytes": 30}]
    monkeypatch.setattr(S, "ROOT", tmp_path)
    monkeypatch.setattr(S, "claim_snapshot", lambda: ({0x1000: {"owner": "other"}} if blocked == "claim" else {},
                                                      {"status": "remote-read-only"}))
    monkeypatch.setattr(S, "bundle_view", lambda p: copy.deepcopy(view))
    monkeypatch.setattr(S.comdat, "source_intervals", lambda *a: {})
    monkeypatch.setattr(S.eligibility, "servable", lambda **kw: lambda r: blocked != "eligibility")
    monkeypatch.setattr(S.eligibility, "latest_verdicts", lambda: {})
    monkeypatch.setattr(S, "old_choice", lambda rows, scratch: {"key": "0x00001000", "name": "root", "rva": "0x00001000", "sources": ["game/root.cpp"]})
    output = tmp_path / "build/router_shadow/shadow.jsonl"
    args = SimpleNamespace(bundle=tmp_path, index=index_path, donors=None, output=output, count=2, lanes=["closure"])
    records = S.run(args)
    assert all(p.read_bytes() == raw for p, raw in before.items())
    assert set(p for p in refs.rglob("*") if p.is_file()) == {refs / "0x1000"}
    assert {p.name for p in rev.iterdir()} == {"functions.csv", "symbols.csv"}
    assert len(S.check_log(output)) == 2
    assert bool(records[0]["new_choice"]) == (blocked is None)
    assert records[1]["new_choice"] is None and records[1]["old_choice"] is None
    if blocked:
        assert records[0]["skipped_candidates"][0]["reason"] == ("not-eligible" if blocked == "eligibility" else "not-claimable")
    else:
        assert records[0]["agreement"] is True
    assert all(r["schema"] == S.SCHEMA and r["routed"] is False and not r["violations"] for r in records)
    assert set(records[0]) == {"schema", "timestamp_utc", "ordinal", "mode", "sampling", "lane", "old_choice", "new_choice",
                              "routed", "bundle", "root_unlock_score", "family", "donor_tier", "old_stale", "agreement",
                              "eligibility", "assertion_evidence", "old_context", "live_check", "skipped_candidates", "violations"}
    assert S.main(["--output", str(output), "--check"]) == 0
    records[0]["violations"] = ["gain-exceeds-closure-proof"]
    output.write_text(json.dumps(records[0]) + "\n")
    assert S.main(["--output", str(output), "--check"]) == 1


def test_check_diagnostic_route_even_if_violation_field_was_empty(tmp_path, view):
    record = S.make_record(None, root(), view, matched=set(), eligible=True, claimable=True,
                           claim_info={}, ordinal=1, lane="closure")
    record["routed"] = True
    output = tmp_path / "shadow.jsonl"
    output.write_text(json.dumps(record) + "\n")
    assert S.main(["--output", str(output), "--check"]) == 1


@pytest.mark.parametrize("tamper", ["gain", "eligible", "claimable", "passing", "additive"])
def test_check_reaudits_records_without_trusting_violation_list(tmp_path, view, tamper):
    record = S.make_record(None, root(), view, matched=set(), eligible=True, claimable=True,
                           claim_info={}, ordinal=1, lane="closure")
    if tamper == "gain":
        record["new_choice"]["single_root_bytes"] += 45
    elif tamper in ("eligible", "claimable"):
        record["eligibility"]["passed" if tamper == "eligible" else "claimable"] = False
    elif tamper == "passing":
        record["assertion_evidence"]["already_passing"] = True
    else:
        record["root_unlock_score"]["non_additive"] = False
    output = tmp_path / "shadow.jsonl"
    output.write_text(json.dumps(record) + "\n")
    assert S.main(["--output", str(output), "--check"]) == 1


def test_raw_historical_serializer_disagreement_is_visible_diagnostic(tmp_path, monkeypatch):
    run = raw_bundle(tmp_path)
    def disagree(*args):
        raise S.artifacts.BundleError("historical serializer differs")
    monkeypatch.setattr(S.artifacts, "core_check", disagree)
    view = S.bundle_view(run)
    assert view["metadata"]["freshness"]["receipt_core_check"] == "historical serializer differs"
    assert not view["metadata"]["authoritative"]


def test_raw_receipt_file_must_match_report_even_with_diagnostic_core_mismatch(tmp_path):
    run = raw_bundle(tmp_path)
    path = run / "receipt.json"
    receipt = json.loads(path.read_text())
    receipt["commit"] = "b" * 40
    path.write_text(json.dumps(receipt))
    with pytest.raises(S.artifacts.BundleError, match="report receipt file"):
        S.bundle_view(run)


def test_old_staleness_requires_bundle_evidence(view):
    old = {"kind": "link", "name": "root", "rva": None, "sources": ["game/root.cpp"]}
    assert S.already_passing(old, view["status"]) is False
    view["status"][0] = status(passed=True)
    assert S.already_passing(old, view["status"]) is True
    assert S.already_passing({**old, "name": "unknown", "sources": ["missing.cpp"]}, view["status"]) is False


def test_old_selector_reuses_no_claim_skip_rules(tmp_path, monkeypatch):
    rows = S.link_check.queue_rows({**census(), "bytes": {"wrong.cpp": 10, "consumer.cpp": 20}})
    monkeypatch.setattr(S, "git", lambda *a: "tip")
    monkeypatch.setattr(S.link_check, "_git", lambda *a, **k: "")
    monkeypatch.setattr(S.link_check, "linked_since", lambda c: (set(), "census", ""))
    with S.inspect_selectors({}):
        item = S.old_choice(rows, tmp_path)
    assert item["name"] == NAME
    assert item["sources"] == ["consumer.cpp", "wrong.cpp"]
    assert not list(tmp_path.iterdir())


def test_agreement_normalizes_name_lease_vs_body_key():
    old = {"key": "0xF1234567", "name": "root", "rva": None}
    assert S.agreement(old, root()) is True
    assert S.agreement({**old, "name": "other"}, root()) is False
    assert S.agreement(None, root()) is None


def test_old_falls_back_to_next_work_without_rotation_or_claims(tmp_path, monkeypatch):
    import next_work
    def choose():
        assert sys.argv == ["next_work.py", "--json", "--repair-every", "0"]
        assert S.repair_queue.repair_turn() is False
        print(json.dumps({"selection": {"function": "root", "target_rva": "0x00001000", "source": "game/root.cpp"}}))
    monkeypatch.setattr(next_work, "main", choose)
    with S.inspect_selectors({}):
        item = S.old_choice([], tmp_path)
    assert item["kind"] == "body" and item["rva"] == "0x00001000"
    assert not list(tmp_path.iterdir())
