"""Discovery-only BFME1 adaptation: synthetic i386 COFF and PE, no compiler."""
import csv
import json
from pathlib import Path
import struct
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import place_bodies as pb


@pytest.mark.parametrize("name", [
    "?push_back@?$vector@H@_STL@@QAEXABH@Z", "_auxsort", "_luaB_call",
    "___mbtowc", "_WSAStartup@8",
])
def test_function_names_are_placeable(name):
    assert pb.placeable(name)


@pytest.mark.parametrize("name", [
    "__ehhandler$?f@@YAXXZ", "__unwindfunclet$?f@@YAXXZ$0", "_$E36", "_name@x", "name",
])
def test_compiler_generated_symbols_are_not(name):
    assert not pb.placeable(name)


BODY = bytes.fromhex("558bec83ec105356578bf18b45088b4d0c33c05f5e5bc9c3")
CALL_BODY = BODY[:-1] + b"\xe8\0\0\0\0\xc3"
ROW_FIELDS = ["name", "rva", "target_rva", "target_size", "source", "status", "notes"]


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def row(name, address, size=1, source="game/Real.cpp", notes="", status="matched"):
    return dict(name=name, rva=f"0x{address:08X}", target_rva=f"0x{address:08X}",
                target_size=str(size), source=source, status=status, notes=notes)


def pe_image(text, *, base=0x400000, virtual_size=None, suffix=b""):
    data = bytearray(0x200)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, 0x84, 0x14C, 1, 0, 0, 0, 0xE0, 0)
    struct.pack_into("<H", data, 0x98, 0x10B)
    struct.pack_into("<I", data, 0x98 + 28, base)
    struct.pack_into("<8sIIIIIIHHI", data, 0x178, b".text", virtual_size or len(text),
                     0x1000, len(text), 0x200, 0, 0, 0, 0, 0x60000020)
    return bytes(data) + text + suffix


def coff(functions, *, data_symbol=None):
    """Each (names, body, relocations) owns a section; names can be aliases."""
    functions = [(names if isinstance(names, list) else [names], body, relocs)
                 for names, body, relocs in functions]
    count = len(functions) + bool(data_symbol)
    symbols, relocations = [], []
    for i, (names, body, relocs) in enumerate(functions, 1):
        for name in names:
            symbols.append((name, i, 0, 0x20))
        relocations.append(relocs)
    if data_symbol:
        symbols.append((data_symbol, count, 0, 0))
        functions.append(([data_symbol], BODY, []))
        relocations.append([])
    for relocs in relocations:
        for _, _, name in relocs:
            if not any(s[0] == name for s in symbols):
                symbols.append((name, 0, 0, 0x20))
    data = bytearray(20 + 40 * count)
    for i, (_, body, relocs) in enumerate(functions):
        raw = len(data)
        data.extend(body)
        reloc = len(data)
        for off, kind, name in relocs:
            index = next(j for j, s in enumerate(symbols) if s[0] == name)
            data.extend(struct.pack("<IIH", off, index, kind))
        flags = 0xC0000040 if data_symbol and i == count - 1 else 0x60000020
        struct.pack_into("<8sIIIIIIHHI", data, 20 + 40 * i, b".text", 0, 0, len(body),
                         raw, reloc, 0, len(relocs), 0, flags)
    sym_pointer = len(data)
    strings = bytearray(b"\0\0\0\0")
    for name, section, value, kind in symbols:
        encoded = name.encode()
        if len(encoded) > 8:
            field = struct.pack("<II", 0, len(strings))
            strings.extend(encoded + b"\0")
        else:
            field = encoded.ljust(8, b"\0")
        data.extend(struct.pack("<8sIhHBB", field, value, section, kind, 2, 0))
    struct.pack_into("<I", strings, 0, len(strings))
    data.extend(strings)
    struct.pack_into("<HHIIIHH", data, 0, 0x14C, count, 0, sym_pointer, len(symbols), 0, 0)
    return bytes(data)


