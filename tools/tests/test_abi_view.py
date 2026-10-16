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
    0x1000: call(0x1000, 0x1100),            # retail calls the ILT
    0x1010: call(0x1010, 0x1300),            # and the cdecl body directly
    0x1100: jmp(0x1100, 0x1200),             # ILT -> thiscall body
    0x1200: bytes([0x8B, 0xC1, 0xC2, 0x08, 0x00]),   # mov eax, ecx; ret 8
    0x1300: bytes([0xC3]),                   # cdecl body
    0x1400: bytes([0xC2, 0x04, 0x00]),       # never called
}
REAL = "?real@Foo@@QAEPAHPAHH@Z"             # thiscall, (int*, int) -> int*: ret 8
CDECL = "?c@@YAXHH@Z"


def row(name, rva, size, source="game/a.cpp", status="matched", notes="x"):
    return {"name": name, "target_rva": f"0x{rva:08X}", "target_size": str(size),
            "source": source, "status": status, "notes": notes}


@pytest.fixture
def ctx():
    def make(rows=None, code=CODE):
        rows = rows if rows is not None else [row(REAL, 0x1200, 5), row(CDECL, 0x1300, 1),
                                              row("?other@@QAEXH@Z", 0x1400, 3)]
        data = pe(code)
        import build
        return abi_view.Context(rows=rows, data=data, sections=build.pe_sections(data))
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
    assert abi_view.view_verdict(ctx(), "?v@Bar@@QAEPAHPAHH@Z", 0x1100, REAL) is None


def test_view_at_the_body_accepted(ctx):
    assert abi_view.view_verdict(ctx(), "?v@Bar@@QAEPAHPAHH@Z", 0x1200, REAL) is None


def test_hidden_return_equivalence_accepted(ctx):
    # (hidden Pos*, int) returning the pointer == (int*, int) -> int*
    assert abi_view.view_verdict(ctx(), "?v@Bar@@QAE?AUPos@@H@Z", 0x1100, REAL) is None


def test_cdecl_view_accepted(ctx):
    assert abi_view.view_verdict(ctx(), "?v@@YAXHPAX@Z", 0x1300, CDECL) is None


@pytest.mark.parametrize("name,address,canonical,why", [
    ("?v@Bar@@QAEXH@Z", 0x1400, "?other@@QAEXH@Z", "no retail `call` reaches"),
    ("?v@Bar@@QAEPAHPAHH@Z", 0x1100, "?wrong@@QAEXHH@Z", "which no matched row names"),
    (REAL, 0x1100, REAL, "names the pin itself"),
    ("?v@Bar@@QAEPAHPAHH@Z", 0x2100, REAL, "outside .text"),
    ("?v@@YAPAHPAHH@Z", 0x1100, REAL, "calling conventions differ"),
    ("?v@Bar@@QAEXH@Z", 0x1100, REAL, "no layout"),                 # pops 4, retail 8
    ("?v@Bar@@QAEXMH@Z", 0x1100, REAL, "no layout"),                # float where int*
    ("?v@Bar@@QAENPAHH@Z", 0x1100, REAL, "no layout"),              # ST0 return vs EAX
    ("?v@Bar@@QAEXVAsciiString@@H@Z", 0x1100, REAL, "does not decode"),
    ("?v@@YAXHHH@Z", 0x1300, CDECL, "no layout"),                   # cdecl stack differs
])
def test_refusals(ctx, name, address, canonical, why):
    assert why in abi_view.view_verdict(ctx(), name, address, canonical)


def test_the_pin_already_naming_the_body_is_not_a_view(ctx):
    rows = [row(REAL, 0x1200, 5), row("?v@Bar@@QAEPAHPAHH@Z", 0x1200, 5)]
    assert "is itself a matched row" in abi_view.view_verdict(ctx(rows), "?v@Bar@@QAEPAHPAHH@Z", 0x1100, REAL)


