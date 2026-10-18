"""build.wine_path bounds a stuck winepath and clears Wine before retrying."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402


def test_winepath_timeout_resets_wine_and_retries(tmp_path, monkeypatch):
    calls, resets = [], []
    monkeypatch.setattr(build, "_WINE_PATH_CACHE", {})
    monkeypatch.setattr(build.shutil, "which", lambda name: "/usr/bin/winepath")

    def fake_check_output(command, text, timeout):
        calls.append(timeout)
        if len(calls) == 1:
            raise subprocess.TimeoutExpired(command, timeout)
        return "Z:\\tmp\\converted\n"

    monkeypatch.setattr(build.subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(build, "wine_reset",
                        lambda reason, *, label="build": resets.append((reason, label)))

    assert build.wine_path(tmp_path / "converted") == "Z:\\tmp\\converted"
    assert calls == [build.WINE_PATH_TIMEOUT, build.WINE_PATH_TIMEOUT]
    assert resets == [(f"after winepath -w {tmp_path / 'converted'} timed out", "build")]


def test_winepath_times_out_twice_loudly(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(build, "_WINE_PATH_CACHE", {})
    monkeypatch.setattr(build.shutil, "which", lambda name: "/usr/bin/winepath")

    def fake_check_output(command, text, timeout):
        calls.append(timeout)
        raise subprocess.TimeoutExpired(command, timeout)

    monkeypatch.setattr(build.subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(build, "wine_reset", lambda *args, **kwargs: None)

    with pytest.raises(SystemExit, match="Wine is stuck"):
        build.wine_path(tmp_path / "converted")
    assert len(calls) == 2