class Lab:
    def __init__(self, path, monkeypatch):
        self.path = path
        self.exe = path / "retail.exe"
        self.functions = path / "targets/game/reverse/functions.csv"
        self.symbols = path / "targets/game/reverse/symbols.csv"
        self.denylist = path / "denylist.txt"
        self.source = path / "game/Unit.cpp"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("// existing reconstructed TU\n")
        self.obj = path / "Unit.obj"
        monkeypatch.setattr(pb.build, "ROOT", path)
        monkeypatch.setattr(pb.build, "EXE", self.exe)
        monkeypatch.setattr(pb.build, "FUNCTIONS", self.functions)
        monkeypatch.setattr(pb.build, "SYMBOLS", self.symbols)
        def forbidden(*args, **kwargs):
            pytest.fail("discovery attempted a subprocess / compilation / writer / whole-ledger load")
        monkeypatch.setattr(pb.eligibility, "load_rows", forbidden)
        monkeypatch.setattr(pb.build, "load_all_function_rows", forbidden)
        monkeypatch.setattr(pb.locate.harvest, "compile_obj", forbidden)
        monkeypatch.setattr(pb.build, "compile_source", forbidden)
        monkeypatch.setattr(pb.build.subprocess, "run", forbidden)
        monkeypatch.setattr(pb.locate.ledger_io, "append_rows", forbidden, raising=False)
        self.ledgers()
        self.image({0x1080: BODY})
        self.object()

    def ledgers(self, rows=(), pins=()):
        write_csv(self.functions, ROW_FIELDS, rows)
        write_csv(self.symbols, ["name", "address", "notes"], pins)
        for name in ("exports.csv", "data_rows.csv", "deleted_rows.csv"):
            (self.functions.parent / name).write_bytes(b"unchanged\r\n")

    def image(self, bodies, *, base=0x400000, virtual_size=None, suffix=b""):
        text = bytearray(b"\xcc" * 0x500)
        for rva, body in bodies.items():
            text[rva - 0x1000:rva - 0x1000 + len(body)] = body
        self.exe.write_bytes(pe_image(text, base=base, virtual_size=virtual_size, suffix=suffix))

    def object(self, functions=None, **kwargs):
        self.obj.write_bytes(coff(functions or [("?f@@YAXXZ", BODY, [])], **kwargs))

    def scan(self, **kwargs):
        return pb.discover([("game/Unit.cpp", self.obj)], denylist=self.denylist, **kwargs)

    def call(self, rva=0x1080, target=0x1400, name="?callee@@YAXXZ", addend=0):
        offset = len(CALL_BODY) - 5
        compiled = bytearray(CALL_BODY)
        struct.pack_into("<i", compiled, offset, addend)
        retail = bytearray(CALL_BODY)
        struct.pack_into("<i", retail, offset, target + addend - (rva + offset + 4))
        return bytes(compiled), bytes(retail), [(offset, pb.REL32, name)]


@pytest.fixture
def lab(tmp_path, monkeypatch):
    return Lab(tmp_path, monkeypatch)


def test_unique_hit_is_only_candidate_placement(lab):
    report = lab.scan()
    entry = report["bodies"][0]
    assert entry["status"] == "unique-hit"
    assert entry["candidate_rva"] == 0x1080
    assert not entry["blocked_by"]
    assert report["evidence"] == entry["evidence"] == "candidate"
    assert "never identity evidence" in report["notice"]
    assert report["required_gates"] == ["identity validation", "add_match", "pin_consistency"]


def test_multiple_hits_remain_visible(lab):
    lab.image({0x1080: BODY, 0x1180: BODY})
    entry = lab.scan()["bodies"][0]
    assert entry["status"] == "multiple-hits"
    assert [h["rva"] for h in entry["hits"]] == [0x1080, 0x1180]
    assert entry["candidate_rva"] is None


def test_overlapping_hits_are_not_lost(lab):
    lab.object([("_repeat", b"\x90" * 20, [])])
    lab.image({0x1080: b"\x90" * 21})
    assert [h["rva"] for h in lab.scan()["bodies"][0]["hits"]] == [0x1080, 0x1081]


