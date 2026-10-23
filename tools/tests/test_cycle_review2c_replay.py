"""Round-3 real-data audit; reads the recorded PE/COFF files, never relinks.

Defaults identify the owner-supplied recordings. Set BFME_REVIEW2C_RUN and
BFME_REVIEW2C_PRIOR to relocated copies. Missing recordings skip explicitly.
Only the selected function ledger rows are retained. Expected-behavior tests
intentionally fail on 97575654f3; byte-evidence controls must pass.
"""
import csv
import hashlib
import json
import os
from pathlib import Path

import pytest

from test_cycle_review2_evidence import lc

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(os.environ.get('BFME_REVIEW2C_RUN',
    '/home/thag/Projects/Open-BFME-1/build/bfme2_port/cycle_test/run7_replay'))
PRIOR = Path(os.environ.get('BFME_REVIEW2C_PRIOR',
    '/home/thag/Projects/Open-BFME-1/.claude/worktrees/bfme2-port-p4/build/review2'))
SWITCHES = [0xaf8c0, 0xb2950, 0x1f58c0, 0x1f5940, 0x20dee0, 0x21e0d0,
            0x28ef30, 0x28ef80, 0x2c5780, 0x2c7e30, 0x45cdc0, 0x55e070,
            0x5a6410, 0x5a6630, 0x739cc0, 0x7ff450, 0x90c400, 0x91b3c0,
            0x91b6a0, 0x9de300]
# Maximum relative byte-end of the access, derived from the instructions below.
# Two LOD accessors admit index 17 and need 72 bytes, but their datum is 68.
RANGES = {0x62870: 36, 0x13cde0: 256, 0x13d700: 256, 0x13d750: 256,
          0x13e8c0: 256, 0x1c0ad0: 256, 0x1c2710: 256, 0x747a30: 48,
          0x8251c0: 4, 0x844710: 128, 0x9843d0: 72, 0x9843f0: 72,
          0x9cb970: 1024, 0x9e19c0: 1024, 0x9e1a00: 1024, 0x9e1a40: 1024,
          0x9e6020: 8, 0x9e7f90: 1024, 0x9e7fd0: 1024}
LOD = {0x9843d0, 0x9843f0}
BITCOUNTS = {0x13cde0, 0x13d700, 0x13d750, 0x13e8c0, 0x1c0ad0, 0x1c2710}
CRCS = {0x9e19c0, 0x9e1a00, 0x9e1a40, 0x9e7f90, 0x9e7fd0}


class RecordedObjects(lc.Objects):
    """Preserve original map basenames while reading renamed recorded objects."""
    def __init__(self, names):
        self.originals = {original: RUN / 'zzobj' / short for short, original in names.items()}
        super().__init__([Path('/recorded') / name for name in self.originals])

    def get(self, path):
        path = Path(path)
        if path not in self.cache:
            original = self.originals.get(path.name.lower())
            if original is None:
                return None
            raw = original.read_bytes()
            self.cache[path] = lc.parse_coff(raw) + (raw,)
        return self.cache[path]


