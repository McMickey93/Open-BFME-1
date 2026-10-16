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


@pytest.fixture(scope="module")
def rows():
    return build.load_all_function_rows()


@pytest.fixture(scope="module")
def scanner(rows):
    return P.Scanner(rows)


@pytest.fixture(scope="module")
def symbols_text():
    return build.SYMBOLS.read_text(encoding="utf-8")


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
    if diff.get("rows_added") or diff.get("rows_removed"):
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
    found = conflicts(tmp_path, rows, scanner, symbols_text, rows_removed=[owner],
                      rows_added=[dict(owner, name="?method@Rva009F5370Vector@@QAEXXZ")])
    assert ("existing-pin-now-conflicts", COPY_NAME, COPY_BODY) in found
    # the renamed row is refused too: the left-behind real pin still names the body
    assert ("row-on-other-identity", "?method@Rva009F5370Vector@@QAEXXZ", COPY_BODY) in found


def test_r1_5_losing_abi_view_on_an_alias_pin_only_warns(tmp_path, rows, scanner,
                                                         symbols_text):
    """VIEW_NAME is an address-derived spelling: once it is no view it names
    another identity's body, which under option (b) warns and lists it for the
    pin drain instead of blocking."""
    view = next(r for r in (P._norm(x, P.PIN_FIELDS) for x in
                            csv.DictReader(io.StringIO(symbols_text)))
                if r["name"] == VIEW_NAME and int(r["address"], 16) == VIEW_PIN)
    assert P.pin_exemption(view) == "view" and P.alias_spelling(VIEW_NAME)
    plain = dict(view, notes="no longer a view", _overflow="")
    warnings = []
    found = conflicts(tmp_path, rows, scanner, symbols_text, warnings, pins_removed=[view],
                      pins_added=[plain])
    assert found == []
    assert [(k, n, a) for k, n, a, _w, _b in warnings] == \
        [("existing-pin-now-conflicts", VIEW_NAME, VIEW_PIN)]


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
    """376d78b9c1: the real row lands on 0x008AD8F0 and ?bfmeApply1236 stays."""
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
    assert [(n, a, b) for _k, n, a, _w, b in warnings] == [(alias, body, body)]
    log = tmp_path / "alias.tsv"
    monkeypatch.setenv("BFME_PIN_ALIAS_LOG", str(log))
    monkeypatch.setattr(P, "_git_text", lambda *a, **k: "376d78b9c1\n")
    P.record_alias_cleanup(warnings, "376d78b9c1")
    P.record_alias_cleanup(warnings, "376d78b9c1")
    lines = log.read_text().splitlines()
    assert lines[0].split("\t") == P.ALIAS_LOG_FIELDS
    assert len(lines) == 2, "one line per (name, address, body), however often it is seen"
    assert lines[1].split("\t")[:4] == [alias, "0x008AD8F0", "0x008AD8F0", "376d78b9c1"]


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


def test_r2_1_an_override_needs_the_callers_relocation(scanner):
    """Review round 2: a word in the caller's source (a comment) once passed.
    Only the caller's compiled object, naming the exact symbol at the call
    site, proves the override."""
    if not _binding_object_ready():
        pytest.skip("0x008AD8F0's object is not built in this checkout")
    why = "caller=0x008AD8F0 calls it under this name"
    assert P.verify_override(scanner, None, BINDING_NAME, BINDING_CALLEE, why) is None
    for other in (FAKE, "?refresh@Rva008AD750StringBinding@@QAEXPAVOther@@@Z",
                  "??0Rva008AD750StringBinding@@QAE@XZ"):
        assert "object names" in P.verify_override(scanner, None, other, BINDING_CALLEE, why)
    assert "no E8/E9" in P.verify_override(scanner, None, BINDING_NAME, BINDING_CALLEE + 1, why)


def test_r2_1_generated_noted_and_masm_callers_prove_nothing(scanner):
    funclet = "caller=0x00C57408 its unwind funclet destroys the string"     # gen-funclet note
    assert "hand-written C++" in P.verify_override(scanner, None, "??1Rva8CD130String@@QAE@XZ",
                                                   EASTRING_BODY, funclet)
    masm = next(r for r in build.load_all_function_rows()
                if r["status"] == "matched" and r["source"].startswith("game/masm_dumps/"))
    why = f"caller={masm['target_rva']} a hand-written dump"
    assert "hand-written C++" in P.verify_override(scanner, None, FAKE, EASTRING_BODY, why)
    assert "no caller" in P.verify_override(scanner, None, FAKE, EASTRING_BODY, "trust me, it is")


def test_r2_1_a_stale_object_proves_nothing(scanner, monkeypatch):
    import delta_sources
    monkeypatch.setattr(delta_sources, "object_is_current", lambda source, obj: False)
    why = "caller=0x008AD8F0 calls it under this name"
    assert "missing or stale" in P.verify_override(scanner, None, BINDING_NAME, BINDING_CALLEE, why)


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
    found = conflicts(tmp_path, rows, scanner, symbols_text, rows_removed=[owner],
                      rows_added=[moved], pins_added=[pin(FAKE, EASTRING_BODY)])
    assert ("pin-on-other-identity", FAKE, EASTRING_BODY) not in found


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
