"""Independent review-2 counterexamples. No compiler, linker, Wine, or real cycle.

The PE reader and ledger-to-object path lookup use synthetic inputs. COFF
parsing, per-row measurement, shifted checks, closure, and credited byte counts
are production code. Every regression assertion describes the required refusal.
"""
import csv
import json
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import link_cycle as lc


F, A, B, EH, REH, ACTION = 0x60000, 0x61000, 0x62000, 0x65000, 0x66000, 0x67000
DATA, RDATA, TYPE, STUB = 0x80000, 0x81000, 0x84000, 0x90000


def dword(value):
    return struct.pack("<I", value & 0xFFFFFFFF)


class ImageCase:
    def __init__(self, tmp_path, monkeypatch):
        self.root, self.patch = tmp_path, monkeypatch
        # Provenance reads the same synthetic source tree as the fixture.
        monkeypatch.setattr(lc, "ROOT", tmp_path)
        self.I, self.R = bytearray(0xA0000), bytearray(0xA0000)
        self.shift_sites, self.paths, self.rows, self.source_objects, self.publics = set(), [], [], {}, {}
        self.sections = lc.SectionList([
            (".text", 0x60000, 0x10000), (".rdata", 0x80000, 0x10000), (".stubd", STUB, 0x1000)])
        self.pins = {}

    def retail_extent(self, name, address, size):
        """Independent synthetic retail truth, supplied before measuring COFF."""
        path = self.root / 'targets/game/reverse/data_rows.csv'
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text('name,address,address_kind,size,source,status\n')
        with path.open('a') as f:
            f.write(f'{name},{address:#x},rva,{size},game/data.cpp,matched\n')

    def put(self, at, data, *, retail=None):
        self.I[at:at + len(data)] = data
        if retail is not None:
            self.R[at:at + len(retail)] = retail

    def ptr(self, at, target):
        self.I[at:at + 4] = dword(lc.BASE + target)
        self.shift_sites.add(at)

    def object(self, basename, sections, symbols):
        """sections: (name, raw bytes, [(offset, target name, relocation type)])."""
        path = self.root / basename
        lc.write_coff(path, [(name, 0x60101020 if name.startswith(".text") else 0xC0300040,
                              body, 2 if name.startswith(".text") else 0)
                             for name, body, _ in sections], symbols)
        raw = bytearray(path.read_bytes())
        _, syms = lc.parse_coff(raw)
        by_name = {y.name: i for i, y in syms.items()}
        old_symbols = struct.unpack_from("<I", raw, 8)[0]
        relocations = bytearray()
        for number, (_, _, rels) in enumerate(sections):
            if rels:
                struct.pack_into("<I", raw, 20 + 40 * number + 24, old_symbols + len(relocations))
                struct.pack_into("<H", raw, 20 + 40 * number + 32, len(rels))
                for offset, name, kind in rels:
                    relocations += struct.pack("<IIH", offset, by_name[name], kind)
        raw[old_symbols:old_symbols] = relocations
        struct.pack_into("<I", raw, 8, old_symbols + len(relocations))
        path.write_bytes(raw)
        lc.parse_coff(raw)  # The fixture must be a complete, readable i386 COFF.
        self.paths.append(path)
        return path

    def row(self, obj, name, rva, size, source=None, notes=""):
        source = source or "game/" + obj.stem + ".cpp"
        self.source_objects[source] = obj
        self.rows.append(dict(name=name, source=source, notes=notes, status="matched",
                              target_rva=f"0x{rva:08X}", target_size=str(size)))

    def public(self, obj, name, rva):
        self.publics[name] = (rva, obj.name)

    def measure(self):
        out = self.root / "measurement"
        out.mkdir(exist_ok=True)
        (out / "base.map").write_text("\n".join(
            f" 0001:00000000 {name} {lc.BASE + rva:08x} f {obj}"
            for name, (rva, obj) in self.publics.items()))
        (out / "shft.exe").touch()
        shifted = bytearray(self.I)
        for site in self.shift_sites:
            shifted[site:site + 4] = dword(lc.u32(self.I, site) + lc.SHIFT_BASE - lc.BASE)
        self.patch.setattr(lc, "pe_view", lambda path: (
            None, shifted if Path(path).name == "shft.exe" else self.I, self.sections, {}))
        self.patch.setattr(lc, "row_obj", lambda row: self.source_objects[row["source"]])
        objects = lc.Objects(self.paths)
        units, _ = lc.analyze(self.rows, objects)
        result = lc.measure(out, units, [], objects, self.R, self.sections, {}, self.pins,
                            True, lc.SHIFT_BASE)
        with (out / "link_status.csv").open(newline="") as handle:
            status = list(csv.DictReader(handle))
        return result, status


