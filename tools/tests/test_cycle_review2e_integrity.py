"""Round-5 nearby variants; real COFF/measurement, no compiler or real link.

Assertions state required behavior and remain failing while a defect exists.
"""
from pathlib import Path

import pytest

from test_cycle_review2d_integrity import Case, known_extent, lc, section, symbol
import body_guard


@pytest.mark.parametrize('width,offset,allowed', [(1, 3, True), (2, 2, True),
    (4, 0, True), (2, 3, False), (4, 1, False)])
@pytest.mark.parametrize('inventory', [False, True])
def test_fixed_ranges_without_retail_extent(tmp_path, monkeypatch, width, offset, allowed, inventory):
    c = Case(tmp_path, monkeypatch)
    load = {1: b'\x0f\xb6\x40', 2: b'\x0f\xb7\x40', 4: b'\x8b\x40'}[width]
    raw = b'\xb8'+bytes(4)+load+bytes([offset])+b'\xc3'
    c.code('_f', 0x1000, raw, [(1, '_a', 0x3000, 0x3100, 0)])
    c.data('_a', 0x3000, 0x3100, b'GOODBAD!', b'GOODTAIL', size=4)
    if inventory:
        c.inventory([('0x3100', 1024, '.rdata', 'global', 'group', 'high')])
    result, rows = c.run()
    assert bool(result['credit_unique_bytes']) == allowed, rows


@pytest.mark.parametrize('source', ['direct', 'register', 'stack'])
@pytest.mark.parametrize('load,allowed', [(b'\x8b\x01', True), (b'\x0f\xb7\x01', False),
    (b'\x0f\xb6\x41\x03', False), (b'\x8b\x41\x01', False)])
def test_pointer_storage_consumed_as_whole_words(tmp_path, monkeypatch, source, load, allowed):
    c = Case(tmp_path, monkeypatch)
    raw = {'direct': b'\xb9'+bytes(4), 'register': b'\xb8'+bytes(4)+b'\x89\xc1',
           'stack': b'\x68'+bytes(4)+b'\x59'}[source]+load+b'\xc3'
    c.code('_f', 0x1000, raw, [(1, '_pointer', 0x3200, 0x3300, 0)])
    c.data('_pointer', 0x3200, 0x3300, bytes(4), bytes(4),
           refs=[(0, '_value', 0x3000, 0x3100, 0)])
    c.data('_value', 0x3000, 0x3100, b'GOOD', b'GOOD')
    known_extent(c)
    result, rows = c.run()
    assert bool(result['credit_unique_bytes']) == allowed, rows


@pytest.mark.parametrize('copy', [b'\x89\xc1', b'\x50\x59', b'\x8d\x48\x01\x49'])
@pytest.mark.parametrize('covered', [1, 8])
def test_text_address_copies_verify_the_full_read(tmp_path, monkeypatch, copy, covered):
    c = Case(tmp_path, monkeypatch)
    raw = b'\xb8'+bytes(4)+copy+b'\xdd\x01\xb8'+bytes(4)+b'\xc3'
    c.code('_f', 0x1000, raw,
           [(1, '_g', 0x1100, 0x1100, 0)])
    c.code('_g', 0x1100, b'\x90'*(covered-1)+b'\xc3')
    if covered == 1:
        c.I[0x1101:0x1108] = c.S[0x1101:0x1108] = b'\x02'*7
        c.R[0x1101:0x1108] = b'\x01'*7
    result, rows = c.run()
    assert rows[0]['closed_strict'] == str(int(covered == 8)), rows
    assert result['credit_unique_bytes'] == covered + (len(raw) if covered == 8 else 0)


@pytest.mark.parametrize('padding', [b'X', b'XYZAB'])
@pytest.mark.parametrize('corrupt', [False, True])
def test_literal_padding_and_live_bytes(tmp_path, monkeypatch, padding, corrupt):
    c = Case(tmp_path, monkeypatch)
    c.code('_f', 0x1000, b'\xb8'+bytes(4)+b'\xc3', [(1, '$SG1', 0x3000, 0x3100, 0)])
    c.data('$SG1', 0x3000, 0x3100, b'ok\0'+bytes(len(padding)),
           (b'no\0' if corrupt else b'ok\0')+padding)
    result, rows = c.run()
    assert result['credit_unique_bytes'] == (0 if corrupt else 6), rows


