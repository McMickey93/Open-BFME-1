"""Round-5 narrow, read-only audit of removals in cumulative delta5 items 1-3."""
import csv
import hashlib
import json
from pathlib import Path

import pytest

from test_cycle_review2c_replay import RecordedObjects, RUN, lc

ROOT = Path(__file__).resolve().parents[2]
PRIOR = Path('/home/thag/Projects/Open-BFME-1/.claude/worktrees/bfme2-port-p4/build/review2')
SAMPLE = [0x844710, 0x9E19C0, 0x9D5990, 0x9E8130,
          0x5D6D0, 0x102090, 0x9C8660, 0x9C8680, 0x9AC4B0, 0x548DB0,
          0x28EF30, 0x28EF80, 0x5A6410, 0x91B6A0]
SWITCHES = {0x28EF30: (44, 10, 36, 2), 0x28EF80: (44, 10, 36, 2),
            0x5A6410: (56, 15, 44, 3), 0x91B6A0: (44, 14, 36, 2)}
STDCALL = [0x5D6D0, 0x102090, 0x548DB0]
SUPPORT = 0x548D90  # verified callback used by the sampled EnumThreadWindows caller
CLASSIFICATIONS = {
    0x844710: ('correct', '128 equal table bytes; no independent retail extent for the indexed read'),
    0x9E19C0: ('correct', '1024 equal CRC bytes; no independent retail extent for the indexed read'),
    0x9D5990: ('correct', '8 equal bytes; fixed qword store passes, returned address has no independent extent'),
    0x9E8130: ('correct', '7022 equal prime-table bytes; returned address has no independent retail extent'),
    0x9C8660: ('correct', '256-byte independent extent; pointer-difference loop loses tracked provenance; owner limit'),
    0x9C8680: ('correct', '256-byte independent extent; pointer-difference loop loses tracked provenance; owner limit'),
    0x9AC4B0: ('correct', '1024-byte independent extent; sub register index loses tracked provenance; owner limit'),
    0x5D6D0: ('wrong', '10/27-byte complete literals; LoadLibraryA/GetProcAddress/FreeLibrary consume stdcall arguments'),
    0x102090: ('wrong', '37-byte complete literal; CreateMutexA and CloseHandle consume stdcall arguments'),
    0x548DB0: ('wrong', 'verified 15-byte callback passed as whole pointer to EnumThreadWindows; stale stack tag'),
    0x28EF30: ('wrong', 'cmp/ja bounds 10 byte-map entries; all 10 bytes and two jump destinations verified'),
    0x28EF80: ('wrong', 'cmp/ja bounds 10 byte-map entries; all 10 bytes and two jump destinations verified'),
    0x5A6410: ('wrong', 'cmp/ja bounds 15 byte-map entries; all 15 bytes and three jump destinations verified'),
    0x91B6A0: ('wrong', 'cmp/ja bounds 14 byte-map entries; all 14 bytes and two jump destinations verified'),
}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