def test_dir32_and_rel32_masking_and_possible_pin(lab):
    compiled, retail, relocs = lab.call()
    compiled = b"\xb8\0\0\0\0" + compiled
    retail = b"\xb8\x98\x76\x54\x32" + retail
    # Prefix moved the call site, so re-encode retail's displacement.
    offset = relocs[0][0] + 5
    retail = bytearray(retail)
    struct.pack_into("<i", retail, offset, 0x1400 - (0x1080 + offset + 4))
    lab.object([("?f@@YAXXZ", compiled, [(1, 6, "_data"), (offset, pb.REL32, "?callee@@YAXXZ")])])
    lab.image({0x1080: retail})
    report = lab.scan()
    assert report["bodies"][0]["candidate_rva"] == 0x1080
    assert [(p["name"], p["rva"]) for p in report["possible_pins"]] == [("?callee@@YAXXZ", 0x1400)]


def test_callee_agreement_filters_multiple_hits(lab):
    compiled, first, relocs = lab.call(target=0x1400)
    _, second, _ = lab.call(rva=0x1180, target=0x1440)
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: first, 0x1180: second})
    lab.ledgers([row("?callee@@YAXXZ", 0x1400)])
    entry = lab.scan()["bodies"][0]
    assert entry["status"] == "multiple-hits"
    assert entry["candidate_rva"] == 0x1080
    assert entry["placement_basis"] == "callee-filtered"
    assert entry["hits"][0]["matched_callees"][0]["rva"] == 0x1400
    assert entry["hits"][1]["conflicting_callees"][0]["rva"] == 0x1440


def test_unique_hit_with_conflicting_callee_cannot_harvest(lab):
    compiled, retail, relocs = lab.call()
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail})
    lab.ledgers([row("?callee@@YAXXZ", 0x1440)])
    report = lab.scan()
    assert report["bodies"][0]["candidate_rva"] is None
    assert report["bodies"][0]["hits"][0]["conflicting_callees"]
    assert report["possible_pins"] == []


@pytest.mark.parametrize("source,notes", [
    ("game/gen_small/Lie.cpp", ""), ("game/gen_asm/Lie.cpp", ""),
    ("game/masm_dumps/Lie.cpp", ""), ("game/Lie.asm", ""),
    ("game/Lie.s", ""), ("game/Lie.cpp", "gen-dump"),
])
def test_generated_and_assembly_rows_are_not_callee_identity_sources(lab, source, notes):
    compiled, first, relocs = lab.call(target=0x1400)
    _, second, _ = lab.call(rva=0x1180, target=0x1440)
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: first, 0x1180: second})
    lab.ledgers([row("?callee@@YAXXZ", 0x1400, source=source, notes=notes)])
    entry = lab.scan()["bodies"][0]
    assert entry["candidate_rva"] is None
    assert all(not h["matched_callees"] for h in entry["hits"])


def test_pin_candidates_can_filter_but_do_not_become_identity_proof(lab):
    compiled, retail, relocs = lab.call()
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail})
    lab.ledgers(pins=[dict(name="?callee@@YAXXZ", address="0x1400", notes="pinharvest candidate")])
    report = lab.scan()
    assert report["bodies"][0]["hits"][0]["matched_callees"]
    assert report["possible_pins"] == []
    assert report["evidence"] == "candidate"


def test_refuses_pin_on_another_one_identity_name(lab):
    compiled, retail, relocs = lab.call()
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail})
    owner = row("?realOwner@@YAXXZ", 0x1400)
    assert pb.one_identity.real_names_by_address([owner])[0x1400] == {owner["name"]}
    lab.ledgers([owner])
    report = lab.scan()
    assert report["possible_pins"] == []
    assert report["refused_pins"][0]["reasons"] == ["other-identity"]
    assert report["refused_pins"][0]["other_identities"] == [owner["name"]]


def test_shared_emitted_names_are_overclaim_signal_never_fold_pins(lab):
    compiled, retail, relocs = lab.call()
    lab.object([(["?f@@YAXXZ", "?g@@YAXXZ"], compiled, relocs)])
    lab.image({0x1080: retail})
    report = lab.scan()
    assert {b["name"] for b in report["bodies"]} == {"?f@@YAXXZ", "?g@@YAXXZ"}
    assert all(b["possible_folded_body"] for b in report["bodies"])
    assert all("multiple-emitted-names" in b["blocked_by"] for b in report["bodies"])
    assert report["possible_pins"] == []
    assert "never prove a fold" in pb.readable(report)


