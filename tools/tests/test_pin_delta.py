"""The pin_consistency delta gate: no NEW candidate-list or identity debt.

Approved by the project lead 2026-10-16. The --candidates violations and
one-address-many-names cannot be baselined (baselines only shrink), so the
gate judges a diff instead: existing debt never blocks, new debt is refused.
The mistakes pinned down here:

  * a delta that re-reports existing debt would block every commit until the
    drain finishes, and would get the gate turned off;
  * dropping one bad address from a multi-body violation must pass, adding one
    must not;
  * an ILT-CONFIRMED pin passes even though its walk reaches a body another
    name owns, and an ILT-CONTRADICTED one is refused (the 829632cac6 pair);
  * the base side is DERIVED from the diff, so it must equal a full parse.
"""
import csv
import io
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import build  # noqa: E402
import ilt_oracle  # noqa: E402
import pin_consistency as P  # noqa: E402

PAIR_DTOR = "??1?$pair@$$CBVAsciiString@@W4BuildableStatus@@@_STL@@QAE@XZ"
PAIR_CONFIRMED, PAIR_CONTRADICTED = 0x0000FF10, 0x00036291
# A matched identity in the lib region: no ILT slot, so the oracle cannot judge
# a name there and the identity rule must.
EASTRING_DTOR, EASTRING_BODY = "??1EAStringC@@QAE@XZ", 0x00891B80
OTHER_BODY = 0x00850600            # ??0INIException, a 103-byte matched body
FAKE = "?fake@Foo@@QAEXXZ"
FREE_THUNK = 0x009F6C3A            # imports MSVCR71 free, not operator delete


# The tests below judge diffs against the live ledger, but every address a test
# reasons about is pinned to a fixed WORLD: its live rows and pins are dropped
# and exactly these stand there instead, so a landing on master (a row at
# 0x009E3880, the BattlePlan ctor, ...) cannot change what a test means.
# Image facts (ILT slots and windows, retail bytes) stay real.
GEN = dict(source="game/gen_small/thunks_036.cpp", notes="gen-thunk")
WORLD_ROWS = {
    0x00891B80: [("??1EAStringC@@QAE@XZ", 22, {})],                                  # EASTRING_BODY
    0x00850600: [("??0INIException@@QAA@HPBDZZ", 103, {})],                          # OTHER_BODY
    0x00479040: [("?winSetEnabledBorderColor@GameWindow@@QAEHHH@Z", 37, {})],       # BORDER_BODY
    0x009E3880: [],                                                                   # INI_LIST_BODY
    0x009F5370: [("??$_M_allocate_and_copy@PBUICoord2D@@@?$vector@UICoord2D@@V?$allocator@UICoord2D@@@"
                  "_STL@@@_STL@@IAEPAUICoord2D@@IPBU2@0@Z", 96, {})],                # COPY_BODY
    0x001C1EA0: [("?rva001C1EA0@Rva001C1EA0Object@@QAEX_N@Z", 64, {})],             # VIEW_PIN's body
    0x008AD8F0: [("?method@Rva008AD8F0@@QAEXPAX@Z", 603, {})],
    0x00285F10: [("??0BannerCarrierUpdate@@QAE@PAVThing@@PBVModuleData@@@Z", 164, {})],   # BP_BODY
    0x000287C7: [("??RRva000287C7FactoryCtorThunk@@QAEXXZ", 5, {})],
    0x0005F2B0: [("?Rva0005F2B0InitializeAppWindows@@YA_NPAXH_N@Z", 64, {})],       # UNT_BODY
    0x00134AF0: [("?j_00134af0@@YAXXZ", 5, GEN)],                                    # PAIR_BODY
    0x00887940: [("??1AsciiString@@QAE@XZ", 46, {}), ("??1UnicodeString@@QAE@XZ", 46, {})],  # RELEASE
    0x003872F0: [],
}
WORLD_PINS = {
    0x00891B80: [("??1Rva8CD130String@@QAE@XZ", "test")],
    0x009E3880: [("??1?$List@PAUINISection@@@@UAE@XZ", "test")],
    0x009F5370: [("??$_M_allocate_and_copy@PBUICoord2D@@@?$vector@UICoord2D@@V?$allocator@UICoord2D@@@"
                  "_STL@@@_STL@@IAEPAUICoord2D@@IPBU2@0@Z", "test")],
    0x0001E33F: [("?rva001C1EA0@Rva002E6B70Object@@QAEX_N@Z",
                  "abi-view=?rva001C1EA0@Rva001C1EA0Object@@QAEX_N@Z;test")],
    0x008AD8F0: [("?bfmeApply1236@BfmeB1236@@QAEXPAX@Z", "test")],
    0x00285F10: [("?construct@AutoHealBehaviorModuleData@@AAEXXZ", "test"),
                 ("?construct@AutoHealBehaviorModuleData@@QAEXXZ", "test"),
                 ("?construct@Rva000287C7FactoryCtorTarget@@QAEXXZ", "test")],
    0x000287C7: [("??0?$BFMEFactoryModuleData@VBattlePlanUpdateModuleData@@$0KA@@@QAE@XZ", "test")],
    0x0005F2B0: [],
    0x00018633: [("??1?$pair@$$CBVAsciiString@@PAVThingTemplate@@@_STL@@QAE@XZ", "test")],
    0x0000FF10: [],
    0x003872F0: [],
    0x00036291: [],
}


@pytest.fixture(scope="module")
def rows():
    live = [r for r in build.load_all_function_rows() if int(r["target_rva"], 16) not in WORLD_ROWS]
    return live + [row(name, address, size, **extra)
                   for address, claims in sorted(WORLD_ROWS.items())
                   for name, size, extra in claims]


@pytest.fixture(scope="module")
def scanner(rows):
    return P.Scanner(rows)


@pytest.fixture(scope="module")
def live_scanner():
    """The checkout's own ledger, for the override tests that need a built
    caller object: those read real rows and skip when the object is absent."""
    return P.Scanner()


@pytest.fixture(scope="module")
def symbols_text():
    lines = build.SYMBOLS.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [lines[0]]
    for line in lines[1:]:
        try:
            address = int(line.split(",", 2)[1], 16)
        except (IndexError, ValueError):
            address = None
        if address not in WORLD_PINS:
            kept.append(line if line.endswith("\n") else line + "\n")
    kept += [f"{name},0x{address:08X},{notes}\n"
             for address, pins in sorted(WORLD_PINS.items()) for name, notes in pins]
    return "".join(kept)


def pin(name, address, notes="test"):
    return P._norm({"name": name, "address": f"0x{address:08X}", "notes": notes}, P.PIN_FIELDS)


def row(name, address, size, source="game/Test/Fake.cpp", status="matched", notes="test"):
    return P._norm({"name": name, "export_rva": "", "target_rva": f"0x{address:08X}",
                    "target_size": str(size), "source": source, "status": status,
                    "notes": notes}, P.FUNCTION_FIELDS)


