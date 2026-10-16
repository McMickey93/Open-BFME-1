"""Round-8 review probes (build/linkfleet/test_probe_lc_r7.py), kept as regression tests."""
import sys
from pathlib import Path
WT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WT / "tools" / "tests")); sys.path.insert(0, str(WT / "tools"))
from test_zz_probe_r6 import _ledger, _run, HDR, Y, R, C  # noqa
import pytest

S = "?leaf@@YAXXZ"
D = "?gData@@3HA"
V = "??_7Foo@@6B@"
X = "?other@@YAXXZ"
FN = "targets/game/reverse/functions.csv"
DR = "targets/game/reverse/data_rows.csv"
DH = "name,address,address_kind,size,section,source,status,evidence,model\n"
DIR = "targets/game/reverse/dir32_addresses.csv"


def test_p1_single_definer_copy_callee_rehomed(monkeypatch, tmp_path):
    # Y is a single COMDAT copy in b.obj (e.g. a /Gy function), c.obj calls Y.
    # Y calls R; R's row re-homed -> Y's kept copy now "wrong". Census: retail.
    _ledger(monkeypatch, tmp_path, HDR + f"{R},,0x1000,16,game/r.cpp,matched,\n",
            HDR + f"{R},,0x2000,16,game/r.cpp,matched,\n")
    census = {"r.obj": ([], [R]), "b.obj": ([(Y, "dB", "retail")], []), "c.obj": ([], [])}
    now = {"r.obj": ([], [R]), "b.obj": ([(Y, "dB", "wrong")], [], [R]), "c.obj": ([], [], [Y])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


def test_p2_two_step_chain(monkeypatch, tmp_path):
    # Y shared (b, c); Y calls R (single copy in r.obj); R calls S; only S moves.
    # Y's verdict depends on R's ADDRESS only, so no flip is expected for Y;
    # R is not touched by c.obj. LINKS is correct here.
    _ledger(monkeypatch, tmp_path, HDR + f"{S},,0x1000,16,game/s.cpp,matched,\n",
            HDR + f"{S},,0x2000,16,game/s.cpp,matched,\n")
    census = {"r.obj": ([(R, "dR", "retail")], []), "b.obj": ([(Y, "dB", "retail")], []),
              "c.obj": ([(Y, "dB", "retail")], [])}
    now = {"r.obj": ([(R, "dR", "wrong")], [], [S]), "b.obj": ([(Y, "dB", "retail")], [], [R]),
           "c.obj": ([(Y, "dB", "retail")], [], [R])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    # c.obj touches R (it references it): R's copy flipped -> must not LINK
    assert not linked, ("false LINKS", sel, unk)


def test_p3_third_party_row_on_callee_address(monkeypatch, tmp_path):
    # R and X both claimed 0x1000 at the census (shared over-claim: Y's mismatch
    # there was "unknown", non-blocking). X's over-claim row is retired; now
    # Y's call to R disagrees with a single claim -> "wrong". Only X changed.
    _ledger(monkeypatch, tmp_path,
            HDR + f"{R},,0x1000,16,game/r.cpp,matched,\n{X},,0x1000,16,game/x.cpp,matched,\n",
            HDR + f"{R},,0x1000,16,game/r.cpp,matched,\n")
    census = {"r.obj": ([], [R]), "b.obj": ([(Y, "dB", "unknown")], []), "c.obj": ([(Y, "dB", "unknown")], [])}
    now = {"r.obj": ([], [R]), "b.obj": ([(Y, "dB", "wrong")], [], [R]), "c.obj": ([(Y, "dB", "wrong")], [], [R])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


def test_p4_data_reference_shared(monkeypatch, tmp_path):
    _ledger(monkeypatch, tmp_path, DH + f"{D},0x1000,va,4,.data,game/d.cpp,matched,e,m\n",
            DH + f"{D},0x1004,va,4,.data,game/d.cpp,matched,e,m\n", DR)
    census = {"b.obj": ([(Y, "dB", "retail")], []), "c.obj": ([(Y, "dB", "retail")], [])}
    now = {"b.obj": ([(Y, "dB", "wrong")], [], [D]), "c.obj": ([(Y, "dB", "wrong")], [], [D])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {DR})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


def test_p4b_data_reference_only_in_kept_holder(monkeypatch, tmp_path):
    # c.obj references Y only; Y's kept copy (b.obj, shared with d.obj) reads D.
    _ledger(monkeypatch, tmp_path, DH + f"{D},0x1000,va,4,.data,game/d.cpp,matched,e,m\n",
            DH + f"{D},0x1004,va,4,.data,game/d.cpp,matched,e,m\n", DR)
    census = {"b.obj": ([(Y, "dB", "retail")], []), "d.obj": ([(Y, "dB", "retail")], []), "c.obj": ([], [])}
    now = {"b.obj": ([(Y, "dB", "wrong")], [], [D]), "d.obj": ([(Y, "dB", "wrong")], [], [D]),
           "c.obj": ([], [], [Y])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {DR})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


@pytest.mark.parametrize("shared", [True, False])
def test_p5_vtable_dir32_real_diff(monkeypatch, tmp_path, shared):
    # a REAL dir32 diff (the r6 probe only passed through the unreadable-census fallback)
    _ledger(monkeypatch, tmp_path, f"name,va\n{V},0x00801000\n", f"name,va\n{V},0x00801008\n", DIR)
    census = {"b.obj": ([(Y, "dB", "retail")], []), "c.obj": ([], [])}
    now = {"b.obj": ([(Y, "dB", "wrong")], [], [V]), "c.obj": ([], [], [Y])}
    if shared:
        census["d.obj"] = ([(Y, "dB", "retail")], [])
        now["d.obj"] = ([(Y, "dB", "wrong")], [], [V])
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {DIR})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


def test_p6_changed_name_only_in_unreadable_holder(monkeypatch, tmp_path):
    _ledger(monkeypatch, tmp_path, HDR + f"{R},,0x1000,16,game/r.cpp,matched,\n",
            HDR + f"{R},,0x2000,16,game/r.cpp,matched,\n")
    census = {"b.obj": ([(Y, "dB", "retail")], []), "d.obj": ([(Y, "dB", "retail")], []), "c.obj": ([], [])}
    now = {"b.obj": ([(Y, "dB", "wrong")], [], [R]), "d.obj": ([(Y, "dB", "wrong")], [], [R]),
           "c.obj": ([], [], [Y])}
    import test_link_check as T
    orig = T._rule_fixture
    monkeypatch.setattr(T, "_rule_fixture", lambda *a, **k: orig(*a, **{**k, "stale_objects": ("b.obj",)}))
    import test_zz_probe_r6 as P
    monkeypatch.setattr(P, "_rule_fixture", lambda *a, **k: orig(*a, **{**k, "stale_objects": ("b.obj",)}))
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)


def test_p7_clean_no_truth_change_gets_real_verdict(monkeypatch, tmp_path):
    # no ledger change at all: a shared retail copy must still give LINKS
    census = {"b.obj": ([(Y, "dB", "retail")], []), "c.obj": ([(Y, "dB", "retail")], [])}
    now = {"b.obj": ([(Y, "dB", "retail")], [], [R]), "c.obj": ([(Y, "dB", "retail")], [], [R])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), set())
    print("refreshed", list(refreshed), sel, unk)
    assert linked and not unk


