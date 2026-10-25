"""Synthetic cross-image discovery: real PE headers, no compiler or ledger writes.

Ports the applicable BFME2 bfme1_sweep mask/placement/near cases; landing,
fold pinning and donor-specific library policy intentionally have no port.
"""
import csv
import json
from pathlib import Path
import struct
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bfme2_retail_sweep as sweep

NAME = "?donor@@YAHXZ"
BODY = bytes.fromhex("558bec83ec105356578bf18b45088b4d0c33c05f5e5bc9c3")
FIELDS = ["name", "target_rva", "target_size", "source", "status", "notes"]


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def row(name=NAME, rva=0x1080, body=BODY, source="Code/GameEngine/Donor.cpp", **kwargs):
    return dict(name=name, target_rva=f"0x{rva:08X}", target_size=str(len(body)),
                source=source, status="matched", notes="", **kwargs)


def pe(text, *, base=0x400000, rdata=b"hello\0", image_size=0x100000):
    data = bytearray(0x400)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, 0x84, 0x14C, 2, 0, 0, 0, 0xE0, 0)
    struct.pack_into("<H", data, 0x98, 0x10B)
    struct.pack_into("<I", data, 0x98 + 28, base)
    struct.pack_into("<I", data, 0x98 + 56, image_size)
    for i, (name, rva, payload, raw) in enumerate([
            (b".text", 0x1000, text, 0x400), (b".rdata", 0x2000, rdata, 0x400 + len(text))]):
        struct.pack_into("<8sIIIIIIHHI", data, 0x178 + i * 40, name, len(payload),
                         rva, len(payload), raw, 0, 0, 0, 0, 0x60000020)
    return bytes(data) + text + rdata


class Lab:
    def __init__(self, path, monkeypatch):
        self.root = path / "target"
        self.donor = path / "donor"
        self.donor_exe = self.donor / "baselines/bfme2/workshop-vanilla-1.06/files/game.dat"
        self.exe = self.root / "retail.exe"
        self.functions = self.root / "targets/game/reverse/functions.csv"
        self.symbols = self.functions.with_name("symbols.csv")
        self.donor_functions = self.donor / "reverse/functions.csv"
        self.donor_symbols = self.donor_functions.with_name("symbols.csv")
        self.source = "Code/GameEngine/Donor.cpp"
        self.source_text = "int donor() { return 7; }\n"
        self.set_sources()
        monkeypatch.setattr(sweep.build, "ROOT", self.root)
        monkeypatch.setattr(sweep.build, "EXE", self.exe)
        monkeypatch.setattr(sweep.build, "FUNCTIONS", self.functions)
        monkeypatch.setattr(sweep.build, "SYMBOLS", self.symbols)
        monkeypatch.setattr(sweep, "OUT", self.root / "build/bfme2_retail_sweep")
        monkeypatch.setattr(sweep.eligibility, "_lift_keys", lambda: frozenset())
        monkeypatch.setattr(sweep.eligibility, "no_ground_truth", lambda rva: False)
        monkeypatch.setattr(sweep.eligibility, "latest_verdicts", lambda: {})
        monkeypatch.setattr(sweep.placement.pin_consistency, "load_routes", lambda: set())
        def forbidden(*args, **kwargs):
            pytest.fail("discovery called a compiler/writer/whole-ledger loader")
        monkeypatch.setattr(sweep, "donor_revision", lambda root: "a" * 40)
        monkeypatch.setattr(sweep.subprocess, "run", forbidden)
        monkeypatch.setattr(sweep.build, "compile_source", forbidden)
        monkeypatch.setattr(sweep.build, "load_all_function_rows", forbidden)
        monkeypatch.setattr(sweep.eligibility, "load_rows", forbidden)
        self.ledgers()
        self.images()

    def set_sources(self):
        for root, source in [(self.donor, self.source), (self.root, "game/Real.cpp")]:
            path = root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self.source_text)

    def ledgers(self, donors=None, targets=(), donor_pins=(), target_pins=()):
        write_csv(self.donor_functions, FIELDS, donors if donors is not None else [row()])
        write_csv(self.functions, FIELDS, targets)
        for path, rows in [(self.donor_symbols, donor_pins), (self.symbols, target_pins)]:
            write_csv(path, ["name", "address", "notes"], rows)

    def images(self, donors=None, targets=None, *, donor_base=0x400000, target_base=0x900000,
               donor_string=b"hello\0", target_string=b"hello\0"):
        for path, bodies, base, string in [
                (self.donor_exe, donors if donors is not None else {0x1080: BODY}, donor_base, donor_string),
                (self.exe, targets if targets is not None else {0x1180: BODY}, target_base, target_string)]:
            text = bytearray(b"\xcc" * 0x800)
            for rva, body in bodies.items():
                text[rva - 0x1000:rva - 0x1000 + len(body)] = body
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(pe(bytes(text), base=base, rdata=string))

    def scan(self, **kwargs):
        return sweep.scan(self.donor, **kwargs)