def _line(p):
    return f"{p['name']},{p['address']},{P.joined(p)}\n"


def fake_delta(tmp_path, rows, symbols_text, *, pins_added=(), pins_removed=(),
               rows_added=(), rows_removed=()):
    """A Delta whose new side is ROWS/SYMBOLS_TEXT with the diff applied, no git."""
    work = P.Delta.__new__(P.Delta)
    work.base_ref, work.new_ref = "BASE", ":"
    work.new_rows = P._multiset_minus(list(rows), rows_removed, P.FUNCTION_FIELDS) + \
        [dict(r) for r in rows_added]
    gone = {_line(p) for p in pins_removed}
    kept = "".join(l for l in symbols_text.splitlines(keepends=True)
                   if l.replace("\r", "") not in gone)
    work.new_symbols = tmp_path / "symbols.csv"
    work.new_symbols.write_text(kept + "".join(_line(p) for p in pins_added),
                                encoding="utf-8", newline="")
    work.pins_added, work.pins_removed = list(pins_added), list(pins_removed)
    work.rows_added, work.rows_removed = list(rows_added), list(rows_removed)
    work._group()
    return work


def conflicts(tmp_path, rows, scanner, symbols_text, warnings=None, **diff):
    work = fake_delta(tmp_path, rows, symbols_text, **diff)
    if scanner is None or diff.get("rows_added") or diff.get("rows_removed"):
        scanner = P.Scanner(work.new_rows)
    return [(kind, name, address) for kind, name, address, _why
            in P.new_identity_conflicts(work, scanner, work.base_scanner(scanner),
                                        ilt_oracle.oracle(), warnings)]


# -- identity: one address, many names --------------------------------------

def test_the_ilt_confirmed_pin_of_829632cac6_passes(tmp_path, rows, scanner, symbols_text):
    """0x0000FF10 walks to the shared AsciiString release body, which other
    names own; the ILT slot itself proves the pair destructor, so it passes."""
    assert ilt_oracle.check(PAIR_DTOR, PAIR_CONFIRMED)[0] == ilt_oracle.CONFIRMED
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     pins_added=[pin(PAIR_DTOR, PAIR_CONFIRMED)]) == []


def test_the_ilt_contradicted_pin_is_refused(tmp_path, rows, scanner, symbols_text):
    """The same name on 0x00036291, whose slot's window excludes it."""
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     pins_added=[pin(PAIR_DTOR, PAIR_CONTRADICTED)]) == \
        [("ilt-contradicted", PAIR_DTOR, PAIR_CONTRADICTED)]


def test_a_pin_on_another_identity_is_refused(tmp_path, rows, scanner, symbols_text):
    assert ilt_oracle.check(FAKE, EASTRING_BODY)[0] == ilt_oracle.UNTESTABLE
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     pins_added=[pin(FAKE, EASTRING_BODY)]) == \
        [("pin-on-other-identity", FAKE, EASTRING_BODY)]


def test_a_pin_naming_its_own_identity_passes(tmp_path, rows, scanner, symbols_text):
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     pins_added=[pin(EASTRING_DTOR, EASTRING_BODY)]) == []


def test_only_a_placeholder_spelling_its_own_address_is_exempt(tmp_path, rows, scanner,
                                                               symbols_text):
    """The frozen-gen-caller compat pin (owner ruling 2026-10-15) claims no
    identity; the same spelling one byte off is an identity claim and judged."""
    own, off = "?d_00891b80@@YAXXZ", "?d_00891b81@@YAXXZ"
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     pins_added=[pin(own, EASTRING_BODY)]) == []
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     pins_added=[pin(off, EASTRING_BODY)]) == \
        [("pin-on-other-identity", off, EASTRING_BODY)]


def test_an_inadmissible_route_is_refused(tmp_path, rows, scanner, symbols_text):
    """route= buys the exemption only when the image proves it."""
    found = conflicts(tmp_path, rows, scanner, symbols_text,
                      pins_added=[pin("??3@YAXPAX@Z", FREE_THUNK, "route=MSVCR71.dll!free")])
    assert [(kind, name) for kind, name, _a in found] == [("route", "??3@YAXPAX@Z")]


def test_an_identity_row_on_another_identity_is_refused(tmp_path, rows, scanner, symbols_text):
    """The row side of one-address-many-names; a generated row claims nothing."""
    real = row(FAKE, EASTRING_BODY, 22)
    generated = row("?d_00891b80@@YAXXZ", EASTRING_BODY, 22, source="game/gen_asm/d_x.asm",
                    notes="gen-dump")
    assert conflicts(tmp_path, rows, scanner, symbols_text, rows_added=[real]) == \
        [("row-on-other-identity", FAKE, EASTRING_BODY)]
    assert conflicts(tmp_path, rows, scanner, symbols_text, rows_added=[generated]) == []


def test_an_edited_pin_is_not_an_added_pin(tmp_path, rows, scanner, symbols_text):
    """A notes-only edit shows as -/+ of one (name, address); nothing is added,
    and a pin that conflicted before and after is no NEW conflict."""
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     pins_added=[pin(FAKE, EASTRING_BODY, "new note")],
                     pins_removed=[pin(FAKE, EASTRING_BODY, "old note")]) == []


# Review round 1 (2026-10-16), one regression per finding.

BORDER_BODY = 0x00479040            # ?winSetEnabledBorderColor@GameWindow@@QAEHHH@Z, 37 bytes
BORDER_VARIANT = "?winSetEnabledBorderColor@GameWindow@@QAEHII@Z"
INI_LIST_BODY = 0x009E3880          # pinned ??1?$List@PAUINISection@@@@UAE@XZ, no row
INI_BLOCK_LIST = "??1?$List@PAUINIBlock@@@@UAE@XZ"
SPELLING = "?method@Rva00479040Window@@QAEHHH@Z"   # a second, address-derived spelling


def test_r1_2_confirmed_does_not_beat_a_real_owner(tmp_path, rows, scanner, symbols_text):
    """A signature variant salted to fit the slot's window is CONFIRMED; the
    body already has a real name the slot does not refute, so it is refused."""
    assert ilt_oracle.check(BORDER_VARIANT, BORDER_BODY)[0] == ilt_oracle.CONFIRMED
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     pins_added=[pin(BORDER_VARIANT, BORDER_BODY)]) == \
        [("pin-on-other-identity", BORDER_VARIANT, BORDER_BODY)]


def test_r1_3_a_pin_only_name_is_an_identity(tmp_path, rows, scanner, symbols_text):
    """No functions.csv row names 0x009E3880; its real-name pin does."""
    assert not scanner.identities.get(INI_LIST_BODY)
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     pins_added=[pin(INI_BLOCK_LIST, INI_LIST_BODY)]) == \
        [("pin-on-other-identity", INI_BLOCK_LIST, INI_LIST_BODY)]


def _row_at(rows, address):
    return next(P._norm(r, P.FUNCTION_FIELDS) for r in rows
                if int(r["target_rva"], 16) == address and P.names_identity(r))


