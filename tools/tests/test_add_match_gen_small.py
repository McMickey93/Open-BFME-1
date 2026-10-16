"""add_match may repoint a game/gen_small/ claim to real C++, narrowly.

Approved by the project lead 2026-10-15: a gen-dtor placeholder
(game/gen_small/dtors_NNN.cpp / dtorsv_NNN.cpp) is retired by --replace-rva like a
gen-dump dump, and a hand-written claim in a game/gen_small/ U3*/W3* TU by
--replace-rva --correct-identity with token-exact identity evidence. The frozen
gen_small file is never edited: its remaining rows and every matched caller of the
retired name are re-verified in the same build, and the tool refuses when that
file also defines the new name.
"""
import csv
import io
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import add_match

HEADER = "name,export_rva,target_rva,target_size,source,status,notes"
RVA = "0x00707E60"
DTOR_OLD = "??_EGen_dtorv_00707e60@@UAEPAXI@Z"
DTOR_TU = "game/gen_small/dtorsv_000.cpp"
DTOR_ROW = f"{DTOR_OLD},,{RVA},84,{DTOR_TU},matched,gen-dtor;ghidra=gap"
SIBLING_ROW = (f"??_EGen_dtorv_00707f00@@UAEPAXI@Z,,0x00707F00,84,{DTOR_TU},matched,"
               "gen-dtor;ghidra=gap")
REAL = "??_ERoadType@@QAEPAXI@Z"
SOURCE_REL = "game/GameEngineDevice/Source/W3DDevice/GameClient/W3DRoadBuffer.cpp"

# The destructors the placeholders call: RoadType's behind its matched ILT row (as in
# retail: ??1Gen_dtorv_00707e60 is pinned at ILT 0x0001DE49 -> 0x007070C0), Thing's
# directly at its pinned address.
SUPPORT = [
    "?j_0001de49@@YAXXZ,,0x0001DE49,5,game/gen_small/gthunks_032.cpp,matched,"
    "gen-thunk;gap;target=0x007070C0",
    "??1RoadType@@QAE@XZ,,0x007070C0,131,game/GameEngine/RoadTypeDestructor.cpp,matched,real",
    "??1Thing@@UAE@XZ,,0x00709000,20,game/GameEngine/Thing.cpp,matched,real",
]
PINS = [
    "??1Gen_dtorv_00707e60@@UAE@XZ,0x0001DE49,gen-dtor class destructor",
    "??1Gen_dtor_0070a000@@UAE@XZ,0x00709000,gen-dtor class destructor",
    "??1Gen_dtorv_0070a000@@UAE@XZ,0x00709000,gen-dtor class destructor",
]

HAND_OLD = "?init@Rva0005DA80WideToAnsi@@QAEXPBGI@Z"
HAND_TU = "game/gen_small/W3AtlStringConversion.cpp"
HAND_RVA = "0x0005DA80"
HAND_ROW = (f"{HAND_OLD},,{HAND_RVA},107,{HAND_TU},matched,"
            "Open-BFME1 wide-to-ANSI conversion holder init; address-derived name")
HAND_NEW = "?Init@?$CW2AEX@$0IA@@ATL@@AAEXPBGI@Z"
PROOF = "targets/game/reverse/identity_evidence/0005da80-atl.md"
GOOD_PROOF = f"`{HAND_RVA}` ledgered as `{HAND_OLD}` is `{HAND_NEW}`.\n"


class Recorder:
    """subprocess.run double: records each build command, answers GATE."""

    def __init__(self, gate):
        self.gate = gate
        self.builds = []

    def __call__(self, command, **kwargs):
        if command and command[0] == "git":
            return SimpleNamespace(returncode=1, stdout=b"", stderr=b"")
        assert set(kwargs) == {"cwd", "env"}, kwargs
        self.builds.append(list(command))
        return SimpleNamespace(returncode=self.gate)


