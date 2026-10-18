"""link_census bounds a stuck link and clears Wine before retrying it."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import link_census as census  # noqa: E402


def prepare(tmp_path, monkeypatch, watch):
    root = tmp_path
    out = root / "build" / "link_census"
    monkeypatch.setattr(census, "ROOT", root)
    monkeypatch.setattr(census, "OUT", out)
    monkeypatch.setattr(census.build, "vc71_root", lambda: root)
    monkeypatch.setattr(census.build, "compiler_environment", lambda compiler_root: {})
    monkeypatch.setattr(census.build, "watch_compiler", watch)
    monkeypatch.setattr(census, "LINK_TIMEOUT", 12.0)
    monkeypatch.setattr(census, "LINK_ATTEMPTS", 2)
    return out


def test_timeout_resets_wine_and_retries(tmp_path, monkeypatch):
    calls, resets = [], []

    def watch(command, env, *, merge_output, timeout, timeout_note):
        calls.append(timeout)
        if len(calls) == 1:
            return subprocess.CompletedProcess(command, 124, b"", timeout_note)
        return subprocess.CompletedProcess(command, 0, b"linked\r\n", b"")

    out = prepare(tmp_path, monkeypatch, watch)
    monkeypatch.setattr(census, "wine_reset", lambda reason: resets.append(reason))

    log, _, code = census.link([tmp_path / "a.obj"], tag="census")

    assert code == 0
    assert calls == [12.0, 12.0]
    assert resets == ["after the census link timed out"]
    assert log == "linked\n"
    assert (out / "census.log").read_text(encoding="utf-8") == "linked\n"


def test_last_timeout_writes_the_attempt_log_before_failing(tmp_path, monkeypatch):
    calls, resets = [], []

    def watch(command, env, *, merge_output, timeout, timeout_note):
        calls.append(timeout)
        return subprocess.CompletedProcess(command, 124, b"", timeout_note)

    out = prepare(tmp_path, monkeypatch, watch)
    monkeypatch.setattr(census, "wine_reset", lambda reason: resets.append(reason))

    with pytest.raises(SystemExit, match="timed out after 12s on 2 attempt"):
        census.link([tmp_path / "a.obj"], tag="census")

    assert calls == [12.0, 12.0]
    assert resets == ["after the census link timed out",
                      "after the census link timed out for the last time"]
    log = (out / "census.log").read_text(encoding="utf-8")
    assert "link timed out after 12s" in log