def test_r1_4_demoting_the_owner_in_the_same_commit_does_not_clear_the_way(
        tmp_path, rows, scanner, symbols_text):
    """A placeholder spelling, so the ILT has no say and only identity decides."""
    owner = _row_at(rows, BORDER_BODY)
    demoted = dict(owner, status="failed")
    found = conflicts(tmp_path, rows, scanner, symbols_text, rows_removed=[owner],
                      rows_added=[demoted], pins_added=[pin(SPELLING, BORDER_BODY)])
    assert ("pin-on-other-identity", SPELLING, BORDER_BODY) in found
    found = conflicts(tmp_path, rows, scanner, symbols_text, rows_removed=[owner],
                      pins_added=[pin(SPELLING, BORDER_BODY)])
    assert ("pin-on-other-identity", SPELLING, BORDER_BODY) in found


def test_r1_4_a_rename_moves_the_identity(tmp_path, rows, scanner, symbols_text):
    """Replacing the row at its own address and pinning the new name passes."""
    owner = _row_at(rows, EASTRING_BODY)
    renamed = dict(owner, name=FAKE)
    old_pin = [r for r in (P._norm(x, P.PIN_FIELDS) for x in
                           csv.DictReader(io.StringIO(symbols_text)))
               if int(r["address"], 16) == EASTRING_BODY]
    found = conflicts(tmp_path, rows, scanner, symbols_text, rows_removed=[owner],
                      rows_added=[renamed], pins_removed=old_pin,
                      pins_added=[pin(FAKE, EASTRING_BODY)])
    assert found == []


# A body named by one row and a same-name pin on the body itself; no ILT slot,
# so only identity can decide.
COPY_BODY = 0x009F5370
COPY_NAME = ("??$_M_allocate_and_copy@PBUICoord2D@@@?$vector@UICoord2D@@V?$allocator@UICoord2D@@@"
             "_STL@@@_STL@@IAEPAUICoord2D@@IPBU2@0@Z")
# An abi-view pin whose body is named differently (its canonical).
VIEW_NAME, VIEW_PIN = "?rva001C1EA0@Rva002E6B70Object@@QAEX_N@Z", 0x0001E33F


def test_r1_5_a_rename_that_leaves_the_old_pin_behind_is_refused(tmp_path, rows, scanner,
                                                                 symbols_text):
    owner = _row_at(rows, COPY_BODY)
    assert owner["name"] == COPY_NAME
    other = "?copyOther@ICoord2DVector@@QAEXXZ"          # a real, different name
    found = conflicts(tmp_path, rows, scanner, symbols_text, rows_removed=[owner],
                      rows_added=[dict(owner, name=other)])
    assert ("existing-pin-now-conflicts", COPY_NAME, COPY_BODY) in found
    # the renamed row is refused too: the left-behind real pin still names the body
    assert ("row-on-other-identity", other, COPY_BODY) in found
    # renaming to an alias spelling (option a) leaves the real pin the body's
    # only identity, and the alias row landing beside it is refused
    alias = "?method@Rva009F5370Vector@@QAEXXZ"
    found = conflicts(tmp_path, rows, scanner, symbols_text, rows_removed=[owner],
                      rows_added=[dict(owner, name=alias)])
    assert found == [("row-on-other-identity", alias, COPY_BODY)]


def test_r1_5_losing_abi_view_on_an_alias_pin_only_warns(tmp_path, rows, scanner,
                                                         symbols_text):
    """VIEW_NAME is an address-derived spelling, and so is its body's only row
    (?rva001C1EA0@Rva001C1EA0Object): once it is no view, an alias pin on an
    alias-named body is no conflict at all (option a); against a real name it
    would warn, not block (option b)."""
    view = next(r for r in (P._norm(x, P.PIN_FIELDS) for x in
                            csv.DictReader(io.StringIO(symbols_text)))
                if r["name"] == VIEW_NAME and int(r["address"], 16) == VIEW_PIN)
    assert P.pin_exemption(view) == "view" and P.alias_spelling(VIEW_NAME)
    plain = dict(view, notes="no longer a view", _overflow="")
    warnings = []
    found = conflicts(tmp_path, rows, scanner, symbols_text, warnings, pins_removed=[view],
                      pins_added=[plain])
    assert found == [] and warnings == []


# Option (b), project lead 2026-10-16: an existing ALIAS pin left on a body a
# real row now names warns and is listed; a REAL-named one still blocks.

def test_b_the_alias_predicate_is_the_ilt_tier():
    aliases = ["?method@Rva008AD8F0@@QAEXPAX@Z", "?rva001C1EA0@Object@@QAEX_N@Z",
               "?bfmeApply1236@BfmeB1236@@QAEXPAX@Z", "?BfmeGo921E@@YGXPAX@Z",
               "?d_008ad8f0@@YAXXZ", "?dup_00499f30@@YAXXZ", "?j_00134af0@@YAXXZ",
               "??1Gen_uw_000224d0@@QAE@XZ", "??0ArrayValue008B9C60@@QAE@XZ", "$L314"]
    real = ["??1EAStringC@@QAE@XZ", "?winSetEnabledBorderColor@GameWindow@@QAEHHH@Z",
            "??0TBuff@@QAE@PAVDrawable@@H@Z", PAIR_DTOR]
    assert [n for n in aliases if not P.alias_spelling(n)] == []
    assert [n for n in real if P.alias_spelling(n)] == []


def test_b_a_row_landing_under_an_alias_pin_warns_and_is_logged(tmp_path, rows, scanner,
                                                                symbols_text, monkeypatch):
    """376d78b9c1: ?method@Rva008AD8F0 lands on 0x008AD8F0 and ?bfmeApply1236
    stays; both are aliases, so nothing conflicts; the log keeps one line per key."""
    body = 0x008AD8F0
    owner = next(P._norm(r, P.FUNCTION_FIELDS) for r in rows if int(r["target_rva"], 16) == body)
    alias = "?bfmeApply1236@BfmeB1236@@QAEXPAX@Z"
    assert P.alias_spelling(alias)
    placeholder = dict(owner, name="?d_008ad8f0@@YAXXZ", source="game/gen_asm/d_008a9710.asm",
                       notes="gen-dump")
    work = fake_delta(tmp_path, rows, symbols_text, rows_removed=[placeholder], rows_added=[])
    work.new_rows = list(rows)                 # the new side is today's ledger
    work.rows_added = [owner]
    work._group()
    warnings = []
    found = P.new_identity_conflicts(work, scanner, work.base_scanner(scanner),
                                     ilt_oracle.oracle(), warnings)
    assert found == []
    # option (a): the landing row ?method@Rva008AD8F0 is itself an alias
    # spelling, so the alias pin beside it is no conflict and nothing is listed
    assert warnings == []
    entries = [("existing-pin-now-conflicts", alias, body, "walk: test", body, "376d78b9c1")]
    log = tmp_path / "alias.tsv"
    monkeypatch.setenv("BFME_PIN_ALIAS_LOG", str(log))
    P.record_alias_cleanup(entries)
    P.record_alias_cleanup(entries)
    lines = log.read_text().splitlines()
    assert lines[0].split("\t") == P.ALIAS_LOG_FIELDS
    assert len(lines) == 2, "one line per (name, address, body), however often it is seen"
    assert lines[1].split("\t")[:5] == [alias, "0x008AD8F0", "0x008AD8F0",
                                          "existing-pin-now-conflicts", "376d78b9c1"]