def arrange(tmp_path, monkeypatch, *, rows, name=REAL, rva=RVA, size="84",
            source=SOURCE_REL, replace_rva=RVA, extra=(), gate=0,
            callers=(), shadow=False, proof=None, definers=(), support=True,
            pins=PINS):
    reverse = tmp_path / "targets/game/reverse"
    reverse.mkdir(parents=True)
    src = tmp_path / source
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_bytes(b"void body() {}\r\n")
    functions = reverse / "functions.csv"
    rows = list(rows) + (SUPPORT if support else [])
    functions.write_bytes((HEADER + "\r\n" + "".join(r + "\r\n" for r in rows)).encode())
    (reverse / "symbols.csv").write_text("name,address,notes\n" + "".join(p + "\n" for p in pins))
    deleted = reverse / "deleted_rows.csv"
    deleted.write_bytes(b"name,target_rva,reason\n")
    if proof is not None:
        path = tmp_path / PROOF
        path.parent.mkdir(parents=True)
        path.write_text(proof)
    build_sh = tmp_path / "build.sh"
    build_sh.write_text("#!/bin/sh\nexit 0\n")
    build_sh.chmod(0o755)
    recorder = Recorder(gate)
    monkeypatch.setattr(add_match.subprocess, "run", recorder)
    seen = SimpleNamespace(callers=[], shadow=[], definers=[])

    def fake_callers(root, replaced):
        seen.callers.append((replaced["name"], replaced["rva"]))
        return list(callers)

    def fake_defines(root, source_rel, symbol):
        seen.shadow.append((source_rel, symbol))
        return shadow

    def fake_definers(root, symbol):
        seen.definers.append(symbol)
        return list(definers)

    monkeypatch.setattr(add_match, "gen_small_definers", fake_definers)
    monkeypatch.setattr(add_match, "orphaned_caller_selectors", fake_callers)
    monkeypatch.setattr(add_match, "frozen_tu_defines", fake_defines)
    monkeypatch.setattr(sys, "argv", [
        "add_match.py", name, rva, size, source, "--root", str(tmp_path),
        *(("--replace-rva", replace_rva) if replace_rva else ()), *extra])
    files = (functions, deleted, src)
    return files, recorder, seen


def snapshot(files):
    return tuple(path.read_bytes() for path in files)


def refused(files):
    before = snapshot(files)
    with pytest.raises(SystemExit):
        add_match.main()
    assert snapshot(files) == before


# --- allowed -------------------------------------------------------------------------

def test_gen_dtor_repoint_lands_and_reverifies_frozen_tu_and_callers(tmp_path, monkeypatch):
    callers = ["row:0x00012345:20:?caller@@YAXXZ"]
    files, recorder, seen = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW],
                                    callers=callers)
    add_match.main()
    ledger = files[0].read_text()
    assert DTOR_OLD not in ledger
    assert f"{REAL},,{RVA},84,{SOURCE_REL},matched," in ledger
    assert ledger.count(RVA) == 1
    (command,) = recorder.builds
    assert command[1:] == [SOURCE_REL, *callers, DTOR_TU]
    assert seen.callers == [(DTOR_OLD, 0x00707E60)]
    assert seen.shadow == [(DTOR_TU, REAL)]
    assert seen.definers == [REAL]
    tombstone = list(csv.reader(io.StringIO(files[1].read_text())))[-1]
    assert tombstone[:2] == [DTOR_OLD, RVA]
    assert "gen-dtor scaffold placeholder" in tombstone[2]
    assert "Prior notes: gen-dtor;ghidra=gap" in tombstone[2]


@pytest.mark.parametrize("tu,old,new", [
    ("game/gen_small/dtors_004.cpp", "??_GGen_dtor_0070a000@@UAEPAXI@Z", "??_GThing@@UAEPAXI@Z"),
    ("game/gen_small/dtorsv_000.cpp", "??_EGen_dtorv_0070a000@@UAEPAXI@Z",
     "??_EThing@@UAEPAXI@Z"),
])
def test_both_gen_dtor_families_are_admitted(tmp_path, monkeypatch, tu, old, new):
    row = f"{old},,0x0070A000,30,{tu},matched,gen-dtor"
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[row], rva="0x0070A000",
                                 size="30", replace_rva="0x0070A000", name=new)
    add_match.main()
    assert old not in files[0].read_text()
    # last row of its TU: nothing left there to re-verify or to shadow the new body
    assert recorder.builds[0][1:] == [SOURCE_REL]