def test_existing_other_body_identity_is_not_a_placement_admission(lab):
    lab.ledgers([row("?other@@YAXXZ", 0x1080, size=len(BODY))])
    entry = lab.scan()["bodies"][0]
    assert entry["candidate_rva"] == 0x1080  # retain discovery evidence
    assert entry["possible_folded_body"]
    assert "other-identity" in entry["blocked_by"]


@pytest.mark.parametrize("base", [0x400000, 0x63000000])
def test_bfme1_rva_and_va_are_tagged_not_guessed(lab, base):
    lab.image({0x1080: BODY}, base=base)
    report = lab.scan()
    hit = report["bodies"][0]["hits"][0]
    assert report["image_base"] == base
    assert report["address_kind"] == "RVA"
    assert hit["rva"] == report["bodies"][0]["candidate_rva"] == 0x1080
    assert hit["va"] == base + 0x1080


def test_rel32_pin_address_stays_rva_with_nondefault_image_base(lab):
    compiled, retail, relocs = lab.call()
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail}, base=0x63000000)
    assert lab.scan()["possible_pins"][0]["rva"] == 0x1400


def test_no_ledger_source_or_object_bytes_change_cli_json_and_readable(lab, capsys):
    compiled, retail, relocs = lab.call()
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail})
    before = {p: p.read_bytes() for p in lab.path.rglob("*") if p.is_file()}
    args = ["--object", "game/Unit.cpp", str(lab.obj), "--denylist", str(lab.denylist)]
    assert pb.main(args + ["--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["possible_pins"]
    assert pb.main(args) == 0
    assert "Candidate evidence only" in capsys.readouterr().out
    after = {p: p.read_bytes() for p in lab.path.rglob("*") if p.is_file()}
    assert before == after  # includes every ledger, source, PE and object


@pytest.mark.parametrize("flag", ["--apply", "--emit"])
def test_no_writer_cli_exists(lab, flag):
    with pytest.raises(SystemExit) as exc:
        pb.main(["--object", "game/Unit.cpp", str(lab.obj), flag])
    assert exc.value.code == 2


def test_threshold_and_denylist_are_recorded(lab):
    lab.denylist.write_text("# rejected candidate\n?f@@YAXXZ\n")
    report = lab.scan(minimum=32)
    assert report["configuration"]["minimum_body_size"] == 32
    assert report["configuration"]["denied_names"] == ["?f@@YAXXZ"]
    assert report["bodies"][0]["status"] == "denied"
    lab.denylist.unlink()
    assert lab.scan(minimum=32)["bodies"][0]["status"] == "below-minimum"


def test_no_data_symbols_even_if_their_bytes_match(lab):
    lab.object(data_symbol="?Data@@3HA")
    assert [b["name"] for b in lab.scan()["bodies"]] == ["?f@@YAXXZ"]


def test_only_file_backed_text_is_searched(lab):
    lab.image({}, virtual_size=0x1000, suffix=BODY)
    assert lab.scan()["bodies"][0]["status"] == "no-hit"


def test_nonzero_rel32_addend_is_explicit_and_no_pin(lab):
    compiled, retail, relocs = lab.call(addend=3)
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail})
    report = lab.scan()
    call = report["bodies"][0]["hits"][0]["callees"][0]
    assert (call["encoded_rva"], call["rva"], call["addend"]) == (0x1403, 0x1400, 3)
    assert report["possible_pins"] == []
    assert report["refused_pins"][0]["reasons"] == ["nonzero-relocation-addend"]


def test_conflicting_call_sites_do_not_emit_pin(lab):
    compiled, retail, relocs = lab.call()
    other = bytes([0x53]) + compiled[1:]
    other_retail = bytearray(bytes([0x53]) + retail[1:])
    offset = relocs[0][0]
    struct.pack_into("<i", other_retail, offset, 0x1440 - (0x1180 + offset + 4))
    lab.object([("?f@@YAXXZ", compiled, relocs),
                ("?g@@YAXXZ", other, [(offset, pb.REL32, "?callee@@YAXXZ")])])
    lab.image({0x1080: retail, 0x1180: other_retail})
    report = lab.scan()
    assert report["possible_pins"] == []
    assert "conflicting-call-sites" in report["refused_pins"][0]["reasons"]