@pytest.fixture
def case(tmp_path, monkeypatch):
    return ImageCase(tmp_path, monkeypatch)


def assert_uncredited(case, *, name="_caller"):
    result, status = case.measure()
    caller = next(r for r in status if r["name"] == name)
    print(json.dumps({"credit_unique_bytes": result["credit_unique_bytes"], "row": caller,
                      "twins": result["twins"], "eh": result["eh_thunks"]}, sort_keys=True))
    assert caller["closed_strict"] == "0", "unsafe row acquired closed-strict credit"


def test_non_icf_code_addresses_must_not_collapse_to_a_byte_twin(case):
    """Two distinct retail function pointers become equal in the produced image."""
    body = b"\x31\xc0\xc3"
    provider = case.object("provider.obj", [(".text", body, [])], [("_a", 1, 0, lc.EXTERNAL)])
    case.row(provider, "_a", A, len(body))
    case.public(provider, "_a", A)
    case.put(A, body, retail=body)
    # B has a ledger extent, but its source no longer emits the required body.
    absent = case.object("absent.obj", [(".text", b"\xc3", [])], [("_unrelated", 1, 0, lc.EXTERNAL)])
    case.row(absent, "_b", B, len(body))
    case.R[B:B + len(body)] = body
    raw = b"\xb8" + bytes(4) + b"\x3d" + bytes(4) + b"\x0f\x94\xc0\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "_a", lc.DIR32), (6, "_a", lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_a", 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, A)
    case.ptr(F + 6, A)
    case.R[F + 1:F + 5], case.R[F + 6:F + 10] = dword(lc.BASE + A), dword(lc.BASE + B)
    assert lc.u32(case.I, F + 1) == lc.u32(case.I, F + 6)
    assert lc.u32(case.R, F + 1) != lc.u32(case.R, F + 6)
    assert_uncredited(case)


def test_ilt_route_equivalence_must_not_collapse_pointer_identity(case):
    """A direct-call route is not permission to merge observable pointer values."""
    body = b"\x31\xc0\xc3"
    provider = case.object("provider.obj", [(".text", body, [])], [("_a", 1, 0, lc.EXTERNAL)])
    case.row(provider, "_a", A, len(body))
    case.public(provider, "_a", A)
    case.put(A, body, retail=body)
    thunk = 0x20000  # Inside BFME1's retail ILT range.
    case.R[thunk:thunk + 5] = b"\xe9" + dword(A - thunk - 5)
    raw = b"\xb8" + bytes(4) + b"\x3d" + bytes(4) + b"\x0f\x94\xc0\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "_a", lc.DIR32), (6, "_a", lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_a", 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, A)
    case.ptr(F + 6, A)
    case.R[F + 1:F + 5], case.R[F + 6:F + 10] = dword(lc.BASE + A), dword(lc.BASE + thunk)
    assert_uncredited(case)


def test_twin_must_not_launder_generated_dependency_into_strict_closure(case):
    body = b"\x31\xc0\xc3"
    provider = case.object("provider.obj", [(".text", body, [])], [("_a", 1, 0, lc.EXTERNAL)])
    case.row(provider, "_a", A, len(body), source="game/gen_asm/provider.cpp")
    case.public(provider, "_a", A)
    case.put(A, body, retail=body)
    absent = case.object("absent.obj", [(".text", b"\xc3", [])], [("_unrelated", 1, 0, lc.EXTERNAL)])
    case.row(absent, "_b", B, len(body))
    case.R[B:B + len(body)] = body
    raw = b"\xe8" + bytes(4) + b"\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "_a", lc.REL32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_a", 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, b"\xe8" + dword(A - F - 5) + b"\xc3",
             retail=b"\xe8" + dword(B - F - 5) + b"\xc3")
    assert_uncredited(case)