@pytest.fixture
def lab(tmp_path, monkeypatch):
    return Lab(tmp_path, monkeypatch)


@pytest.mark.parametrize("targets,status,count", [({0x1180: BODY}, "unique", 1),
                                                  ({0x1180: BODY, 0x1280: BODY}, "multiple", 2),
                                                  ({}, "none", 0)])
def test_placement_unique_multiple_none(lab, targets, status, count):
    lab.images(targets=targets)
    record = lab.scan()["records"][0]
    assert record["placement"] == status
    assert len(record["hits"]) == count
    assert all(h["tier"] == "T2" for h in record["hits"])


def pointer_body(base, rva, callee):
    return b"\xb8" + struct.pack("<I", base + 0x2000) + b"\xe8" + struct.pack("<i", callee - rva - 10) + BODY


def test_relocations_rvas_and_both_image_bases(lab):
    a = pointer_body(0x400000, 0x1080, 0x1400)
    b = pointer_body(0x900000, 0x1180, 0x1500)
    lab.ledgers(donors=[row(body=a)])
    lab.images(donors={0x1080: a}, targets={0x1180: b})
    report = lab.scan()
    assert (report["donor_image_base"], report["target_image_base"]) == (0x400000, 0x900000)
    h = report["records"][0]["hits"][0]
    assert h["rva"] == 0x1180 and h["exact"]
    assert h["dir32"][0]["donor_rva"] == h["dir32"][0]["target_rva"] == 0x2000
    assert h["strings"][0]["agreement"] == "matched"
    assert h["calls"][0]["target_rva"] == 0x1500
    assert h["tier"] == "T2", "placement, strings and unknown calls cannot prove identity"


@pytest.mark.parametrize("kind", ["absolute", "call", "opcode"])
def test_relocation_requires_target_shape_and_opcodes_agree(lab, kind):
    a = pointer_body(0x400000, 0x1080, 0x1400)
    b = bytearray(pointer_body(0x900000, 0x1180, 0x1500))
    if kind == "absolute":
        struct.pack_into("<I", b, 1, 0x7FFFFFFF)
    elif kind == "call":
        struct.pack_into("<i", b, 6, 0x700000)
    else:
        b[10] = 0x40
    lab.ledgers(donors=[row(body=a)])
    lab.images(donors={0x1080: a}, targets={0x1180: bytes(b)})
    record = lab.scan()["records"][0]
    assert record["placement"] == "none"
    assert not any(h["exact"] for h in record["hits"])


def test_e8_inside_a_pointer_does_not_steal_dir32(lab):
    blob = b"\xc7\x00\xb8\xe8\x40\x00" + BODY
    lab.images(donors={0x1080: blob})
    assert sweep.volatile_fields(blob, sweep.Image(lab.donor_exe), 0x1080) == {2: "dir32"}


def test_call_displacement_cannot_open_another_rel32(lab):
    blob = b"\xe8" + struct.pack("<i", 0xE8) + BODY
    lab.images(donors={0x1080: blob})
    assert sweep.volatile_fields(blob, sweep.Image(lab.donor_exe), 0x1080) == {1: "rel32"}


def test_internal_branch_displacement_stays_fixed(lab):
    blob = b"\xe9\x01\0\0\0" + BODY
    lab.images(donors={0x1080: blob})
    assert sweep.volatile_fields(blob, sweep.Image(lab.donor_exe), 0x1080) == {}


def test_t1_requires_independent_clean_target_identity(lab):
    lab.ledgers(targets=[row(rva=0x1180, source="game/Real.cpp")])
    h = lab.scan()["records"][0]["hits"][0]
    assert h["tier"] == "T1"
    assert h["identity_evidence"][0]["kind"] == "same-decorated-symbol"
    assert h["work_status"] == "closed"
    assert h["suggested_model"] == "Luna Medium"


def test_same_name_pin_is_only_a_lead(lab):
    lab.ledgers(target_pins=[dict(name=NAME, address="0x00001180", notes="pinharvest")])
    assert lab.scan()["records"][0]["hits"][0]["tier"] == "T2"