def test_p8_unrelated_truth_change_keeps_real_verdict(monkeypatch, tmp_path):
    _ledger(monkeypatch, tmp_path, HDR + f"{X},,0x1000,16,game/x.cpp,matched,\n",
            HDR + f"{X},,0x3000,16,game/x.cpp,matched,\n")
    census = {"b.obj": ([(Y, "dB", "retail")], []), "c.obj": ([(Y, "dB", "retail")], [])}
    now = {"b.obj": ([(Y, "dB", "retail")], [], [R]), "c.obj": ([(Y, "dB", "retail")], [], [R])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    assert linked and not unk


def test_p2a_pure_two_step(monkeypatch, tmp_path):
    # c.obj references Y only; Y shared (b, d) calls R; R (single copy, r.obj)
    # calls S; only S's row moves. Y's verdict depends on R's address: unchanged.
    _ledger(monkeypatch, tmp_path, HDR + f"{S},,0x1000,16,game/s.cpp,matched,\n",
            HDR + f"{S},,0x2000,16,game/s.cpp,matched,\n")
    census = {"r.obj": ([(R, "dR", "retail")], []), "b.obj": ([(Y, "dB", "retail")], []),
              "d.obj": ([(Y, "dB", "retail")], []), "c.obj": ([], [])}
    now = {"r.obj": ([(R, "dR", "wrong")], [], [S]), "b.obj": ([(Y, "dB", "retail")], [], [R]),
           "d.obj": ([(Y, "dB", "retail")], [], [R]), "c.obj": ([], [], [Y])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    assert linked and not unk


def test_p3b_co_claimant_of_own_address_retired(monkeypatch, tmp_path):
    # Y's OWN row shares 0x1000 with X's over-claim (verdict wrong->unknown);
    # X's row is retired: Y's copy is now "wrong". Only X changed.
    _ledger(monkeypatch, tmp_path,
            HDR + f"{Y},,0x1000,16,game/y.cpp,matched,\n{X},,0x1000,16,game/x.cpp,matched,\n",
            HDR + f"{Y},,0x1000,16,game/y.cpp,matched,\n")
    census = {"b.obj": ([(Y, "dB", "unknown")], []), "c.obj": ([(Y, "dB", "unknown")], [])}
    now = {"b.obj": ([(Y, "dB", "wrong")], []), "c.obj": ([(Y, "dB", "wrong")], [])}
    linked, sel, unk, refreshed = _run(monkeypatch, census, now, list(census), {FN})
    print("refreshed", list(refreshed), sel, unk)
    assert not linked, ("false LINKS", sel, unk)