def test_unit_closure_must_check_a_reachable_unledgered_section_tail(case):
    """A local helper shares a section with a matched leaf; its bytes are unchecked."""
    section = b"\xc3" + b"\xcc" * 15 + b"\xb8\x02\0\0\0\xc3"
    provider = case.object("provider.obj", [(".text", section, [])],
                           [("_head", 1, 0, lc.EXTERNAL), ("_helper", 1, 16, lc.EXTERNAL)])
    case.row(provider, "_head", A, 1)
    case.public(provider, "_head", A)
    case.public(provider, "_helper", A + 16)
    case.put(A, section, retail=section)
    case.R[A + 17] = 1  # The reached helper should return 1, not 2.
    raw = b"\xe8" + bytes(4) + b"\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "_helper", lc.REL32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_helper", 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    linked = b"\xe8" + dword(A + 16 - F - 5) + b"\xc3"
    case.put(F, linked, retail=linked)
    assert_uncredited(case)


def test_unrelocated_direct_call_must_not_disappear_from_closure(case):
    """An encoded direct call has no COFF relocation and reaches unmeasured code."""
    code = b"\xe8" + dword(A - F - 5) + b"\xc3"
    caller = case.object("caller.obj", [(".text", code, [])], [("_caller", 1, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(code))
    case.public(caller, "_caller", F)
    case.put(F, code, retail=code)
    case.put(A, b"\xb8\x02\0\0\0\xc3", retail=b"\xb8\x01\0\0\0\xc3")
    assert_uncredited(case)


def eh_case(case, *, states=1):
    raw = b"\x68" + bytes(4) + b"\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "__ehhandler$_caller", lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("__ehhandler$_caller", 0, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, EH)
    case.R[F + 1:F + 5] = dword(lc.BASE + REH)
    case.public(caller, "__ehhandler$_caller", EH)
    case.put(EH, b"\xb8" + dword(lc.BASE + DATA) + b"\xe9" + dword(A - EH - 10))
    case.shift_sites.add(EH + 1)
    case.R[REH:REH + 10] = b"\xb8" + dword(lc.BASE + RDATA) + b"\xe9" + dword(A - REH - 10)
    for image, fi in ((case.I, DATA), (case.R, RDATA)):
        image[fi:fi + 24] = struct.pack("<IiIIII", 0x19930520, states, lc.BASE + fi + 0x100, 0, 0, 0)
        for i in range(states):
            image[fi + 0x100 + i * 8:fi + 0x108 + i * 8] = struct.pack("<iI", -1, 0)
    case.shift_sites.add(DATA + 8)


def test_eh_handler_jump_must_not_hide_an_unresolved_stub(case):
    eh_case(case)
    case.I[EH + 6:EH + 10] = dword(STUB - EH - 10)
    # The thunk's E9 now enters non-executable, zero-filled .stubd.
    assert_uncredited(case)


def test_eh_unwind_call_must_participate_in_dependency_closure(case):
    eh_case(case)
    case.ptr(DATA + 0x104, ACTION)
    case.R[RDATA + 0x104:RDATA + 0x108] = dword(lc.BASE + ACTION)
    case.put(ACTION, b"\xe8" + dword(STUB - ACTION - 5) + b"\xc3",
             retail=b"\xe8" + dword(A - ACTION - 5) + b"\xc3")
    assert_uncredited(case)


def test_eh_funclet_data_operands_must_be_verified(case):
    eh_case(case)
    case.ptr(DATA + 0x104, ACTION)
    case.R[RDATA + 0x104:RDATA + 0x108] = dword(lc.BASE + ACTION)
    case.put(ACTION, b"\xa1" + dword(lc.BASE + TYPE) + b"\xc3",
             retail=b"\xa1" + dword(lc.BASE + TYPE + 16) + b"\xc3")
    case.ptr(ACTION + 1, TYPE)
    case.put(TYPE, dword(2))
    case.R[TYPE + 16:TYPE + 20] = dword(1)
    assert_uncredited(case)


def test_eh_catch_type_identity_must_be_verified(case):
    eh_case(case)
    for image, fi, descriptor in ((case.I, DATA, TYPE), (case.R, RDATA, TYPE + 32)):
        image[fi + 12:fi + 20] = dword(1) + dword(lc.BASE + fi + 0x200)
        image[fi + 0x200:fi + 0x214] = struct.pack("<iiiiI", 0, 0, 0, 1, lc.BASE + fi + 0x220)
        image[fi + 0x220:fi + 0x230] = struct.pack("<IIiI", 0, lc.BASE + descriptor, 0, lc.BASE + ACTION)
    case.shift_sites.update({DATA + 16, DATA + 0x210, DATA + 0x224, DATA + 0x22C})
    case.put(ACTION, b"\xc3", retail=b"\xc3")
    case.put(TYPE, bytes(8) + b".?AVWrong@@\0")
    descriptor = bytes(8) + b".?AVRight@@\0"
    case.R[TYPE + 32:TYPE + 32 + len(descriptor)] = descriptor
    case.retail_extent('_type', TYPE + 32, 19)  # MSVC descriptor header + .?AVRight@@ NUL
    assert_uncredited(case)


def test_eh_unwind_table_cap_must_fail_closed(case):
    eh_case(case, states=401)
    last = 0x100 + 400 * 8
    case.ptr(DATA + last + 4, ACTION)
    case.R[RDATA + last + 4:RDATA + last + 8] = dword(lc.BASE + ACTION)
    case.put(ACTION, b"\xb8\x02\0\0\0\xc3", retail=b"\xb8\x01\0\0\0\xc3")
    assert_uncredited(case)


def test_data_mapping_must_be_one_to_one_for_entire_datums(case):
    """A[i]=7; return B[1] becomes G[i]=7; return G[1], although A != B."""
    raw = b"\xc7\x04\x8d" + bytes(4) + dword(7) + b"\xa1" + dword(4) + b"\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(3, "_g", lc.DIR32), (12, "_g", lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_g", 0, 0, lc.EXTERNAL)])
    data = case.object("data.obj", [(".data", bytes(8), [])], [("_g", 1, 0, lc.EXTERNAL)])
    case.public(data, "_g", DATA)
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 3, DATA)
    case.ptr(F + 12, DATA + 4)
    case.R[F + 3:F + 7] = dword(lc.BASE + RDATA)
    case.R[F + 12:F + 16] = dword(lc.BASE + RDATA + 0x104)
    assert_uncredited(case)