@pytest.fixture(scope='module')
def replay():
    delta_path = PRIOR / 'delta5.json'
    if not (RUN / 'base.exe').is_file() or not delta_path.is_file():
        pytest.skip('owner-supplied read-only recordings unavailable')
    delta = json.loads(delta_path.read_text())
    wanted = {int(row['retail_rva'], 16): dict(row, item=stage['item'])
              for stage in delta['stages'][:3] for row in stage['removed_rows']
              if int(row['retail_rva'], 16) in SAMPLE}
    assert len(wanted) == len(SAMPLE)
    previous = json.loads((ROOT/'tools/tests/fixtures/cycle_review2d_audit.json').read_text())
    inputs = {name: RUN/name for name in previous['inputs'] if name != 'retail'}
    inputs['retail'] = lc.build.EXE
    before = {name: digest(path) for name, path in inputs.items()}
    assert before == previous['inputs']
    inputs['delta5'] = delta_path
    inputs['final_status'] = PRIOR/'round5_5/link_status.csv'
    before.update({name: digest(inputs[name]) for name in ('delta5', 'final_status')})
    with inputs['final_status'].open() as stream:
        statuses = {r['name']: r for r in csv.DictReader(stream)
                    if r['name'] in {v['name'] for v in wanted.values()}}
    assert all(r['closed_strict'] == '0' for r in statuses.values())
    with (ROOT/'targets/game/reverse/functions.csv').open() as stream:
        rows = [r for r in csv.DictReader(stream) if r['status'] == 'matched'
                and (int(r['target_rva'], 16) == SUPPORT or
                     int(r['target_rva'], 16) in wanted
                     and r['name'] == wanted[int(r['target_rva'], 16)]['name'])]
    assert len(rows) == len(SAMPLE)+1
    names, _ = lc.zz_names(RUN)
    objs = RecordedObjects(names)
    original = lc.row_obj
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lc, 'row_obj', lambda row: Path('/recorded')/original(row).name.lower())
        units, _ = lc.analyze(rows, objs)
    _, R, rsecs, rimp = lc.pe_view(lc.build.EXE)
    _, I, isecs, limp = lc.pe_view(RUN/'base.exe')
    mapped = lc.read_map((RUN/'base.map').read_text(encoding='latin-1'), lc.BASE, names)
    m = lc.Measure(units, [], mapped, I, R, isecs, rimp, limp, {}, objs,
                   {int(r['target_rva'], 16): int(r['target_size']) for r in rows})
    m.rsecs, m.retail_sites = rsecs, lc.retail_relocs.site_rvas()
    records = {r['row']['rva']: r for r in m.run()}
    shifted = lc.Shifted(RUN, I, isecs, rsecs, True, lc.SHIFT_BASE, set())
    support = records[SUPPORT]
    a, z = support['linked'], support['row']['size']
    evidence = dict(inputs=before, rows=[], support=dict(
        retail_rva=hex(SUPPORT), linked=hex(a), size=z, source=support['row']['source'],
        linked_bytes=bytes(I[a:a+z]).hex(), retail_bytes=bytes(R[SUPPORT:SUPPORT+z]).hex(),
        code_diffs=lc.nonreloc_diffs(I[a:a+z], R[SUPPORT:SUPPORT+z], support['masked']),
        shift=shifted.words(a, z, support['masked'], support['rels']), failures=support['fails']))
    for rva in SAMPLE:
        rec = records[rva]
        at, size = rec['linked'], rec['row']['size']
        row = dict(wanted[rva], linked=hex(at), failures=rec['fails'],
                   classification=CLASSIFICATIONS[rva][0], proof=CLASSIFICATIONS[rva][1],
                   full_run_status=statuses[rec['row']['name']],
                   source_sha256=digest(ROOT/rec['row']['source']),
                   linked_bytes=bytes(I[at:at+size]).hex(), retail_bytes=bytes(R[rva:rva+size]).hex(),
                   code_diffs=lc.nonreloc_diffs(I[at:at+size], R[rva:rva+size], rec['masked']),
                   shift=shifted.words(at, size, rec['masked'], rec['rels']),
                   instructions=[dict(offset=ins.address-lc.BASE-at, bytes=ins.bytes.hex(),
                                      asm=ins.mnemonic+' '+ins.op_str)
                                 for ins in lc.code_flow(I[at:at+size], at+lc.BASE)[0]], refs=[])
        for owner, ref in m.pending:
            if owner is not rec:
                continue
            kind = m.resolve(ref)
            item = dict(name=ref[2], linked=hex(ref[0]), retail=hex(ref[1]),
                        addend=ref[5], width=ref[7], indexed=ref[8], uses=ref[9],
                        verdict=m.ref_check(ref)[0], kind=kind[0])
            if kind[0] == 'datum':
                a, b, z = kind[1]
                node = m.dnodes[kind[1]]
                item.update(key=[hex(a), hex(b), z], extent=m.retail_datum_size(b, z, ref[2]),
                            linked_bytes=bytes(I[a:a+z]).hex(), retail_bytes=bytes(R[b:b+z]).hex(),
                            diffs=lc.nonreloc_diffs(I[a:a+z], R[b:b+z], node['masked']),
                            shift=shifted.data(kind[1], node), failures=node['fails'])
            row['refs'].append(item)
        evidence['rows'].append(row)
    evidence['recorded_object_hashes'] = {path.name: hashlib.sha256(obj[2]).hexdigest()
                                        for path, obj in objs.cache.items() if obj}
    out = ROOT/'build/review2e'
    out.mkdir(parents=True, exist_ok=True)
    (out/'sample.json').write_text(json.dumps(evidence, indent=2)+'\n')
    yield m, records, evidence
    for name, path in inputs.items():
        assert digest(path) == before[name], name
    for path, obj in objs.cache.items():
        if obj:
            assert objs.originals[path.name.lower()].read_bytes() == obj[2]


@pytest.mark.parametrize('rva', SAMPLE, ids=lambda n: f'{n:08X}')
def test_sample_code_and_provider_bytes(replay, rva):
    m, records, evidence = replay
    row = next(r for r in evidence['rows'] if int(r['retail_rva'], 16) == rva)
    assert records[rva]['placed']
    assert row['code_diffs'] == 0 and row['shift'] is None
    for ref in row['refs']:
        if ref['kind'] == 'datum':
            assert ref['diffs'] == 0 and ref['shift'] is None


def test_callback_support_is_fully_verified(replay):
    _, _, evidence = replay
    assert evidence['support']['size'] == 15
    assert evidence['support']['code_diffs'] == 0
    assert evidence['support']['shift'] is None
    assert evidence['support']['failures'] == []


