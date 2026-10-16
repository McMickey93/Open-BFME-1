"""Round-9 review probes (build/linkfleet/test_probe_lc_r8.py), kept as regression tests."""
import sys
from pathlib import Path
WT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WT / "tools" / "tests")); sys.path.insert(0, str(WT / "tools"))
from test_zz_probe_r6 import _ledger, _run, HDR, Y, R, C  # noqa
import pytest

N = "?imported@@YAXXZ"
G = "?gen_thunk_00001000@@YAXXZ"
O = "?obj_sym@?A0x12345678@@YAXXZ"
D = "?gData@@3HA"
E = "?gOther@@3HA"
FN = "targets/game/reverse/functions.csv"
SY = "targets/game/reverse/symbols.csv"
DR = "targets/game/reverse/data_rows.csv"
DIR = "targets/game/reverse/dir32_addresses.csv"
DH = "name,address,address_kind,size,section,source,status,evidence,model\n"
SH = "name,address,notes\n"


def _single_holder(ref, verdict_now="wrong"):
    """c.obj references Y only; Y is a single COMDAT copy kept in b.obj whose body references `ref`."""
    census = {"b.obj": ([(Y, "dB", "retail")], [], [ref]), "c.obj": ([], [], [Y])}
    now = {"b.obj": ([(Y, "dB", verdict_now)], [], [ref]), "c.obj": ([], [], [Y])}
    return census, now


def test_q1_own_definition_reference(monkeypatch, tmp_path):
    # c.obj's OWN single COMDAT Y (kept in c) calls R; only R's row moves.
    _ledger(monkeypatch, tmp_path, HDR + f"{R},,0x1000,16,game/r.cpp,matched,\n",
            HDR + f"{R},,0x2000,16,game/r.cpp,matched,\n")
    census = {"r.obj": ([], [R]), "c.obj": ([(Y, "dB", "retail")], [])}
    now = {"r.obj": ([], [R]), "c.obj": ([(Y, "dB", "wrong")], [], [R])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


def test_q1b_own_definition_reference_kept_later_copy(monkeypatch, tmp_path):
    # c.obj first (kept) and d.obj both define Y; Y calls R; only R moves.
    _ledger(monkeypatch, tmp_path, HDR + f"{R},,0x1000,16,game/r.cpp,matched,\n",
            HDR + f"{R},,0x2000,16,game/r.cpp,matched,\n")
    census = {"r.obj": ([], [R]), "c.obj": ([(Y, "dB", "retail")], []), "d.obj": ([(Y, "dB", "retail")], [])}
    now = {"r.obj": ([], [R]), "c.obj": ([(Y, "dB", "wrong")], [], [R]), "d.obj": ([(Y, "dB", "wrong")], [], [R])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


@pytest.mark.parametrize("case", ["move", "reorder", "route_reorder"])
def test_q2_pin_moves_between_addresses(monkeypatch, tmp_path, case):
    # R has no functions.csv row: RetailTruth reads its FIRST symbols.csv pin
    # (link_census.pins: found.setdefault) and its FIRST route= note.
    old, new = {
        "move": (SH + f"{R},0x00001000,x\n", SH + f"{R},0x00002000,x\n"),
        # same two lines, swapped: the first pin (the one RetailTruth uses) moved
        "reorder": (SH + f"{R},0x00001000,a\n{R},0x00002000,b\n", SH + f"{R},0x00002000,b\n{R},0x00001000,a\n"),
        "route_reorder": (SH + f"{R},0x00003000,route=0x00001000\n{R},0x00004000,route=0x00002000\n",
                          SH + f"{R},0x00004000,route=0x00002000\n{R},0x00003000,route=0x00001000\n"),
    }[case]
    _ledger(monkeypatch, tmp_path, old, new, SY)
    census, now = _single_holder(R)
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {SY})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


def test_q3_row_size_change(monkeypatch, tmp_path):
    _ledger(monkeypatch, tmp_path, HDR + f"{R},,0x1000,16,game/r.cpp,matched,\n",
            HDR + f"{R},,0x1000,32,game/r.cpp,matched,\n")
    census, now = _single_holder(R)
    census["r.obj"] = ([], [R]); now["r.obj"] = ([], [R])
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


@pytest.mark.parametrize("case", ["own_row_added", "kind_flip"])
def test_q4_data_rows_at_reloc_target(monkeypatch, tmp_path, case):
    # Y's kept copy (b.obj, single) has a DIR32 to D; D's dir32 entry is unchanged.
    old, new = {
        # D gains a data row: RetailTruth.ledger outranks the dir32 pin
        "own_row_added": (DH, DH + f"{D},0x01000004,va,4,.data,game/d.cpp,matched,e,m\n"),
        "other_name_same_va": (DH, DH + f"{E},0x01000000,va,4,.data,game/d.cpp,matched,e,m\n"),
        "kind_flip": (DH + f"{D},0x01000000,va,4,.data,game/d.cpp,matched,e,m\n",
                      DH + f"{D},0x01000000,rva,4,.data,game/d.cpp,matched,e,m\n"),
    }[case]
    _ledger(monkeypatch, tmp_path, old, new, DR)
    census, now = _single_holder(D)
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {DR})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


