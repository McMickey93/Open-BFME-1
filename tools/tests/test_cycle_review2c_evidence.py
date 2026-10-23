"""Round-3 independent counterexamples: assertions fail while the defect exists.

Only synthetic COFF/images and production Python measurement are used. No
compiler, linker, Wine, signing key, or authoritative publication is invoked.
"""
import json

import pytest

from test_cycle_review2_evidence import ImageCase, F, A, DATA, RDATA, dword, lc


@pytest.fixture
def case(tmp_path, monkeypatch):
    return ImageCase(tmp_path, monkeypatch)


def caller(case, raw, relocs, names):
    obj = case.object('caller.obj', [('.text', raw, relocs)],
                      [('_caller', 1, 0, lc.EXTERNAL)] + names)
    case.row(obj, '_caller', F, len(raw))
    case.public(obj, '_caller', F)
    case.put(F, raw, retail=raw)
    return obj


def outcome(case):
    result, rows = case.measure()
    row = next(r for r in rows if r['name'] == '_caller')
    print(json.dumps(dict(credit=result['credit_unique_bytes'], failures=row['failures'],
                         closed=row['closed_strict']), sort_keys=True))
    return result, row


def data_provider(case, payload):
    obj = case.object('data.obj', [('.data', payload, [])], [('_g', 1, 0, lc.EXTERNAL)])
    case.public(obj, '_g', DATA)
    case.put(DATA, payload)
    case.R[RDATA:RDATA + len(payload)] = payload
    return obj


def retail_datum(case, size):
    # Independent retail extent: a short selected COFF copy cannot define the
    # datum's domain. Whole-datum verification replaces integer range analysis.
    reverse = case.root / 'targets/game/reverse'
    reverse.mkdir(parents=True, exist_ok=True)
    (reverse / 'data_rows.csv').write_text(
        'name,address,address_kind,size,source,status\n'
        f'_g,{RDATA:#x},rva,{size},game/data.cpp,matched\n')


def pointer(case, site, linked, retail):
    case.ptr(F + site, linked)
    case.R[F + site:F + site + 4] = dword(lc.BASE + retail)


@pytest.mark.parametrize('form', ['register', 'bitstring', 'string', 'code_section'])
def test_access_range_cannot_be_evaded_by_operand_form(case, form):
    """All forms read bytes outside the provider; linked/retail values differ."""
    if form == 'register':
        # mov eax,offset _g; mov eax,[eax+4]; ret
        raw, site = b'\xb8' + bytes(4) + b'\x8b\x40\x04\xc3', 1
        data_provider(case, bytes(4))
        target, lt, rt = '_g', DATA, RDATA
    elif form == 'string':
        # mov esi,offset _g; mov ecx,2; rep lodsd; ret
        raw, site = b'\xbe' + bytes(4) + b'\xb9' + dword(2) + b'\xf3\xad\xc3', 1
        data_provider(case, bytes(4))
        target, lt, rt = '_g', DATA, RDATA
    elif form == 'bitstring':
        # bt [g],ecx with ecx=32 accesses g+4, not g.
        raw, site = b'\xb9' + dword(32) + b'\x0f\xa3\x0d' + bytes(4) + b'\x0f\x92\xc0\xc3', 8
        data_provider(case, bytes(4))
        target, lt, rt = '_g', DATA, RDATA
    else:
        # A memory operand aimed at .text never enters the data-width check.
        leaf = case.object('leaf.obj', [('.text', b'\xc3', [])], [('_a', 1, 0, lc.EXTERNAL)])
        case.row(leaf, '_a', A, 1)
        case.public(leaf, '_a', A)
        case.put(A, b'\xc3', retail=b'\xc3')
        raw, site = b'\xdd\x05' + bytes(4) + b'\xc3', 2  # fld qword [_a]
        target, lt, rt = '_a', A, A
    if form != 'code_section':
        retail_datum(case, 8)
    caller(case, raw, [(site, target, lc.DIR32)], [(target, 0, 0, lc.EXTERNAL)])
    pointer(case, site, lt, rt)
    start = 1 if form == 'code_section' else 4
    case.I[lt + start:lt + 8] = b'\x02' * (8 - start)
    case.R[rt + start:rt + 8] = b'\x01' * (8 - start)
    # Add only a ledger claim, leaving source objects and both images identical.
    claimed = case.rows.pop()
    before, _ = case.measure()
    frozen = bytes(case.I)
    case.rows.append(claimed)
    after, row = outcome(case)
    assert bytes(case.I) == frozen
    print({'form': form, 'before': before['credit_unique_bytes'],
           'after': after['credit_unique_bytes'],
           'unverified_linked': case.I[lt+start:lt+8].hex(),
           'unverified_retail': case.R[rt+start:rt+8].hex()})
    assert row['closed_strict'] == '0', 'operand form bypassed complete-access verification'
    assert after['credit_unique_bytes'] == before['credit_unique_bytes']


