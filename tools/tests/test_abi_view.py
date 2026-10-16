"""abi-view= pins: compilation views, never identities (tools/abi_view.py).

Approved by the project lead 2026-10-16. A view is admitted only when retail
calls its address, the address reaches a body whose matched row carries the
canonical name, and the ABI (convention, stack slots, return class, retail
cleanup) agrees."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import abi_view  # noqa: E402

TEXT = 0x1000


def pe(code):
    """A one-section PE: .text at RVA 0x1000 holding CODE ({rva: bytes})."""
    image = bytearray(0x2000)
    image[0:2] = b"MZ"
    image[0x3C:0x40] = (0x80).to_bytes(4, "little")
    image[0x80:0x84] = b"PE\0\0"
    image[0x86:0x88] = (1).to_bytes(2, "little")
    image[0x94:0x96] = (0xE0).to_bytes(2, "little")
    at = 0x80 + 24 + 0xE0
    image[at:at + 8] = b".text\0\0\0"
    for k, value in enumerate((0x1000, TEXT, 0x1000, 0x1000)):
        image[at + 8 + 4 * k:at + 12 + 4 * k] = value.to_bytes(4, "little")
    image[at + 36:at + 40] = (0x60000020).to_bytes(4, "little")
    for rva, data in code.items():
        image[rva:rva + len(data)] = data
    return bytes(image)


def call(site, target):
    return bytes([0xE8]) + struct.pack("<i", target - (site + 5))


def jmp(site, target):
    return bytes([0xE9]) + struct.pack("<i", target - (site + 5))


CODE = {
    # caller 0x1000..0x1020, NOP-filled so it decodes linearly
    0x1000: call(0x1000, 0x1100) + b"\x90" * 11,        # retail calls the ILT
    0x1010: call(0x1010, 0x1300) + b"\x90" * 3,         # and the cdecl body directly
    0x1018: bytes([0xB8]) + call(0x1019, 0x1400) + b"\x90" * 2,
    # ^ an E8 byte inside `mov eax, imm32` whose raw rel32 reaches 0x1400: not a call (N2)
    0x1100: jmp(0x1100, 0x1200),             # ILT -> thiscall body
    0x1200: bytes([0x8B, 0xC1, 0xC2, 0x08, 0x00]),   # mov eax, ecx; ret 8
    0x1300: bytes([0xC3]),                   # cdecl body
    0x1400: bytes([0xC2, 0x04, 0x00]),       # never called
}
REAL = "?real@Foo@@QAEPAHPAHH@Z"             # thiscall, (int*, int) -> int*: ret 8
VIEW = "?rva00001200@Bar@@QAEPAHPAHH@Z"     # an address-derived view of it
CALLER = "?caller@@YAXXZ"
CDECL = "?c@@YAXHH@Z"


def row(name, rva, size, source="game/a.cpp", status="matched", notes="x"):
    return {"name": name, "target_rva": f"0x{rva:08X}", "target_size": str(size),
            "source": source, "status": status, "notes": notes}


@pytest.fixture
def ctx():
    def make(rows=None, code=CODE, pins=None):
        rows = rows if rows is not None else [row(REAL, 0x1200, 5), row(CDECL, 0x1300, 1),
                                              row("?other@@QAEXH@Z", 0x1400, 3)]
        rows = rows + [row(CALLER, 0x1000, 0x20)]
        data = pe(code)
        import build
        return abi_view.Context(rows=rows, data=data, sections=build.pe_sections(data), pins=pins or {},
                                read_source=lambda source: "int plain_cpp_source;\n")
    return make


# --- decoding ---

@pytest.mark.parametrize("sym,forms", [
    ("?f@A@@QAEXHH@Z", [("E", "v", ("i", "i"))]),
    ("?f@A@@QAEXMN@Z", [("E", "v", ("f", "d"))]),
    ("?f@@YGHPAX@Z", [("G", "i", ("i",))]),
    ("?f@@YIHHHH@Z", [("I", "i", ("r", "r", "i"))]),
    ("??0Foo@@QAE@HI@Z", [("E", "v", ("i", "i"))]),
    ("?f@A@@QAE?AUPos@@H@Z", [("E", "i", ("i", "i")), ("E", "R", ("i",))]),
    ("_Rva003F4F70@16", [("G", "?", ("i",) * 4)]),
    ("?f@A@@QAEXPAUB@@0@Z", [("E", "v", ("i", "i"))]),          # back-reference
    ("??0?$vector@HV?$allocator@H@_STL@@@_STL@@QAE@ABV01@@Z", [("E", "v", ("i",))]),
])
def test_signature(sym, forms):
    assert abi_view.signature(sym) == forms


@pytest.mark.parametrize("sym", [
    "?f@A@@QAEXVAsciiString@@@Z",      # by-value aggregate parameter: size unknown
    "?f@@YAXHZZ",                      # varargs
    "notmangled",
])
def test_undecodable_signatures(sym):
    assert abi_view.signature(sym) is None


# --- admission ---

def test_view_through_the_ilt_accepted(ctx):
    assert abi_view.view_verdict(ctx(), VIEW, 0x1100, REAL) is None


def test_view_at_the_body_accepted(ctx):
    assert abi_view.view_verdict(ctx(), VIEW, 0x1200, REAL) is None


def test_same_function_respelt_accepted(ctx):
    # the canonical's own qualified name with other parameter spellings
    assert abi_view.view_verdict(ctx(), "?real@Foo@@QAEPAXPAXH@Z", 0x1100, REAL) is None


def test_hidden_return_equivalence_accepted(ctx):
    # (hidden Pos*, int) returning the pointer == (int*, int) -> int*
    assert abi_view.view_verdict(ctx(), "?rva00001200@Bar@@QAE?AUPos@@H@Z", 0x1100, REAL) is None


def test_cdecl_view_accepted(ctx):
    assert abi_view.view_verdict(ctx(), "?rva00001300@@YAXHPAX@Z", 0x1300, CDECL) is None
    assert abi_view.view_verdict(ctx(), "?c@@YAXPAXH@Z", 0x1300, CDECL) is None


@pytest.mark.parametrize("name,address,canonical,why", [
    ("?rva00001400@Bar@@QAEXH@Z", 0x1400, "?other@@QAEXH@Z", "no decoded retail `call` reaches"),  # N2
    (VIEW, 0x1100, "?wrong@@QAEXHH@Z", "which no matched row names"),
    (REAL, 0x1100, REAL, "names the pin itself"),
    (VIEW, 0x2100, REAL, "outside .text"),
    ("?rva00001200@Bar@@YAPAHPAHH@Z", 0x1100, REAL, "calling conventions differ"),
    ("?rva00001200@Bar@@QAEXH@Z", 0x1100, REAL, "no layout"),          # pops 4, retail 8
    ("?rva00001200@Bar@@QAEXMH@Z", 0x1100, REAL, "no layout"),         # float where int*
    ("?rva00001200@Bar@@QAENPAHH@Z", 0x1100, REAL, "no layout"),       # ST0 return vs EAX
    ("?rva00001200@Bar@@QAEXVAsciiString@@H@Z", 0x1100, REAL, "does not decode"),
    ("?c@@YAXHHH@Z", 0x1300, CDECL, "no layout"),                       # cdecl stack differs
    ("?c@@YA?AUPos@@H@Z", 0x1300, CDECL, "ambiguous"),                  # N3: cdecl aggregate on one side
    ("?v@Bar@@QAEPAHPAHH@Z", 0x1100, REAL, "name-correction candidate"),  # S1: a real-sounding name
])
def test_refusals(ctx, name, address, canonical, why):
    assert why in abi_view.view_verdict(ctx(), name, address, canonical)


def test_b1_view_may_not_be_a_ledger_name(ctx):
    # the name is matched elsewhere (any status, any address): it is that function's identity
    for status in ("matched", "partial"):
        rows = [row(REAL, 0x1200, 5), row(VIEW, 0x1300, 1, status=status)]
        assert "functions.csv row's name" in abi_view.view_verdict(ctx(rows), VIEW, 0x1100, REAL)
    # S3: the pinned address's own matched row
    rows = [row(REAL, 0x1200, 5), row(VIEW, 0x1200, 5)]
    assert "functions.csv row's name" in abi_view.view_verdict(ctx(rows), VIEW, 0x1100, REAL)


def test_b1_view_pinned_to_two_bodies_refused(ctx):
    pins = {VIEW: [0x1100, 0x1300]}
    assert "reach another body" in abi_view.view_verdict(ctx(pins=pins), VIEW, 0x1100, REAL)
    assert abi_view.view_verdict(ctx(pins={VIEW: [0x1100, 0x1200]}), VIEW, 0x1100, REAL) is None


def test_placeholder_canonical_needs_an_address_name_and_checks_cleanup_only(ctx):
    rows = [row("?dup_00001200@@YAXXZ", 0x1200, 5), row(CDECL, 0x1300, 1)]
    dup = "?dup_00001200@@YAXXZ"
    assert abi_view.view_verdict(ctx(rows), "?rva00001200@Bar@@QAEXHH@Z", 0x1100, dup) is None
    assert "retail pops 8" in abi_view.view_verdict(ctx(rows), "?rva00001200@Bar@@QAEXH@Z", 0x1100, dup)
    # S4: a real-sounding view over a placeholder is refused
    assert "name-correction candidate" in abi_view.view_verdict(ctx(rows), "?draw@Render2D@@QAEXHH@Z", 0x1100, dup)
    gen = [row("?d_00001300@@YAXXZ", 0x1300, 1, source="game/gen_asm/d.asm", notes="gen-dump")]
    assert "__cdecl view cannot be checked" in abi_view.view_verdict(
        ctx(gen), "?rva00001300@@YAXH@Z", 0x1300, "?d_00001300@@YAXXZ")


def test_n1_resolve_stops_at_a_named_tail_jump(ctx):
    # 0x1100 is an E9, but a matched row names it a function: it is not a stub
    rows = [row(REAL, 0x1200, 5), row("?tail@Foo@@QAEXXZ", 0x1100, 5)]
    assert ctx(rows).resolve(0x1100) == 0x1100
    assert ctx().resolve(0x1100) == 0x1200


def test_unmatched_canonical_row_refused(ctx):
    rows = [row(REAL, 0x1200, 5, status="partial")]
    assert "which no matched row names" in abi_view.view_verdict(ctx(rows), VIEW, 0x1100, REAL)


# --- round 2 ---

def test_n1_view_carrying_route_refused(ctx):
    assert "may not also carry route=" in abi_view.view_verdict(
        ctx(), VIEW, 0x1100, REAL, "abi-view=x;route=0x00001200")
    assert abi_view.view_verdict(ctx(), VIEW, 0x1100, REAL, "abi-view=x;why") is None


@pytest.mark.parametrize("name,admitted", [
    ("?rva00001200@Bar@@QAEPAHPAHH@Z", True),             # method is exactly rva<body>
    ("?Rva00001100@Bar@@QAEPAHPAHH@Z", True),             # ... or Rva<pinned address>
    ("?real@Rva00001200Bar@@QAEPAHPAHH@Z", True),         # Rva<addr><Word> class, canonical's method
    ("?real@Rva00001200@@QAEPAHPAHH@Z", True),
    ("?computeThreat1200@Bar@@QAEPAHPAHH@Z", False),      # guessed name + address
    ("?computeThreat00001200@Bar@@QAEPAHPAHH@Z", False),
    ("?computeThreat@Rva00001200Bar@@QAEPAHPAHH@Z", False),  # address class, invented method
    ("?rva00001200x@Bar@@QAEPAHPAHH@Z", False),
    ("?rva00009999@Bar@@QAEPAHPAHH@Z", False),            # another address
    ("?v@Bar@@QAEPAHPAURva00001200Arg@@H@Z", False),      # address only in a parameter type
])
def test_n2_address_derived_names(ctx, name, admitted):
    got = abi_view.view_verdict(ctx(), name, 0x1100, REAL)
    assert (got is None) is admitted, got


def test_n3_name_regression_parses_quoted_notes(monkeypatch):
    import name_regression
    text = ('name,address,notes\n'
            '?quoted@@YAXXZ,0x00001200,"abi-view=?real@@YAXXZ;why, comma"\n')
    # csv.reader sees the quoted notes field, so is_view recognises the view
    import csv
    import io
    rows = list(csv.reader(io.StringIO(text)))
    assert abi_view.is_view(",".join(rows[1][2:]))
    assert "csv.reader(io.StringIO(read(root, old, path)" in (ROOT / "tools/name_regression.py").read_text()


def test_n4_asm_and_unreadable_canonicals_are_placeholders(ctx):
    c = ctx()

    def unreadable(source):
        raise OSError(source)
    c.read_source = unreadable
    assert abi_view.placeholder_canonical(c, row("?real@Foo@@QAEXHH@Z", 0x1200, 5, source="game/masm_dumps/x.asm"))
    assert abi_view.placeholder_canonical(c, row("?real@Foo@@QAEXHH@Z", 0x1200, 5, source="game/no/such/file.cpp"))


def test_n5_slot_and_label_readers_skip_views():
    for path in ("tools/vtable_slots.py", "tools/dis_retail.py", "tools/family_scan.py"):
        assert "abi_view.is_view(" in (ROOT / path).read_text(encoding="utf-8")


# --- B2: one field test everywhere ---

@pytest.mark.parametrize("notes,view", [
    ("abi-view=?x@@YAXXZ;why", True),
    ("why;abi-view=?x@@YAXXZ", True),
    ("not an abi-view=, keep", False),
    ("x;notabi-view=?y", False),
])
def test_is_view_is_the_field_form(notes, view):
    assert abi_view.is_view(notes) is view


def test_ilt_oracle_reads_no_view_pin_and_every_other_pin(tmp_path):
    import ilt_oracle
    rev = tmp_path / "targets/game/reverse"
    rev.mkdir(parents=True)
    (rev / "functions.csv").write_text("name,export_rva,target_rva,target_size,source,status,notes\n"
                                       "?real@@YAXXZ,,0x00001000,4,game/a.cpp,matched,x\n")
    (rev / "symbols.csv").write_text("name,address,notes\n"
                                     "?view@@YAXXZ,0x00001000,abi-view=?real@@YAXXZ;why, with a comma\n"
                                     "?pin@@YAXXZ,0x00002000,plain pin\n"
                                     "?fake@@YAXXZ,0x00003000,not an abi-view=, keep\n")
    names = {name for _src, name, _rva, _row in ilt_oracle.ledger_rows(tmp_path)}
    assert names == {"?real@@YAXXZ", "?pin@@YAXXZ", "?fake@@YAXXZ"}


# --- S2: identity readers skip views ---

def test_name_regression_recorded_components_skip_views(monkeypatch):
    import name_regression
    symbols = ("name,address,notes\n"
               "?view@Rva00001200Bar@@QAEXXZ,0x00001200,abi-view=?real@@YAXXZ;x\n"
               "?pin@Foo@@QAEXXZ,0x00001300,plain\n")
    monkeypatch.setattr(name_regression, "read",
                        lambda root, ref, path: symbols if path == name_regression.SYMBOLS else "va,name\n")
    out = name_regression._recorded_components(None, "HEAD")
    assert "Foo" in out and "Rva00001200Bar" not in out


def test_brief_and_callers_of_filter_views():
    # both read symbols.csv rows and must skip abi-view= pins by the same field test
    for path in ("tools/brief.py", "tools/callers_of.py"):
        assert "abi_view.is_view(" in (ROOT / path).read_text(encoding="utf-8")


# --- the ledger: migration result, gate wiring, identity tools ---

REAL_EXE = ROOT / "inputs/baselines/bfme1/retail-1.03-unpacked/files/lotrbfme.exe"
needs_retail = pytest.mark.skipif(not REAL_EXE.exists(), reason="retail image not present")


@needs_retail
def test_efd7b316f7_position_view_is_a_name_correction_candidate():
    # ABI-equivalent (hidden-return), but `position` on an Rva<addr> class is not
    # the canonical's method (round-2 N2): listed for the lead, not admitted
    c = abi_view.Context()
    assert "name-correction candidate" in abi_view.view_verdict(
        c, "?position@Rva001C86B0Object@@QAE?AURva0075BE60Position@@PAUCoord3D@@@Z", 0x000421AE,
        "?bfmeGetPosition421AE@Object@@QAEPBUCoord3D@@PAU2@0@Z")
    assert abi_view.view_verdict(
        c, "?bfmeGetPosition421AE@Rva001C86B0Object@@QAE?AURva0075BE60Position@@PAUCoord3D@@@Z", 0x000421AE,
        "?bfmeGetPosition421AE@Object@@QAEPBUCoord3D@@PAU2@0@Z") is None
    # its sibling is refused twice over: an invented method name, and a by-value
    # Position the decoration cannot size
    assert "name-correction candidate" in abi_view.view_verdict(
        c, "?create@Rva004588D0DecalTemplate@@QAEXURva0075BE60Position@@IHAAVRadiusDecal@@M@Z", 0x0000D3E6,
        "?createRadiusDecal@RadiusDecalTemplate@@QAEXMMMIHAAVRadiusDecal@@M@Z")
    assert "does not decode" in abi_view.view_verdict(
        c, "?createRadiusDecal@Rva004588D0DecalTemplate@@QAEXURva0075BE60Position@@IHAAVRadiusDecal@@M@Z",
        0x0000D3E6, "?createRadiusDecal@RadiusDecalTemplate@@QAEXMMMIHAAVRadiusDecal@@M@Z")


@needs_retail
def test_every_ledger_view_validates():
    assert abi_view.check() == []


@needs_retail
def test_pin_consistency_fails_an_inadmissible_view(tmp_path, capsys):
    import pin_consistency
    good = ("?worldToCell@Pathfinder@@QAE_NPBVCoord3D@@PAUICoord2D@@@Z,0x003D7EC0,"
            "abi-view=?worldToCell@Pathfinder@@QAE_NPBUCoord3D@@PAUICoord2D@@@Z;x\n")
    path = tmp_path / "symbols.csv"
    path.write_text("name,address,notes\n" + good +
                    "?bad@View@@QAEXH@Z,0x003D7EC0,abi-view=?worldToCell@Pathfinder@@QAE_NPBUCoord3D@@PAUICoord2D@@@Z\n")
    with pytest.raises(SystemExit):
        pin_consistency.verify_views(path)
    assert "?bad@View@@QAEXH@Z" in capsys.readouterr().out
    path.write_text("name,address,notes\n" + good)
    assert pin_consistency.verify_views(path) == {
        ("?worldToCell@Pathfinder@@QAE_NPBVCoord3D@@PAUICoord2D@@@Z", 0x003D7EC0)}


@needs_retail
def test_real_reviewer_cases_refused():
    c = abi_view.Context()
    # B1 probe1: winSetEnabledColor (a real ledger name) as a view of winSetEnabledBorderColor
    assert "functions.csv row's name" in abi_view.view_verdict(
        c, "?winSetEnabledColor@GameWindow@@QAEHHH@Z", 0x00014867,
        "?winSetEnabledBorderColor@GameWindow@@QAEHHH@Z")
    # S3: the pin's own matched row
    assert "functions.csv row's name" in abi_view.view_verdict(
        c, "?getAdjustedVisionRangeForObject@Rva002BD020AI@@SAMPBVObject@@H@Z", 0x0002481B,
        "?getAdjustedVisionRangeForObject@AI@@SAMPBVObject@@H@Z")
    # S1: real-sounding names over unrelated canonicals
    assert "name-correction candidate" in abi_view.view_verdict(
        c, "?Draw_Sentence@Render2DSentenceHHHH@@QAEXIIII@Z", 0x0093EB50, "?d_0093eb50@@YAXXZ")


@needs_retail
def test_s5_naked_lift_canonical_is_no_proven_abi():
    c = abi_view.Context()
    row = next(r for r in c.at[0x006C3170] if r["name"] == "?drawEvents@W3DRadar@@IAEXHHHH@Z")
    assert abi_view.placeholder_canonical(c, row)