@pytest.mark.parametrize('rva', sorted(SWITCHES), ids=lambda n: f'{n:08X}')
def test_switch_storage_has_independent_complete_byte_evidence(replay, monkeypatch, rva):
    import body_guard
    m, records, _ = replay
    rec = records[rva]
    at, size = rec['linked'], rec['row']['size']
    offset, count, pointers, slots = SWITCHES[rva]
    assert offset+count == size
    assert m.I[at+offset:at+offset+count] == m.R[rva+offset:rva+offset+count]
    assert max(m.R[rva+offset:rva+offset+count]) < slots
    for k in range(slots):
        assert at <= lc.u32(m.I, at+pointers+4*k)-lc.BASE < at+pointers
        assert rva <= lc.u32(m.R, rva+pointers+4*k)-lc.BASE < rva+pointers
    # Bound is the immediately preceding cmp/jump, not an arbitrary symbolic
    # index proof: cmp eax,count-1; ja default; movzx eax,[eax+byte_table].
    insns = lc.code_flow(m.I[at:at+size], at+lc.BASE)[0]
    index = next(i for i, ins in enumerate(insns) if ins.mnemonic == 'movzx')
    assert insns[index-2].mnemonic == 'cmp'
    assert insns[index-2].operands[1].imm == count-1
    assert insns[index-1].mnemonic == 'ja'
    obj = m.objs.originals[Path(rec['unit']['obj']).name]
    row = dict(name=rec['row']['name'], source=rec['row']['source'],
               target_rva=hex(rva), target_size=str(size), notes='')
    monkeypatch.setattr(body_guard.build, 'row_object', lambda row: obj)
    monkeypatch.setattr(body_guard.build, 'read_target_bytes', lambda a,z: bytes(m.R[a:a+z]))
    class Context:
        def same_function(self, address, name):
            return address == rva and name == row['name']
    stats = {}
    assert body_guard.row_findings(row, Context(), stats) == []
    assert stats.get('ltable_entries', 0) > 0


@pytest.mark.parametrize('rva', sorted(SWITCHES), ids=lambda n: f'{n:08X}')
def test_verified_compiler_switch_byte_table_is_not_refused(replay, rva):
    _, records, _ = replay
    assert not any(f.startswith('code-storage-range-unknown:')
                   for f in records[rva]['fails']), records[rva]['fails']


@pytest.mark.parametrize('rva', STDCALL, ids=lambda n: f'{n:08X}')
def test_stdcall_argument_cleanup_does_not_invent_numeric_observations(replay, rva):
    _, records, _ = replay
    assert not any(f.startswith('address-numeric-use:')
                   for f in records[rva]['fails']), records[rva]['fails']


@pytest.mark.parametrize('defect', ['signed-bound', 'missing-bound', 'wide-map',
    'uncovered-map', 'map-content', 'slot-outside', 'slot-identity', 'missing-slot-relocation',
    'bypass-entry', 'wrong-jump-index'])
def test_compiler_byte_map_requires_complete_bounded_evidence(replay, defect):
    import copy
    m, records, _ = replay
    m = copy.copy(m)
    rec = records[0x28EF30]
    at, size = rec['linked'], rec['row']['size']
    unit = rec['unit']
    o = m.objs.get(Path(unit['obj']))
    # Private images/COFF metadata only: the recording and shared fixture stay
    # unchanged, including for mutations whose bytes agree in both images.
    m.I, m.R = bytearray(m.I), bytearray(m.R)
    raw = bytearray(m.I[at:at+size])
    if defect == 'signed-bound':
        raw[7] = 0x7f
    elif defect == 'missing-bound':
        raw[4:7] = b'\x85\xc0\x90'
    elif defect == 'wide-map':
        raw[10] = 0xb7
    elif defect == 'uncovered-map':
        raw[6] = size
    elif defect == 'map-content':
        m.R[0x28EF30+53] ^= 1
    elif defect == 'slot-outside':
        raw[53] = 255
    elif defect == 'slot-identity':
        m.R[0x28EF30+36] ^= 1
    elif defect == 'missing-slot-relocation':
        secs = list(o[0])
        sec = secs[unit['sec']-1] = copy.copy(secs[unit['sec']-1])
        sec.relocs = [(a,b,c) for a,b,c in sec.relocs if a != rec['row']['off']+36]
        o = (secs, o[1], o[2])
    elif defect == 'bypass-entry':
        m.code_entries = dict(m.code_entries)
        m.code_entries[at] = set(m.code_entries[at]) | {9}
    elif defect == 'wrong-jump-index':
        raw[18] = 0x8d
    m.I[at:at+size] = raw
    insns = lc.code_flow(raw, at+lc.BASE)[0]
    load = next(i for i in insns if i.mnemonic == 'movzx')
    assert m.bounded_byte_map(insns, load, at, 0x28EF30, size, o,
                              unit['sec'], rec['row']['off']) is None