def test_r1_6_a_pin_inside_a_named_body_is_refused(tmp_path, rows, scanner, symbols_text):
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     pins_added=[pin(FAKE, BORDER_BODY + 0x10)]) == \
        [("pin-inside-body", FAKE, BORDER_BODY + 0x10)]


# 0x008AD8F0's object (built by this worktree's gate) calls 0x008AD750 at
# 0x008AD909 through a REL32 naming exactly this symbol.
BINDING_CALLER, BINDING_CALLEE = 0x008AD8F0, 0x008AD750
BINDING_NAME = "?refresh@Rva008AD750StringBinding@@QAEXPAVRva8CD130Value@@@Z"


def _binding_object_ready():
    import delta_sources
    row = next(r for r in build.load_all_function_rows()
               if int(r["target_rva"], 16) == BINDING_CALLER and r["status"] == "matched")
    obj = build.row_object(row)
    return obj.exists() and delta_sources.object_is_current(build.ROOT / row["source"], obj)


def test_r2_1_an_override_needs_the_callers_relocation(live_scanner):
    """Review round 2: a word in the caller's source (a comment) once passed.
    Only the caller's compiled object, naming the exact symbol at the call
    site, proves the override."""
    if not _binding_object_ready():
        pytest.skip("0x008AD8F0's object is not built in this checkout")
    why = "caller=0x008AD8F0 calls it under this name"
    assert P.verify_override(live_scanner, None, BINDING_NAME, BINDING_CALLEE, why) is None
    for other in (FAKE, "?refresh@Rva008AD750StringBinding@@QAEXPAVOther@@@Z",
                  "??0Rva008AD750StringBinding@@QAE@XZ"):
        assert "object names" in P.verify_override(live_scanner, None, other, BINDING_CALLEE, why)
    assert "no E8/E9" in P.verify_override(live_scanner, None, BINDING_NAME, BINDING_CALLEE + 1, why)


def test_r2_1_generated_noted_and_masm_callers_prove_nothing(live_scanner):
    funclet = "caller=0x00C57408 its unwind funclet destroys the string"     # gen-funclet note
    assert "hand-written C++" in P.verify_override(live_scanner, None, "??1Rva8CD130String@@QAE@XZ",
                                                   EASTRING_BODY, funclet)
    masm = next(r for r in build.load_all_function_rows()
                if r["status"] == "matched" and r["source"].startswith("game/masm_dumps/"))
    why = f"caller={masm['target_rva']} a hand-written dump"
    assert "hand-written C++" in P.verify_override(live_scanner, None, FAKE, EASTRING_BODY, why)
    assert "no caller" in P.verify_override(live_scanner, None, FAKE, EASTRING_BODY, "trust me, it is")


def test_r2_1_a_stale_object_proves_nothing(live_scanner, monkeypatch):
    import delta_sources
    monkeypatch.setattr(delta_sources, "object_is_current", lambda source, obj: False)
    why = "caller=0x008AD8F0 calls it under this name"
    assert "missing or stale" in P.verify_override(live_scanner, None, BINDING_NAME, BINDING_CALLEE, why)


def test_r2_2_alias_means_the_functions_own_components():
    """Placeholder PARAMETER types do not make a real Class::method an alias,
    and generator tokens count only at a boundary with their address."""
    assert not P.alias_spelling("?calculate@PartitionManagerImpl@@QAEXPAUGen009F5040Node@@PAH11@Z")
    assert not P.alias_spelling("?Update_Sub_Object_Transforms@RenderObjClass@@UAEXXZ")
    assert ilt_oracle.tier("?Update_Sub_Object_Transforms@RenderObjClass@@UAEXXZ") == "real"
    assert ilt_oracle.tier("?Set_Fun_Mode@Foo@@QAEXXZ") == "real"
    assert ilt_oracle.tier("sub_00401000") == "placeholder"
    assert ilt_oracle.tier("?x@@YAXPAUFoo_Gen_@@@Z") == "placeholder"   # Gen_ at a boundary
    assert ilt_oracle.tier("?x@GenericThing@@QAEXXZ") == "real"
    assert P.alias_spelling("??1?$pair@$$CBVAsciiString@@W4Rva001360E0Mapped@@@_STL@@QAE@XZ"), \
        "a class's own template arguments are part of the class"


def test_r2_3_the_identity_tools_are_protected_and_pinned_at_push():
    import protected_paths
    assert protected_paths.protected(["tools/abi_view.py", "tools/ilt_oracle.py",
                                      "tools/pin_consistency.py"]) == \
        ["tools/abi_view.py", "tools/ilt_oracle.py", "tools/pin_consistency.py"]
    hook = (TOOLS.parent / ".githooks/pre-push").read_text()
    loop = hook[hook.index("for checker in tools/pin_consistency.py"):]
    loop = loop[:loop.index("done")]
    assert "differs from pushed snapshot" in loop
    for tool in ("pin_consistency.py", "ilt_oracle.py", "abi_view.py"):
        assert f"tools/{tool}" in loop


def test_r2_4_a_moved_identity_does_not_guard_the_address_it_left(tmp_path, rows, scanner,
                                                                 symbols_text):
    """The row moves to another address in the same commit; pinning the
    vacated address is judged against the new state only."""
    owner = _row_at(rows, EASTRING_BODY)
    moved = dict(owner, target_rva="0x00891B90")
    work = fake_delta(tmp_path, rows, symbols_text, rows_removed=[owner],
                      rows_added=[moved], pins_added=[pin(FAKE, EASTRING_BODY)])
    new_scanner = P.Scanner(work.new_rows)
    found = P.new_identity_conflicts(work, new_scanner, work.base_scanner(new_scanner),
                                     ilt_oracle.oracle())
    # not refused for the moved real name; what stays behind is the alias pin
    # ??1Rva8CD130String, and alias pins never block (option b)
    assert found == []


def test_r1_7_an_override_is_exact_and_never_excuses_a_contradiction():
    found = [("pin-on-other-identity", FAKE, EASTRING_BODY, "w"),
             ("pin-on-other-identity", FAKE, EASTRING_BODY + 1, "w"),
             ("ilt-contradicted", FAKE, EASTRING_BODY, "w"),
             ("pin-inside-body", FAKE, EASTRING_BODY, "w")]
    left, applied = P.apply_overrides(found, {(FAKE, EASTRING_BODY): "caller=0x1 why"})
    assert left == found[1:] and [c for c, _r in applied] == found[:1]


