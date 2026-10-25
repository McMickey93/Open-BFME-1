#!/usr/bin/env python3
"""Compare selectors without dispatch, claims, rotation writes or compilation.

Each draw removes its choices only in memory. Lanes rotate closure/family/donor
to inspect all three queues; this is a ranked diagnostic sample, not throughput
or a production scheduling policy. Raw cycle directories are diagnostic only.
Trusted local census pickles have the same trust requirement as comdat_families.

  router_shadow.py --bundle RUN --index CENSUS --donors build/bfme2_retail_sweep/match.json --count 20 --check
  router_shadow.py --check                  # check the existing JSONL
"""
import argparse
from contextlib import ExitStack, contextmanager, redirect_stdout
import csv
import io
import json
from pathlib import Path
import pickle
import re
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch

import bfme2_retail_sweep as sweep
import claims
import closure_report as closure
import comdat_families as comdat
import cycle_artifacts as artifacts
import eligibility
import link_check
import repair_queue

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "bfme1-router-shadow/1"
DEFAULT_LOG = ROOT / "build/router_shadow/shadow.jsonl"
LIVE = {"status": "not-run", "passed": None,
        "reason": "link_check preview can compile stale objects and write evaluated verdicts; no safe live check requested"}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True,
                          timeout=60, check=True).stdout.strip()


def claim_snapshot():
    """Inspect origin without fetch, local ref updates, leases or claim commits.

    A remote marker whose object is absent locally is conservatively busy (its
    expiry cannot be inspected). claims.live owns expiry semantics when known.
    A network failure makes *every* proposed key unclaimable.
    """
    try:
        refs = git("ls-remote", claims.REMOTE, "refs/claims/*")
    except (OSError, subprocess.SubprocessError) as exc:
        return {}, {"status": "unavailable", "reason": str(exc), "unknown_markers": 0}
    held, unknown = {}, 0
    for line in refs.splitlines():
        sha, ref = line.split()
        key = int(ref.rsplit("/", 1)[1], 16)
        try:
            subject = git("show", "-s", "--format=%s", sha)
            info = json.loads(subject)
            active = claims.live({key: (sha, info)})
            if active:
                held[key] = info
        except (OSError, ValueError, TypeError, AttributeError, subprocess.SubprocessError):
            held[key] = {"owner": "unknown remote marker", "expires": float("inf")}
            unknown += 1
    return held, {"status": "remote-read-only", "reason": None, "unknown_markers": unknown}


@contextmanager
def inspect_selectors(held):
    """Adapt legacy APIs that otherwise fetch refs or advance rotation state.

    Only their I/O boundaries are replaced; eligibility and queue predicates
    remain BFME1's. Mutation entry points fail loudly, including future changes.
    This context is single-threaded and is never used by a production router.
    """
    def forbidden(*_args, **_kwargs):
        raise RuntimeError("shadow selector attempted mutation")

    with ExitStack() as stack:
        stack.enter_context(patch.object(claims, "active", lambda *a, **k: dict(held)))
        stack.enter_context(patch.object(claims, "_fetch_master", lambda *a, **k: git("rev-parse", "origin/master")))
        for name in ("claim", "renew", "release", "fetch", "_mirror", "queue_landed"):
            stack.enter_context(patch.object(claims, name, forbidden))
        stack.enter_context(patch.object(repair_queue, "repair_turn", lambda *a, **k: False))
        yield