def test_hand_written_gen_small_identity_correction_lands(tmp_path, monkeypatch):
    sibling = (f"?Rva0005B7A0GetConversionCodePage@@YGIXZ,,0x0005B7A0,90,{HAND_TU},"
               "matched,address-derived name")
    files, recorder, seen = arrange(
        tmp_path, monkeypatch, rows=[HAND_ROW, sibling], name=HAND_NEW, rva=HAND_RVA,
        size="107", replace_rva=HAND_RVA,
        source="game/GameEngine/Source/Common/T3AtlCImageCreateFromGdiplusBitmap.cpp",
        extra=("--correct-identity", HAND_OLD, "--identity-evidence", PROOF),
        proof=GOOD_PROOF)
    add_match.main()
    ledger = files[0].read_text()
    assert HAND_OLD + "," not in ledger
    assert "identity-correction=" + PROOF in ledger
    assert recorder.builds[0][-1] == HAND_TU
    assert seen.shadow == [(HAND_TU, HAND_NEW)]
    tombstone = list(csv.reader(io.StringIO(files[1].read_text())))[-1]
    assert tombstone[0] == HAND_OLD
    assert "Identity evidence: " + PROOF in tombstone[2]
    assert "Prior notes: Open-BFME1 wide-to-ANSI" in tombstone[2]


# --- refused -------------------------------------------------------------------------

@pytest.mark.parametrize("row", [
    # generator output that is not a gen-dtor placeholder
    # (gen-thunk/gen-dump/gen-tgrid/gen-shim rows were replaceable before this change)
    f"?e_00707e60@@YAXXZ,,{RVA},84,game/gen_small/thunks_008.cpp,matched,gen-ehstub",
    f"?i_00707e60@@YAXXZ,,{RVA},84,game/gen_small/imports_000.cpp,matched,gen-import",
    f"$L1234,,{RVA},84,game/gen_small/uw_gen_001.cpp,matched,gen-funclet;parent=0x00707000",
    f"?x@@YAXXZ,,{RVA},84,game/gen_small/named_000.cpp,matched,gen-alias;object-symbol=?y@@YAXXZ",
    # gen-dtor note outside the dtors files, or a dtors file without the note
    f"{DTOR_OLD},,{RVA},84,game/gen_small/fam_001.cpp,matched,gen-dtor",
    f"{DTOR_OLD},,{RVA},84,{DTOR_TU},matched,authored",
    f"{DTOR_OLD},,{RVA},84,{DTOR_TU},unmatched,gen-dtorish",
    # a real-source row is not a scaffold
    f"?real@@YAXXZ,,{RVA},84,game/GameEngine/Real.cpp,matched,authored",
    # a hand-written gen_small row is a named claim: it needs --correct-identity
    f"{HAND_OLD},,{RVA},84,{HAND_TU},matched,address-derived name",
])
def test_non_admitted_rows_refused_without_identity_correction(tmp_path, monkeypatch, row):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[row])
    refused(files)
    assert recorder.builds == []


def test_wrong_bytes_restore_everything(tmp_path, monkeypatch):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW], gate=1)
    refused(files)
    assert len(recorder.builds) == 1


def test_red_caller_or_frozen_tu_restores_everything(tmp_path, monkeypatch):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW], gate=2,
                                 callers=["row:0x00012345:20:?caller@@YAXXZ"])
    refused(files)
    assert "row:0x00012345:20:?caller@@YAXXZ" in recorder.builds[0]


def test_frozen_tu_defining_the_new_name_is_refused(tmp_path, monkeypatch):
    files, recorder, seen = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW],
                                    shadow=True)
    refused(files)
    assert seen.shadow == [(DTOR_TU, REAL)]


@pytest.mark.parametrize("rows,kwargs", [
    # two rows at the address
    ([DTOR_ROW, f"?other@@YAXXZ,,{RVA},84,game/GameEngine/Other.cpp,matched,authored"], {}),
    # the new name already claims another address
    ([DTOR_ROW, f"{REAL},,0x00700000,84,game/GameEngine/Other.cpp,matched,authored"], {}),
    # the new extent overlaps a matched neighbour
    ([DTOR_ROW, "?n@@YAXXZ,,0x00707E90,16,game/GameEngine/N.cpp,matched,authored"],
     {"size": "84"}),
])
def test_one_body_per_address(tmp_path, monkeypatch, rows, kwargs):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=rows, **kwargs)
    refused(files)
    assert recorder.builds == []


