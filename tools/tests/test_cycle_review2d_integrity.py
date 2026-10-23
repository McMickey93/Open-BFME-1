"""Round-4 independent measurement counterexamples. No compiler or real link.

Only PE loading is replaced: real COFF parsing, relocation checks, datum discovery,
shift verification, closure and the displayed credit series are production code.
The synthetic images are already linked, just like a read-only replay.
"""
import csv
import json
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import body_guard
import link_cycle as lc


BASE = lc.BASE


def symbol(index, name, section, value=0, storage=lc.EXTERNAL):
    s = lc.Sym()
    s.i, s.name, s.sec, s.value, s.cls = index, name, section, value, storage
    return s


def section(size, name, relocs=(), ptr=4):
    s = lc.Sec()
    s.idx, s.name, s.size, s.ptr = 1, name, size, ptr
    s.flags, s.sel, s.relocs = 0, 0, list(relocs)
    return s


class ImageSections(dict):
    @property
    def all(self):
        return [(n, a, z) for n, (a, z) in self.items()]


class Case:
    def __init__(self, tmp_path, monkeypatch):
        self.root = tmp_path
        monkeypatch.setattr(lc, "ROOT", tmp_path)
        self.out = tmp_path / "run"
        self.out.mkdir()
        (self.out / "shft.exe").touch()
        self.I, self.R, self.S = (bytearray(0x6000) for _ in range(3))
        self.secs = ImageSections({".text": (0x1000, 0x1000), ".rdata": (0x3000, 0x1000)})
        self.objs, self.units, self.maplines = lc.Objects([]), [], []
        self.imports = {}
        monkeypatch.setattr(lc, "pe_view", self.pe_view)

    def pe_view(self, path):
        return None, self.S if path.name == "shft.exe" else self.I, self.secs, {}

    def add_object(self, name, obj):
        p = self.root / name
        secs, syms, original = obj
        lc.write_coff(p, [(s.name, 0x60100020 if s.name == ".text" else 0x40300040,
                           original[s.ptr:s.ptr+s.size], 0) for s in secs],
                      [(s.name, s.sec, s.value, s.cls) for s in syms.values()])
        raw = bytearray(p.read_bytes())
        symptr = lc.u32(raw, 8)
        relocations = bytearray()
        for n, sec in enumerate(secs):
            if sec.relocs:
                struct.pack_into("<I", raw, 20+40*n+24, symptr+len(relocations))
                struct.pack_into("<H", raw, 20+40*n+32, len(sec.relocs))
                for reloc in sec.relocs:
                    relocations += struct.pack("<IIH", *reloc)
        raw[symptr:symptr] = relocations
        struct.pack_into("<I", raw, 8, symptr+len(relocations))
        p.write_bytes(raw)
        if p not in self.objs.paths:
            self.objs.paths.append(p)
        self.objs.by_base[name] = p
        self.objs.cache.pop(p, None)
        self.objs.get(p)  # validate and parse the physical COFF used by measurement
        return p

    def mapped(self, name, rva, obj):
        self.maplines.append(f" 0001:{rva:08x} {name} {BASE+rva:08x} {obj}")

    def code(self, name, at, raw, refs=()):
        """refs: (operand offset, target symbol, linked RVA, retail RVA, addend)."""
        raw = bytearray(raw)
        linked, retail, shifted = bytearray(raw), bytearray(raw), bytearray(raw)
        syms, relocs = {0: symbol(0, name, 1)}, []
        for k, (off, target, lt, rt, addend) in enumerate(refs, 1):
            syms[k] = symbol(k, target, 0)
            relocs.append((off, k, lc.DIR32))
            for buf, value in ((raw, addend), (linked, BASE+lt), (retail, BASE+rt),
                               (shifted, lc.SHIFT_BASE+lt)):
                struct.pack_into("<I", buf, off, value & 0xFFFFFFFF)
        for image, data in ((self.I, linked), (self.R, retail), (self.S, shifted)):
            image[at:at+len(raw)] = data
        ob = f"c{len(self.units)}.obj"
        p = self.add_object(ob, ([section(len(raw), ".text", relocs)], syms, b"\0"*4 + raw))
        self.mapped(name, at, ob)
        row = dict(name=name, sym=name, rva=at, size=len(raw), off=0,
                   kind="real", provenance="real", source=f"game/{ob}.cpp")
        self.units.append(dict(id=len(self.units), obj=str(p), sec=1, secname=".text",
                               size=len(raw), head=name, head_cls=lc.EXTERNAL, starts=[at], rows=[row]))

    def data(self, name, lt, rt, linked, retail, size=None, refs=()):
        size = len(linked) if size is None else size
        raw, linked, retail, shifted = map(bytearray, (linked[:size], linked, retail, linked))
        syms, relocs = {0: symbol(0, name, 1)}, []
        for k, (off, target, dest, rdest, addend) in enumerate(refs, 1):
            syms[k] = symbol(k, target, 0)
            relocs.append((off, k, lc.DIR32))
            for buf, value in ((raw, addend), (linked, BASE+dest), (retail, BASE+rdest),
                               (shifted, lc.SHIFT_BASE+dest)):
                struct.pack_into("<I", buf, off, value)
        for image, at, data in ((self.I, lt, linked), (self.S, lt, shifted), (self.R, rt, retail)):
            image[at:at+len(data)] = data
        ob = f"d{len(self.objs.paths)}.obj"
        self.add_object(ob, ([section(size, ".rdata", relocs)], syms, b"\0"*4+raw))
        self.mapped(name, lt, ob)

    def inventory(self, rows):
        p = self.root / "targets/game/reverse/retail_inventory/data_items.csv"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["rva", "size", "section", "class", "detail", "confidence"])
            w.writerows(rows)

    def run(self):
        (self.out / "base.map").write_text("\n".join(self.maplines))
        result = lc.measure(self.out, self.units, [], self.objs, self.R, self.secs, self.imports, {}, True, lc.SHIFT_BASE)
        with (self.out / "link_status.csv").open() as f:
            rows = list(csv.DictReader(f))
        assert result["shift"]["checked"] and result["shift"]["failed"] == {}
        return result, rows

    def without_caller(self):
        saved = self.units
        self.units = [u for u in saved if u["head"] != "_f"]
        try:
            return self.run()[0]["credit_unique_bytes"]
        finally:
            self.units = saved