def bundle_view(directory):
    """Validate bound graph/status/report, retaining unsigned raw runs as diagnostics.

    No raw run can acquire authority, even if its receipt says authoritative.
    Packaged bundles use the existing host-stamp/rules/freshness validation.
    """
    directory = Path(directory)
    if (directory / artifacts.MANIFEST).exists():
        bundle = artifacts.load_bundle(directory, root=ROOT)
        fr = bundle.freshness(root=ROOT)
    else:
        receipt = json.loads((directory / "receipt.json").read_text())
        fr = artifacts.freshness(receipt, root=ROOT)
        fr.update(authoritative=False, reason="not-authoritative", sub_reason="raw-unstamped-diagnostic")
        # Historical raw runs may predate today's receipt serializer. Keep its
        # disagreement visible, and require the report's exact receipt hash
        # below. This path never calls serve(), installs a bundle or routes.
        try:
            artifacts.core_check(receipt, ROOT)
            fr["receipt_core_check"] = "reproduced"
        except artifacts.BundleError as exc:
            fr["receipt_core_check"] = str(exc)
        bundle = SimpleNamespace(receipt=receipt, dir=directory,
                                 link_status=directory / "link_status.csv",
                                 closure_graph=directory / "closure_graph.json.gz",
                                 closure_roots=directory / "closure/closure_roots.json",
                                 closure_blockers=directory / "closure/closure_blockers.csv")
    receipt = bundle.receipt
    graph = closure.load_graph(bundle.closure_graph, receipt["closure_graph_sha256"])
    ok, edges, rows, _ = graph
    status = closure.status_rows(bundle.link_status)
    closed = closure.reference_closure(ok, edges)
    closure.check_rows(rows, closed, status)
    credit = closure.unique_bytes((r["rva"], r["rva"] + r["size"]) for r in rows
                                  if r["real"] and r["placed"] and r["self_strict"] and r["node"] in closed)
    artifacts.same("graph credit", credit, receipt["series"]["credit_unique_bytes"])
    artifacts.same("status digest", closure.sha256_bytes(closure.read_bytes(bundle.link_status)),
                   receipt["series"]["link_status_sha256"])
    report = closure.load_roots(bundle.closure_roots)
    artifacts.same("receipt graph digests", receipt["closure_graph_sha256"], receipt["series"]["closure_graph_sha256"])
    artifacts.same("report graph", report["graph"], {"bound": True, "label": closure.BOUND,
                                                    "sha256": receipt["closure_graph_sha256"]})
    artifacts.same("report receipt file", report["receipt_sha256"], artifacts.sha256_file(directory / "receipt.json"))
    artifacts.same("report receipt", report["receipt_core_sha256"], receipt["core_sha256"])
    artifacts.same("report status", report["link_status_sha256"], receipt["series"]["link_status_sha256"])
    artifacts.same("report blockers", report["blockers"]["sha256"],
                   closure.sha256_bytes(closure.read_bytes(bundle.closure_blockers)))
    # Reproduces ALL root scores and joint summary from the graph, not just hashes.
    items, _notes, joint = repair_queue.closure_queue(bundle)
    proof = {r["root"].lower(): r["conditional_gain_bytes"] for r in report["roots"]}
    return {"items": items, "proof": proof, "joint_only": joint, "status": status, "graph": graph,
            "metadata": {"path": str(directory.resolve()), "commit": receipt["commit"],
                         "freshness": fr, "authoritative": fr["authoritative"],
                         "reason": fr.get("reason"), "sub_reason": fr.get("sub_reason"),
                         "comparison_only": True}}


