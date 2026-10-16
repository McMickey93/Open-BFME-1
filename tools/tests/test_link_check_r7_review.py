"""Round-7 review probes (build/linkfleet/test_probe_lc_r6.py), kept as regression tests."""
import sys, subprocess
from pathlib import Path
WT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WT / "tools" / "tests")); sys.path.insert(0, str(WT / "tools"))
from test_link_check import _rule_fixture, _Path, ROWS, _judge, C  # noqa
import pytest

Y = "?caller@@YAXXZ"     # inline COMDAT that calls R
R = "?callee@@YAXXZ"
HDR = "name,export_rva,target_rva,target_size,source,status,notes\n"

def _ledger(monkeypatch, tmp_path, old, new, path="targets/game/reverse/functions.csv"):
    real_root = C.ROOT
    (tmp_path / Path(path).parent).mkdir(parents=True, exist_ok=True)
    (tmp_path / path).write_text(new)
    real = subprocess.run
    def fake(cmd, *a, **k):
        if cmd[:2] == ["git", "show"] and cmd[2].endswith(":" + path):
            return subprocess.CompletedProcess(cmd, 0, old, "")
        if cmd[:2] == ["git", "show"]:
            return subprocess.CompletedProcess(cmd, 0, (real_root / cmd[2].split(":", 1)[1]).read_text(), "")
        return real(cmd, *a, **k)
    monkeypatch.setattr(C.subprocess, "run", fake)
    orig = C.truth_changes
    def tc(commit, since, names):
        saved = C.ROOT
        C.ROOT = tmp_path
        try:
            got = orig(commit, since, names)
        finally:
            C.ROOT = saved
        print("truth_changes ->", sorted(got))
        return got
    monkeypatch.setattr(C, "truth_changes", tc)

def _run(monkeypatch, census, now, ledger, since, owners=None):
    ix, refreshed, facts_of = _rule_fixture(monkeypatch, list(census), census, now, ledger=ledger,
                                            since=since, owners=owners, census_owners=owners,
                                            inputs={n: {'game/' + n[:-4] + '.cpp'} for n in census})
    ix["blockers"] = {"c.cpp": {"linked": True}}; ix["bytes"] = {"c.cpp": 10}
    mine = _Path("c.obj")
    C.apply_selection_rule(ix, [mine], None, ROWS, compile_limit=0)
    sel, unk = _judge(ix, mine, facts_of)
    res = {k: [] for k in ("unresolved", "duplicates", "comdat", "addresses")}
    res.update(selected=sel, preview_unknown=unk)
    return C.report("c.cpp", mine, res, ix, 10), sel, unk, refreshed

@pytest.mark.parametrize("change", ["rehome", "delete", "icf-owner"])
def test_callee_row_change_flips_caller_copy(monkeypatch, tmp_path, change):
    # b.obj and c.obj both carry COMDAT Y (identical dB); b first -> kept. Y's
    # body calls R. Census: Y retail. Since then only R's functions.csv row
    # moved (re-homed to a twin / deleted / icf-owner over-claim): Y's kept
    # copy now resolves its call to another address (or none) -> wrong/unknown.
    old = HDR + f"{R},,0x00001000,16,game/r.cpp,matched,\n"
    new = HDR + {"rehome": f"{R},,0x00002000,16,game/r.cpp,matched,\n",
                 "delete": "",
                 "icf-owner": f"{R},,0x00001000,16,game/r.cpp,matched,icf-owner=?x@@YAXXZ\n"}[change]
    _ledger(monkeypatch, tmp_path, old, new)
    census = {"r.obj": ([], [R]), "b.obj": ([(Y, "dB", "retail")], [], [R]),
              "c.obj": ([(Y, "dB", "retail")], [], [R])}
    verdict = "wrong" if change == "rehome" else "unknown"
    now = {"r.obj": ([], [R]), "b.obj": ([(Y, "dB", verdict)], [], [R]),
           "c.obj": ([(Y, "dB", verdict)], [], [R])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, ["r.obj", "b.obj", "c.obj"],
                                       {"targets/game/reverse/functions.csv"})
    print("refreshed", list(refreshed), "sel", sel, "unk", unk)
    assert not linked, ("false LINKS", sel, unk)

