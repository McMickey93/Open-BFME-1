"""matched_caller grades a proposal only on independent evidence and refuses the known false-positive shapes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matched_caller as M  # noqa: E402

BODY, STUB = 0x156070, 0x0001A2B3
REAL = "?groupAttackTeam@AIGroup@@QAEXPBVTeam@@HW4CommandSourceType@@@Z"


class FakeTruth:
    def __init__(self, ledger=None):
        self.ledger = ledger or {}

    def _stub(self, address):
        return BODY if address == STUB else None


def setup(monkeypatch, ledger=None):
    monkeypatch.setattr(M, "_TRUTH", FakeTruth(ledger))


def row(name, notes=""):
    return {"name": name, "notes": notes}


def call(caller="?doAttack@AIGroup@@QAEXXZ", home="0x100", by_pin=False):
    return {"caller": caller, "home": home, "by_pin": by_pin, "source": "a.cpp"}


def judge(calls, rows, callee=REAL, pins=None, oracle=lambda n, b: "UNTESTABLE", row_names=()):
    return M.judge(callee, BODY, STUB, calls, {BODY: rows}, set(row_names), pins or {}, oracle)


def test_access_variants_stay_in_their_group():
    assert M.access_variants("??1X@@MAE@XZ") == ["??1X@@EAE@XZ", "??1X@@UAE@XZ"]
    assert M.access_variants("?f@C@@QAEXXZ") == ["?f@C@@AAEXXZ", "?f@C@@IAEXXZ"]
    assert M.access_variants("??_7X@@6B@") == []


def test_oracle_grade_needs_a_unique_access_letter(monkeypatch):
    setup(monkeypatch)
    rows = [row("?groupGuardPosition@Open2Group156070@@QAEXXZ")]
    assert judge([call()], rows, oracle=lambda n, b: "CONFIRMED" if n == REAL else "CONTRADICTED")[0] == "oracle"
    assert judge([call()], rows, oracle=lambda n, b: "CONFIRMED")[0] == "single"


def test_refusals(monkeypatch):
    setup(monkeypatch)
    placeholder = [row("?dup_00156070@@YAXXZ")]
    assert judge([call()], [row("?ji_00156070@@YAXXZ")])[0] == "refused"                 # import thunk
    assert judge([call()], [row("?realName@C@@QAEXXZ")])[0] == "refused"                 # two real names
    assert judge([call()], placeholder, callee="??4VectorClassDummy@@QAEAAV0@ABV0@@Z")[0] == "refused"
    assert judge([call()], [row("?dup_00156070@@YAXXZ", "object-symbol=" + REAL)])[0] == "refused"  # circular
    assert judge([call()], placeholder, row_names={REAL})[0] == "refused"                 # already a row
    assert judge([call()], placeholder, oracle=lambda n, b: "CONTRADICTED")[0] == "refused"
    assert judge([call()], placeholder, pins={REAL: {frozenset({0x200000})}})[0] == "refused"


def test_object_symbol_elsewhere_is_refused(monkeypatch):
    setup(monkeypatch, {M.link_census._normal(REAL): {0xD16F0}})
    assert judge([call()], [row("?dup_00156070@@YAXXZ")])[0] == "refused"


def test_pin_readings_either_way_are_consistent(monkeypatch):
    setup(monkeypatch)
    pins = {REAL: {frozenset({STUB + 0x400000, STUB})}}      # a VA pin of the stub: one reading reaches the body
    grade, why = judge([call()], [row("?dup_00156070@@YAXXZ")], pins=pins,
                       oracle=lambda n, b: "CONFIRMED" if n == REAL else "CONTRADICTED")
    assert grade == "oracle" and any("pin lineage" in w for w in why)


def test_multi_needs_distinct_real_ledger_homed_callers(monkeypatch):
    setup(monkeypatch)
    monkeypatch.setattr(M, "upstream_declares", lambda name: True)
    rows = [row("?dup_00156070@@YAXXZ")]
    same_body = [call(home="0x100"), call(home="0x100")]
    assert judge(same_body, rows)[0] == "single"                                         # one COMDAT, two TUs
    placeholder_callers = [call("?f@Rva00100000@@QAEXXZ", "0x100"), call("?g@Rva00200000@@QAEXXZ", "0x200")]
    assert judge(placeholder_callers, rows)[0] == "single"                               # condition (c)
    pinned = [call(home="0x100", by_pin=True), call("?h@AIGroup@@QAEXXZ", "0x200")]
    assert judge(pinned, rows)[0] == "single"                                            # pin-homed caller
    good = [call(home="0x100"), call("?h@AIGroup@@QAEXXZ", "0x200")]
    assert judge(good, rows)[0] == "multi"
    assert judge(good, rows, pins={REAL: {frozenset({BODY})}})[0] == "single"             # agreement = a pin


def test_round2_template_access_and_tail_and_stand_in():
    tmpl = "??1?$_List_base@PAVDrawable@@V?$allocator@PAVDrawable@@@_STL@@@_STL@@QAE@XZ"
    assert any("@@AAE@XZ" in v for v in M.access_variants(tmpl))
    assert "?f@@YGXXZ" in M.access_variants("?f@@YAXXZ")
    assert "?g@C@@QBEIXZ" in M.tail_variants("?g@C@@QBEHXZ")
    assert not M.STAND_IN.search("?getOverallBestWinStreak@SkirmishBattleHonors@@QBEHXZ")
    assert M.STAND_IN.search("??4VectorClassDummy@@QAEAAV0@ABV0@@Z")
