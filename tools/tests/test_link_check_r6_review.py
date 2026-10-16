"""Round-6 review probes (build/review_linkcheck_r5/test_probe_r5.py), kept as regression tests."""
import sys
from pathlib import Path
WT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WT / "tools" / "tests")); sys.path.insert(0, str(WT / "tools"))
from test_link_check import _rule_fixture, _Path, ROWS, _judge, C  # noqa
import pytest
S = "?shared@@YAXXZ"

def _run(monkeypatch, built, since, census, now, ledger, checked="c.obj", owners=None):
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, now, ledger=ledger,
                                            built=built, since=since, owners=owners, census_owners=owners,
                                            inputs={n: {'game/' + n[:-4] + '.cpp'} for n in census})
    ix["blockers"] = {"c.cpp": {"linked": True}}; ix["bytes"] = {"c.cpp": 10}
    mine = _Path(checked)
    C.apply_selection_rule(ix, [mine], None, ROWS, compile_limit=0)
    sel, unk = _judge(ix, mine, facts_of)
    res = {k: [] for k in ("unresolved", "duplicates", "comdat", "addresses")}
    res.update(selected=sel, preview_unknown=unk)
    return C.report("c.cpp", mine, res, ix, 10), sel, unk

@pytest.mark.parametrize("built", [None, {"c.obj", "a.obj"}])
def test_rehomed_strong_row_same_owner(monkeypatch, built):
    # census: a.obj defines S (retail); c.obj references S. Now: S re-homed to b.obj
    # (wrong body), owners unchanged ({} both times).
    census = {"a.obj": ([], [S]), "b.obj": ([], []), "c.obj": ([], [], [S])}
    now = {"a.obj": ([], []), "b.obj": ([(S, "dX", "wrong")], []), "c.obj": ([], [], [S])}
    linked, sel, unk = _run(monkeypatch, built, {"game/a.cpp", "game/b.cpp"}, census, now,
                            ["a.obj", "b.obj", "c.obj"])
    assert not linked, (sel, unk)

def test_truth_change_without_object_change(monkeypatch):
    # c.cpp (checked) only REFERENCES S. b.obj and d.obj both define COMDAT S
    # (digest dB); d.cpp owns S's row. Since the census only targets/game/
    # reverse/functions.csv changed: S's row was re-homed to another retail RVA
    # (same source, so ledger_owners is unchanged) -- or a symbols.csv pin for
    # S landed. Census verdict of the kept copy (b.obj, first) was "retail";
    # under today's truth dB is "wrong" (b/d not re-read: their inputs are
    # unchanged). The next census marks c `selected`.
    census = {"b.obj": ([(S, "dB", "retail")], []), "d.obj": ([(S, "dB", "retail")], []),
              "c.obj": ([], [], [S])}
    now = {"b.obj": ([(S, "dB", "wrong")], []), "d.obj": ([(S, "dB", "wrong")], []),
           "c.obj": ([], [], [S])}
    owners = {S: {"d.obj"}}
    linked, sel, unk = _run(monkeypatch, None, {"targets/game/reverse/functions.csv"}, census, now,
                            ["b.obj", "d.obj", "c.obj"], owners=owners)
    assert not linked, (sel, unk)


def test_command_moves_includes_asm(monkeypatch):
    """Round 6 F1: an .asm source whose ml command changed since the census moves."""
    import subprocess
    import build
    asm = next(p for p in (WT / "game").rglob("*.asm") if p.is_file())
    text = (WT / "tools/build.py").read_text()
    census_text = text.replace('"-Cx",', '"-Cp",')
    assert census_text != text
    real = subprocess.run

    def fake(cmd, *a, **k):
        if cmd[:2] == ["git", "show"]:
            return subprocess.CompletedProcess(cmd, 0, census_text, "")
        return real(cmd, *a, **k)
    monkeypatch.setattr(C.subprocess, "run", fake)
    obj = build.obj_path(asm)
    assert C.command_moves("deadbeef", {obj: asm}) == {obj.name}


def test_truth_changes_reads_rows_pins_and_object_symbols(monkeypatch, tmp_path):
    import subprocess
    old = "name,address,notes\n?a@@YAXXZ,0x1,x\n?b@@YAXXZ,0x2,y\n"
    new = "name,address,notes\n?a@@YAXXZ,0x1,x\n?b@@YAXXZ,0x3,y\n?c@@YAXXZ,0x4,z\n"
    monkeypatch.setattr(C, "ROOT", tmp_path)
    monkeypatch.setattr(C, "_TRUTH_MEMO", {})
    (tmp_path / "targets/game/reverse").mkdir(parents=True)
    (tmp_path / "targets/game/reverse/symbols.csv").write_text(new)
    monkeypatch.setattr(C.subprocess, "run",
                        lambda cmd, *a, **k: subprocess.CompletedProcess(cmd, 0, old, ""))
    since = {"targets/game/reverse/symbols.csv"}
    assert C.truth_changes("c", since, {"?a@@YAXXZ", "?b@@YAXXZ", "?c@@YAXXZ"}) == {"?b@@YAXXZ", "?c@@YAXXZ"}
    assert C.truth_changes("c", set(), {"?b@@YAXXZ"}) == set()           # no ledger file changed
    monkeypatch.setattr(C.subprocess, "run", lambda cmd, *a, **k: subprocess.CompletedProcess(cmd, 128, "", "x"))
    monkeypatch.setattr(C, "_TRUTH_MEMO", {})                             # memoised per process and commit
    assert C.truth_changes("c", since, {"?a@@YAXXZ"}) == {"?a@@YAXXZ"}   # unreadable census: all changed