def test_object_replaced_during_enumeration_is_refused(lab, monkeypatch):
    original = pb.locate.object_functions
    def changed(path):
        yield from original(path)
        path.write_bytes(path.read_bytes() + b"replaced")
    monkeypatch.setattr(pb.locate, "object_functions", changed)
    with pytest.raises(ValueError, match="object changed"):
        lab.scan()


def test_weak_mask_cannot_be_placement(lab):
    lab.object([("?f@@YAXXZ", b"\xe8\0\0\0\0" * 5,
                 [(1 + i * 5, pb.REL32, "?callee@@YAXXZ") for i in range(5)])])
    entry = lab.scan()["bodies"][0]
    assert entry["status"] == "weak-pattern"
    assert entry["candidate_rva"] is None


def test_unknown_relocation_is_visible_not_silently_masked(lab):
    lab.object([("?f@@YAXXZ", BODY, [(1, 0x9999, "_data")])])
    entry = lab.scan()["bodies"][0]
    assert entry["status"] == "unsupported-body"
    assert "0x9999" in entry["reason"]


def test_small_row_inside_candidate_is_reported_as_overlap(lab):
    lab.ledgers([row("?interior@@YAXXZ", 0x1084, size=2)])
    entry = lab.scan()["bodies"][0]
    assert "overlapping-extent" in entry["blocked_by"]
    assert entry["hits"][0]["overlapping_rows"][0]["rva"] == 0x1084


def test_sparse_pin_notes_are_normalized_before_owner_check(lab):
    compiled, retail, relocs = lab.call()
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail})
    lab.symbols.write_bytes(b"name,address,notes\r\n?other@@YAXXZ,0x1400\r\n")
    report = lab.scan()
    assert report["possible_pins"] == []
    assert report["refused_pins"][0]["other_identities"] == ["?other@@YAXXZ"]


def test_compatibility_pin_is_not_another_real_identity(lab):
    compiled, retail, relocs = lab.call()
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail})
    lab.ledgers(pins=[dict(name="?b_00001400@@YAXXZ", address="0x1400", notes="compat")])
    assert lab.scan()["possible_pins"][0]["rva"] == 0x1400


def test_abi_view_in_comma_overflow_does_not_claim_identity(lab):
    compiled, retail, relocs = lab.call()
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail})
    lab.symbols.write_bytes(b"name,address,notes\r\n?other@@YAXXZ,0x1400,note,extra;abi-view=some-owner\r\n")
    assert lab.scan()["possible_pins"][0]["rva"] == 0x1400


def test_pin_at_proven_ilt_slot_checks_identity_at_body(lab):
    compiled, retail, relocs = lab.call(target=0x1005)
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    thunk = b"\xe9" + struct.pack("<i", 0x1400 - 0x100A)
    lab.image({0x1005: thunk, 0x1080: retail})
    lab.ledgers([row("?owner@@YAXXZ", 0x1400)])
    report = lab.scan()
    assert report["possible_pins"] == []
    assert report["refused_pins"][0]["other_identities"] == ["?owner@@YAXXZ"]


def test_callee_body_and_ilt_slot_agree_without_subtracting_va(lab):
    compiled, retail, relocs = lab.call(target=0x1005)
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    thunk = b"\xe9" + struct.pack("<i", 0x1400 - 0x100A)
    lab.image({0x1005: thunk, 0x1080: retail}, base=0x63000000)
    lab.ledgers([row("?callee@@YAXXZ", 0x1400)])
    hit = lab.scan()["bodies"][0]["hits"][0]
    assert hit["matched_callees"][0]["rva"] == 0x1005
    assert not hit["conflicting_callees"]


def test_pin_into_existing_body_is_withheld(lab):
    compiled, retail, relocs = lab.call(target=0x1402)
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail})
    lab.ledgers([row("?owner@@YAXXZ", 0x1400, size=10)])
    report = lab.scan()
    assert not report["possible_pins"]
    assert "interior-of-existing-body" in report["refused_pins"][0]["reasons"]