def test_stdcall_consumes_pointer_argument_before_branch_stack_join(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    # LoadLibraryA(name); if (eax) FreeLibrary(eax); return 0.
    # Both callees pop their one argument; no address bits are observed.
    raw = b'\x68'+bytes(4)+b'\xff\x15'+bytes(4)+b'\x85\xc0\x74\x07\x50\xff\x15'+bytes(4)+b'\x31\xc0\xc3'
    c.code('_f', 0x1000, raw, [(1, '_name', 0x3000, 0x3100, 0),
        (7, '__imp__LoadLibraryA@4', 0x3500, 0x3500, 0),
        (18, '__imp__FreeLibrary@4', 0x3504, 0x3504, 0)])
    c.data('_name', 0x3000, 0x3100, b'ok\0\0', b'ok\0\0')
    known_extent(c, '_name')
    c.imports = {0x3500: ('kernel32.dll', 'LoadLibraryA'), 0x3504: ('kernel32.dll', 'FreeLibrary')}
    monkeypatch.setattr(lc, 'pe_view', lambda path: (None,
        c.S if path.name == 'shft.exe' else c.I, c.secs, c.imports))
    result, rows = c.run()
    assert result['credit_unique_bytes'] == len(raw), rows[0]['failures']


def test_backward_register_index_is_conservatively_refused(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    # return table[1-i]; mirrors the real 0x009AC4B0 reverse lookup.
    # The current tracker cannot establish the subtracted register's domain.
    # Document this limit without requiring new symbolic index evaluation.
    raw = b'\xb9'+bytes(4)+b'\xc1\xe0\x02\x29\xc1\x8b\x01\xc3'
    c.code('_f', 0x1000, raw, [(1, '_table', 0x3004, 0x3104, 4)])
    c.data('_table', 0x3000, 0x3100, b'GOODTAIL', b'GOODTAIL')
    known_extent(c, '_table', size=8)
    result, rows = c.run()
    assert result['credit_unique_bytes'] == 0, rows
    assert 'address-numeric-use:_table' in rows[0]['failures']


@pytest.mark.parametrize('different_prefix', [False, True])
def test_local_literal_suffix_uses_body_guard_semantic_extent(tmp_path, monkeypatch, different_prefix):
    c = Case(tmp_path, monkeypatch)
    c.code('_f', 0x1000, b'\xb8'+bytes(4)+b'\xc3', [(1, '$SG1', 0x3003, 0x3103, 3)])
    path = Path(c.units[0]['obj'])
    obj = c.objs.get(path)
    code = obj[2][obj[0][0].ptr:obj[0][0].ptr+6]
    literal = b'preok\0\0\0'
    c.add_object(path.name, ([section(6, '.text', [(1, 1, lc.DIR32)]),
                             section(8, '.rdata', ptr=10)],
        {0: symbol(0, '_f', 1), 1: symbol(1, '$SG1', 2, storage=lc.STATIC)},
        bytes(4)+code+literal))
    c.I[0x3000:0x3008] = c.S[0x3000:0x3008] = literal
    c.R[0x3100:0x3108] = (b'XXX' if different_prefix else b'pre')+b'ok\0XY'
    info = dict(data=bytes(4)+literal,
        sections=[dict(characteristics=0x40, raw_pointer=4, raw_size=8,
                       reloc_count=0, reloc_pointer=0)],
        symbols=[dict(name='$SG1', section=1, storage=3, value=0, aux=0)])
    monkeypatch.setattr(body_guard, '_retail', lambda at, size: bytes(c.R[at:at+size]))
    assert body_guard._static_content(info, info['symbols'][0], lc.BASE+0x3100, 3) == ('ok', '')
    result, rows = c.run()
    assert result['credit_unique_bytes'] == 6, rows[0]['failures']


@pytest.mark.parametrize('decorated', [True, False])
def test_unknown_abi_does_not_discard_argument_tags(tmp_path, monkeypatch, decorated):
    c = Case(tmp_path, monkeypatch)
    name = '__imp__API@4' if decorated else '__imp__API'
    # The argument slot is dead only with independently known callee cleanup.
    raw = b'\x68'+bytes(4)+b'\xff\x15'+bytes(4)+b'\x58\x85\xc0\x31\xc0\xc3'
    c.code('_f', 0x1000, raw, [(1, '_name', 0x3000, 0x3100, 0),
                             (7, name, 0x3500, 0x3500, 0)])
    c.data('_name', 0x3000, 0x3100, b'ok\0\0', b'ok\0\0')
    known_extent(c, '_name')
    c.imports = {0x3500: ('kernel32.dll', 'API')}
    monkeypatch.setattr(lc, 'pe_view', lambda path: (None,
        c.S if path.name == 'shft.exe' else c.I, c.secs, c.imports))
    result, rows = c.run()
    assert bool(result['credit_unique_bytes']) == decorated, rows
    assert ('address-numeric-use:_name' in rows[0]['failures']) != decorated


def test_stdcall_rebases_surviving_local_pointer_tags(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    # The first push is a local. API consumes only the second push. Reading
    # the local's representation after the call must still be refused.
    raw = b'\x68'+bytes(4)+b'\x6a\x00\xff\x15'+bytes(4)+b'\x58\x85\xc0\x31\xc0\xc3'
    c.code('_f', 0x1000, raw, [(1, '_name', 0x3000, 0x3100, 0),
        (9, '__imp__API@4', 0x3500, 0x3500, 0)])
    c.data('_name', 0x3000, 0x3100, b'ok\0\0', b'ok\0\0')
    known_extent(c, '_name')
    c.imports = {0x3500: ('kernel32.dll', 'API')}
    monkeypatch.setattr(lc, 'pe_view', lambda path: (None,
        c.S if path.name == 'shft.exe' else c.I, c.secs, c.imports))
    result, rows = c.run()
    assert result['credit_unique_bytes'] == 0
    assert 'address-numeric-use:_name' in rows[0]['failures']


@pytest.mark.parametrize('ret_bytes,allowed', [('4', True), ('0 4', False), ('', False)])
def test_direct_callee_cleanup_uses_unambiguous_bfme1_abi_evidence(tmp_path, monkeypatch, ret_bytes, allowed):
    import struct
    import callee_protos
    c = Case(tmp_path, monkeypatch)
    raw = b'\x68'+bytes(4)+b'\xe8'+struct.pack('<i', 0x1100-0x100a)+b'\x58\x85\xc0\x31\xc0\xc3'
    c.code('_f', 0x1000, raw, [(1, '_name', 0x3000, 0x3100, 0)])
    c.code('_callee', 0x1100, b'\xc2\x04\x00')
    c.data('_name', 0x3000, 0x3100, b'ok\0\0', b'ok\0\0')
    known_extent(c, '_name')
    monkeypatch.setattr(callee_protos, 'load', lambda: {0x1100: {'ret_bytes': ret_bytes}})
    _, rows = c.run()
    assert rows[0]['closed_strict'] == str(int(allowed)), rows


@pytest.mark.parametrize('read', [b'\x8b\x00', b'\x0f\xb6\x40\xfd'])
def test_literal_suffix_does_not_exempt_wider_or_prefix_reads(tmp_path, monkeypatch, read):
    c = Case(tmp_path, monkeypatch)
    raw = b'\xb8'+bytes(4)+read+b'\xc3'
    c.code('_f', 0x1000, raw, [(1, '$SG1', 0x3003, 0x3103, 3)])
    c.data('$SG1', 0x3000, 0x3100, b'preok\0\0\0', b'XXXok\0XY')
    result, rows = c.run()
    assert result['credit_unique_bytes'] == 0, rows


def test_stdcall_partial_argument_storage_keeps_surviving_raw_bytes(tmp_path, monkeypatch):
    c = Case(tmp_path, monkeypatch)
    # An unaligned copied pointer straddles callee-discarded storage and a
    # surviving local. Its surviving two bytes are still representation bytes.
    raw = b'\xc7\x44\x24\x02'+bytes(4)+b'\xff\x15'+bytes(4)+b'\x0f\xb6\x04\x24\xc3'
    c.code('_f', 0x1000, raw, [(4, '_name', 0x3000, 0x3100, 0),
        (10, '__imp__API@4', 0x3500, 0x3500, 0)])
    c.data('_name', 0x3000, 0x3100, b'ok\0\0', b'ok\0\0')
    known_extent(c, '_name')
    c.imports = {0x3500: ('kernel32.dll', 'API')}
    monkeypatch.setattr(lc, 'pe_view', lambda path: (None,
        c.S if path.name == 'shft.exe' else c.I, c.secs, c.imports))
    result, rows = c.run()
    assert result['credit_unique_bytes'] == 0
    assert 'address-numeric-use:_name' in rows[0]['failures']