@pytest.mark.parametrize("source", [
    "game/gen_small/RoadType.cpp",
    "game/gen_asm/d_00707e60.asm",
    "game/masm_dumps/RoadType.asm",
    "inputs/reference/RoadType.cpp",
    "game/GameEngine/RoadType.h",
])
def test_successor_must_be_real_compiled_cpp(tmp_path, monkeypatch, source):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW], source=source)
    refused(files)
    assert recorder.builds == []


@pytest.mark.parametrize("extra,size", [
    (("--no-verify",), "84"),
    (("--boundary-evidence", "ret at +0x50"), "88"),
])
def test_no_unverified_or_reshaped_gen_small_repoint(tmp_path, monkeypatch, extra, size):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW], extra=extra, size=size)
    refused(files)
    assert recorder.builds == []


def test_gen_dtor_is_not_an_identity_correction(tmp_path, monkeypatch):
    files, _, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW],
                          extra=("--correct-identity", DTOR_OLD, "--identity-evidence", PROOF),
                          proof=f"{RVA} {DTOR_OLD} {REAL}\n")
    refused(files)


def hand(tmp_path, monkeypatch, *, proof, row=HAND_ROW, old=HAND_OLD):
    return arrange(tmp_path, monkeypatch, rows=[row], name=HAND_NEW, rva=HAND_RVA,
                   size="107", replace_rva=HAND_RVA,
                   extra=("--correct-identity", old, "--identity-evidence", PROOF),
                   proof=proof)


@pytest.mark.parametrize("text", [
    f"{HAND_OLD} is {HAND_NEW}.\n",                       # no RVA
    f"0x0005DA90 {HAND_OLD} is {HAND_NEW}.\n",            # wrong RVA
    f"{HAND_RVA} is {HAND_NEW}.\n",                       # no old name
    f"{HAND_RVA} is not {HAND_OLD}.\n",                   # no new name
    f"{HAND_RVA} {HAND_OLD} is x{HAND_NEW}.\n",           # new name only inside a token
])
def test_hand_written_correction_needs_token_exact_evidence(tmp_path, monkeypatch, text):
    files, recorder, _ = hand(tmp_path, monkeypatch, proof=text)
    refused(files)
    assert recorder.builds == []


def test_hand_written_correction_needs_the_exact_old_name(tmp_path, monkeypatch):
    files, _, _ = hand(tmp_path, monkeypatch, proof=GOOD_PROOF + "?wrong@@YAXXZ\n",
                       old="?wrong@@YAXXZ")
    refused(files)


@pytest.mark.parametrize("row", [
    # generator-numbered file names and generator/alias notes are not hand-written
    HAND_ROW.replace(HAND_TU, "game/gen_small/zhstl_001.cpp"),
    HAND_ROW.replace(HAND_TU, "game/gen_small/fam_001.cpp"),
    HAND_ROW.replace("Open-BFME1 wide-to-ANSI", "gen-shim;family=f1"),
    HAND_ROW.replace("Open-BFME1 wide-to-ANSI", "zh-landmulti;object-symbol=?y@@YAXXZ"),
    HAND_ROW.replace(",matched,", ",unmatched,"),
])
def test_only_hand_written_matched_gen_small_rows_are_correctable(tmp_path, monkeypatch, row):
    files, _, _ = hand(tmp_path, monkeypatch, proof=GOOD_PROOF, row=row)
    refused(files)


def test_live_state_helpers_refuse_a_test_root(tmp_path):
    row = {"name": DTOR_OLD, "rva": 0x00707E60}
    with pytest.raises(SystemExit):
        add_match.orphaned_caller_selectors(tmp_path, row)
    with pytest.raises(SystemExit):
        add_match.frozen_tu_defines(tmp_path, DTOR_TU, REAL)


# --- review round 1 regressions ---------------------------------------------------

@pytest.mark.parametrize("source", [
    "game/./gen_small/RoadType.cpp",                    # S1: '.' detour
    "game/GameEngine/../gen_small/RoadType.cpp",        # S1: '..' detour
    "game//gen_small/RoadType.cpp",                     # S1: empty component
    "game/Gen_Small/RoadType.cpp",                      # S1: case-insensitive host
    "game/GEN_ASM/RoadType.cpp",
])
def test_s1_successor_path_detours_refused(tmp_path, monkeypatch, source):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW],
                                 source=source)
    refused(files)
    assert recorder.builds == []


