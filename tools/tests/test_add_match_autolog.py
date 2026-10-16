"""add_match records its own `landed` verdict, and a deferral comes back when
the blocker it names has landed (approved by the project lead 2026-10-16;
ported from Open-BFME-2 4ebbfc02b2 and ab1a8a5ed6).

The mistakes pinned down here:
  * a landing that forgets its verdict leaves an old `blocked` as the log's
    last word on a matched body, and nothing waiting on it ever learns;
  * a second run, or a reverted landing, must not leave a stray `landed`;
  * `blocked-on=0x2000, 0x3000` read as [0x2000] released a caller whose
    second blocker was still missing; malformed tokens release nothing;
  * a blocker that had already landed when the deferral was written does not
    release it, nor does a generated row at the blocker's address, and a dead
    end never comes back.
"""
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import add_match  # noqa: E402
import check_csv  # noqa: E402
import eligibility  # noqa: E402
import re_log  # noqa: E402

HEADER = "name,export_rva,target_rva,target_size,source,status,notes"
DUMP = "?d_00abcd00@@YAXXZ,,0x00ABCD00,32,game/gen_asm/d_00abcd00.asm,matched,gen-dump"
REAL = "?realBody@Thing@@QAEXXZ"
SOURCE_REL = "game/GameEngine/Source/Common/Thing.cpp"
OLD_LOG = (f"{REAL}\t0x00ABCD00\t32\tblocked\tcallee unresolved blocker=callee/x t=40 model=m\n"
           "?caller@Thing@@QAEXXZ\t0x00ABCE00\t64\tblocked\twaits blocked-on=0x00ABCD00 "
           "blocker=callee/x t=30 model=m\n")