@pytest.mark.parametrize("evidence", ["missing", "partition"])
@pytest.mark.parametrize("form", ["indexed", "register", "bitstring", "string"])
def test_short_provider_cannot_define_the_retail_array_extent(tmp_path, monkeypatch, evidence, form):
    c = Case(tmp_path, monkeypatch)
    if form == "indexed":
        # int f(unsigned i) { return table[i]; } -- retail accepts i=1.
        raw, slot = b"\x8b\x04\x85" + bytes(4) + b"\xc3", 3
    elif form == "register":
        # mov ecx,offset table; mov eax,[ecx+4]; ret
        raw, slot = b"\xb9" + bytes(4) + b"\x8b\x41\x04\xc3", 1
    elif form == "bitstring":
        # Bit 33 is bit 1 of table[1]: linked 'B' has it, retail 'T' does not.
        raw, slot = b"\xb9\x21\0\0\0\x0f\xa3\x0d" + bytes(4) + b"\x0f\x92\xc0\xc3", 8
    else:
        # mov esi,offset table; mov ecx,2; rep lodsd; ret
        raw, slot = b"\xbe" + bytes(4) + b"\xb9\x02\0\0\0\xf3\xad\xc3", 1
    c.code("_f", 0x1000, raw, [(slot, "_table", 0x3000, 0x3100, 0)])
    c.data("_table", 0x3000, 0x3100, b"GOODBAD!", b"GOODTAIL", size=4)
    if evidence == "partition":
        # An inventory partition at an interior reference has no array
        # ownership/type evidence and must not shrink the array's domain.
        c.inventory([("0x3100", 4, ".rdata", "global", "global", "medium"),
                     ("0x3104", 4, ".rdata", "global", "global", "medium")])
    before, frozen = c.without_caller(), bytes(c.I)
    result, rows = c.run()
    assert bytes(c.I) == frozen
    print(json.dumps(dict(form=form, evidence=evidence, before=before,
                          after=result["credit_unique_bytes"], failures=rows[0]["failures"])))
    assert c.I[0x3004:0x3008] != c.R[0x3104:0x3108]
    assert result["credit_unique_bytes"] == 0, (result["credit_unique_bytes"], rows)