def test_scanned_generated_source_cannot_supply_pin_evidence(lab):
    compiled, retail, relocs = lab.call()
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: retail})
    source = lab.path / "game/gen_small/Unit.cpp"
    source.parent.mkdir(parents=True)
    source.write_text("// generated dump\n")
    report = pb.discover([(source, lab.obj)], denylist=lab.denylist)
    assert "non-identity-source" in report["bodies"][0]["blocked_by"]
    assert report["possible_pins"] == []


def test_mismatching_discovered_callee_cannot_supply_further_pins(lab):
    compiled, retail, relocs = lab.call(target=0x1440)
    lab.object([("?f@@YAXXZ", compiled, relocs), ("?callee@@YAXXZ", BODY, [])])
    lab.image({0x1080: retail, 0x1400: BODY})
    report = lab.scan()
    assert "conflicting-candidate-callee" in report["bodies"][0]["blocked_by"]
    assert report["bodies"][0]["hits"][0]["conflicting_callees"][0]["agreement"] == "conflicting-candidate"
    assert report["possible_pins"] == []


def test_no_fold_pin_to_another_emitted_body(lab):
    compiled, retail, relocs = lab.call()
    lab.object([("?f@@YAXXZ", compiled, relocs), ("?other@@YAXXZ", BODY, [])])
    lab.image({0x1080: retail, 0x1400: BODY})
    report = lab.scan()
    assert report["possible_pins"] == []
    assert report["refused_pins"][0]["other_candidate_names"] == ["?other@@YAXXZ"]
    assert "other-candidate-name" in report["refused_pins"][0]["reasons"]


def test_no_search_in_following_coff_function_span(lab):
    # locate owns extents within executable sections; keep that behavior when
    # there are several symbols in one ordinary (non-COMDAT) .text section.
    obj = bytearray(coff([(["?f@@YAXXZ", "?g@@YAXXZ"], BODY + b"\x90" * 20, [])]))
    sym_pointer = struct.unpack_from("<I", obj, 8)[0]
    struct.pack_into("<I", obj, sym_pointer + 18 + 8, len(BODY))
    lab.obj.write_bytes(obj)
    lab.image({0x1080: BODY + b"\x90" * 20})
    first, second = lab.scan()["bodies"]
    assert (first["size"], first["candidate_rva"]) == (len(BODY), 0x1080)
    assert (second["size"], second["candidate_rva"]) == (20, 0x1080 + len(BODY))


def test_missing_object_refuses_without_compilation(lab, capsys):
    with pytest.raises(SystemExit) as exc:
        pb.main(["--object", "game/Unit.cpp", str(lab.path / "missing.obj")])
    assert exc.value.code == 2
    assert "missing.obj" in capsys.readouterr().err


def test_changed_object_after_scan_discards_the_entire_report(lab, monkeypatch):
    original = pb.Evidence
    def evidence_then_changed(*args):
        result = original(*args)
        lab.obj.write_bytes(lab.obj.read_bytes() + b"replacement")
        return result
    monkeypatch.setattr(pb, "Evidence", evidence_then_changed)
    with pytest.raises(ValueError, match="object changed"):
        lab.scan()


def test_naked_cpp_row_cannot_filter_candidates_or_harvest_pins(lab):
    compiled, first, relocs = lab.call(target=0x1400)
    _, second, _ = lab.call(rva=0x1180, target=0x1440)
    lab.object([("?f@@YAXXZ", compiled, relocs)])
    lab.image({0x1080: first, 0x1180: second})
    (lab.source.parent / "Real.cpp").write_text("__declspec(naked) void callee() { __asm { ret } }\n")
    lab.ledgers([row("?callee@@YAXXZ", 0x1400)])
    assert lab.scan()["bodies"][0]["candidate_rva"] is None
    lab.source.write_text("__declspec(naked) void f() { __asm { ret } }\n")
    lab.image({0x1080: first})
    report = lab.scan()
    assert "non-identity-source" in report["bodies"][0]["blocked_by"]
    assert report["possible_pins"] == []