def test_placeholder_canonical_checks_retail_cleanup_only(ctx):
    rows = [row("?dup_00001200@@YAXXZ", 0x1200, 5), row(CDECL, 0x1300, 1)]
    assert abi_view.view_verdict(ctx(rows), "?v@Bar@@QAEXHH@Z", 0x1100, "?dup_00001200@@YAXXZ") is None
    assert "retail pops 8" in abi_view.view_verdict(ctx(rows), "?v@Bar@@QAEXH@Z", 0x1100, "?dup_00001200@@YAXXZ")
    gen = [row("?d_00001300@@YAXXZ", 0x1300, 1, source="game/gen_asm/d.asm", notes="gen-dump")]
    assert "__cdecl view cannot be checked" in abi_view.view_verdict(ctx(gen), "?v@@YAXH@Z", 0x1300, "?d_00001300@@YAXXZ")


def test_unmatched_canonical_row_refused(ctx):
    rows = [row(REAL, 0x1200, 5, status="partial")]
    assert "which no matched row names" in abi_view.view_verdict(ctx(rows), "?v@Bar@@QAEPAHPAHH@Z", 0x1100, REAL)


# --- the ledger: migration result, gate wiring, identity tools ---

REAL_EXE = ROOT / "inputs/baselines/bfme1/retail-1.03-unpacked/files/lotrbfme.exe"
needs_retail = pytest.mark.skipif(not REAL_EXE.exists(), reason="retail image not present")


@needs_retail
def test_efd7b316f7_position_view_validates():
    import build
    c = abi_view.Context()
    assert abi_view.view_verdict(
        c, "?position@Rva001C86B0Object@@QAE?AURva0075BE60Position@@PAUCoord3D@@@Z", 0x000421AE,
        "?bfmeGetPosition421AE@Object@@QAEPBUCoord3D@@PAU2@0@Z") is None
    # its sibling passes a by-value Position: not machine-verifiable, so refused
    assert "does not decode" in abi_view.view_verdict(
        c, "?create@Rva004588D0DecalTemplate@@QAEXURva0075BE60Position@@IHAAVRadiusDecal@@M@Z", 0x0000D3E6,
        "?createRadiusDecal@RadiusDecalTemplate@@QAEXMMMIHAAVRadiusDecal@@M@Z")


@needs_retail
def test_every_ledger_view_validates():
    assert abi_view.check() == []


@needs_retail
def test_pin_consistency_fails_an_inadmissible_view(tmp_path, capsys):
    import pin_consistency
    path = tmp_path / "symbols.csv"
    path.write_text("name,address,notes\n"
                    "?position@Rva001C86B0Object@@QAE?AURva0075BE60Position@@PAUCoord3D@@@Z,0x000421AE,"
                    "abi-view=?bfmeGetPosition421AE@Object@@QAEPBUCoord3D@@PAU2@0@Z;x\n"
                    "?bad@View@@QAEXH@Z,0x000421AE,abi-view=?bfmeGetPosition421AE@Object@@QAEPBUCoord3D@@PAU2@0@Z\n")
    with pytest.raises(SystemExit):
        pin_consistency.verify_views(path)
    assert "?bad@View@@QAEXH@Z" in capsys.readouterr().out
    path.write_text("name,address,notes\n"
                    "?position@Rva001C86B0Object@@QAE?AURva0075BE60Position@@PAUCoord3D@@@Z,0x000421AE,"
                    "abi-view=?bfmeGetPosition421AE@Object@@QAEPBUCoord3D@@PAU2@0@Z;x\n")
    assert pin_consistency.verify_views(path) == {
        ("?position@Rva001C86B0Object@@QAE?AURva0075BE60Position@@PAUCoord3D@@@Z", 0x000421AE)}


def test_ilt_oracle_reads_no_view_pin(tmp_path):
    import ilt_oracle
    rev = tmp_path / "targets/game/reverse"
    rev.mkdir(parents=True)
    (rev / "functions.csv").write_text("name,export_rva,target_rva,target_size,source,status,notes\n"
                                       "?real@@YAXXZ,,0x00001000,4,game/a.cpp,matched,x\n")
    (rev / "symbols.csv").write_text("name,address,notes\n"
                                     "?view@@YAXXZ,0x00001000,abi-view=?real@@YAXXZ;why, with a comma\n"
                                     "?pin@@YAXXZ,0x00002000,plain pin\n")
    names = {name for _src, name, _rva, _row in ilt_oracle.ledger_rows(tmp_path)}
    assert names == {"?real@@YAXXZ", "?pin@@YAXXZ"}
