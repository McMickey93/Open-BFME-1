"""Round-3 nearby controls for fixed classes and A-F admission boundaries."""
import itertools

import pytest

from test_cycle_review2c_evidence import case, caller, pointer, outcome
from test_cycle_review2_evidence import F, A, DATA, RDATA, dword, lc


@pytest.mark.parametrize('branch', ['call', 'jmp'])
def test_distinct_ilt_routes_to_one_body_remain_allowed(case, branch):
    leaf = case.object('leaf.obj', [('.text', b'\xc3', [])], [('_a', 1, 0, lc.EXTERNAL)])
    case.row(leaf, '_a', A, 1)
    case.public(leaf, '_a', A)
    case.put(A, b'\xc3', retail=b'\xc3')
    opcode, tail = (b'\xe8', b'\xc3') if branch == 'call' else (b'\xe9', b'')
    for i, thunk in enumerate((0x20000, 0x20010)):
        at, name = F+i*16, f'_caller{i}'
        case.R[thunk:thunk+5] = b'\xe9' + dword(A-thunk-5)
        obj = case.object(f'caller{i}.obj', [('.text', opcode+bytes(4)+tail, [(1, '_a', lc.REL32)])],
                          [(name, 1, 0, lc.EXTERNAL), ('_a', 0, 0, lc.EXTERNAL)])
        case.row(obj, name, at, 5+len(tail))
        case.public(obj, name, at)
        case.put(at, opcode+dword(A-at-5)+tail, retail=opcode+dword(thunk-at-5)+tail)
    result, rows = case.measure()
    assert result['credit_unique_bytes'] == 11+2*len(tail)
    assert all(row['closed_strict'] == '1' for row in rows)


@pytest.mark.parametrize('reverse', [False, True])
@pytest.mark.parametrize('order', list(itertools.permutations(range(3))))
def test_pointer_identity_settles_all_users_independently_of_discovery_order(reverse, order):
    m = lc.Measure.__new__(lc.Measure)
    m._init_state()
    m.ilt_body = lambda target: 200  # Three allowed routes to the same body.
    refs = [(100, 200), (100, 204), (100, 208)]
    if reverse:
        refs = [(r, l) for l, r in refs]
    failures = [[], [], []]
    for n in order:
        m.code_identity(*refs[n], pointer=True, fails=failures[n])
    m.settle_code_identities()
    assert all(failures)


@pytest.mark.parametrize('note', ['gen-funclet', 'gen-import', 'gen-alias'])
def test_generated_note_on_an_ordinary_source_path_still_blocks_callers(case, note):
    obj = case.object('leaf.obj', [('.text', b'\xc3', [])], [('_a', 1, 0, lc.EXTERNAL)])
    case.row(obj, '_a', A, 1, source='game/ordinary.cpp', notes=note)
    case.public(obj, '_a', A)
    case.put(A, b'\xc3', retail=b'\xc3')
    raw = b'\xe8' + bytes(4) + b'\xc3'
    caller(case, raw, [(1, '_a', lc.REL32)], [('_a', 0, 0, lc.EXTERNAL)])
    case.put(F, b'\xe8' + dword(A-F-5) + b'\xc3', retail=b'\xe8' + dword(A-F-5) + b'\xc3')
    _, row = outcome(case)
    assert row['closed_strict'] == '0'


def test_literal_pointer_in_a_later_indirect_entry_is_refused(case):
    raw = b'\xc3\xa1' + dword(lc.BASE+DATA) + b'\xc3'
    obj = case.object('leaf.obj', [('.text', raw, [])], [('_a', 1, 0, lc.EXTERNAL)])
    case.row(obj, '_a', A, len(raw))
    case.public(obj, '_a', A)
    case.put(A, raw, retail=raw)
    case.put(DATA, dword(2), retail=dword(1))
    caller(case, b'\xb8'+dword(1)+b'\xff\xd0\xc3', [(1, '_a', lc.DIR32)], [('_a', 0, 0, lc.EXTERNAL)])
    pointer(case, 1, A+1, A+1)
    case.R[:2] = b'MZ'
    case.patch.setattr(lc.retail_relocs, 'site_rvas', lambda: (A+2, F+1))
    _, row = outcome(case)
    assert row['closed_strict'] == '0'


def test_cc_exclusion_also_matches_bfme1_for_an_operand_byte(case):
    # BFME1's rule excludes *every* retail CC byte, including immediate values.
    raw = b'\x68' + dword(0xcc) + b'\x58\xc3' + b'\xcc'*5
    caller(case, raw, [], [])
    first, _ = outcome(case)
    assert first['credit_unique_bytes'] == 6
    case.rows[0]['target_size'] = '7'
    second, _ = outcome(case)
    assert second['credit_unique_bytes'] == 6


@pytest.mark.parametrize('age,offset,allowed', [(86400, 0, True), (86400.01, 0, False),
                                               (0, 600, True), (0, 600.01, False)])
def test_authority_age_and_clock_skew_boundary(monkeypatch, age, offset, allowed):
    import cycle_artifacts as ca
    monkeypatch.setattr(ca, 'receipt_end', lambda receipt: 100000-age+offset)
    monkeypatch.setattr(ca, 'ancestry', lambda *args: (True, 0, 'known'))
    monkeypatch.setattr(ca, 'local_rules', lambda *args: 'rules')
    monkeypatch.setattr(ca, 'rules_of', lambda *args: 'rules')
    monkeypatch.setattr(ca, 'local_tool_digest', lambda *args: 'digest')
    fr = ca.freshness({'commit': 'f'*40}, now=100000)
    assert (ca.refusal(fr) is None) is allowed


def test_retail_datum_evidence_is_bound_even_when_absent(tmp_path):
    import link_cycle_context as context
    reverse = tmp_path / 'targets/game/reverse'
    reverse.mkdir(parents=True)
    name = 'targets/game/reverse/retail_inventory/data_items.csv'
    assert context.input_hashes(tmp_path)[name] is None
    evidence = tmp_path / name
    evidence.parent.mkdir()
    evidence.write_text('rva,size\n0x81000,8\n')
    before = context.input_hashes(tmp_path)[name]
    evidence.write_text('rva,size\n0x81000,12\n')
    assert before != context.input_hashes(tmp_path)[name]
