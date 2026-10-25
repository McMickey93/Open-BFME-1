"""Targeted negative controls for review-2 trust/closure claims. No native tools."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import closure_report as cr
import cycle_artifacts as ca
import cycle_stamp
import link_cycle as lc
import publish_cycle as pc
from cycle_fixture import NOW, measured_run


def test_control_unsigned_locally_fabricated_bundle_is_diagnostic(tmp_path, monkeypatch):
    run, _ = measured_run(tmp_path / "run")
    bundle = tmp_path / "bundle"
    pc.make_bundle(run, bundle, "synthetic-unsigned-control")
    monkeypatch.setattr(ca, "ancestry", lambda *a: (True, 0, "synthetic ancestor"))
    with pytest.raises(ca.Refused) as caught:
        ca.serve(bundle, now=NOW)
    assert caught.value.reason == "not-authoritative"
    assert caught.value.sub_reason == "unstamped"


def test_control_modified_manifest_cannot_keep_host_signature(tmp_path, monkeypatch):
    # Test only HMAC integrity; this does not simulate execution authority.
    from cycle_fixture import host_stamp
    key = cycle_stamp.keygen(tmp_path / "temporary-host-key")
    monkeypatch.setattr(cycle_stamp, "_reader_key_for_tests", key)
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest = bundle / ca.MANIFEST
    manifest.write_text('{"members":{"receipt.json":{"sha256":"original"}}}')
    host_stamp(bundle, key)
    assert cycle_stamp.verify(bundle) is None
    manifest.write_text('{"members":{"receipt.json":{"sha256":"replacement"}}}')
    assert cycle_stamp.verify(bundle) == "bad-stamp"


@pytest.mark.parametrize("change,reason", [("old", "stale"), ("future", "corrupt"),
                                         ("rules", "incompatible-rules")])
def test_control_time_and_rule_identity_refuse(change, reason):
    freshness = {"rules_match": change != "rules", "future": change == "future",
                 "stale": change == "old", "max_age_hours": 24}
    assert ca.refusal(freshness)[0] == reason


def test_control_graph_cycles_unknown_targets_and_overflow_are_conservative():
    root, other = ("unit", 1), ("unit", 2)
    good = {root: True, other: True}
    cycle = {root: {other}, other: {root}}
    assert cr.reference_closure(good, cycle) == lc.greatest_closure(good, cycle) == set(good)
    good[other] = False
    assert not cr.reference_closure(good, cycle)
    assert not lc.greatest_closure(good, cycle)
    for target in (("fill", 7), ("stub", 7), ("dump", 7), ("unit", 999)):
        assert not cr.reference_closure({root: True}, {root: {target}})
    blockers = {("unit", i) for i in range(10, 18)}
    state = cr.propagate(blockers, {n: {root} for n in blockers}, str)
    assert state[root] is cr.OVER
    assert root in state  # Overflow is a blocker, never an omitted edge or leaf.


def test_control_donor_and_placement_remain_non_admitting():
    import bfme2_retail_sweep as sweep
    import place_bodies as placement
    import router_shadow as shadow
    record = {"name": "?donor@@YAXXZ", "source": "Code/donor.cpp", "placement": "unique",
              "donor_names": ["?donor@@YAXXZ"]}
    hit = {"rva": 0x60000, "size": 20, "tier": "T2", "work_status": "open", "target_rows": [],
           "identity_evidence": [], "layout_disagreement": [], "exact": True, "strings": [],
           "other_identities": [], "callee_conflicts": [], "extent_conflict": False}
    assert sweep.tier_for(record, hit) == "T2"
    candidate = shadow.donor_candidate(record, hit)
    assert candidate["single_root_bytes"] == 0
    assert not candidate["identity_claimed"]
    assert not shadow.donor_identity_proven(candidate)
    record["donor_names"].append("?other@@YAXXZ")
    assert sweep.tier_for(record, hit) == "T3"
    hit["layout_disagreement"] = ["field offset differs"]
    assert sweep.tier_for(record, hit) == "T5"
    assert "never identity" in placement.NOTICE