@pytest.mark.parametrize("via_pin", [False, True])
def test_t3_multiname_donor_is_never_t1(lab, via_pin):
    other = "?rival@@YAHXZ"
    donors = [row()] if via_pin else [row(), row(name=other)]
    pins = [dict(name=other, address="0x00001080", notes="ICF lead")] if via_pin else []
    lab.ledgers(donors=donors, donor_pins=pins, targets=[row(rva=0x1180, source="game/Real.cpp")])
    report = lab.scan()
    assert all(r["donor_names"] == sorted([NAME, other]) for r in report["records"])
    assert all(h["tier"] == "T3" for r in report["records"] for h in r["hits"])


def test_t4_near_match_records_differences_even_in_longest_anchor(lab):
    changed = bytearray(BODY)
    changed[8] = 0x56
    lab.images(targets={0x1180: bytes(changed)})
    r = lab.scan()["records"][0]
    h = r["hits"][0]
    assert r["placement"] == "none" and not h["exact"]
    assert h["tier"] == "T4" and 0.9 <= h["similarity"] < 1
    assert h["diff_summary"] == [dict(offset=8, donor=0x57, target=0x56)]


@pytest.mark.parametrize("a,b,kind", [
    (b"\x8b\x41\x20", b"\x8b\x41\x24", "member-displacement"),
    (b"\xc2\x04\x00", b"\xc2\x08\x00", "stack-cleanup")])
def test_t5_layout_and_calling_convention_evidence(lab, a, b, kind):
    left, right = BODY + a, BODY + b
    lab.ledgers(donors=[row(body=left)])
    lab.images(donors={0x1080: left}, targets={0x1180: right})
    h = lab.scan()["records"][0]["hits"][0]
    assert h["tier"] == "T5"
    assert h["layout_disagreement"][0]["kind"] == kind


def test_straddling_dir32_cannot_hide_a_layout_change(lab):
    a = b"\x81\xc1\x20\x01\x00\x00" + BODY
    b = b"\x81\xc1\x7c\x01\x00\x00" + BODY
    lab.ledgers(donors=[row(body=a)])
    lab.images(donors={0x1080: a}, targets={0x1180: b})
    # Make the unaligned dword 0x0120C181 fall within the donor image.
    raw = bytearray(lab.donor_exe.read_bytes())
    struct.pack_into("<I", raw, 0x98 + 56, 0x1000000)
    lab.donor_exe.write_bytes(raw)
    assert sweep.volatile_fields(a, sweep.Image(lab.donor_exe), 0x1080) == {}
    h = lab.scan()["records"][0]["hits"][0]
    assert h["tier"] == "T4" and h["diff_count"] == 1


def test_callee_ledger_agreement_and_conflict(lab):
    a, b = pointer_body(0x400000, 0x1080, 0x1400), pointer_body(0x900000, 0x1180, 0x1500)
    callee = "?callee@@YAXXZ"
    for address, tier, agreement in [(0x1500, "T2", "matched"), (0x1600, "T2", "conflict")]:
        lab.ledgers(donors=[row(body=a), row(name=callee, rva=0x1400)],
                    targets=[row(name=callee, rva=address, source="game/Real.cpp")])
        lab.images(donors={0x1080: a, 0x1400: BODY}, targets={0x1180: b, address: BODY})
        h = lab.scan()["records"][0]["hits"][0]
        assert h["calls"][0]["agreement"] == agreement
        assert h["tier"] == tier
        if agreement == "conflict":
            assert any(b.startswith("callee-conflict") for b in h["blocked_by"])


def test_string_conflict_is_not_a_ready_exact_donor(lab):
    a, b = pointer_body(0x400000, 0x1080, 0x1400), pointer_body(0x900000, 0x1180, 0x1500)
    lab.ledgers(donors=[row(body=a)])
    lab.images(donors={0x1080: a}, targets={0x1180: b}, target_string=b"different\0")
    h = lab.scan()["records"][0]["hits"][0]
    assert h["exact"] and h["tier"] == "T4"
    assert h["strings"][0]["agreement"] == "conflict"