@pytest.mark.parametrize("form", ["direct", "register"])
def test_text_storage_observes_relocated_bytes_not_code_equivalence(tmp_path, monkeypatch, form):
    c = Case(tmp_path, monkeypatch)
    if form == "direct":
        # movzx eax,byte ptr [g+2]; ret
        raw, slot, lt, addend = b"\x0f\xb6\x05"+bytes(4)+b"\xc3", 3, 0x1102, 2
    else:
        # mov ecx,offset g; movzx eax,byte ptr [ecx+2]; ret
        raw, slot, lt, addend = b"\xb9"+bytes(4)+b"\x0f\xb6\x41\x02\xc3", 1, 0x1100, 0
    c.code("_f", 0x1000, raw, [(slot, "_g", lt, lt, addend)])
    c.code("_g", 0x1100, b"\xb8"+bytes(4)+b"\xc3", [(1, "_value", 0x3000, 0x3100, 0)])
    c.data("_value", 0x3000, 0x3100, b"GOOD", b"GOOD")
    known_extent(c)  # Keep the legitimate pointer provider eligible; isolate the raw-byte refusal.
    before, frozen = c.without_caller(), bytes(c.I)
    result, rows = c.run()
    assert bytes(c.I) == frozen
    # f returns 0x30 instead of 0x31. g is legitimate relocated code, but
    # reading its representation is a different proof obligation.
    assert (c.I[0x1102], c.R[0x1102]) == (0x30, 0x31)
    print(json.dumps(dict(form=form, before=before, after=result["credit_unique_bytes"],
                          actual=0x30, expected=0x31, failures=rows[0]["failures"])))
    assert before == result["credit_unique_bytes"] == 6
    assert "code-storage-raw-relocation:_g" in rows[0]["failures"]
    assert rows[0]["closed_strict"] == "0", (result["credit_unique_bytes"], rows)