def test_r1_8b_one_parser_for_both_sides():
    """A route= past an unquoted comma: --check (load_routes) reads only the
    first notes field, abi_view the joined notes; the delta reads both the same
    way on both sides."""
    raw = next(csv.DictReader(io.StringIO(
        "name,address,notes\n?x@@YAXXZ,0x00001000,first, then; route=0x00002000\n")))
    norm = P._norm(raw, P.PIN_FIELDS)
    assert norm["notes"] == "first" and P.pin_exemption(norm) is None
    assert P.joined(norm) == "first, then; route=0x00002000"


def test_r1_8c_the_diff_is_literal():
    assert "--no-textconv" in P._diff_sides("A", "B") and "--no-ext-diff" in P._diff_sides("A", None)


# -- the candidate list: one name, many addresses ---------------------------

def test_a_new_candidate_on_another_body_is_new_debt(tmp_path, rows, scanner, symbols_text):
    """A second candidate for a consistent name, at a body of another size."""
    work = fake_delta(tmp_path, rows, symbols_text,
                      pins_added=[pin(EASTRING_DTOR, OTHER_BODY)])
    new_lists = P.candidate_lists(work.new_rows, work.new_symbols)
    debt, affected = P.new_candidate_debt(work, work.base_scanner(scanner), scanner, new_lists)
    assert [(v["symbol"], v["kind"]) for v in debt] == [(EASTRING_DTOR, "size-disagreement")]
    assert affected >= 1


class StubImage:
    def resolve(self, address):
        return address, [address]


class StubScanner:
    """inspect() calls any set containing a 'bad' address a violation."""

    def __init__(self, bad):
        self.bad, self.image = bad, StubImage()

    def inspect(self, name, addresses):
        bodies = sorted(set(addresses))
        if len(bodies) > 1 and set(bodies) & self.bad:
            return {"symbol": name, "bodies": bodies, "kind": "divergent-bodies", "evidence": ""}
        return None


class StubDelta:
    def __init__(self, touched, base_sets, changed=()):
        self._touched, self._base, self.changed = touched, base_sets, set(changed)

    def touched_names(self):
        return set(self._touched)

    def base_candidates(self, names):
        return {n: set(self._base.get(n, ())) for n in names}


def debt_of(new_lists, base_sets, touched, bad=frozenset({0xB1, 0xB2})):
    stub = StubScanner(set(bad))
    debt, _affected = P.new_candidate_debt(StubDelta(touched, base_sets), stub, stub, new_lists)
    return [v["symbol"] for v in debt]


def test_existing_debt_never_blocks():
    """The 210 drained by op-1 stay red in --candidates and never block a diff."""
    assert debt_of({"old": [0xA0, 0xB1], "other": [0xA0, 0xA1]},
                   {"other": [0xA0]}, touched={"other"}) == []


def test_dropping_a_bad_address_passes_and_adding_one_is_refused():
    assert debt_of({"x": [0xA0, 0xB1]}, {"x": [0xA0, 0xB1, 0xB2]}, touched={"x"}) == []
    assert debt_of({"x": [0xA0, 0xB1, 0xB2]}, {"x": [0xA0, 0xB1]}, touched={"x"}) == ["x"]
    assert debt_of({"x": [0xA0, 0xB2]}, {"x": [0xA0, 0xB1]}, touched={"x"}) == ["x"], \
        "swapping one bad body for another is new debt, not the old violation"


def test_a_name_the_diff_never_touches_is_judged_only_through_a_changed_walk():
    """A ledger change at an address on an untouched name's walk re-judges it."""
    lists = {"y": [0xA0, 0xB1]}
    stub = StubScanner({0xB1})
    quiet = StubDelta(set(), {}, changed={0xC0})
    assert P.new_candidate_debt(quiet, stub, stub, lists)[1] == 0
    moved = StubDelta(set(), {}, changed={0xB1})
    base = StubScanner(set())       # consistent before the row at 0xB1 changed
    assert [v["symbol"] for v in P.new_candidate_debt(moved, base, stub, lists)[0]] == ["y"]


# -- the derived base side ---------------------------------------------------

def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                          text=True).stdout


def test_diff_rows_reads_every_side_and_folds_comma_overflow(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "targets/game/reverse").mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "t")
    sym = repo / P.SYMBOLS_REL
    sym.write_bytes(b"name,address,notes\r\n?a@@YAXXZ,0x00001000,one\r\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    sym.write_bytes(b"name,address,notes\r\n?a@@YAXXZ,0x00001000,one\r\n"
                    b"?b@@YAXXZ,0x00002000,two, with a comma\r\n")
    monkeypatch.setattr(P, "ROOT", repo)
    removed, added = P.diff_rows("HEAD", None, P.SYMBOLS_REL, P.PIN_FIELDS)
    assert removed == [] and added == [P._norm({"name": "?b@@YAXXZ", "address": "0x00002000",
                                                "notes": "two", None: [" with a comma"]},
                                               P.PIN_FIELDS)]
    assert added[0]["notes"] == "two" and P.joined(added[0]) == "two, with a comma"
    assert P.diff_rows("HEAD", ":", P.SYMBOLS_REL, P.PIN_FIELDS) == ([], [])
    _git(repo, "add", "-A")
    assert P.diff_rows("HEAD", ":", P.SYMBOLS_REL, P.PIN_FIELDS)[1] == added
    _git(repo, "commit", "-qm", "new")
    assert P.diff_rows("HEAD~1", "HEAD", P.SYMBOLS_REL, P.PIN_FIELDS)[1] == added
    assert P.diff_rows("HEAD", "HEAD~1", P.SYMBOLS_REL, P.PIN_FIELDS)[0] == added
    sym.write_bytes(sym.read_bytes() + b'?c@@YAXXZ,0x00003000,"two\r\nlines"\r\n')
    with pytest.raises(SystemExit, match="spans lines"):
        P.diff_rows("HEAD", None, P.SYMBOLS_REL, P.PIN_FIELDS)


# 6e667721a8 changes four functions.csv addresses and adds pins.
DERIVED_COMMIT = "6e667721a8"


def test_the_derived_base_side_equals_a_full_parse(scanner):
    have = subprocess.run(["git", "cat-file", "-e", f"{DERIVED_COMMIT}^{{commit}}"],
                          cwd=P.ROOT, capture_output=True)
    if have.returncode:
        pytest.skip(f"{DERIVED_COMMIT} is not in this clone")
    work = P.Delta(f"{DERIVED_COMMIT}^", DERIVED_COMMIT)
    try:
        new_scanner = P.Scanner(work.new_rows)
        derived = work.base_scanner(new_scanner)
        text = P._read_side(f"{DERIVED_COMMIT}^", P.FUNCTIONS_REL)
        full_rows = list(csv.DictReader(io.StringIO(text, newline="")))
        full = P.Scanner(full_rows)
        for table in ("ledger_sizes", "ledger_matched", "identities"):
            left = {k: v for k, v in getattr(full, table).items() if v}
            right = {k: v for k, v in getattr(derived, table).items() if v}
            assert left == right, table
        base_symbols = Path(work._tmp.name) / "base.csv"
        base_symbols.write_text(P._read_side(f"{DERIVED_COMMIT}^", P.SYMBOLS_REL),
                                encoding="utf-8", newline="")
        lists = P.candidate_lists(full_rows, base_symbols)
        touched = work.touched_names()
        assert touched and work.base_candidates(touched) == \
            {n: set(lists.get(n, ())) for n in touched}
    finally:
        work.close()