@pytest.mark.parametrize("case", ["rehome", "pin_add", "pin_delete", "data_row", "object_symbol"])
def test_direct_truth_change(monkeypatch, tmp_path, case):
    # The checked c.obj references Y; b.obj (first) and d.obj define COMDAT Y.
    path, old, new = {
        "rehome": ("targets/game/reverse/functions.csv", HDR + f"{Y},,0x1000,16,game/d.cpp,matched,\n",
                   HDR + f"{Y},,0x2000,16,game/d.cpp,matched,\n"),
        "pin_add": ("targets/game/reverse/symbols.csv", "name,address,notes\n",
                    f"name,address,notes\n{Y},0x2000,x\n"),
        "pin_delete": ("targets/game/reverse/symbols.csv", f"name,address,notes\n{Y},0x1000,x\n",
                       "name,address,notes\n"),
        "data_row": ("targets/game/reverse/data_rows.csv",
                     "name,address,address_kind,size,section,source,status,evidence,model\n"
                     f"{Y},0x1000,va,4,.data,game/d.cpp,matched,e,m\n",
                     "name,address,address_kind,size,section,source,status,evidence,model\n"
                     f"{Y},0x1004,va,4,.data,game/d.cpp,matched,e,m\n"),
        "object_symbol": ("targets/game/reverse/functions.csv",
                          HDR + f"?other@@YAXXZ,,0x1000,16,game/d.cpp,matched,object-symbol=?zzz@@YAXXZ\n",
                          HDR + f"?other@@YAXXZ,,0x1000,16,game/d.cpp,matched,object-symbol={Y}\n"),
    }[case]
    _ledger(monkeypatch, tmp_path, old, new, path)
    census = {"b.obj": ([(Y, "dB", "retail")], []), "d.obj": ([(Y, "dB", "retail")], []),
              "c.obj": ([], [], [Y])}
    now = {"b.obj": ([(Y, "dB", "wrong")], []), "d.obj": ([(Y, "dB", "wrong")], []),
           "c.obj": ([], [], [Y])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, ["b.obj", "d.obj", "c.obj"], {path},
                                       owners={Y: {"d.obj"}})
    print("refreshed", list(refreshed), "sel", sel, "unk", unk)
    assert not linked, ("false LINKS", sel, unk)

def test_dir32_change(monkeypatch, tmp_path):
    D = "?gData@@3HA"
    path = "targets/game/reverse/dir32_addresses.csv"
    census = {"b.obj": ([(Y, "dB", "retail")], [], [D]), "c.obj": ([], [], [Y, D])}
    now = {"b.obj": ([(Y, "dB", "wrong")], [], [D]), "c.obj": ([], [], [Y, D])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, ["b.obj", "c.obj"], {path})
    print("refreshed", list(refreshed), "sel", sel, "unk", unk)
    assert not linked, ("false LINKS", sel, unk)


@pytest.mark.parametrize("argv", [["--hook"], ["--hook", "--no-such-flag", "game/a.cpp"],
                                  ["--hook", "--deadline", "x", "game/a.cpp"]])
def test_hook_usage_errors_exit_zero(capsys, argv):
    assert C.main(argv) == 0
    assert "LINKED PREVIEW UNKNOWN" in capsys.readouterr().out


def test_truth_changes_normalises_anonymous_namespace_hashes(monkeypatch, tmp_path):
    old = "name,address,notes\n?f@?A0x1234abcd@@YAXXZ,0x1,x\n"
    new = "name,address,notes\n?f@?A0x9999ffff@@YAXXZ,0x1,x\n"
    _ledger(monkeypatch, tmp_path, old, new, "targets/game/reverse/symbols.csv")
    since = {"targets/game/reverse/symbols.csv"}
    assert C.truth_changes("c", since, {"?f@?A0x55555555@@YAXXZ"}) == set()
    assert C.truth_changes("c", since, None) == set()


def test_truth_changes_full_diff_and_unreadable_census(monkeypatch, tmp_path):
    old = HDR + f"{R},,0x00001000,16,game/r.cpp,matched,\n{Y},,0x2,4,game/y.cpp,matched,\n"
    new = HDR + f"{R},,0x00003000,16,game/r.cpp,matched,\n{Y},,0x2,4,game/y.cpp,matched,\n"
    _ledger(monkeypatch, tmp_path, old, new)
    assert C.truth_changes("c", {"targets/game/reverse/functions.csv"}, None) == {R}
    assert isinstance(C.truth_changes("", {"targets/game/reverse/functions.csv"}, None), C.AllNames)


def test_dir32_and_reloc_names_are_truth_files():
    assert "targets/game/reverse/dir32_addresses.csv" in C.TRUTH_FILES
    assert "targets/game/reverse/reloc_names.csv" in C.TRUTH_FILES
