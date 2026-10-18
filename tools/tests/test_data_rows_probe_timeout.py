"""data_rows bounds Wine probe compiles and clears Wine before retrying."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import data_rows  # noqa: E402


class ProbeBuild:
    _SWEEP_INCLUDE_DIRS = []

    def __init__(self, codes):
        self.codes = iter(codes)
        self.calls = []
        self.resets = []

    def watch_compiler(self, command, env, *, merge_output, timeout, timeout_note):
        self.calls.append((merge_output, timeout))
        code = next(self.codes)
        if code == 124:
            return subprocess.CompletedProcess(command, 124, b"", timeout_note)
        return subprocess.CompletedProcess(command, code, b"probe ok\r\n", b"")

    def wine_reset(self, reason, *, label="build"):
        self.resets.append((reason, label))


def test_probe_timeout_resets_wine_and_retries(monkeypatch):
    monkeypatch.setattr(data_rows, "PROBE_TIMEOUT", 7.0)
    monkeypatch.setattr(data_rows, "PROBE_ATTEMPTS", 2)
    build = ProbeBuild([124, 0])

    proc = data_rows._run_probe(build, ["cl"], {})

    assert proc.returncode == 0
    assert proc.stdout == "probe ok\n"
    assert build.calls == [(True, 7.0), (True, 7.0)]
    assert build.resets == [("after a data-row probe timed out", "data_rows")]


def test_last_probe_timeout_returns_the_bounded_failure(monkeypatch):
    monkeypatch.setattr(data_rows, "PROBE_TIMEOUT", 7.0)
    monkeypatch.setattr(data_rows, "PROBE_ATTEMPTS", 2)
    build = ProbeBuild([124, 124])

    proc = data_rows._run_probe(build, ["cl"], {})

    assert proc.returncode == 124
    assert "data-row probe timed out after 7s" in proc.stdout
    assert build.calls == [(True, 7.0), (True, 7.0)]
    assert build.resets == [("after a data-row probe timed out", "data_rows")] * 2