def test_data_storage_reading_one_byte_of_a_pointer_must_match_that_byte(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    # unsigned char f() { return ((unsigned char *)&pointer)[1]; }
    c.code("_f", 0x1000, b"\x0f\xb6\x05"+bytes(4)+b"\xc3",
           [(3, "_pointer", 0x3201, 0x3301, 1)])
    c.data("_pointer", 0x3200, 0x3300, bytes(4), bytes(4),
           refs=[(0, "_value", 0x3000, 0x3100, 0)])
    c.data("_value", 0x3000, 0x3100, b"GOOD", b"GOOD")
    known_extent(c)  # Keep the legitimate pointer provider eligible; isolate the raw-byte refusal.
    c.inventory([("0x3300", 4, ".rdata", "global", "pointer", "high"),
                 ("0x3100", 4, ".rdata", "global", "scalar", "high")])
    before, frozen = c.without_caller(), bytes(c.I)
    result, rows = c.run()
    assert bytes(c.I) == frozen
    assert (c.I[0x3201], c.R[0x3301]) == (0x30, 0x31)
    print(json.dumps(dict(before=before, after=result["credit_unique_bytes"],
                          actual=0x30, expected=0x31, failures=rows[0]["failures"])))
    assert result["credit_unique_bytes"] == 0, rows

    assert "data-raw-relocation:_pointer" in rows[0]["failures"]


@pytest.mark.parametrize("token_retail", [0x3100, 0x3104])
def test_pointer_derived_index_can_differ_inside_a_fully_verified_array(tmp_path, monkeypatch, token_retail):
    c = Case(tmp_path, monkeypatch)
    # return table[(unsigned)&token & 255];  Both indices are within the same
    # complete 256-byte array. No pointer arithmetic escapes either datum.
    # The index register carries a number derived from a DIFFERENT relocation.
    raw = b"\xb8"+bytes(4)+b"\x25\xff\0\0\0\x0f\xb6\x80"+bytes(4)+b"\xc3"
    c.code("_f", 0x1000, raw, [(1, "_token", 0x3000, token_retail, 0),
                              (13, "_table", 0x3200, 0x3400, 0)])
    c.data("_token", 0x3000, token_retail, b"GOOD", b"GOOD")
    c.data("_table", 0x3200, 0x3400, bytes(range(256)), bytes(range(256)))
    # Independent full extents are present. This counterexample does not rely
    # on the missing/short inventory evidence of the first finding.
    p = c.root / "targets/game/reverse/data_rows.csv"
    p.parent.mkdir(parents=True)
    p.write_text("name,address,address_kind,size,section,source,status,evidence,model\n"
                 f"_token,{token_retail:#x},rva,4,.rdata,game/token.cpp,matched,complete token,review\n"
                 "_table,0x3400,rva,256,.rdata,game/table.cpp,matched,complete array,review\n")
    before, frozen = c.without_caller(), bytes(c.I)
    result, rows = c.run()
    assert bytes(c.I) == frozen
    li = lc.u32(c.I, 0x1001) & 255
    ri = lc.u32(c.R, 0x1001) & 255
    assert 0 <= li < 256 and 0 <= ri < 256
    assert (c.I[0x3200+li], c.R[0x3400+ri]) == (0, token_retail & 255)
    print(json.dumps(dict(before=before, after=result["credit_unique_bytes"],
                          linked_index=li, retail_index=ri, failures=rows[0]["failures"])))
    # Final owner decision: no numeric address observations, even when
    # the particular low bits happen to agree in this recording.
    assert result["credit_unique_bytes"] == 0, rows
    assert "address-numeric-use:_token" in rows[0]["failures"]


def test_register_carried_text_address_requires_full_memory_coverage(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    # mov eax,offset g; fld qword ptr [eax]; ret -- the direct fld [g]
    # version is rejected by the round-3 fix, but this spelling bypasses it.
    c.code("_f", 0x1000, b"\xb8"+bytes(4)+b"\xdd\x00\xc3", [(1, "_g", 0x1100, 0x1100, 0)])
    c.code("_g", 0x1100, b"\xc3")
    c.I[0x1101:0x1108] = c.S[0x1101:0x1108] = b"\x02" * 7
    c.R[0x1101:0x1108] = b"\x01" * 7
    before, frozen = c.without_caller(), bytes(c.I)
    result, rows = c.run()
    assert bytes(c.I) == frozen
    print(json.dumps(dict(before=before, after=result["credit_unique_bytes"],
                          failures=rows[0]["failures"], actual=c.I[0x1100:0x1108].hex(),
                          expected=c.R[0x1100:0x1108].hex())))
    assert rows[0]["closed_strict"] == "0", rows


@pytest.mark.parametrize("name", ["?IsLocked@RegistryClass@@0_NA", "?m_zoomToValid@ScreenMotionBlurFilter@@1_NA",
                                  "?is9x@?1??isWindows9x@@YA_NXZ@4_NA", "_flag"])
def test_known_byte_access_is_not_expanded_to_a_coarse_inventory_partition(tmp_path, monkeypatch, name):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\x0f\xb6\x05"+bytes(4)+b"\xc3", [(3, name, 0x3000, 0x3100, 0)])
    c.data(name, 0x3000, 0x3100, b"\1", b"\1")
    c.inventory([("0x3100", 4, ".rdata", "global", "global", "medium")])
    result, rows = c.run()
    # The only memory use is a fixed one-byte access, fully verified. An
    # inventory partition supplies neither sizeof nor three more live bytes.
    assert result["credit_unique_bytes"] == 8, rows


def test_static_string_padding_allowed_by_bfme1_is_not_a_dependency(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\xb8"+bytes(4)+b"\xc3", [(1, "$SG1", 0x3000, 0x3100, 0)])
    # A compiler $SG literal is static in its caller's own object, never an
    # external symbol supplied by another TU.
    p = Path(c.units[0]["obj"])
    o = c.objs.get(p)
    code = o[2][o[0][0].ptr:o[0][0].ptr+6]
    c.add_object(p.name, ([section(6, ".text", [(1, 1, lc.DIR32)]),
                           section(4, ".rdata", ptr=10)],
                          {0: symbol(0, "_f", 1), 1: symbol(1, "$SG1", 2, storage=lc.STATIC)},
                          b"\0"*4+code+b"ok\0\0"))
    c.I[0x3000:0x3004] = c.S[0x3000:0x3004] = b"ok\0\0"
    c.R[0x3100:0x3104] = b"ok\0X"
    # Run the actual BFME1 rule, not a reimplementation of its exception.
    info = {"data": b"\0"*4+b"ok\0\0", "sections": [dict(characteristics=0x40,
            raw_pointer=4, raw_size=4, reloc_count=0, reloc_pointer=0)],
            "symbols": [dict(name="$SG1", section=1, storage=3, value=0, aux=0)]}
    monkeypatch.setattr(body_guard, "_retail", lambda at, size: bytes(c.R[at:at+size]))
    assert body_guard._static_content(info, info["symbols"][0], BASE+0x3100, 0) == ("ok", "")
    result, rows = c.run()
    assert result["credit_unique_bytes"] == 6, rows


def test_full_known_array_detects_a_bad_tail(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\x8b\x04\x85"+bytes(4)+b"\xc3", [(3, "_table", 0x3000, 0x3100, 0)])
    c.data("_table", 0x3000, 0x3100, b"GOODBAD!", b"GOODTAIL")
    c.inventory([("0x3100", 8, ".rdata", "global", "array", "high")])
    result, rows = c.run()
    assert result["credit_unique_bytes"] == 0
    assert "data-content:_table" in rows[0]["failures"]


def test_equal_bounded_array_remains_eligible(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\x8b\x04\x85"+bytes(4)+b"\xc3", [(3, "_table", 0x3000, 0x3100, 0)])
    c.data("_table", 0x3000, 0x3100, b"GOODTAIL", b"GOODTAIL")
    c.inventory([("0x3100", 8, ".rdata", "global", "array", "high")])
    # Owner decision: even a correct inventory partition proves no sizeof.
    result, _ = c.run()
    assert result["credit_unique_bytes"] == 0
    ledger = c.root / "targets/game/reverse/data_rows.csv"
    ledger.write_text("name,address,address_kind,size,source,status\n"
                      "_table,0x3100,rva,8,game/table.cpp,matched\n")
    result, _ = c.run()
    assert result["credit_unique_bytes"] == 8


def known_extent(c, name="_value", address=0x3100, size=4):
    p = c.root / "targets/game/reverse/data_rows.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("name,address,address_kind,size,source,status\n"
                 f"{name},{address:#x},rva,{size},game/data.cpp,matched\n")


@pytest.mark.parametrize("operation", [b"\x25\xff\0\0\0", b"\x0d\x01\0\0\0",
                                       b"\x35\x01\0\0\0", b"\xc1\xe8\x01",
                                       b"\x3d\x01\0\0\0", b"\x69\xc0\x03\0\0\0",
                                       b"\x88\x04\x24", b"\x66\xb8\0\0", b"\x89\xc1\xb8\0\0\0\0\xf3\xad"])
def test_numeric_address_uses_refuse_even_with_independent_extent(tmp_path, monkeypatch, operation):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\xb8"+bytes(4)+operation+b"\xc3",
           [(1, "_value", 0x3000, 0x3100, 0)])
    c.data("_value", 0x3000, 0x3100, b"GOOD", b"GOOD")
    known_extent(c)
    result, rows = c.run()
    assert result["credit_unique_bytes"] == 0
    assert "address-numeric-use:_value" in rows[0]["failures"]


def test_pointer_loaded_from_a_relocated_slot_cannot_be_used_numerically(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\xa1"+bytes(4)+b"\x25\xff\0\0\0\xc3",
           [(1, "_pointer", 0x3200, 0x3300, 0)])
    c.data("_pointer", 0x3200, 0x3300, bytes(4), bytes(4),
           refs=[(0, "_value", 0x3000, 0x3100, 0)])
    c.data("_value", 0x3000, 0x3100, b"GOOD", b"GOOD")
    known_extent(c)
    result, rows = c.run()
    assert result["credit_unique_bytes"] == 0
    assert "address-numeric-use:_pointer" in rows[0]["failures"]


@pytest.mark.parametrize("copy", [b"\x89\xc1\x8b\x01", b"\x89\xc1\xb8\0\0\0\0\x8b\x01", b"\x50\x59\x8b\x01",
                                   b"\x89\x04\x24\x8b\x0c\x24\x8b\x01"])
def test_ordinary_register_and_stack_pointer_copies_keep_fixed_access_credit(tmp_path, monkeypatch, copy):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\xb8"+bytes(4)+copy+b"\xc3",
           [(1, "_value", 0x3000, 0x3100, 0)])
    c.data("_value", 0x3000, 0x3100, b"GOOD", b"GOOD")
    known_extent(c)
    result, rows = c.run()
    assert rows[0]["closed_strict"] == "1", rows
    assert result["credit_unique_bytes"] == 6 + len(copy)


def test_push_pop_does_not_erase_numeric_address_provenance(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\x68"+bytes(4)+b"\x58\x25\xff\0\0\0\xc3",
           [(1, "_value", 0x3000, 0x3100, 0)])
    c.data("_value", 0x3000, 0x3100, b"GOOD", b"GOOD")
    known_extent(c)
    result, rows = c.run()
    assert result["credit_unique_bytes"] == 0
    assert "address-numeric-use:_value" in rows[0]["failures"]


@pytest.mark.parametrize("load", [b"\xb9"+bytes(4)+b"\x0f\xb6\x01\xc3",
                                   b"\x8d\x0d"+bytes(4)+b"\x0f\xb6\x01\xc3"])
def test_register_carried_text_fixed_read_with_complete_coverage_passes(tmp_path, monkeypatch, load):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, load, [(2 if load[0] == 0x8d else 1, "_g", 0x1100, 0x1100, 0)])
    c.code("_g", 0x1100, b"\xc3")
    result, rows = c.run()
    assert rows[0]["closed_strict"] == "1", rows
    assert result["credit_unique_bytes"] == len(load) + 1


def test_register_text_address_ambiguous_join_refuses(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    # mov eax,g; test ecx,ecx; je load; add eax,4; load: fld qword [eax]; ret
    c.code("_f", 0x1000, b"\xb8"+bytes(4)+b"\x85\xc9\x74\x03\x83\xc0\x04\xdd\x00\xc3",
           [(1, "_g", 0x1100, 0x1100, 0)])
    c.code("_g", 0x1100, b"\xc3")
    _, rows = c.run()
    assert rows[0]["closed_strict"] == "0"


@pytest.mark.parametrize("size,api,allowed", [(16, 'CoCreateInstance', True), (15, 'CoCreateInstance', False),
                                              (16, 'UnknownAPI', False)])
def test_guid_consumer_uses_fixed_api_range_not_inventory(tmp_path, monkeypatch, size, api, allowed):
    c = Case(tmp_path, monkeypatch)
    # IID and CLSID are arguments 4 and 1, each a fixed 16-byte read.
    raw = b"\x50\x68"+bytes(4)+b"\x6a\x01\x6a\x00\x68"+bytes(4)+b"\xff\x15"+bytes(4)+b"\xc3"
    c.code("_f", 0x1000, raw, [(2, "_guid", 0x3000, 0x3100, 0),
                              (11, "_guid", 0x3000, 0x3100, 0),
                              (17, "__imp__API", 0x3500, 0x3500, 0)])
    c.data("_guid", 0x3000, 0x3100, bytes(range(size)), bytes(range(size)))
    c.inventory([("0x3100", 20, ".rdata", "global", "guid and padding", "medium")])
    c.imports = {0x3500: ('ole32.dll', api)}
    monkeypatch.setattr(c, 'pe_view', lambda path: (None,
        c.S if path.name == 'shft.exe' else c.I, c.secs, {0x3500: ('ole32.dll', api)}))
    monkeypatch.setattr(lc, 'pe_view', c.pe_view)
    result, rows = c.run()
    assert rows[0]['closed_strict'] == str(int(allowed)), rows
    assert bool(result['credit_unique_bytes']) == allowed


def test_wider_literal_consumer_still_requires_following_bytes(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\xdd\x05"+bytes(4)+b"\xc3", [(2, "$SG1", 0x3000, 0x3100, 0)])
    c.data("$SG1", 0x3000, 0x3100, b"ok\0\0BAD!", b"ok\0XTAIL")
    result, rows = c.run()
    assert result['credit_unique_bytes'] == 0
    assert rows[0]['closed_strict'] == '0'


def test_indirect_pointer_load_retains_numeric_provenance(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\xb9"+bytes(4)+b"\x8b\x01\x25\xff\0\0\0\xc3",
           [(1, "_pointer", 0x3200, 0x3300, 0)])
    c.data("_pointer", 0x3200, 0x3300, bytes(4), bytes(4),
           refs=[(0, "_value", 0x3000, 0x3100, 0)])
    c.data("_value", 0x3000, 0x3100, b"GOOD", b"GOOD")
    known_extent(c)
    result, rows = c.run()
    assert result['credit_unique_bytes'] == 0
    assert 'address-numeric-use:_pointer' in rows[0]['failures']


def test_indirect_whole_pointer_copy_remains_allowed(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    c.code("_f", 0x1000, b"\xb9"+bytes(4)+b"\x8b\x01\xc3",
           [(1, "_pointer", 0x3200, 0x3300, 0)])
    c.data("_pointer", 0x3200, 0x3300, bytes(4), bytes(4),
           refs=[(0, "_value", 0x3000, 0x3100, 0)])
    c.data("_value", 0x3000, 0x3100, b"GOOD", b"GOOD")
    known_extent(c)
    result, rows = c.run()
    assert rows[0]['closed_strict'] == '1', rows
    assert result['credit_unique_bytes'] == 8


@pytest.mark.parametrize('numeric', [False, True])
def test_whole_indexed_pointer_copies_keep_provenance(tmp_path, monkeypatch, numeric):
    c = Case(tmp_path, monkeypatch)
    raw = b'\x8b\x04\x8d'+bytes(4)+(b'\x25\xff\0\0\0' if numeric else b'')+b'\xc3'
    c.code('_f', 0x1000, raw, [(3, '_pointer', 0x3200, 0x3300, 0)])
    c.data('_pointer', 0x3200, 0x3300, bytes(4), bytes(4),
           refs=[(0, '_value', 0x3000, 0x3100, 0)])
    c.data('_value', 0x3000, 0x3100, b'GOOD', b'GOOD')
    known_extent(c)
    with (c.root/'targets/game/reverse/data_rows.csv').open('a') as f:
        f.write('_pointer,0x3300,rva,4,game/data.cpp,matched\n')
    result, rows = c.run()
    assert rows[0]['closed_strict'] == str(int(not numeric)), rows
    assert result['credit_unique_bytes'] == (0 if numeric else 8)


def test_numeric_operation_directly_on_pointer_storage_refuses(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    c.code('_f', 0x1000, b'\x81\x25'+bytes(4)+b'\xff\0\0\0\xc3',
           [(2, '_pointer', 0x3200, 0x3300, 0)])
    c.data('_pointer', 0x3200, 0x3300, bytes(4), bytes(4),
           refs=[(0, '_value', 0x3000, 0x3100, 0)])
    c.data('_value', 0x3000, 0x3100, b'GOOD', b'GOOD')
    known_extent(c)
    result, rows = c.run()
    assert result['credit_unique_bytes'] == 0
    assert 'address-numeric-use:_pointer' in rows[0]['failures']


@pytest.mark.parametrize('operation', [b'\x0f\xb6\x44\x24\x01',
    b'\xc6\x04\x24\0\x8b\x04\x24\x25\xff\0\0\0'])
def test_copied_pointer_storage_does_not_lose_raw_byte_provenance(tmp_path, monkeypatch, operation):
    c = Case(tmp_path, monkeypatch)
    # Save the whole pointer, overwrite the register without observing it,
    # then read/change the saved representation through a partial operand.
    raw=b'\xb8'+bytes(4)+b'\x89\x04\x24\xb8\0\0\0\0'+operation+b'\xc3'
    c.code('_f',0x1000,raw,[(1,'_value',0x3000,0x3100,0)])
    c.data('_value',0x3000,0x3100,b'GOOD',b'GOOD')
    known_extent(c)
    result, rows=c.run()
    assert result['credit_unique_bytes']==0
    assert 'address-numeric-use:_value' in rows[0]['failures']


def test_string_advance_does_not_erase_text_address_provenance(tmp_path, monkeypatch):
    c=Case(tmp_path,monkeypatch)
    # mov esi,g; lodsd; mov eax,[esi]; ret. Only the first dword is verified.
    c.code('_f',0x1000,b'\xbe'+bytes(4)+b'\xad\x8b\x06\xc3',[(1,'_g',0x1100,0x1100,0)])
    c.code('_g',0x1100,b'\xc3\x90\x90\x90')
    c.I[0x1104:0x1108]=c.S[0x1104:0x1108]=b'\x02'*4
    c.R[0x1104:0x1108]=b'\x01'*4
    result,rows=c.run()
    assert rows[0]['closed_strict']=='0'
    assert result['credit_unique_bytes']==4


@pytest.mark.parametrize('register',[False,True])
def test_unknown_text_index_does_not_invent_a_function_storage_domain(tmp_path,monkeypatch,register):
    c=Case(tmp_path,monkeypatch)
    raw=(b'\xba'+bytes(4)+b'\x0f\xb6\x04\x0a\xc3' if register else b'\x0f\xb6\x81'+bytes(4)+b'\xc3')
    c.code('_f',0x1000,raw,[(1 if register else 3,'_g',0x1100,0x1100,0)])
    c.code('_g',0x1100,b'\xc3')
    c.I[0x1101]=c.S[0x1101]=2
    c.R[0x1101]=1
    result,rows=c.run()
    assert rows[0]['closed_strict']=='0'
    assert result['credit_unique_bytes']==1
    assert 'code-storage-range-unknown:_g' in rows[0]['failures']
