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
