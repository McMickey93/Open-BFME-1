"""No derived BFME1 data identity may become ownership through bundle ranking."""
import sys
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cycle_fixture import measured_run
import cycle_artifacts as ca
import data_back_rank as rank


def test_unavailable_provider_names_missing_evidence_and_binds_measured_inputs(tmp_path, capsys):
    run, r = measured_run(tmp_path / "run")
    # Derived names/sizes cannot supply the missing typed/verified evidence view.
    (run / "data_ledger.csv").write_text("name,size,owner\nGuessedName,999999,provisional\n")
    doc = rank.unavailable(r)
    rank.check_member(doc, r)
    assert doc["status"] == "unavailable" and doc["inputs"] == r["inputs"]
    assert "verified data_rows" in doc["reason"] and "ownership" in doc["reason"]
    out = tmp_path / "rank.json"
    assert rank.main([str(run), "--json", str(out)]) == 2
    assert ca.read_json(out) == doc
    assert "[reason=unavailable]" in capsys.readouterr().err


def test_unavailable_cannot_be_relabelled_success(tmp_path):
    _, r = measured_run(tmp_path / "run")
    doc = rank.unavailable(r)
    doc.update(status="available", addresses=[])
    with pytest.raises(ca.BundleError):
        rank.check_member(doc, r)