@pytest.fixture
def landing(tmp_path, monkeypatch):
    reverse = tmp_path / "targets/game/reverse"
    reverse.mkdir(parents=True)
    source = tmp_path / SOURCE_REL
    source.parent.mkdir(parents=True)
    source.write_bytes(f"// {REAL} present-unmatched\r\nvoid realBody() {{}}\r\n".encode())
    (reverse / "functions.csv").write_bytes(f"{HEADER}\r\n{DUMP}\r\n".encode())
    (reverse / "deleted_rows.csv").write_bytes(b"name,target_rva,reason\n")
    (reverse / "re_attempts.log").write_bytes(OLD_LOG.encode())
    (tmp_path / "build.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    monkeypatch.setattr(add_match, "DEFAULT_ROOT", tmp_path)
    real_run = subprocess.run
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    state = {"rc": 0}

    def run(command, *args, **kwargs):     # the byte gate's verdict is the test's
        if command[0] == "git":
            return real_run(command, *args, **kwargs)
        return SimpleNamespace(returncode=state["rc"])
    monkeypatch.setattr(add_match.subprocess, "run", run)
    monkeypatch.setenv("BFME_CLAIMS", "off")
    monkeypatch.setattr(sys, "argv", [
        "add_match.py", REAL, "0x00ABCD00", "32", SOURCE_REL, "--replace-rva", "0x00ABCD00",
        "--root", str(tmp_path), "--model", "test-model"])
    return tmp_path, state


def _log(root):
    return (root / "targets/game/reverse/re_attempts.log").read_bytes()


def test_a_verified_landing_records_landed_once(landing):
    root, _state = landing
    add_match.main()
    raw = _log(root)
    assert raw.startswith(OLD_LOG.encode()), "append-only"
    new = raw[len(OLD_LOG):].decode()
    assert new.endswith("\n") and "\r" not in new and new.count("\n") == 1
    fields = new.rstrip("\n").split("\t")
    assert fields[:4] == [REAL, "0x00ABCD00", "32", "landed"]
    assert f"landed-by=add_match source={SOURCE_REL} " in fields[4]
    assert "extent=0x00ABCD00..0x00ABCD20" in fields[4] and "model=test-model" in fields[4]
    problems = []
    check_csv.check_re_attempts_append_only(OLD_LOG.encode(), raw, problems)
    assert problems == [], "the guard accepts the appended verdict"
    # idempotent: the same landing again writes nothing
    text = add_match.record_landing(root, REAL, 0x00ABCD00, 32, SOURCE_REL, "model=test-model")
    assert text is not None and _log(root) == raw


def test_a_failed_verification_records_nothing(landing):
    root, state = landing
    state["rc"] = 1
    with pytest.raises(SystemExit):
        add_match.main()
    assert _log(root) == OLD_LOG.encode()


def test_a_voided_landing_is_recorded_again(landing):
    root, _state = landing
    text = add_match.record_landing(root, REAL, 0x00ABCD00, 32, SOURCE_REL, "model=m")
    once = _log(root)
    with (root / "targets/game/reverse/re_attempts.log").open("ab") as handle:
        handle.write(f"{REAL}\t0x00ABCD00\t32\tvoid\tretract the landing model=m\n".encode())
    add_match.record_landing(root, REAL, 0x00ABCD00, 32, SOURCE_REL, "model=m")
    assert _log(root).count(b"\tlanded\t") == 2
    assert text is not None and once.count(b"\tlanded\t") == 1


def test_another_source_or_size_is_another_landing(landing):
    root, _state = landing
    add_match.record_landing(root, REAL, 0x00ABCD00, 32, SOURCE_REL, "model=m")
    add_match.record_landing(root, REAL, 0x00ABCD00, 32, SOURCE_REL + "x", "model=m")
    add_match.record_landing(root, REAL, 0x00ABCD00, 33, SOURCE_REL, "model=m")
    assert _log(root).count(b"\tlanded\t") == 3


def test_the_writer_refuses_a_broken_row(tmp_path):
    log = tmp_path / "re_attempts.log"
    log.write_bytes(b"")
    for bad in (("a\tb", "0x1", "1", "landed", "e"), ("a", "0x1", "1", "landed", "e\nf"),
                ("a", "0x1", "1", "fixed", "e"), ("a", "zz", "1", "landed", "e")):
        with pytest.raises((SystemExit, ValueError)):
            re_log.append(*bad, path=log)
    assert log.read_bytes() == b""


# -- blocked-on= and the queue ------------------------------------------------

def test_blocked_on_is_all_or_nothing():
    assert re_log.blocked_on("x blocked-on=0x2000,0x3000 y") == [0x2000, 0x3000]
    assert re_log.blocked_on("blocked-on=0x2000, 0x3000") == []
    assert re_log.blocked_on("no token") == []
    with pytest.raises(SystemExit):
        re_log.blocked_on("blocked-on=0x2000, 0x3000", status="blocked")
    with pytest.raises(SystemExit):
        re_log.blocked_on("blocked-on=0x2000", status="no-match")


def _rows(*specs):
    out = []
    for name, rva, source, notes in specs:
        out.append({"name": name, "export_rva": "", "target_rva": f"0x{rva:08X}",
                    "target_size": "16", "source": source, "status": "matched", "notes": notes})
    return out


CALLER, BLOCKER, OTHER = 0x1000, 0x2000, 0x3000
REAL_ROW = ("?blocker@X@@QAEXXZ", BLOCKER, "game/X.cpp", "model=m")
OTHER_ROW = ("?other@X@@QAEXXZ", OTHER, "game/X.cpp", "model=m")
GEN_ROW = ("?d_00002000@@YAXXZ", BLOCKER, "game/gen_asm/d_x.asm", "gen-dump")


def _write(tmp_path, *lines):
    log = tmp_path / "re_attempts.log"
    log.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    return log


def deferral(tokens="blocked-on=0x00002000", status="blocked"):
    return f"?caller@X@@QAEXXZ\t0x{CALLER:08X}\t32\t{status}\twall {tokens} blocker=callee/x model=m"


def landed(rva=BLOCKER, name="?blocker@X@@QAEXXZ"):
    return f"{name}\t0x{rva:08X}\t16\tlanded\tlanded-by=add_match source=game/X.cpp model=m"


def test_a_deferral_comes_back_when_its_blocker_lands(tmp_path):
    log = _write(tmp_path, deferral(), landed())
    released = eligibility.released_rvas(log, rows=_rows(REAL_ROW))
    assert set(released) == {CALLER} and released[CALLER][1] == [BLOCKER]


def test_a_blocker_that_had_already_landed_releases_nothing(tmp_path):
    log = _write(tmp_path, landed(), deferral())
    assert eligibility.released_rvas(log, rows=_rows(REAL_ROW)) == {}


def test_a_generated_row_or_a_missing_resolution_releases_nothing(tmp_path):
    log = _write(tmp_path, deferral(), landed())
    assert eligibility.released_rvas(log, rows=_rows(GEN_ROW)) == {}
    log = _write(tmp_path, deferral())
    assert eligibility.released_rvas(log, rows=_rows(REAL_ROW)) == {}


def test_every_named_blocker_must_land(tmp_path):
    log = _write(tmp_path, deferral("blocked-on=0x00002000,0x00003000"), landed())
    assert eligibility.released_rvas(log, rows=_rows(REAL_ROW)) == {}
    log = _write(tmp_path, deferral("blocked-on=0x00002000,0x00003000"), landed(),
                 landed(OTHER, "?other@X@@QAEXXZ"))
    assert set(eligibility.released_rvas(log, rows=_rows(REAL_ROW, OTHER_ROW))) == {CALLER}
    log = _write(tmp_path, deferral("blocked-on=0x00002000, 0x00003000"), landed(),
                 landed(OTHER, "?other@X@@QAEXXZ"))
    assert eligibility.released_rvas(log, rows=_rows(REAL_ROW, OTHER_ROW)) == {}


def test_a_dead_end_or_a_later_deferral_without_the_token_is_not_released(tmp_path):
    log = _write(tmp_path, deferral(status="no-match"), landed())
    assert eligibility.released_rvas(log, rows=_rows(REAL_ROW)) == {}
    later = "?caller@X@@QAEXXZ\t0x00001000\t32\tblocked\tnew wall blocker=regalloc/x model=m"
    log = _write(tmp_path, deferral(), landed(), later)
    assert eligibility.released_rvas(log, rows=_rows(REAL_ROW)) == {}


def test_released_is_served_as_untried(tmp_path, monkeypatch):
    log = _write(tmp_path, f"?caller@X@@QAEXXZ\t0x{CALLER:08X}\t32\tblocked\tfirst blocker=x/y model=m",
                 deferral(), landed())
    monkeypatch.setattr(re_log, "RE_ATTEMPTS", log)
    monkeypatch.setattr(eligibility, "load_rows", lambda *a, **k: _rows(REAL_ROW))
    eligibility._RELEASED.clear()
    latest = eligibility.latest_verdicts(log)
    assert latest[CALLER] == "blocked"
    assert not eligibility.deferred(CALLER, latest)
    assert eligibility.attempt_counts(log).get(CALLER, 0) == 0
    re_log._reset()
    monkeypatch.setattr(eligibility, "load_rows", lambda *a, **k: _rows(GEN_ROW))
    eligibility._RELEASED.clear()
    assert eligibility.deferred(CALLER, latest)
    assert eligibility.attempt_counts(log)[CALLER] == 2
    eligibility._RELEASED.clear()