# 2014d152ca: an ILT slot -> a 5-byte pair destructor -> the string release
# body 0x00887940, which a dozen destructors own. The pin names the 5-byte body.
PAIR_SLOT, PAIR_BODY, RELEASE = 0x00018633, 0x00134AF0, 0x00887940
PAIR_PLACEHOLDER = "??1?$pair@$$CBVAsciiString@@W4Rva001360E0Mapped@@@_STL@@QAE@XZ"


def test_a_tail_jump_target_is_another_function(tmp_path, rows, scanner, symbols_text):
    """The walk stops at the body the ILT slot serves; the release body's many
    owners say nothing about the pair destructor that tail-jumps into it. (That
    5-byte body itself carries a real-name pin, pair<AsciiString,ThingTemplate*>,
    which is what a second spelling there is refused against.)"""
    assert scanner.image.resolve(PAIR_SLOT)[1] == [PAIR_SLOT, PAIR_BODY, RELEASE]
    assert len(scanner.identities[RELEASE]) > 1
    work = fake_delta(tmp_path, rows, symbols_text, pins_added=[pin(PAIR_PLACEHOLDER, PAIR_SLOT)])
    found = P.new_identity_conflicts(work, scanner, work.base_scanner(scanner), ilt_oracle.oracle())
    assert [(k, a) for k, _n, a, _w in found] == [("pin-on-other-identity", PAIR_SLOT)]
    why = found[0][3]
    assert "ThingTemplate" in why and f"0x{RELEASE:08X}" not in why


def _evidence_repo(tmp_path, monkeypatch):
    repo = tmp_path / "ev"
    (repo / P.EVIDENCE_REL).mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "t")
    old = repo / P.EVIDENCE_REL / "a.md"
    old.write_text(f"pin-identity-override: {FAKE} 0x00891B80 caller=0x00C57408 already spent\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    monkeypatch.setattr(P, "ROOT", repo)
    return repo


def test_r1_1_overrides_are_read_from_the_index(tmp_path, monkeypatch):
    """Pre-commit judges the index (new_ref ':'); the old `git grep` put
    --cached after the pattern and died, so no staged override was ever read."""
    repo = _evidence_repo(tmp_path, monkeypatch)
    evidence = repo / P.EVIDENCE_REL / "a.md"
    evidence.write_text(evidence.read_text() + "# proof\r\n"
                        f"pin-identity-override: {FAKE} 0x00479040 caller=0x00C57408 "
                        "the funclet calls it by this name\r\n")
    assert P.added_overrides("HEAD", ":") == [], "unstaged: not in the index yet"
    assert [(n, a) for n, a, _r in P.added_overrides("HEAD", None)] == [(FAKE, 0x00479040)]
    _git(repo, "add", "-A")
    assert [(n, a) for n, a, _r in P.added_overrides("HEAD", ":")] == [(FAKE, 0x00479040)], \
        "only the line this diff adds; the committed one is spent"
    _git(repo, "commit", "-qm", "new")
    assert [(n, a) for n, a, _r in P.added_overrides("HEAD~1", "HEAD")] == [(FAKE, 0x00479040)]


def test_r1_7_an_added_override_needs_its_trailer(tmp_path, monkeypatch):
    import protected_paths
    repo = _evidence_repo(tmp_path, monkeypatch)
    monkeypatch.chdir(repo)
    (repo / P.EVIDENCE_REL / "b.md").write_text(
        f"pin-identity-override: {FAKE} 0x00479040 caller=0x00C57408 the funclet calls it\n")
    _git(repo, "add", "-A")
    message = tmp_path / "msg"
    message.write_text("subject\n\nbody\n")
    assert protected_paths.check_staged(str(message)) == 1
    message.write_text(f"subject\n\nIdentity-Override: {FAKE} 0x00479040\n")
    assert protected_paths.check_staged(str(message)) == 0
    _git(repo, "commit", "-qm", "no trailer")
    assert protected_paths.check_range("HEAD~1", "HEAD") == 1
    _git(repo, "commit", "-q", "--amend", "-m", f"t\n\nIdentity-Override: {FAKE} 0x479040")
    assert protected_paths.check_range("HEAD~1", "HEAD") == 0


def test_b_the_default_alias_log_is_the_main_checkouts(monkeypatch):
    monkeypatch.delenv("BFME_PIN_ALIAS_LOG", raising=False)
    common = Path(P._git_text("rev-parse", "--path-format=absolute", "--git-common-dir").strip())
    assert P.alias_log_path() == common.parent / "build/linkfleet/ds/pin_alias_cleanup.tsv"
    monkeypatch.setenv("BFME_PIN_ALIAS_LOG", "/tmp/elsewhere.tsv")
    assert P.alias_log_path() == Path("/tmp/elsewhere.tsv")


def test_r2_5_a_merge_does_not_redeclare_a_parents_override(tmp_path, monkeypatch):
    import protected_paths
    repo = _evidence_repo(tmp_path, monkeypatch)
    monkeypatch.chdir(repo)
    base = _git(repo, "rev-parse", "HEAD").strip()
    _git(repo, "checkout", "-q", "-b", "side")
    (repo / P.EVIDENCE_REL / "b.md").write_text(
        f"pin-identity-override: {FAKE} 0x00479040 caller=0x00C57408 the funclet calls it\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", f"side\n\nIdentity-Override: {FAKE} 0x00479040")
    _git(repo, "checkout", "-q", "-")
    (repo / "other.txt").write_text("x")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "main side")
    _git(repo, "merge", "-q", "--no-ff", "-m", "merge without trailers", "side")
    assert protected_paths.check_range(base, "HEAD") == 0


