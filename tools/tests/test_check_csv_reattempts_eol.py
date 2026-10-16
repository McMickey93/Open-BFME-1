"""re_attempts.log is LF-only and append-only (approved by the project lead
2026-10-16). check_csv compares the staged/ref log with its base, CR-at-EOL
ignored, so the one-time normalisation passes and union-merge duplication,
removed or edited rows and new CRLF rows are refused."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import check_csv  # noqa: E402

A = b"?a@@YAXXZ\t0x00001000\t4\tblocked\tfirst t=1 model=m"
B = b"?b@@YAXXZ\t0x00002000\t4\tpartial\tsecond t=1 model=m"
C = b"?c@@YAXXZ\t0x00003000\t4\tconverted\tthird t=1 model=m"


def problems_for(base, new):
    out = []
    check_csv.check_re_attempts_append_only(base, new, out)
    return out


def test_plain_append_passes():
    assert problems_for(A + b"\n" + B + b"\n", A + b"\n" + B + b"\n" + C + b"\n") == []


def test_the_one_time_normalisation_passes():
    assert problems_for(A + b"\r\n" + B + b"\r\n", A + b"\n" + B + b"\n") == []
    assert problems_for(A + b"\r\n" + B + b"\r\n", A + b"\n" + B + b"\n" + C + b"\n") == []


def test_appended_crlf_line_refused():
    got = problems_for(A + b"\n", A + b"\n" + B + b"\r\n")
    assert got and "appended line 2 ends in CRLF" in got[0] and "-X renormalize" in got[0]


def test_kept_line_gaining_crlf_refused():
    assert "gained a CRLF ending" in problems_for(A + b"\n" + B + b"\n", A + b"\r\n" + B + b"\n")[0]


def test_removed_or_edited_rows_refused():
    assert "removed" in problems_for(A + b"\n" + B + b"\n", A + b"\n")[0]
    assert "line 2 differs" in problems_for(A + b"\n" + B + b"\n", A + b"\n" + C + b"\n")[0]


def test_union_duplication_refused():
    # a union-merged rebase across the normalisation re-adds the CRLF rows as LF
    base = A + b"\r\n" + B + b"\r\n"
    dup_inside = A + b"\n" + A + b"\n" + B + b"\n" + B + b"\n"
    assert "differs" in problems_for(base, dup_inside)[0]
    dup_appended = A + b"\n" + B + b"\n" + A + b"\n" + B + b"\n"
    assert "repeat a run of existing rows" in problems_for(base, dup_appended)[0]


def test_a_single_repeated_row_is_a_coincidence_not_duplication():
    # the real log holds rows written twice; one repeated row alone passes
    assert problems_for(A + b"\n" + B + b"\n", A + b"\n" + B + b"\n" + A + b"\n") == []
    assert problems_for(A + b"\n" + B + b"\n", A + b"\n" + B + b"\n" + A + b"\n" + C + b"\n") == []


def test_last_line_without_newline():
    assert problems_for(A + b"\n" + B, A + b"\n" + B + b"\n" + C) == []


def test_missing_log_is_not_judged():
    assert problems_for(None, A + b"\n") == []
    assert problems_for(A + b"\n", None) == []


REVIEW = Path("/home/thag/Projects/Open-BFME-1/build/review_crlf_r1")


@pytest.mark.skipif(not (REVIEW / "reb.log").exists(), reason="review simulation not present")
def test_reviewers_rebase_simulation():
    old = (REVIEW / "old.log").read_bytes()
    new = (REVIEW / "new.log").read_bytes()
    rebased = (REVIEW / "reb.log").read_bytes()
    assert problems_for(old, new) == []             # the normalisation itself
    assert problems_for(new, rebased)               # its rebase duplicated ~922 rows


def test_read_re_attempts_states(monkeypatch, tmp_path):
    monkeypatch.setattr(check_csv, "ROOT", tmp_path)
    assert check_csv.read_re_attempts(None) is None          # no log in that tree
    log = tmp_path / check_csv.RE_ATTEMPTS_REL
    log.parent.mkdir(parents=True)
    log.write_bytes(b"x\n")
    assert check_csv.read_re_attempts(None) == b"x\n"
    assert check_csv.read_re_attempts("HEAD") is None         # no such object: no log there


def test_read_re_attempts_fails_loudly_when_show_fails(monkeypatch):
    calls = []

    class Done:
        def __init__(self, code, out=b"", err=b"boom"):
            self.returncode, self.stdout, self.stderr = code, out, err

    def fake_run(cmd, **kw):
        calls.append(cmd)
        return Done(0) if "cat-file" in cmd else Done(128)
    monkeypatch.setattr(check_csv.subprocess, "run", fake_run)
    with pytest.raises(SystemExit):
        check_csv.read_re_attempts("HEAD")


def test_re_log_record_writes_lf(monkeypatch, tmp_path):
    import re_log
    log = tmp_path / "re_attempts.log"
    log.write_bytes(b"")
    monkeypatch.setattr(re_log, "RE_ATTEMPTS", log)
    monkeypatch.setattr(re_log, "_census_tag", lambda status, rva, symbol, evidence: evidence)
    monkeypatch.setattr(re_log, "_require_tags", lambda status, evidence: evidence)
    re_log._record(["?f@@YAXXZ", "0x00401000", "16", "blocked", "evidence t=1 model=m"])
    data = log.read_bytes()
    assert data.endswith(b"\n") and b"\r" not in data