@pytest.mark.parametrize("source,notes,status,text", [
    ("Code/gen_small/x.cpp", "", "matched", "int x() {return 1;}"),
    ("Code/masm_dumps/x.asm", "", "matched", "ret"),
    ("Code/GameEngine/Donor.cpp", "gen-dump", "matched", "int x(){}"),
    ("Code/GameEngine/Donor.cpp", "", "pending", "int x(){}"),
    ("Code/GameEngine/Donor.cpp", "", "matched", "__declspec(naked) void x(){}"),
    ("Code/GameEngine/Donor.cpp", "", "matched", "void x(){__emit 0xc3;}"),
    ("Code/GameEngine/Donor.cpp", "", "matched", "void x(){__asm {ret}}")])
def test_gen_dump_unmatched_and_lift_donors_excluded(lab, source, notes, status, text):
    path = lab.donor / source
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    r = row(source=source)
    r.update(notes=notes, status=status)
    lab.ledgers(donors=[r])
    assert lab.scan()["records"] == []


def test_vendored_note_is_preserved_as_a_provenance_lead(lab):
    r = row()
    r["notes"] = "vendored=zlib-1.1.4"
    lab.ledgers(donors=[r])
    report = lab.scan()
    assert report["records"][0]["donor_notes"] == r["notes"]
    assert "BFME1 library provenance" in sweep.packet_text(report, report["records"][0], report["records"][0]["hits"][0])


def test_eligibility_is_consulted_for_retirement_dump_and_closed_source(lab, monkeypatch):
    calls = []
    monkeypatch.setattr(sweep.eligibility, "retired", lambda rva, latest: calls.append(("retired", rva)) or False)
    monkeypatch.setattr(sweep.eligibility, "landed_at", lambda rvas, **kw: calls.append(("landed", rvas)) or set())
    monkeypatch.setattr(sweep.eligibility, "open_dumps", lambda **kw: calls.append(("dumps", kw["rows"])) or kw["rows"])
    lab.ledgers(targets=[row(rva=0x1180, source="game/gen_asm/x.asm")])
    h = lab.scan()["records"][0]["hits"][0]
    assert h["work_status"] == "open"
    assert {c[0] for c in calls} == {"retired", "landed", "dumps"}
    assert h["tier"] == "T2", "a generated row with the same name cannot prove identity"
    monkeypatch.setattr(sweep.eligibility, "retired", lambda *a: True)
    assert lab.scan()["records"][0]["hits"][0]["work_status"] == "retired"


def test_full_donor_extent_including_trailing_int3_is_required(lab):
    a = BODY + b"\xcc\xcc"
    lab.ledgers(donors=[row(body=a)])
    lab.images(donors={0x1080: a}, targets={0x1180: BODY + b"\x90\x90"})
    assert lab.scan()["records"][0]["placement"] == "none"


def test_weak_pattern_never_claims_unique(lab):
    a, b = pointer_body(0x400000, 0x1080, 0x1400)[:10], pointer_body(0x900000, 0x1180, 0x1500)[:10]
    lab.ledgers(donors=[row(body=a)])
    lab.images(donors={0x1080: a}, targets={0x1180: b})
    r = lab.scan(minimum=1)["records"][0]
    assert r["placement"] == "none" and r["search_reason"] == "weak-pattern"


def test_no_writes_to_ledgers_or_sources_for_any_subcommand(lab, capsys):
    paths = [lab.functions, lab.symbols, lab.donor_functions, lab.donor_symbols,
             lab.donor / lab.source, lab.root / "game/Real.cpp", lab.exe, lab.donor_exe]
    before = {p: p.read_bytes() for p in paths}
    assert sweep.main(["scan", "--donor-root", str(lab.donor)]) == 0
    assert sweep.main(["ranked", "--all", "--json"]) == 0
    assert sweep.main(["near", "--all"]) == 0
    assert sweep.main(["show", NAME]) == 0
    assert sweep.main(["packets", "--all"]) == 0
    assert {p: p.read_bytes() for p in paths} == before
    output = capsys.readouterr().out
    assert "tools/add_match.py" in output and "tools/callees.py" in output
    assert "tools/pin_consistency.py --check" in output
    assert lab.source_text in output
    assert list((sweep.OUT / "packets").glob("*.txt"))


@pytest.mark.parametrize("command", ["scan", "packets"])
def test_output_cannot_overwrite_ledgers(lab, command):
    before = lab.functions.read_bytes()
    assert sweep.main(["scan", "--donor-root", str(lab.donor)]) == 0
    args = [command, "--output", str(lab.functions)]
    if command == "scan":
        args.extend(["--donor-root", str(lab.donor)])
    assert sweep.main(args) == 1
    assert lab.functions.read_bytes() == before