def test_data_read_past_definition_extent_must_not_verify_the_previous_datum(case):
    raw = b"\xa1" + dword(4) + b"\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "_g", lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_g", 0, 0, lc.EXTERNAL)])
    data = case.object("data.obj", [(".data", bytes(4), [])], [("_g", 1, 0, lc.EXTERNAL)])
    case.public(data, "_g", DATA)
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, DATA + 4)
    case.R[F + 1:F + 5] = dword(lc.BASE + RDATA + 4)
    case.put(DATA + 4, dword(2))
    case.R[RDATA + 4:RDATA + 8] = dword(1)
    assert_uncredited(case)


def test_unrelocated_pointer_inside_data_must_not_close(case):
    raw = b"\xa1" + bytes(4) + b"\xff\xd0\xc3"
    caller = case.object("caller.obj", [(".text", raw, [(1, "_callback", lc.DIR32)])],
                         [("_caller", 1, 0, lc.EXTERNAL), ("_callback", 0, 0, lc.EXTERNAL)])
    data = case.object("data.obj", [(".data", dword(lc.BASE + A), [])], [("_callback", 1, 0, lc.EXTERNAL)])
    case.public(data, "_callback", DATA)
    case.row(caller, "_caller", F, len(raw))
    case.public(caller, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, DATA)
    case.R[F + 1:F + 5] = dword(lc.BASE + RDATA)
    case.put(DATA, dword(lc.BASE + A))  # No DIR32: this pointer stays at the OLD base.
    case.R[RDATA:RDATA + 4] = dword(lc.BASE + A)
    case.put(A, b"\xb8\x02\0\0\0\xc3", retail=b"\xb8\x01\0\0\0\xc3")
    assert_uncredited(case)