@pytest.fixture(scope='module')
def replay():
    if not (RUN / 'base.exe').is_file() or not (PRIOR / 'delta3.json').is_file():
        pytest.skip('owner-supplied run7_replay/delta3.json unavailable')
    evidence = json.loads((Path(__file__).parent / 'fixtures/cycle_review2c_audit.json').read_text())
    for label, path in {'retail': lc.build.EXE, 'base': RUN/'base.exe',
                        'shifted': RUN/'shft.exe', 'delta': PRIOR/'delta3.json'}.items():
        with path.open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == evidence['inputs'][label]['sha256']
    delta = json.loads((PRIOR / 'delta3.json').read_text())
    wanted = {}
    for finding, addresses in ((2, SWITCHES), (4, RANGES)):
        stage = next(s for s in delta['stages'] if s['finding'] == finding)
        removed = {int(r['retail_rva'], 16): r for r in stage['removed_rows']}
        assert len(stage['removed_rows']) == {2: 95, 4: 185}[finding]
        for address in addresses:
            wanted[address] = removed[address]
    with (ROOT / 'targets/game/reverse/functions.csv').open(newline='') as stream:
        rows = [r for r in csv.DictReader(stream)
                if r['status'] == 'matched' and int(r['target_rva'], 16) in wanted
                and r['name'] == wanted[int(r['target_rva'], 16)]['name']]
    assert len(rows) == 39
    names, _ = lc.zz_names(RUN)
    objs = RecordedObjects(names)
    original = lc.row_obj
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lc, 'row_obj', lambda row: Path('/recorded') / original(row).name.lower())
        units, _ = lc.analyze(rows, objs)
    _, retail, rsecs, rimp = lc.pe_view(lc.build.EXE)
    _, linked, isecs, limp = lc.pe_view(RUN / 'base.exe')
    mapped = lc.read_map((RUN / 'base.map').read_text(encoding='latin-1'), lc.BASE, names)
    m = lc.Measure(units, [], mapped, linked, retail, isecs, rimp, limp, {}, objs,
                   {int(r['target_rva'], 16): int(r['target_size']) for r in rows})
    m.rsecs, m.retail_sites = rsecs, lc.retail_relocs.site_rvas()
    records = m.run()
    assert all(r['placed'] for r in records)
    shifted = lc.Shifted(RUN, linked, isecs, rsecs, True, lc.SHIFT_BASE, set())
    yield m, {r['row']['rva']: r for r in records}, shifted


def instructions(m, record):
    at, row = record['linked'], record['row']
    return lc.code_flow(m.I[at:at+row['size']], at+lc.BASE)[0]


def storage_entries(m, record):
    at, size = record['linked'], record['row']['size']
    out = set()
    for ins in instructions(m, record):
        if ins.mnemonic == 'lea':
            continue
        for op in ins.operands:
            if op.type == lc.capstone.x86.X86_OP_MEM:
                target = (op.mem.disp - lc.BASE) & 0xffffffff
                if at <= target < at+size:
                    out.add(target-at)
    return out


@pytest.mark.parametrize('rva', SWITCHES, ids=lambda n: f'{n:08X}')
def test_recorded_switch_evidence_and_typed_traversal(replay, rva, monkeypatch):
    """Passing control: table bytes, case labels and shifted words all agree."""
    m, records, shifted = replay
    rec = records[rva]
    at, size = rec['linked'], rec['row']['size']
    assert lc.nonreloc_diffs(m.I[at:at+size], m.R[rva:rva+size], rec['masked']) == 0
    assert shifted.words(at, size, rec['masked'], rec['rels']) is None
    storage = storage_entries(m, rec)
    assert storage
    typed, complete, fallthrough = lc.code_flow(m.I[at:at+size], at+lc.BASE, m.code_entries[at]-storage)
    assert typed and complete and not fallthrough
    for ins in typed:
        if (ins.mnemonic == 'call' or ins.mnemonic.startswith(('j', 'loop'))) and ins.operands:
            if ins.operands[0].type == lc.capstone.x86.X86_OP_IMM:
                target = ins.operands[0].imm-lc.BASE
                if not at <= target < at+size:
                    fo = ins.address-lc.BASE-at+ins.imm_offset
                    # Every external transfer was already covered by a COFF
                    # relocation; typed traversal adds no hidden dependency.
                    assert all(k in rec['masked'] for k in range(fo, fo+ins.imm_size))
    # Reuse BFME1's real same-section table/tail verifier on recorded COFF.
    import body_guard
    obj = m.objs.originals[Path(rec['unit']['obj']).name]
    row = dict(name=rec['row']['name'], source=rec['row']['source'],
               target_rva=hex(rva), target_size=str(size), notes='')
    monkeypatch.setattr(body_guard.build, 'row_object', lambda row: obj)
    monkeypatch.setattr(body_guard.build, 'read_target_bytes', lambda a,z: bytes(m.R[a:a+z]))
    class Context:
        def same_function(self, address, name):
            return name == row['name'] and address == rva
    stats = {}
    assert body_guard.row_findings(row, Context(), stats) == []
    assert stats.get('ltable_entries', 0) > 0