def test_s1_symlinked_successor_refused(tmp_path, monkeypatch):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW])
    real = tmp_path / "game/gen_small/RoadType.cpp"
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_text("void body() {}\n")
    link = tmp_path / "game/GameEngine/Link.cpp"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(real)
    sys.argv[sys.argv.index(SOURCE_REL)] = "game/GameEngine/Link.cpp"
    refused(files)
    assert recorder.builds == []


def test_s1_leading_dot_slash_still_accepted(tmp_path, monkeypatch):
    files, _, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW],
                          source=SOURCE_REL)
    sys.argv[sys.argv.index(SOURCE_REL)] = "./" + SOURCE_REL
    add_match.main()
    assert REAL in files[0].read_text()


@pytest.mark.parametrize("name", [
    "??_ERva00707E60Dtor@@QAEPAXI@Z",                   # S2: address-derived class
    "??_EGen_dtorv_00707e61@@UAEPAXI@Z",                # S2: generator class
    "??_Edup_00707e60@@QAEPAXI@Z",
    "??_ERoad0070Type7E60@@QAEPAXI@Z",
    "??_GRoadType@@QAEPAXI@Z",                          # S2: wrong kind for a ??_E slot
    "?d_00707e60@@YAXXZ",                               # S2: not a deleting destructor
    "?freeRoadBuffers@W3DRoadBuffer@@QAEXXZ",
])
def test_s2_gen_dtor_successor_must_be_a_real_class_deleting_dtor(tmp_path, monkeypatch, name):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW], name=name)
    refused(files)
    assert recorder.builds == []


@pytest.mark.parametrize("support,pins", [
    # S3: ??1RoadType only pinned, no matched row
    ([SUPPORT[0]], PINS + ["??1RoadType@@QAE@XZ,0x007070C0,pin only"]),
    # S3: the matched ??1RoadType sits elsewhere than the destructor the placeholder calls
    ([SUPPORT[0], SUPPORT[1].replace("0x007070C0", "0x00706000")], PINS),
    # S3: ??1RoadType unmatched
    ([SUPPORT[0], SUPPORT[1].replace(",matched,", ",unmatched,")], PINS),
    # S3: no pin says which destructor the placeholder calls
    (SUPPORT, PINS[1:]),
])
def test_s3_gen_dtor_needs_a_matched_destructor_row_at_the_called_address(
        tmp_path, monkeypatch, support, pins):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW, *support],
                                 support=False, pins=pins)
    refused(files)
    assert recorder.builds == []


def test_s3_direct_destructor_placement_is_accepted(tmp_path, monkeypatch):
    pins = ["??1Gen_dtorv_00707e60@@UAE@XZ,0x007070C0,gen-dtor class destructor"]
    files, _, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SUPPORT[1]], support=False,
                          pins=pins)
    add_match.main()
    assert REAL in files[0].read_text()


def test_s5_any_linked_gen_small_definer_refuses(tmp_path, monkeypatch):
    files, recorder, seen = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW],
                                    definers=["game_gen_small_uw_gen_000.obj"])
    refused(files)
    assert seen.definers == [REAL]
    assert len(recorder.builds) == 1                    # refused after the build, restored


def test_s5_last_row_still_checks_census_definers(tmp_path, monkeypatch):
    files, _, seen = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW],
                             definers=["game_gen_small_named_001.obj"])
    refused(files)
    assert seen.definers == [REAL] and seen.shadow == []


@pytest.mark.parametrize("old_source,new_source,ok", [
    (HAND_TU, SOURCE_REL, False),                       # S6: moves out of gen_small
    ("game/gen_small/tgrid_001.cpp", SOURCE_REL, False),
    (HAND_TU, HAND_TU, True),                           # same file: nothing new is linked
    ("game/GameEngine/Old.cpp", SOURCE_REL, True),      # unrelated: unchanged behaviour
])
def test_s6_replace_existing_cannot_move_a_gen_small_claim(
        tmp_path, monkeypatch, old_source, new_source, ok):
    row = f"{REAL},,{RVA},84,{old_source},matched,address-derived name"
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[row], replace_rva=None,
                                 source=new_source, extra=("--replace-existing",))
    if ok:
        add_match.main()
        assert f"{REAL},,{RVA},84,{new_source},matched," in files[0].read_text()
    else:
        refused(files)
        assert recorder.builds == []