@pytest.mark.parametrize("notes,source", [
    ("gen-tgrid", "game/template.cpp"),
    ("identity=generated", "game/template.cpp"),
    ("", "game/named_lift.cpp"),
    ("", "game/prebuilt.lib"),
])
def test_real_credit_must_use_bfme1_source_provenance(case, notes, source):
    import progress
    raw = b"\xc3"
    obj = case.object("caller.obj", [(".text", raw, [])], [("_caller", 1, 0, lc.EXTERNAL)])
    case.row(obj, "_caller", F, len(raw), source=source, notes=notes)
    case.public(obj, "_caller", F)
    case.put(F, raw, retail=raw)
    path = case.root / source
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("__declspec(naked) void caller() { __asm { __emit 0xc3 } }\n")
    lane = progress.source_lane(source, notes, naked=source.endswith("named_lift.cpp"))
    assert lane not in progress.DECOMPILED_LANES
    result, _ = case.measure()
    print(f"BFME1 source_lane={lane}; cycle real credit={result['credit_unique_bytes']}")
    assert result["credit_unique_bytes"] == 0


@pytest.mark.parametrize("bad", [False, True])
def test_control_leaf_bytes_still_decide_credit(case, bad):
    raw = b"\xb8\x01\0\0\0\xc3"
    obj = case.object("caller.obj", [(".text", raw, [])], [("_caller", 1, 0, lc.EXTERNAL)])
    case.row(obj, "_caller", F, len(raw))
    case.public(obj, "_caller", F)
    case.put(F, raw, retail=raw)
    if bad:
        case.I[F + 1] = 2
    result, _ = case.measure()
    assert result["credit_unique_bytes"] == (0 if bad else len(raw))


def test_control_duplicate_and_overlapping_rows_do_not_multiply_credit(case):
    obj = case.object("caller.obj", [(".text", b"\xc3", [])], [("_caller", 1, 0, lc.EXTERNAL)])
    case.row(obj, "_caller", F, 1)
    case.rows.append(dict(case.rows[0]))
    case.public(obj, "_caller", F)
    case.put(F, b"\xc3", retail=b"\xc3")
    result, _ = case.measure()
    assert result["real"]["placed_closed_strict"]["rows"] == 2
    assert result["credit_unique_bytes"] == 1


@pytest.mark.parametrize("scenario", ["missing-definition", "wrong-selected", "stub", "alias"])
def test_control_normal_missing_selected_stub_and_alias_paths_fail_closed(case, scenario):
    raw = b"\xe8" + bytes(4) + b"\xc3" if scenario == "stub" else b"\xc3"
    name = "_unrelated" if scenario == "missing-definition" else "_caller"
    rels = [(1, "_missing", lc.REL32)] if scenario == "stub" else []
    symbols = [(name, 1, 0, lc.EXTERNAL)]
    if rels:
        symbols.append(("_missing", 0, 0, lc.EXTERNAL))
    obj = case.object("caller.obj", [(".text", raw, rels)], symbols)
    case.row(obj, "_caller", F, len(raw), notes="gen-alias" if scenario == "alias" else "")
    if scenario != "missing-definition":
        selected = obj
        if scenario == "wrong-selected":
            selected = case.object("other.obj", [(".text", raw, [])], [("_caller", 1, 0, lc.EXTERNAL)])
        case.public(selected, "_caller", F)
    case.put(F, raw, retail=raw)
    if scenario == "stub":
        case.I[F + 1:F + 5] = dword(STUB - F - 5)
        case.R[F + 1:F + 5] = dword(A - F - 5)
    result, _ = case.measure()
    assert result["credit_unique_bytes"] == 0


def verified_eh_providers(case):
    """Real ledger extents for the helper dependencies, rather than EH-only byte guesses."""
    for name, at in (("_handler", A), ("_action", ACTION)):
        obj = case.object(name + ".obj", [(".text", b"\xc3", [])], [(name, 1, 0, lc.EXTERNAL)])
        case.row(obj, name, at, 1)
        case.public(obj, name, at)
        case.put(at, b"\xc3", retail=b"\xc3")


@pytest.mark.parametrize("bad", [False, True])
def test_control_eh_helpers_close_only_with_verified_providers(case, bad):
    eh_case(case)
    verified_eh_providers(case)
    case.ptr(DATA + 0x104, ACTION)
    case.R[RDATA + 0x104:RDATA + 0x108] = dword(lc.BASE + ACTION)
    if bad:
        case.I[ACTION] = 0xCC  # Same identity, but the provider fails its own verdict.
    _, status = case.measure()
    caller = next(r for r in status if r["name"] == "_caller")
    assert caller["closed_strict"] == ("0" if bad else "1")