def test_r2_5_a_missing_override_trailer_has_its_own_message(tmp_path, monkeypatch, capsys):
    import protected_paths
    repo = _evidence_repo(tmp_path, monkeypatch)
    monkeypatch.chdir(repo)
    (repo / P.EVIDENCE_REL / "b.md").write_text(
        f"pin-identity-override: {FAKE} 0x00479040 caller=0x00C57408 the funclet calls it\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "no trailer")
    assert protected_paths.check_range("HEAD~1", "HEAD") == 1
    err = capsys.readouterr().err
    assert "Identity-Override" in err and "Verifier-Change trailer" not in err


# Option (a), pending the project lead's approval (coordinator, 2026-10-16):
# alias-spelled ROWS are no identity either. The BattlePlan case: the real
# ctor row lands on 0x00285F10, whose only other names are the alias row
# ??RRva000287C7FactoryCtorThunk (ILT 0x000287C7) and alias pins.
BP_CTOR, BP_BODY = "??0BattlePlanUpdateModuleData@@QAE@XZ", 0x00285F10
BP_OLD = "??0BannerCarrierUpdate@@QAE@PAVThing@@PBVModuleData@@@Z"
AUTOHEAL = ("?construct@AutoHealBehaviorModuleData@@AAEXXZ", "?construct@AutoHealBehaviorModuleData@@QAEXXZ")


def _battleplan(rows, symbols_text, drop_autoheal_in_parent=True):
    old = next(P._norm(r, P.FUNCTION_FIELDS) for r in rows
               if int(r["target_rva"], 16) == BP_BODY and r["name"] == BP_OLD)
    new = dict(old, name=BP_CTOR,
               source="game/GameEngine/Source/GameLogic/Object/Update/BattlePlanUpdateModuleDataConstructor.cpp",
               notes="identity-correction=targets/game/reverse/identity_evidence/00285f10-battleplan-moduledata-ctor.md")
    pins = [P._norm(r, P.PIN_FIELDS) for r in csv.DictReader(io.StringIO(symbols_text))]
    autoheal = [p for p in pins if p["name"] in AUTOHEAL]
    assert len(autoheal) == 2
    text = "".join(l for l in symbols_text.splitlines(keepends=True)
                   if not l.startswith(AUTOHEAL))
    if drop_autoheal_in_parent:
        return text, dict(rows_removed=[old], rows_added=[new])
    return symbols_text, dict(rows_removed=[old], rows_added=[new], pins_removed=autoheal)


def test_a_a_real_name_may_land_where_only_aliases_stand(tmp_path, rows, symbols_text):
    """Commit 3 of the BattlePlan correction, with the wrong AutoHeal pins
    already gone in its parent: no conflict, the displaced aliases are listed."""
    text, diff = _battleplan(rows, symbols_text)
    warnings = []
    found = conflicts(tmp_path, rows, None, text, warnings, **diff)
    assert found == []
    shown = {(k, n) for k, n, *_rest in warnings}
    assert ("displaced-alias-row", "??RRva000287C7FactoryCtorThunk@@QAEXXZ") in shown
    assert ("displaced-alias-pin", "?construct@Rva000287C7FactoryCtorTarget@@QAEXXZ") in shown


def test_a_removing_a_real_pin_in_the_same_commit_does_not_clear_the_way(tmp_path, rows,
                                                                         symbols_text):
    """The AutoHeal pins are real names: deleting them in the SAME commit as
    the landing is still judged against base and new together (review r1 #4)."""
    text, diff = _battleplan(rows, symbols_text, drop_autoheal_in_parent=False)
    found = conflicts(tmp_path, rows, None, text, **diff)
    assert found == [("row-on-other-identity", BP_CTOR, BP_BODY)]


def test_a_a_real_second_spelling_is_still_refused(tmp_path, rows, scanner, symbols_text):
    """Real-named rows and pins still count: a second real row on EAStringC's
    body, and an alias row landing on a really named body, are refused."""
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     rows_added=[row(FAKE, EASTRING_BODY, 22)]) == \
        [("row-on-other-identity", FAKE, EASTRING_BODY)]
    alias = "?method@Rva00891B80Thing@@QAEXXZ"
    assert P.alias_spelling(alias)
    assert conflicts(tmp_path, rows, scanner, symbols_text,
                     rows_added=[row(alias, EASTRING_BODY, 22)]) == \
        [("row-on-other-identity", alias, EASTRING_BODY)]


# Option (a) review round 1: a real name displaces alias-only identities only
# with evidence (ILT CONFIRMED, or a verified override); alias-on-alias passes.
UNT_BODY = 0x0005F2B0                      # no ILT slot: the oracle cannot judge here
UNT_ALIAS = "?Rva0005F2B0InitializeAppWindows@@YA_NPAXH_N@Z"
GUESS = "?InitializeAppWindowsGuess@@YA_NPAXH_N@Z"


def test_a_r1_a_guessed_real_pin_on_an_untestable_alias_body_is_refused(tmp_path, rows, scanner,
                                                                       symbols_text):
    assert ilt_oracle.check(GUESS, UNT_BODY)[0] == ilt_oracle.UNTESTABLE
    warnings = []
    found = conflicts(tmp_path, rows, scanner, symbols_text, warnings,
                      pins_added=[pin(GUESS, UNT_BODY)])
    assert found == [("pin-on-other-identity", GUESS, UNT_BODY)]
    assert ("displaced-alias-row", UNT_ALIAS) in {(k, n) for k, n, *_ in warnings}


def test_a_r1_a_second_real_row_beside_an_alias_row_lists_it_and_is_refused(tmp_path, rows,
                                                                            symbols_text):
    """The alias row at the SAME address is displaced too (it was skipped)."""
    size = next(int(r["target_size"]) for r in rows
                if int(r["target_rva"], 16) == UNT_BODY and r["name"] == UNT_ALIAS)
    warnings = []
    found = conflicts(tmp_path, rows, None, symbols_text, warnings,
                      rows_added=[row(GUESS, UNT_BODY, size)])
    assert found == [("row-on-other-identity", GUESS, UNT_BODY)]
    assert ("displaced-alias-row", UNT_ALIAS) in {(k, n) for k, n, *_ in warnings}


def test_a_r1_alias_on_alias_passes(tmp_path, rows, scanner, symbols_text):
    assert conflicts(tmp_path, rows, scanner, symbols_text, [],
                     pins_added=[pin("?other@Rva0005F2B0X@@QAEXXZ", UNT_BODY)]) == []


# Option (a) review round 2.

def _unt_alias_row(rows):
    return next(P._norm(r, P.FUNCTION_FIELDS) for r in rows
                if int(r["target_rva"], 16) == UNT_BODY and r["name"] == UNT_ALIAS)


def test_a_r2_1_deleting_the_alias_row_in_the_same_commit_does_not_clear_the_way(
        tmp_path, rows, symbols_text):
    alias = _unt_alias_row(rows)
    found = conflicts(tmp_path, rows, None, symbols_text, [], rows_removed=[alias],
                      pins_added=[pin(GUESS, UNT_BODY)])
    assert found == [("pin-on-other-identity", GUESS, UNT_BODY)]


def test_a_r2_1_demoting_the_alias_row_in_the_same_commit_does_not_clear_the_way(
        tmp_path, rows, symbols_text):
    alias = _unt_alias_row(rows)
    found = conflicts(tmp_path, rows, None, symbols_text, [], rows_removed=[alias],
                      rows_added=[dict(alias, status="failed")],
                      pins_added=[pin(GUESS, UNT_BODY)])
    assert found == [("pin-on-other-identity", GUESS, UNT_BODY)]