@pytest.mark.parametrize("notes", [
    "address-derived name;gen-shim",                    # S8: a gen- part anywhere
    "hand body;identity=generated",
    "hand body; gen-alias;x",
])
def test_s8_generated_marker_in_any_note_part_is_not_hand_written(tmp_path, monkeypatch, notes):
    row = HAND_ROW.replace("Open-BFME1 wide-to-ANSI conversion holder init; address-derived name",
                           notes)
    files, _, _ = hand(tmp_path, monkeypatch, proof=GOOD_PROOF, row=row)
    refused(files)


# --- review round 2 regressions ---------------------------------------------------

@pytest.mark.parametrize("name", [
    "??_EGen_dtorv_0005da80@@UAEPAXI@Z",                # R2-1: generator class
    "?init@Gen_0005da80@@QAEXPBGI@Z",
    "?dup_0005da80@@YAXXZ",
    "?d_0005da80@@YAXXZ",
    "?j_0005da80@@YAXXZ",
])
def test_r2_1_hand_written_successor_cannot_be_a_generator_spelling(
        tmp_path, monkeypatch, name):
    proof = f"`{HAND_RVA}` ledgered as `{HAND_OLD}` is `{name}`.\n"
    files, recorder, _ = hand(tmp_path, monkeypatch, proof=proof)
    sys.argv[1] = name
    refused(files)
    assert recorder.builds == []


def test_r2_1_address_derived_rva_successor_still_allowed(tmp_path, monkeypatch):
    name = "?convert@Rva0005DA80WideToAnsi@@QAEXPBGI@Z"
    files, _, _ = hand(tmp_path, monkeypatch, proof=f"{HAND_RVA} {HAND_OLD} {name}\n")
    sys.argv[1] = name
    add_match.main()
    assert name in files[0].read_text()


def test_r2_2_second_placeholder_pin_refused(tmp_path, monkeypatch):
    # ??1Thing matched at a second pin of the RoadType placeholder must not land ??_EThing.
    pins = PINS + ["??1Gen_dtorv_00707e60@@UAE@XZ,0x00709000,second pin"]
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW],
                                 name="??_EThing@@UAEPAXI@Z", pins=pins)
    refused(files)
    assert recorder.builds == []
    # and the real class is refused too while the pin is ambiguous
    files, recorder, _ = arrange(tmp_path / "b", monkeypatch, rows=[DTOR_ROW, SIBLING_ROW],
                                 pins=pins)
    refused(files)


@pytest.mark.parametrize("row", [
    # R2-3: a non-thunk matched row at the pin address carrying target=
    "?notThunk@@YAXXZ,,0x0001DE49,5,game/GameEngine/X.cpp,matched,authored;target=0x007070C0",
    "?j_0001de49@@YAXXZ,,0x0001DE49,9,game/gen_small/gthunks_032.cpp,matched,"
    "gen-thunk;gap;target=0x007070C0",
])
def test_r2_3_only_an_ilt_thunk_row_routes_to_the_destructor(tmp_path, monkeypatch, row):
    files, recorder, _ = arrange(tmp_path, monkeypatch,
                                 rows=[DTOR_ROW, SIBLING_ROW, row, SUPPORT[1]], support=False)
    refused(files)
    assert recorder.builds == []


def test_r2_3_named_ilt_row_without_gen_note_is_accepted(tmp_path, monkeypatch):
    row = "?j_0001de49@@YAXXZ,,0x0001DE49,5,game/GameEngine/Ilt.cpp,matched,target=0x007070C0"
    files, _, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW, row, SUPPORT[1]],
                          support=False)
    add_match.main()
    assert REAL in files[0].read_text()