@pytest.mark.parametrize("bad", [False, True])
def test_control_eh_catch_descriptor_uses_datum_evidence(case, bad):
    eh_case(case)
    verified_eh_providers(case)
    descriptor = bytes(8) + b".?AVRight@@\0"
    data = case.object("type.obj", [(".rdata", descriptor, [])], [("_type", 1, 0, lc.EXTERNAL)])
    case.public(data, "_type", TYPE)
    case.put(TYPE, descriptor)
    case.R[TYPE + 32:TYPE + 32 + len(descriptor)] = descriptor
    case.retail_extent('_type', TYPE + 32, 19)  # MSVC descriptor header + .?AVRight@@ NUL
    if bad:
        case.I[TYPE + 12] = ord("X")
    for image, fi, ty in ((case.I, DATA, TYPE), (case.R, RDATA, TYPE + 32)):
        image[fi + 12:fi + 20] = dword(1) + dword(lc.BASE + fi + 0x200)
        image[fi + 0x200:fi + 0x214] = struct.pack("<iiiiI", 0, 0, 0, 1, lc.BASE + fi + 0x220)
        image[fi + 0x220:fi + 0x230] = struct.pack("<IIiI", 0, lc.BASE + ty, 0, lc.BASE + ACTION)
    case.shift_sites.update({DATA + 16, DATA + 0x210, DATA + 0x224, DATA + 0x22C})
    _, status = case.measure()
    caller = next(r for r in status if r["name"] == "_caller")
    assert caller["closed_strict"] == ("0" if bad else "1")


def test_control_unrelocated_direct_call_closes_through_a_verified_leaf(case):
    body = b"\xc3"
    provider = case.object("leaf.obj", [(".text", body, [])], [("_leaf", 1, 0, lc.EXTERNAL)])
    case.row(provider, "_leaf", A, 1)
    case.public(provider, "_leaf", A)
    case.put(A, body, retail=body)
    code = b"\xe8" + dword(A - F - 5) + b"\xc3"
    caller = case.object("caller.obj", [(".text", code, [])], [("_caller", 1, 0, lc.EXTERNAL)])
    case.row(caller, "_caller", F, len(code))
    case.public(caller, "_caller", F)
    case.put(F, code, retail=code)
    result, _ = case.measure()
    assert result["credit_unique_bytes"] == 7


@pytest.mark.parametrize("pointer_site", [False, True])
def test_retail_relocation_evidence_distinguishes_literal_numbers_from_pointers(case, pointer_site):
    # Identical word values do not prove a pointer. BFME1's retained HIGHLOW
    # list decides; a genuine pointer needs a matching symbolic COFF relocation.
    case.R[:2] = b"MZ"
    case.patch.setattr(lc.retail_relocs, "site_rvas", lambda: (RDATA,) if pointer_site else ())
    raw = b"\xa1" + bytes(4) + b"\xc3"
    obj = case.object("caller.obj", [(".text", raw, [(1, "_g", lc.DIR32)])],
                      [("_caller", 1, 0, lc.EXTERNAL), ("_g", 0, 0, lc.EXTERNAL)])
    data = case.object("data.obj", [(".data", dword(lc.BASE + A), [])], [("_g", 1, 0, lc.EXTERNAL)])
    case.public(data, "_g", DATA)
    case.row(obj, "_caller", F, len(raw))
    case.public(obj, "_caller", F)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, DATA)
    case.R[F + 1:F + 5] = dword(lc.BASE + RDATA)
    case.put(DATA, dword(lc.BASE + A))
    case.R[RDATA:RDATA + 4] = dword(lc.BASE + A)
    result, _ = case.measure()
    assert result["credit_unique_bytes"] == (0 if pointer_site else len(raw))