def test_a_r2_2_alias_means_the_functions_own_class_or_method_token():
    real = ["?InitDecade123Windows@@YAXXZ",
            "??$InitializeAppWindows@URva0005F2B0@@@WinMainApp@@QAEXXZ",   # a member template's argument
            "??$clamp@M@?A0x3f2a1b2c@@YAMMMM@Z",                             # anonymous namespace
            "?calculate@PartitionManagerImpl@@QAEXPAUGen009F5040Node@@PAH11@Z"]
    alias = ["??1?$pair@$$CBVAsciiString@@W4Rva001360E0Mapped@@@_STL@@QAE@XZ",  # class argument
             "??1Rva8CD130String@@QAE@XZ", "??0ArrayValue008B9C60@@QAE@XZ",
             "?handle@Gen00134AF0@@QAEXXZ", "??1Gen_uw_000224d0@@QAE@XZ"]
    assert [n for n in real if P.alias_spelling(n)] == []
    assert [n for n in alias if not P.alias_spelling(n)] == []


def test_a_r2_3_a_wide_confirmed_window_does_not_displace(tmp_path, rows, symbols_text,
                                                         monkeypatch):
    """CONFIRMED at p_false >= CONFIRMED_P_MAX is not enough over an alias row."""
    class Wide:
        first_thunk, target = 0x401005, []

        def check(self, name, address):
            return ilt_oracle.CONFIRMED, 2e-3, "exact"
    work = fake_delta(tmp_path, rows, symbols_text, pins_added=[pin(GUESS, UNT_BODY)])
    scanner = P.Scanner(work.new_rows)
    real_oracle = ilt_oracle.oracle()
    wide = Wide()
    wide.first_thunk, wide.target = real_oracle.first_thunk, real_oracle.target
    found = P.new_identity_conflicts(work, scanner, work.base_scanner(scanner), wide)
    assert [(k, n) for k, n, *_ in found] == [("pin-on-other-identity", GUESS)]
    wide.check = lambda name, address: (ilt_oracle.CONFIRMED, 4e-4, "exact")
    assert P.new_identity_conflicts(work, scanner, work.base_scanner(scanner), wide) == []


def test_a_r2_4_the_drain_list_heals_its_shape(tmp_path, monkeypatch):
    log = tmp_path / "alias.tsv"
    monkeypatch.setenv("BFME_PIN_ALIAS_LOG", str(log))
    header = "\t".join(P.ALIAS_LOG_FIELDS)
    log.write_text(header + "\nold\t0x00000001\t0x00000001\tc0ffee\twhy five\n"
                   "late\t0x00000002\t0x00000002\tc0ffee\tno final newline", encoding="utf-8")
    P.record_alias_cleanup([("displaced-alias-row", "new", 3, "w", 3, "abc")])
    lines = log.read_text().splitlines()
    assert log.read_text().endswith("\n")
    assert lines[1].split("\t")[3] == "unknown" and lines[2].split("\t")[3] == "unknown"
    assert lines[3].split("\t")[:5] == ["new", "0x00000003", "0x00000003", "displaced-alias-row", "abc"]
    assert all(len(line.split("\t")) == 6 for line in lines)


def test_a_r2_5_pending_rows_reach_the_list_only_when_published(tmp_path, monkeypatch):
    log = tmp_path / "alias.tsv"
    monkeypatch.setenv("BFME_PIN_ALIAS_LOG", str(log))
    monkeypatch.setattr(P, "_git_text", lambda *a, **k: "deadbeef00\n")
    warning = ("displaced-alias-row", "?a@Rva00001000X@@QAEXXZ", 0x1000, "w", 0x1000, "?real@X@@QAEXXZ")
    staged = P.stage_alias_cleanup([warning], "base", "tip")
    assert staged.exists() and not log.exists(), "a verdict alone lists nothing"
    monkeypatch.setattr(P, "introducing_commit", lambda base, tip, trigger: "c0ffee1234")
    assert P.publish_alias_cleanup("tip") == 1
    assert not staged.exists()
    assert log.read_text().splitlines()[1].split("\t")[4] == "c0ffee1234"


# Option (a) review round 3: the address-shaped run and address-derived tails.

def test_a_r3_an_address_followed_by_a_hex_letter_or_after_a_type_code_is_an_alias():
    for name in ("??0?$vector@UGen00261FC0Elem@@V?$allocator@UGen00261FC0Elem@@@_STL@@@_STL@@QAE@XZ",
                 "?x@ShroudManagerImpl008FBA40Element@@QAEXXZ",
                 "?x@Gen_005878D0FirstValue@@QAEXXZ",
                 "?scriptPlayers002EE2D0Call11@@YGXH@Z"):
        assert P.alias_spelling(name), name


def test_a_r3_an_address_derived_tail_is_an_alias_only_at_a_known_start():
    for name in ("?Open2Rec3A4420@@YAXXZ", "?query1A6320@TerrainLogic@@QAEXXZ",
                 "?ParsePath8C4DA0@@YAXXZ", "?Completion215930@@YAXXZ",
                 "??0Rva4048AString@@QAE@XZ", "?get@RvaA2160Offset8Getter@@QAEXXZ"):
        assert P.alias_spelling(name), name
    # a hex-ish tail that is no known start stays a real name ...
    assert not P.alias_spelling("?InitDecade123Windows@@YAXXZ")
    assert not P.alias_spelling("?Decade@X@@QAEXXZ")
    # ... unless it spells the row's own address
    assert P.alias_spelling("?Decade@X@@QAEXXZ", 0xDECADE)


# Option (a) review round 4.

def test_a_r4_a_vendored_or_d3d_format_name_stays_real(rows):
    codec = "??0CCodec_A32B32G32R32F@D3DXTex@@QAE@PAUD3DX_BLT@@@Z"
    try:
        P.set_alias_context([dict(r, notes="") for r in rows])      # format rule alone
        assert not P.alias_spelling(codec, 0x00A37705)
        assert not P.alias_spelling("?f@X8R8G8B8Thing@@QAEXXZ")
        P.set_alias_context([{"name": codec, "target_rva": "0x00A37705", "notes": "vendored=dx9"},
                             {"name": "x", "target_rva": "0x00032B32", "notes": ""}])
        assert not P.alias_spelling(codec, 0x00A37705), "a vendored name is never read as a tail"
        assert P.alias_spelling("?x@Open2Rec32B32@@QAEXXZ"), "the same tail elsewhere is an alias"
    finally:
        P.set_alias_context(rows)


def test_a_r4_known_starts_follow_the_judged_rows(rows):
    try:
        P.set_alias_context([{"name": "x", "target_rva": "0x00ABC12E", "notes": ""}])
        assert 0x00ABC12E in P.known_starts()
        assert P.alias_spelling("?Open2RecABC12E@@YAXXZ")
        P.set_alias_context([])
        assert 0x00ABC12E not in P.known_starts()
    finally:
        P.set_alias_context(rows)