@pytest.mark.parametrize('bound', ['mask', 'movzx', 'branch'])
@pytest.mark.parametrize('short', [False, True])
def test_bounded_index_checks_the_proven_range_instead_of_rejecting_all_indices(case, bound, short):
    """A full 256-byte table is enough; a 255-byte prefix is not."""
    if bound == 'mask':
        prefix = b'\x81\xe1' + dword(255)
    elif bound == 'movzx':
        prefix = b'\x0f\xb6\xc9'  # movzx ecx,cl
    else:
        prefix = b'\x81\xf9' + dword(255) + b'\x77\x07'  # ja ret
    raw = prefix + b'\x0f\xb6\x81' + bytes(4) + b'\xc3'
    site = len(prefix) + 3
    caller(case, raw, [(site, '_g', lc.DIR32)], [('_g', 0, 0, lc.EXTERNAL)])
    data_provider(case, bytes(range(255 if short else 256)))
    retail_datum(case, 256)
    pointer(case, site, DATA, RDATA)
    case.I[DATA+255] = 254 if short else 255
    case.R[RDATA+255] = 255
    _, row = outcome(case)
    assert row['closed_strict'] == str(int(not short)), 'whole retail datum coverage was not respected'


@pytest.mark.parametrize('tail', [False, True])
@pytest.mark.parametrize('mutation', ['none', 'destination', 'storage'])
def test_inline_switch_storage_is_not_an_executable_entry(case, monkeypatch, mutation, tail):
    """A two-case switch, including table bytes, satisfies BFME1 body_guard."""
    # mov eax,[esp+4]; cmp eax,1; ja default; jmp [$table+eax*4]
    # case0: mov eax,10; ret; default/case1: mov eax,20; ret; table
    raw = (b'\x8b\x44\x24\x04\x83\xf8\x01\x77\x0d\xff\x24\x85' + bytes(4)
           + b'\xb8' + dword(10) + b'\xc3' + b'\xb8' + dword(20) + b'\xc3' + bytes(8))
    rels = [(12, '$table', lc.DIR32), (28, '$case0', lc.DIR32), (32, '$case1', lc.DIR32)]
    obj = caller(case, raw, rels, [('$table', 1, 28, lc.STATIC),
                                  ('$case0', 1, 16, lc.STATIC), ('$case1', 1, 22, lc.STATIC)])
    if tail:
        case.rows[0]['target_size'] = '28'
    for site, at in ((12, 28), (28, 16), (32, 22)):
        pointer(case, site, F + at, F + at)
    import body_guard
    monkeypatch.setattr(body_guard.build, 'row_object', lambda _: obj)
    monkeypatch.setattr(body_guard.build, 'read_target_bytes', lambda at, size: bytes(case.R[at:at+size]))
    stats = {}
    assert body_guard.row_findings(case.rows[0], object(), stats) == []
    assert stats['ltable_entries'] == 3
    if mutation == 'destination':
        case.ptr(F + 28, F + 22)
    elif mutation == 'storage':
        case.ptr(F + 12, F + 29)
    _, row = outcome(case)
    assert row['closed_strict'] == str(int(mutation == 'none')), 'table storage/destination verification failed'


@pytest.mark.parametrize('proof', ['ledger', 'scalar', 'literal'])
def test_precise_datum_size_outranks_a_coarse_inventory_partition(case, proof):
    name = {'ledger': '_g', 'scalar': '?value@@3IA',
            'literal': '??_C@_03HASH@abc?$AA@'}[proof]
    payload = b'abc\0' if proof == 'literal' else bytes(4)
    provider = case.object('data.obj', [('.data', payload, [])], [(name, 1, 0, lc.EXTERNAL)])
    case.public(provider, name, DATA)
    case.put(DATA, payload)
    case.R[RDATA:RDATA + 4] = payload
    caller(case, b'\xb8' + bytes(4) + b'\xc3', [(1, name, lc.DIR32)], [(name, 0, 0, lc.EXTERNAL)])
    pointer(case, 1, DATA, RDATA)
    if proof == 'ledger':
        retail_datum(case, 4)
    inventory = case.root / 'targets/game/reverse/retail_inventory/data_items.csv'
    inventory.parent.mkdir(parents=True, exist_ok=True)
    inventory.write_text(f'rva,size\n{RDATA:#x},8\n')
    _, row = outcome(case)
    assert row['closed_strict'] == '1'


def test_text_memory_cannot_admit_an_unledgered_function_as_tail_storage(case):
    # body_guard's ltable rule distinguishes compiler $ labels from functions.
    # A matching unclaimed helper is not a verified switch table or code row.
    raw = b'\xdd\x05' + bytes(4) + b'\xc3' + b'\xcc' * 9 + b'\x90' * 7 + b'\xc3'
    caller(case, raw, [(2, '_helper', lc.DIR32)], [('_helper', 1, 16, lc.STATIC)])
    case.rows[0]['target_size'] = '7'
    pointer(case, 2, F + 16, F + 16)
    _, row = outcome(case)
    assert row['closed_strict'] == '0'
