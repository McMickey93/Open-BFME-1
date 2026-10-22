"""The scoped BFME1 bundle diff: intervals, not renamed symbol totals."""
import copy
import csv
import sys
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cycle_fixture import NOW, bundle, measured_run, rehash, save_receipt
import cycle_artifacts as ca
import cycle_diff as cd
import publish_cycle as pc


def test_union_difference_and_overlap():
    assert cd.union([[2, 4], [1, 3], [4, 5], [8, 9]]) == [[1, 5], [8, 9]]
    assert cd.difference([[1, 10], [12, 20]], [[2, 4], [6, 8], [9, 15]]) == [[1, 2], [4, 6], [8, 9], [15, 20]]


def test_rename_never_gains_credit_and_equal_rules_tool_difference_warns(tmp_path):
    a, ra = measured_run(tmp_path / "a", name="old")
    b, rb = measured_run(tmp_path / "b", name="new", now=NOW + 60)
    rb["tool_dependencies"]["unrelated.py"] = "f" * 64
    rb["tool_digest"] = ca.context.digest(rb["tool_dependencies"])
    save_receipt(b, rb)
    doc = cd.compare(a, b)
    assert doc["totals"] == {"old": 10, "new": 10, "gained": 0, "lost": 0, "delta": 0}
    assert doc["measurement_changed"] == [] and doc["tool_digest_warning"] is True
    assert cd.dumps(doc) == cd.dumps(cd.compare(a, b))


def test_ruler_changes_are_explicit(tmp_path):
    a, _ = measured_run(tmp_path / "a")
    b, rb = measured_run(tmp_path / "b")
    rb["tool_dependencies"]["build.py"] = "f" * 64
    rb["rule_identity"] = ca.context.rule_identity(rb["tool_dependencies"])
    rb["tool_digest"] = ca.context.digest(rb["tool_dependencies"])
    save_receipt(b, rb)
    assert cd.compare(a, b)["measurement_changed"] == ["rule_identity"]


def test_receipt_credit_union_mismatch_refuses(tmp_path):
    run, r = measured_run(tmp_path / "run")
    r["series"]["credit_unique_bytes"] = 99
    save_receipt(run, r)
    with pytest.raises(cd.CycleDiffError, match="credit union"):
        cd.compare(None, run)


def test_first_run_has_no_invented_gain_and_bundle_previous_is_optional(tmp_path):
    a, _ = measured_run(tmp_path / "a")
    b, _ = measured_run(tmp_path / "b", now=NOW + 60)
    doc = cd.compare(None, b)
    assert doc["comparison"] is False and doc["totals"] is None
    assert doc["gained"] is None and doc["lost"] is None
    out = tmp_path / "out"
    pc.make_bundle(b, out, "test", previous=a)
    ca.validate(out)
    assert ca.read_json(out / ca.CYCLE_DIFF)["comparison"] is True


def test_previous_must_be_earlier_and_not_self(tmp_path):
    a, _ = measured_run(tmp_path / "a")
    b, _ = measured_run(tmp_path / "b", now=NOW + 60)
    for run, previous in ((a, b), (a, a)):
        with pytest.raises(pc.RunError):
            pc.make_bundle(run, tmp_path / "out", "test", previous=previous)
    with pytest.raises(pc.RunError):
        pc.make_bundle(b, tmp_path / "out", "test", previous=a, first=True)


def test_diff_total_tamper_with_rehashed_member_refused(tmp_path):
    a, _ = measured_run(tmp_path / "a")
    b, _ = measured_run(tmp_path / "b", now=NOW + 60)
    d = tmp_path / "out"
    pc.make_bundle(b, d, "test", previous=a)
    doc = ca.read_json(d / ca.CYCLE_DIFF)
    doc["totals"]["gained"] += 1
    (d / ca.CYCLE_DIFF).write_text(cd.dumps(doc))
    rehash(d, ca.CYCLE_DIFF)
    with pytest.raises(ca.BundleError):
        ca.validate(d)