def old_choice(rows, scratch):
    """Use link_check next's actual skip/ownership rules with --no-claim.

    The supplied census supplies its ordinary queue. origin/master and later
    census checks use local read-only snapshots, labelled in every record.
    """
    with tempfile.NamedTemporaryFile(mode="w", newline="", dir=scratch, suffix=".csv") as handle:
        writer = csv.DictWriter(handle, fieldnames=link_check.QUEUE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        out = io.StringIO()
        with redirect_stdout(out):
            code = link_check.serve(["--no-claim", "--queue", handle.name])
    match = re.search(r"link queue #(\d+) ", out.getvalue())
    if code == 0 and match:
        row = next(r for r in rows if str(r["rank"]) == match[1])
        return {"selector": "link_check.py next --no-claim", "kind": "link", "name": row["name"],
                "key": f"0x{link_check.claim_key(row['name']):08X}", "rva": None,
                "sources": row["files"].split(";"), "census_bytes": int(row["bytes_unlocked"]),
                "family": row["family"] or None}
    # next_work --json is inspect-only with rotation replaced by the context.
    import next_work
    out = io.StringIO()
    with patch.object(sys, "argv", ["next_work.py", "--json", "--repair-every", "0"]), redirect_stdout(out):
        next_work.main()
    data = json.loads(out.getvalue())
    item = data["selection"]
    if not item:
        return None
    return {"selector": "next_work.py --json --repair-every 0", "kind": "body",
            "name": item["function"], "key": item["target_rva"], "rva": item["target_rva"],
            "sources": [item.get("source", "")], "census_bytes": None, "family": None}


def passing_status(status):
    passing, by_source = set(), {}
    for row in status:
        passed = all(row[k] == "1" for k in ("placed", "self_strict", "closed_strict"))
        if passed:
            passing.add((int(row["retail_rva"], 16), row["name"], row["source"]))
        by_source.setdefault(row["source"], []).append(passed)
    return passing, {s for s, values in by_source.items() if values and all(values)}


def already_passing(item, status):
    if not item:
        return None
    passing, sources = passing_status(status)
    if item.get("kind") == "closure":
        return (int(item["rva"], 16), item["name"], item["sources"][0]) in passing
    if item.get("rva"):
        return any(rva == int(item["rva"], 16) for rva, _name, _source in passing)
    named = [r for r in status if r["name"] == item["name"]]
    if named:
        return all((int(r["retail_rva"], 16), r["name"], r["source"]) in passing for r in named)
    return bool(item["sources"]) and set(item["sources"]) <= sources


def closure_candidate(item, proof):
    return {"kind": "closure", "key": item["target_rva"], "rva": item["target_rva"],
            "name": item["function"], "sources": [item["source"]], "family": None,
            "donor_tier": None, "single_root_bytes": item["conditional_gain_bytes"],
            "proved_single_root_bytes": proof.get(item["target_rva"].lower(), 0),
            "identity_claimed": False, "edit_targets": []}


def family_candidate(family):
    return {"kind": "family", "key": family["claim_key"], "rva": None, "name": family["family"],
            "sources": family["affected_units"], "family": family["family"], "donor_tier": None,
            # Census affected/conditional bytes are NOT closure-proven gains.
            "single_root_bytes": 0, "proved_single_root_bytes": 0,
            "census_affected_bytes": family["bytes_blocked"], "identity_claimed": False,
            "edit_targets": [{"name": family["family"], "source": source}
                             for emitter in family["wrong_emitters"] for source in emitter["sources"]]}


def donor_candidate(record, hit):
    return {"kind": "donor", "key": f"0x{hit['rva']:08X}", "rva": f"0x{hit['rva']:08X}",
            "name": record["name"], "sources": ["game/" + record["source"].removeprefix("Code/")],
            "family": None, "donor_tier": hit["tier"], "expected_donor_tier": sweep.tier_for(record, hit),
            "single_root_bytes": 0, "proved_single_root_bytes": 0, "identity_claimed": False,
            "identity_evidence": hit["identity_evidence"], "work_status": hit["work_status"],
            "placement": record["placement"], "edit_targets": [], "size": hit["size"],
            "target_rows": hit["target_rows"]}


def donor_identity_proven(candidate):
    """Use the donor scanner's BFME1 identity provider, never its placement."""
    keys = sweep.placement.identity_source_keys(candidate["target_rows"])
    return any(e.get("kind") == "same-decorated-symbol" and e.get("name") == candidate["name"]
               and e.get("rva") == int(candidate["rva"], 16)
               and (e["name"], f"0x{e['rva']:08X}") in keys
               and any(r["name"] == e["name"] and r["source"] == e.get("source")
                       and int(r["target_rva"], 16) == e["rva"] for r in candidate["target_rows"])
               for e in candidate["identity_evidence"])


def assertion_evidence(candidate, status, proof, matched):
    if not candidate:
        return {"already_passing": None, "proved_single_root_bytes": 0,
                "matched_edit_targets": [], "donor_identity_proven": None}
    needs_identity = candidate["kind"] == "donor" and (candidate["identity_claimed"] or candidate["donor_tier"] == "T1")
    return {"already_passing": already_passing(candidate, status),
            "proved_single_root_bytes": proof.get((candidate.get("rva") or "").lower(), 0) if candidate["kind"] == "closure" else 0,
            "matched_edit_targets": [t for t in candidate["edit_targets"] if (t["name"], t["source"]) in matched],
            "donor_identity_proven": donor_identity_proven(candidate) if needs_identity else None}


def audit_candidate(candidate, evidence, *, eligible, claimable, routed, authoritative):
    """Pure assertions, shared by observation and historical JSONL checking."""
    violations = []
    if routed and not authoritative:
        violations.append("diagnostic-bundle-routed")
    if not candidate:
        return violations
    if evidence["already_passing"]:
        violations.append("new-already-passing")
    proved = evidence["proved_single_root_bytes"]
    if not 0 <= candidate["single_root_bytes"] <= proved:
        violations.append("gain-exceeds-closure-proof")
    if candidate["kind"] == "donor":
        identity_needed = candidate["identity_claimed"] or candidate["donor_tier"] == "T1"
        if identity_needed and not evidence["donor_identity_proven"]:
            violations.append("placement-upgraded-to-identity")
        if candidate["donor_tier"] != candidate["expected_donor_tier"]:
            violations.append("donor-tier-not-reproduced")
    if candidate["kind"] == "family" and evidence["matched_edit_targets"]:
        violations.append("comdat-changes-matched-body")
    if not eligible:
        violations.append("not-eligible")
    if not claimable:
        violations.append("not-claimable")
    return sorted(set(violations))


def invariant_violations(candidate, *, status, proof, matched, **kwargs):
    """Independent checks of the proposed item; run even for rejected candidates."""
    return audit_candidate(candidate, assertion_evidence(candidate, status, proof, matched), **kwargs)


def agreement(old, new):
    """Compare task names/addresses, not the different name-lease and body keys."""
    if not old or not new:
        return None
    if old["name"] == new["name"]:
        return True
    if old.get("rva") and new.get("rva") and int(old["rva"], 16) == int(new["rva"], 16):
        return True
    return old["key"].lower() == new["key"].lower()


def make_record(old, candidate, view, *, matched, eligible, claimable, claim_info, ordinal, lane):
    meta = view["metadata"]
    evidence = assertion_evidence(candidate, view["status"], view["proof"], matched)
    violations = audit_candidate(candidate, evidence, eligible=eligible, claimable=claimable,
                                 routed=False, authoritative=meta["authoritative"])
    return {"schema": SCHEMA, "timestamp_utc": artifacts.iso_utc(time.time()), "ordinal": ordinal,
            "mode": "shadow-only", "sampling": "ranked-without-replacement; lanes round-robin",
            "lane": lane, "old_choice": old, "new_choice": candidate, "routed": False,
            "bundle": meta, "root_unlock_score": {"single_root_bytes": candidate["single_root_bytes"] if candidate else 0,
                                                       "joint_only": view["joint_only"], "non_additive": True},
            "family": candidate["family"] if candidate else None,
            "donor_tier": candidate["donor_tier"] if candidate else None,
            "old_stale": already_passing(old, view["status"]),
            "agreement": agreement(old, candidate),
            "eligibility": {"passed": eligible, "claimable": claimable, "claims": claim_info},
            "assertion_evidence": evidence,
            "old_context": "supplied census; local origin/master and linked_since snapshot; no fetch",
            "live_check": dict(LIVE), "skipped_candidates": [], "violations": violations}


def summarize(records):
    compared = [r for r in records if r["agreement"] is not None]
    return {"records": len(records), "comparable": len(compared),
            "agreement_rate": sum(r["agreement"] for r in compared) / len(compared) if compared else None,
            "stale_old_tasks": sum(r["old_stale"] is True for r in records),
            "violations": sum(len(r["violations"]) for r in records),
            "records_with_violations": sum(bool(r["violations"]) for r in records),
            "routed": sum(r["routed"] for r in records),
            "skipped_candidates": sum(len(r["skipped_candidates"]) for r in records),
            "lanes": {lane: sum(r["lane"] == lane for r in records) for lane in ("closure", "family", "donor")}}


def run(args):
    held, claim_info = claim_snapshot()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with inspect_selectors(held):
        view = bundle_view(args.bundle)
        with args.index.open("rb") as handle:
            index = pickle.load(handle)
        names = comdat.candidate_names(index)
        sources = {s for s, e in index["blockers"].items() if not e["linked"] and comdat.blocked_names(e) & names}
        families = comdat.analyze(index, comdat.source_intervals(ROOT, sources), homes=comdat.retail_homes(ROOT, names))["families"]
        donors = sweep.load_report(args.donors) if args.donors else None
        queues = {"closure": [closure_candidate(i, view["proof"]) for i in view["items"]],
                  "family": [family_candidate(f) for f in families if f["servable"]],
                  "donor": [donor_candidate(r, h) for r, h in sweep.ranked(donors)] if donors else []}
        stale_skips = {lane: [] for lane in queues}
        if view["metadata"].get("commit"):
            for lane, candidates in queues.items():
                queues[lane], stale_skips[lane] = repair_queue.current_bundle_items(
                    candidates, view["metadata"]["commit"], root=ROOT, graph=view.get("graph"))
        # Narrow ledger filter: never retain the whole functions.csv.
        edits = {(t["name"], t["source"]) for c in queues["family"] for t in c["edit_targets"]}
        matched = set()
        with (ROOT / "targets/game/reverse/functions.csv").open(newline="") as handle:
            for row in csv.DictReader(handle):
                pair = row["name"], row["source"]
                if pair in edits and row["status"] == "matched":
                    matched.add(pair)
        eligible = eligibility.servable(root=ROOT)
        latest = eligibility.latest_verdicts()
        old_rows = link_check.queue_rows(index)
        records, seen_old = [], set()
        for n in range(args.count):
            lane = args.lanes[n % len(args.lanes)]
            candidate, ok, free, skipped = None, None, None, stale_skips[lane]
            stale_skips[lane] = []
            while queues[lane]:
                proposed = queues[lane].pop(0)
                key = int(proposed["key"], 16)
                ok = eligible(key)
                if proposed["kind"] == "donor":
                    ok = ok and sweep.work_state(key, proposed["size"], proposed["target_rows"], latest) == "open"
                free = claim_info["status"] == "remote-read-only" and key not in held
                if ok and free:
                    candidate = proposed
                    break
                skipped.append({"key": proposed["key"], "name": proposed["name"],
                                "reason": "not-eligible" if not ok else "not-claimable"})
            if candidate is None:
                ok, free = None, None
            old = old_choice(old_rows, args.output.parent)
            if old and old["key"] in seen_old:
                old = None  # exhausted fallback; no simulated lease is ever written
            if old:
                seen_old.add(old["key"])
                old_rows = [r for r in old_rows if r["name"] != old["name"]]
            record = make_record(old, candidate, view, matched=matched, eligible=ok, claimable=free,
                                 claim_info=claim_info, ordinal=n + 1, lane=lane)
            record["skipped_candidates"] = skipped
            records.append(record)
            with args.output.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
    return records


def check_log(path):
    records = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("schema") != SCHEMA:
                raise ValueError("incompatible shadow JSONL schema")
            violations = audit_candidate(record["new_choice"], record["assertion_evidence"],
                                         eligible=record["eligibility"]["passed"], claimable=record["eligibility"]["claimable"],
                                         routed=record["routed"], authoritative=record["bundle"]["authoritative"])
            if record["root_unlock_score"]["single_root_bytes"] != (record["new_choice"]["single_root_bytes"] if record["new_choice"] else 0):
                violations.append("record-score-disagrees-with-choice")
            if record["root_unlock_score"]["non_additive"] is not True:
                violations.append("root-scores-marked-additive")
            if record["agreement"] != agreement(record["old_choice"], record["new_choice"]):
                violations.append("agreement-disagrees-with-choices")
            record["violations"] = sorted(set(record["violations"]) | set(violations))
            records.append(record)
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--index", type=Path, default=link_check.INDEX)
    parser.add_argument("--donors", type=Path, help="fingerprint-bound bfme2_retail_sweep scan report")
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--lanes", type=lambda s: s.split(","), default=["closure", "family", "donor"])
    parser.add_argument("--output", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--check", action="store_true", help="fail on any violation; alone, check existing log")
    args = parser.parse_args(argv)
    if args.count < 1 or not args.lanes or any(l not in ("closure", "family", "donor") for l in args.lanes):
        parser.error("positive --count and --lanes closure,family,donor required")
    if args.bundle is None and not args.check:
        parser.error("--bundle required unless checking an existing log")
    try:
        records = run(args) if args.bundle else check_log(args.output)
        summary = summarize(records)
        print(json.dumps(summary, sort_keys=True))
        checked = summarize(check_log(args.output)) if args.check and args.bundle else summary
        return int(args.check and checked["violations"] > 0)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, artifacts.Problem,
            closure.ReportError, pickle.UnpicklingError) as exc:
        parser.exit(2, f"router_shadow: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