@pytest.mark.parametrize("case", ["gen_import_row_retired", "gen_import_target_renamed", "route_note_dropped"])
def test_q5_import_route_change(monkeypatch, tmp_path, case):
    # N is pinned at the FF 25 thunk 0x1000 with route=; the thunk's gen-import row G
    # (another name) is what validated_import_routes requires. Only G or the note changes.
    gen = f"{G},,0x00001000,6,game/gen_small/imp.cpp,matched,gen-import;target={N}\n"
    pin = f"{N},0x00001000,route=KERNEL32.dll!imported\n"
    if case == "route_note_dropped":
        path, old, new = SY, SH + pin, SH + f"{N},0x00001000,x\n"
    else:
        path, old = FN, HDR + gen
        new = HDR if case == "gen_import_row_retired" else HDR + gen.replace(f"target={N}", "target=?x@@YAXXZ")
    _ledger(monkeypatch, tmp_path, old, new, path)
    if path == FN:   # the pin must be visible at both commits
        real = C.subprocess.run
        (tmp_path / SY).write_text(SH + pin)
        def fake(cmd, *a, **k):
            if cmd[:2] == ["git", "show"] and cmd[2].endswith(":" + SY):
                return C.subprocess.CompletedProcess(cmd, 0, SH + pin, "")
            return real(cmd, *a, **k)
        monkeypatch.setattr(C.subprocess, "run", fake)
    census, now = _single_holder(N)
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {path})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


@pytest.mark.parametrize("case", ["rehome", "note_added_elsewhere", "note_removed", "gen_alias_flag"])
def test_q6_truth_reaches_only_through_alias(monkeypatch, tmp_path, case):
    # b.obj's kept Y references O, the object symbol of ledger row X (object-symbol=O);
    # nobody references X itself. Only X's row (or another row's note) changes.
    X = "?ledger_name@@YAXXZ"
    M = "?m@@YAXXZ"
    base = f"{X},,0x1000,16,game/x.cpp,matched,object-symbol={O}\n"
    new = {
        "rehome": base.replace("0x1000", "0x2000"),
        "note_added_elsewhere": base + f"{M},,0x3000,16,game/m.cpp,matched,object-symbol={O}\n",
        "note_removed": f"{X},,0x1000,16,game/x.cpp,matched,\n",
        "gen_alias_flag": f"{X},,0x1000,16,game/x.cpp,matched,gen-alias;object-symbol={O}\n",
    }[case]
    _ledger(monkeypatch, tmp_path, HDR + base, HDR + new)
    # the object spells O with ITS anonymous-namespace hash
    O_obj = O.replace("12345678", "9abcdef0")
    census, now = _single_holder(O_obj)
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


# ---- false-UNKNOWN controls: a truth change that cannot reach the checked file
@pytest.mark.parametrize("path,old,new", [
    (SY, SH + "?far@@YAXXZ,0x00009000,x\n", SH + "?far@@YAXXZ,0x00009008,x\n"),
    (FN, HDR + "?far@@YAXXZ,,0x9000,16,game/f.cpp,matched,\n", HDR + "?far@@YAXXZ,,0x9000,24,game/f.cpp,matched,\n"),
    ("targets/game/reverse/ghidra_functions.csv", "rva,size,name\n0x00009000,16,FUN\n", "rva,size,name\n0x00009000,24,FUN\n"),
])
def test_q7_unrelated_change_still_links(monkeypatch, tmp_path, path, old, new):
    _ledger(monkeypatch, tmp_path, old, new, path)
    census, now = _single_holder(R, verdict_now="retail")
    census["r.obj"] = ([], [R]); now["r.obj"] = ([], [R])
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {path})
    print("refreshed", list(refreshed), sel, unk)
    assert linked and not unk, (sel, unk)


def test_va_spelled_pin_is_its_rva(monkeypatch, tmp_path):
    """symbols.csv spelling a pin as a VA (0x00401000) and later as the RVA
    (0x00001000) is one address: no change; and a co-claimant at the RVA is."""
    _ledger(monkeypatch, tmp_path, SH + f"{R},0x00401000,x\n?z@@YAXXZ,0x00001000,y\n",
            SH + f"{R},0x00401000,x\n", SY)
    import test_link_check as T  # noqa
    C._TRUTH_MEMO.clear()
    assert R in C.truth_changes("c", {SY}, {R})