def git(cwd, *args):
    import subprocess
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "game/gen_small").mkdir(parents=True)
    (tmp_path / "game/gen_small/dtorsv_000.cpp").write_text("struct A {};\n")
    (tmp_path / "game/Other.cpp").write_text("int x;\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "census")
    return tmp_path, git(tmp_path, "rev-parse", "HEAD")


def test_r2_4_census_at_an_equal_gen_small_is_trusted(repo):
    root, commit = repo
    (root / "game/Other.cpp").write_text("int y;\n")          # outside gen_small: irrelevant
    git(root, "commit", "-qam", "later")
    assert add_match.census_gen_small_problem(root, {"meta": {"commit": commit}}) is None


@pytest.mark.parametrize("change", ["commit", "worktree"])
def test_r2_4_stale_census_refused(repo, change):
    root, commit = repo
    (root / "game/gen_small/dtorsv_000.cpp").write_text("struct Renamed {};\n")
    if change == "commit":
        git(root, "commit", "-qam", "EA rename")
    assert "changed since" in add_match.census_gen_small_problem(root, {"meta": {"commit": commit}})


@pytest.mark.parametrize("index", [{}, {"meta": {}}, {"meta": {"commit": ""}},
                                   {"meta": {"commit": "--quiet"}},
                                   {"meta": {"commit": "0123456789abcdef0123"}}])
def test_r2_4_missing_or_unknown_census_commit_refused(repo, index):
    root, _ = repo
    assert add_match.census_gen_small_problem(root, index)


def test_r2_5_absolute_successor_path_accepted(tmp_path, monkeypatch):
    files, _, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW])
    sys.argv[sys.argv.index(SOURCE_REL)] = str(tmp_path / SOURCE_REL)
    add_match.main()
    assert f"{REAL},,{RVA},84,{SOURCE_REL},matched," in files[0].read_text()


def test_r2_6_renamed_gen_dtor_placeholder_is_out_of_scope(tmp_path, monkeypatch, capsys):
    row = DTOR_ROW.replace(DTOR_OLD, "??_EAssetManagerImpl@@UAEPAXI@Z")
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[row, SIBLING_ROW])
    refused(files)
    assert "out of scope" in capsys.readouterr().err


# --- an emptied frozen TU is deleted with the repoint (source claims) -----------------

def frozen_tu(tmp_path, tu=DTOR_TU):
    path = tmp_path / tu
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"// frozen generated TU\r\n")
    return path


def test_last_row_repoint_deletes_the_emptied_tu(tmp_path, monkeypatch):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW])
    tu = frozen_tu(tmp_path)
    add_match.main()
    assert not tu.exists()
    assert f"{REAL},,{RVA},84,{SOURCE_REL},matched," in files[0].read_text()
    # nothing is left in the TU to re-verify
    assert recorder.builds[0][1:] == [SOURCE_REL]


def test_hand_written_last_row_deletes_its_tu(tmp_path, monkeypatch):
    files, recorder, _ = arrange(
        tmp_path, monkeypatch, rows=[HAND_ROW], name=HAND_NEW, rva=HAND_RVA,
        size="107", replace_rva=HAND_RVA,
        source="game/GameEngine/Source/Common/T3AtlCImageCreateFromGdiplusBitmap.cpp",
        extra=("--correct-identity", HAND_OLD, "--identity-evidence", PROOF),
        proof=GOOD_PROOF)
    tu = frozen_tu(tmp_path, HAND_TU)
    add_match.main()
    assert not tu.exists()


def test_tu_with_a_remaining_row_is_kept(tmp_path, monkeypatch):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, SIBLING_ROW])
    tu = frozen_tu(tmp_path)
    add_match.main()
    assert tu.exists()


def test_tu_owning_a_matched_data_row_is_kept(tmp_path, monkeypatch):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW])
    tu = frozen_tu(tmp_path)
    (tmp_path / "targets/game/reverse/data_rows.csv").write_text(
        "name,address,address_kind,size,section,source,status,evidence,model\n"
        f"?g@@3HA,0x01000000,va,4,.data,{DTOR_TU},matched,proof,m\n")
    add_match.main()
    assert tu.exists()


def test_unmatched_row_still_naming_the_tu_is_refused(tmp_path, monkeypatch):
    stale = f"?u@@YAXXZ,,0x00707F80,16,{DTOR_TU},unmatched,gen-dtor"
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW, stale])
    tu = frozen_tu(tmp_path)
    refused(files)
    assert tu.exists()
    assert recorder.builds == []


def test_failed_verification_keeps_the_tu(tmp_path, monkeypatch):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW], gate=1)
    tu = frozen_tu(tmp_path)
    refused(files)
    assert tu.exists()


def test_generated_copy_of_new_name_keeps_the_tu(tmp_path, monkeypatch):
    files, recorder, _ = arrange(tmp_path, monkeypatch, rows=[DTOR_ROW],
                                 definers=["game_gen_small_other.obj"])
    tu = frozen_tu(tmp_path)
    refused(files)
    assert tu.exists()