def _hook_args(paths, **kw):
    return type("A", (), {"paths": paths, "compile_limit": None, "census_only": False, "deadline": 30, **kw})()


@pytest.mark.parametrize("unstaged", ["targets/game/reverse/functions.csv", "targets/game/reverse/symbols.csv",
                                      "targets/game/reverse/data_rows.csv", "tools/build.py",
                                      "inputs/reference/shims/sweep/mss.h", "game/new_header.h"])
def test_hook_unknown_for_any_unstaged_or_untracked_input(monkeypatch, capsys, unstaged):
    monkeypatch.setattr(C, "hook_unstaged", lambda: [unstaged])
    monkeypatch.setattr(C, "main", lambda *a, **k: pytest.fail("no preview over unstaged inputs"))
    assert C.hook_main(_hook_args(["game/a.cpp"])) == 0
    assert f"game/a.cpp: LINKED PREVIEW UNKNOWN (unstaged or untracked inputs differ from the staged state, " \
           f"e.g. {unstaged})" in capsys.readouterr().out


def test_hook_unstaged_lists_ledgers_tools_and_untracked_game_files(monkeypatch):
    calls = []

    def fake_git(*args, **kw):
        calls.append(args)
        return "targets/game/reverse/symbols.csv\0" if args[0] == "diff" else "game/new.h\0"
    monkeypatch.setattr(C, "_git", fake_git)
    assert C.hook_unstaged() == ["targets/game/reverse/symbols.csv", "game/new.h"]
    diff = calls[0]
    for path in ("game", "inputs", "tools", "targets/game/reverse"):   # every truth input (round 7 M1)
        assert path in diff
    assert ":(exclude)targets/game/reverse/re_attempts.log" in diff
    assert calls[1][:2] == ("ls-files", "-z") and "game" in calls[1]


@pytest.mark.parametrize("error", [ValueError("outside the repository"), FileNotFoundError("staged-deleted.cpp"),
                                   __import__("pickle").UnpicklingError("corrupt link_index.pkl"),
                                   SystemExit("link_check: no census index")])
def test_hook_always_exits_zero(monkeypatch, capsys, error):
    monkeypatch.setattr(C, "hook_unstaged", lambda: [])

    def boom(*a, **k):
        raise error
    monkeypatch.setattr(C, "main", boom)
    assert C.hook_main(_hook_args(["game/a.cpp"])) == 0
    assert "game/a.cpp: LINKED PREVIEW UNKNOWN (" in capsys.readouterr().out


def test_hook_refuses_census_only(monkeypatch, capsys):
    monkeypatch.setattr(C, "hook_unstaged", lambda: pytest.fail("refused before anything else"))
    assert C.hook_main(_hook_args(["game/a.cpp"], census_only=True)) == 0
    assert "--census-only is refused under --hook" in capsys.readouterr().out


def test_hook_timeout_never_contradicts_a_printed_verdict(tmp_path):
    """Two files: a.cpp gets its verdict, b.cpp hangs; at the deadline only
    b.cpp is UNKNOWN (timeout), the process exits 0, its children are killed."""
    import subprocess
    import sys as _sys
    code = ("import sys, time, subprocess; sys.path.insert(0, %r); import link_check as C\n"
            "C.hook_unstaged = lambda: []\n"
            "def fake(argv, hook=False):\n"
            "    C._REPORTED.add('game/a.cpp'); print('game/a.cpp: LINKS', flush=True)\n"
            "    child = subprocess.Popen(['sleep', '60']); open(%r, 'w').write(str(child.pid))\n"
            "    time.sleep(60)\n"
            "C.main = fake\n"
            "args = type('A', (), {'paths': ['game/a.cpp', 'game/b.cpp'], 'compile_limit': None, "
            "'census_only': False, 'deadline': 2})()\n"
            "C.hook_main(args)\n") % (str(C.ROOT / "tools"), str(tmp_path / "child.pid"))
    done = subprocess.run([_sys.executable, "-c", code], capture_output=True, text=True, timeout=60, cwd=C.ROOT)
    assert done.returncode == 0
    assert "game/b.cpp: LINKED PREVIEW UNKNOWN (timeout after 2s)" in done.stdout
    assert "game/a.cpp: LINKED PREVIEW UNKNOWN" not in done.stdout
    child = int((tmp_path / "child.pid").read_text())
    import os
    import time
    time.sleep(0.5)
    try:
        os.kill(child, 0)
        alive = open(f"/proc/{child}/stat").read().split()[2] != "Z"
    except OSError:
        alive = False
    assert not alive, "the hook left its child compile running"


def test_main_drops_build_recompile_only(monkeypatch):
    monkeypatch.setenv("BUILD_RECOMPILE_ONLY", "x.cpp")
    monkeypatch.setenv("CL", "/DFOO")
    monkeypatch.setattr(C, "load_index", lambda: (_ for _ in ()).throw(SystemExit("stop")))
    with pytest.raises(SystemExit):
        C.main(["game/a.cpp"])
    import os
    assert "BUILD_RECOMPILE_ONLY" not in os.environ and "CL" not in os.environ