@pytest.mark.parametrize("provider", [False, True])
def test_direct_call_after_inline_data_still_has_a_dependency(case, provider):
    # The jump skips bytes which cannot be decoded as the call's instruction
    # stream. Follow the destination rather than treating inline data as code.
    code = b"\xeb\x02\x0f\x0f\xe8" + dword(A - F - 9) + b"\xc3"
    obj = case.object("caller.obj", [(".text", code, [])], [("_caller", 1, 0, lc.EXTERNAL)])
    case.row(obj, "_caller", F, len(code))
    case.public(obj, "_caller", F)
    case.put(F, code, retail=code)
    if provider:
        leaf = case.object("leaf.obj", [(".text", b"\xc3", [])], [("_leaf", 1, 0, lc.EXTERNAL)])
        case.row(leaf, "_leaf", A, 1)
        case.public(leaf, "_leaf", A)
        case.put(A, b"\xc3", retail=b"\xc3")
    result, _ = case.measure()
    assert result["credit_unique_bytes"] == (len(code) + 1 if provider else 0)


def test_fallthrough_into_unverified_section_tail_does_not_close(case):
    code = b"\x90\xc3"
    obj = case.object("caller.obj", [(".text", code, [])], [("_caller", 1, 0, lc.EXTERNAL)])
    case.row(obj, "_caller", F, 1)  # Only the nop is verified, but execution continues.
    case.public(obj, "_caller", F)
    case.put(F, code, retail=code)
    assert_uncredited(case)


def test_eh_thunk_proof_does_not_cover_an_unverified_neighbor(case):
    eh_case(case)
    verified_eh_providers(case)
    # sym_at() finds the preceding EH map symbol, but its proof covers only
    # the actual thunk, not the bytes beyond it reached by this pointer.
    case.ptr(F + 1, EH + 16)
    case.R[F + 1:F + 5] = dword(lc.BASE + REH + 16)
    assert_uncredited(case)


@pytest.mark.parametrize('provider_lane', ['real', 'generated', 'library'])
@pytest.mark.parametrize('other_target', ['none', 'thunk', 'body'])
def test_vtable_ilt_routes_preserve_global_identity_and_provider(case, provider_lane, other_target):
    """Ordinary slots close; a collision discovered in a later datum revokes both."""
    body = b'\x31\xc0\xc3'
    provider = case.object('provider.obj', [('.text', body, [])], [('_a', 1, 0, lc.EXTERNAL)])
    source = {'real': 'game/provider.cpp', 'generated': 'game/gen_small/provider.cpp',
              'library': 'inputs/vendor/example/example.lib'}[provider_lane]
    case.row(provider, '_a', A, len(body), source=source, notes='vendored=example-1.0' if provider_lane == 'library' else '')
    case.public(provider, '_a', A)
    case.put(A, body, retail=body)
    thunk, second = 0x20000, 0x20010
    for address in (thunk, second):
        case.R[address:address + 5] = b'\xe9' + dword(A - address - 5)
    targets = [thunk] if other_target == 'none' else [thunk, second if other_target == 'thunk' else A]
    for index, target in enumerate(targets):
        name = f'_vtable{index}'
        table = case.object(f'vtable{index}.obj', [('.rdata', bytes(4), [(0, '_a', lc.DIR32)])],
                            [(name, 1, 0, lc.EXTERNAL), ('_a', 0, 0, lc.EXTERNAL)])
        site, retail_site = DATA + 16 * index, RDATA + 16 * index
        case.retail_extent(name, retail_site, 4)  # independent single-slot retail vtable
        case.public(table, name, site)
        case.ptr(site, A)
        case.R[retail_site:retail_site + 4] = dword(lc.BASE + target)
        raw = b'\xb8' + bytes(4) + b'\xc3'
        caller_name, caller_rva = f'_caller{index}', F + 32 * index
        caller = case.object(f'caller{index}.obj', [('.text', raw, [(1, name, lc.DIR32)])],
                             [(caller_name, 1, 0, lc.EXTERNAL), (name, 0, 0, lc.EXTERNAL)])
        case.row(caller, caller_name, caller_rva, len(raw))
        case.public(caller, caller_name, caller_rva)
        case.put(caller_rva, raw, retail=raw)
        case.ptr(caller_rva + 1, site)
        case.R[caller_rva + 1:caller_rva + 5] = dword(lc.BASE + retail_site)
    result, status = case.measure()
    expected = other_target == 'none' and provider_lane != 'generated'
    callers = [r for r in status if r['name'].startswith('_caller')]
    assert all(r['closed_strict'] == str(int(expected)) for r in callers)
    assert result['credit_unique_bytes'] == (6 if expected else 0) + (3 if provider_lane == 'real' else 0)
    assert result['ilt_routes']['pointer'] >= 1
    if provider_lane != 'real':
        assert result[provider_lane]['all']['unique_bytes'] == 3
        assert next(r for r in status if r['name'] == '_a')['kind'] == provider_lane