@pytest.mark.parametrize('rva', SWITCHES, ids=lambda n: f'{n:08X}')
def test_recorded_verified_switch_is_not_refused_as_undecodable(replay, rva):
    m, records, _ = replay
    rec = records[rva]
    print(hex(rva), 'storage offsets', sorted(storage_entries(m, rec)), rec['fails'])
    assert 'code-decode-incomplete' not in rec['fails'], 'verified table storage decoded as instructions'


def indexed_refs(m, record):
    seen = set()
    for owner, ref in m.pending:
        key = (ref[0], ref[1], ref[2])
        if owner is record and ref[8] and key not in seen:
            seen.add(key)
            yield ref


def assert_bound_instruction(rva, instructions):
    pairs = {(i.mnemonic, i.op_str) for i in instructions}
    if rva in BITCOUNTS:
        assert any(i.mnemonic == 'movzx' and i.operands[-1].size == 1 for i in instructions)
    elif rva in CRCS:
        assert any(mn == 'and' and op.endswith(', 0xff') for mn, op in pairs)
    elif rva == 0x62870:
        assert ('and', 'eax, 3') in pairs
    elif rva == 0x9e6020:
        assert ('and', 'esi, 1') in pairs
    elif rva == 0x844710:
        assert ('cmp', 'eax, 0x7f') in pairs and any(mn == 'jbe' for mn, _ in pairs)
    elif rva == 0x8251c0:
        assert ('cmp', 'eax, 4') in pairs and any(mn == 'jae' for mn, _ in pairs)
    elif rva in LOD:
        assert ('cmp', 'eax, 0x11') in pairs and any(mn == 'jg' for mn, _ in pairs)
    elif rva == 0x9cb970:
        assert ('cmp', 'esi, 0x100') in pairs and ('inc', 'esi') in pairs
    elif rva == 0x747a30:
        assert ('add', 'ecx, 6') in pairs
        assert {i.op_str for i in instructions if i.mnemonic == 'mov' and i.op_str.startswith('ecx, ')
                and i.operands[-1].type == lc.capstone.x86.X86_OP_IMM} == {
            'ecx, 1', 'ecx, 2', 'ecx, 3', 'ecx, 4', 'ecx, 5'}


@pytest.mark.parametrize('rva', RANGES, ids=lambda n: f'{n:08X}')
def test_recorded_array_content_and_range_evidence(replay, rva):
    """Passing controls, including two concrete four-byte coverage holes."""
    m, records, shifted = replay
    rec = records[rva]
    assert_bound_instruction(rva, instructions(m, rec))
    assert shifted.words(rec['linked'], rec['row']['size'], rec['masked'], rec['rels']) is None
    refs = list(indexed_refs(m, rec))
    assert refs
    for ref in refs:
        kind = m.resolve(ref)
        assert kind[0] == 'datum'
        a, b, size = kind[1]
        node = m.dnodes[kind[1]]
        assert not node['fails']
        assert shifted.data(kind[1], node) is None
        assert lc.nonreloc_diffs(m.I[a:a+size], m.R[b:b+size], node['masked']) == 0
        if rva in LOD:
            assert size == 68 and RANGES[rva] == 72
            assert m.I[a+68:a+72].hex() == '8988083d'
            assert m.R[b+68:b+72].hex() == '14570701'
            assert m.ref_check(ref)[0]  # Refusal is correct until these bytes are proven.
        else:
            assert RANGES[rva] <= size


@pytest.mark.parametrize('rva', sorted(set(RANGES)-LOD), ids=lambda n: f'{n:08X}')
def test_recorded_in_bounds_array_keeps_allowed_credit(replay, rva):
    m, records, _ = replay
    for ref in indexed_refs(m, records[rva]):
        failures, _, _ = m.ref_check(ref)
        print(hex(rva), ref[2], 'range-end', RANGES[rva], failures)
        assert not any(f.startswith('data-access-extent:') for f in failures), 'bounded verified array rejected'