def test_stale_report_refuses_changed_input(lab):
    assert sweep.main(["scan", "--donor-root", str(lab.donor)]) == 0
    lab.symbols.write_bytes(lab.symbols.read_bytes() + b"?new,0x1100,\r\n")
    assert sweep.main(["ranked"]) == 1


def test_serving_refreshes_eligibility_after_scan(lab, monkeypatch, capsys):
    assert sweep.main(["scan", "--donor-root", str(lab.donor)]) == 0
    monkeypatch.setattr(sweep.eligibility, "retired", lambda *a: True)
    capsys.readouterr()
    assert sweep.main(["ranked", "--json"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert not output["entries"]


def test_symlink_output_cannot_escape_scratch(lab):
    lab.root.mkdir(exist_ok=True)
    sweep.OUT.mkdir(parents=True)
    link = sweep.OUT / "ledger.json"
    link.symlink_to(lab.functions)
    before = lab.functions.read_bytes()
    assert sweep.main(["scan", "--donor-root", str(lab.donor), "--output", str(link)]) == 1
    assert lab.functions.read_bytes() == before


def test_near_never_uses_the_interior_of_a_target_extent(lab):
    changed = bytearray(BODY)
    changed[8] = 0x56
    lab.images(targets={0x1180: bytes(changed)})
    lab.ledgers(targets=[row(rva=0x1170, body=b"\xcc" * (len(BODY) + 0x10), source="game/gen_asm/x.asm")])
    assert lab.scan()["records"][0]["hits"] == []


def test_conflicting_overlaps_are_boundary_review_even_for_a_dump(lab):
    first = row(rva=0x1180, source="game/gen_asm/x.asm")
    other = row(name="?other@@YAXXZ", rva=0x1170, body=b"\xcc" * 0x40, source="game/gen_asm/y.asm")
    lab.ledgers(targets=[first, other])
    assert lab.scan()["records"][0]["hits"][0]["work_status"] == "boundary-review"


def test_ranked_orders_tiers_and_defaults_to_open_candidates(lab):
    lab.ledgers(donors=[row(), row(name="?other@@YAXXZ", rva=0x1280)],
                targets=[row(rva=0x1180, source="game/Real.cpp")])
    lab.images(donors={0x1080: BODY, 0x1280: BODY})
    report = lab.scan()
    assert sweep.ranked(report) == []
    entries = sweep.ranked(report, include_closed=True)
    assert [h["tier"] for _, h in entries] == ["T1", "T2"]


def test_cstring_rejects_binary_short_and_unterminated_payloads(lab):
    for payload in (b"hi\0", b"hello\x01\0", b"hello"):
        lab.images(donor_string=payload)
        assert sweep.Image(lab.donor_exe).cstring(0x402000) is None


def test_exact_search_is_uncapped(lab):
    targets = {0x1000 + 32 * i: BODY for i in range(32)}
    lab.images(targets=targets)
    r = lab.scan(near_cap=1)["records"][0]
    assert r["placement"] == "multiple" and len(r["hits"]) == 32


def test_near_cap_is_recorded_as_incomplete(lab):
    changed = bytearray(BODY)
    changed[8] = 0x56
    lab.images(targets={0x1180: bytes(changed), 0x1280: bytes(changed)})
    r = lab.scan(near_cap=1)["records"][0]
    assert r["near_search_truncated"]
    assert r["placement"] == "none"


def test_ordinary_asm_source_is_excluded(lab):
    r = row(source="Code/GameEngine/lift.asm")
    lab.ledgers(donors=[r])
    assert lab.scan()["records"] == []


@pytest.mark.parametrize("extent", ["0", "-1", "", "unknown"])
def test_donor_without_positive_proven_extent_is_excluded(lab, extent):
    r = row()
    r["target_size"] = extent
    lab.ledgers(donors=[r])
    assert lab.scan()["records"] == []


def test_interval_index_keeps_long_nested_overlaps():
    long = row(rva=0x1000, body=b"x" * 0x200)
    short = row(name="?short@@YAXXZ", rva=0x1080, body=b"x" * 8)
    index = sweep.RowIndex([short, long])
    assert index.overlaps(0x1100, 16) == [long]
    assert index.overlaps(0x1080, 8) == [short, long]
    assert index.overlaps(0x1200, 8) == []


@pytest.mark.parametrize("command", ["land", "apply", "drain"])
def test_no_landing_commands(lab, command):
    with pytest.raises(SystemExit):
        sweep.main([command])