@pytest.mark.parametrize('provider_source,closed', [
    ('inputs/vendor/example/example.lib', True),
    ('game/gen_small/provider.cpp', False),
    ('game/masm_dumps/provider.asm', False),
])
@pytest.mark.parametrize('bad_bytes', [False, True])
def test_verified_library_is_a_dependency_with_separate_credit_series(case, provider_source, closed, bad_bytes):
    body = b'\x31\xc0\xc3'
    provider = case.object('provider.obj', [('.text', body, [])], [('_a', 1, 0, lc.EXTERNAL)])
    case.row(provider, '_a', A, len(body), source=provider_source, notes='vendored=example-1.0')
    case.public(provider, '_a', A)
    case.put(A, b'\x31\xc9\xc3' if bad_bytes else body, retail=body)
    raw = b'\xe8' + bytes(4) + b'\xc3'
    caller = case.object('caller.obj', [('.text', raw, [(1, '_a', lc.REL32)])],
                         [('_caller', 1, 0, lc.EXTERNAL), ('_a', 0, 0, lc.EXTERNAL)])
    case.row(caller, '_caller', F, len(raw))
    case.public(caller, '_caller', F)
    code = b'\xe8' + dword(A - F - 5) + b'\xc3'
    case.put(F, code, retail=code)
    result, status = case.measure()
    assert result['credit_unique_bytes'] == (len(code) if closed and not bad_bytes else 0)
    provider_kind = next(r['kind'] for r in status if r['name'] == '_a')
    assert provider_kind != 'real'
    assert result[provider_kind]['all']['unique_bytes'] == len(body)
    import closure_report as cr
    graph = cr.load_graph(case.root / 'measurement' / cr.GRAPH_FILE)
    assert cr.credit_of(*graph[:3]) == result['credit_unique_bytes']


# BFME1 build_call_thunks permits two route-only calls through different ILTs.
@pytest.mark.parametrize('target_pair,closed', [('body-thunk', True), ('same-thunk', True),
                                               ('two-thunks', True), ('two-bodies', False)])
def test_code_route_injectivity_is_settled_across_all_rows(case, target_pair, closed):
    body = b'\x31\xc0\xc3'
    provider = case.object('provider.obj', [('.text', body, [])], [('_a', 1, 0, lc.EXTERNAL)])
    case.row(provider, '_a', A, len(body))
    case.public(provider, '_a', A)
    case.put(A, body, retail=body)
    thunk, second = 0x20000, 0x20010
    for address in (thunk, second):
        case.R[address:address + 5] = b'\xe9' + dword(A - address - 5)
    targets = {'body-thunk': (A, thunk), 'same-thunk': (thunk, thunk),
               'two-thunks': (thunk, second), 'two-bodies': (A, B)}[target_pair]
    for index, target in enumerate(targets):
        name, rva = f'_caller{index}', F + 32 * index
        raw = b'\xe8' + bytes(4) + b'\xc3'
        obj = case.object(f'caller{index}.obj', [('.text', raw, [(1, '_a', lc.REL32)])],
                          [(name, 1, 0, lc.EXTERNAL), ('_a', 0, 0, lc.EXTERNAL)])
        case.row(obj, name, rva, len(raw))
        case.public(obj, name, rva)
        case.put(rva, b'\xe8' + dword(A - rva - 5) + b'\xc3',
                 retail=b'\xe8' + dword(target - rva - 5) + b'\xc3')
    result, status = case.measure()
    assert result['credit_unique_bytes'] == (15 if closed else 3)
    assert all(r['closed_strict'] == str(int(closed)) for r in status if r['name'].startswith('_caller'))
    assert all(('code-identity-collapse:' in r['failures']) != closed
               for r in status if r['name'].startswith('_caller'))
