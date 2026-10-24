import json
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bfme2_workflow as work
import bfme2_trial as trial
import bfme2_globals as globals_engine


class FakeImage:
    rva = 0x1000
    base = 0x400000
    def __init__(self, text, strings=None):
        self.text = text
        self.strings = strings or {}
    def in_text(self, rva):
        return 0x1000 <= rva < 0x2000
    def in_image(self, va):
        return 0x400000 <= va < 0x500000
    def string(self, va):
        return self.strings.get(va)


BODY = bytes.fromhex('558bec83ec105356578b45088b4d0c33c05f5e5bc9c3')


def test_binary_search_preserves_ambiguity_and_capped_search_is_never_unique():
    donor = FakeImage(BODY)
    target = FakeImage(BODY + b'\xcc' * 8 + BODY)
    matches, truncated = work.search(BODY, {}, target, donor, 0x1000)
    assert not truncated and len(matches) == 2
    assert {m['bucket'] for m in matches} == {'exact-multi'}
    matches, truncated = work.search(BODY, {}, target, donor, 0x1000, cap=1)
    assert truncated and {m['bucket'] for m in matches} == {'truncated'}


def test_near_match_keeps_real_opcode_difference():
    changed = bytearray(BODY)
    changed[2] ^= 1
    matches, _ = work.search(BODY, {}, FakeImage(bytes(changed)), FakeImage(BODY), 0x1000)
    assert matches and matches[0]['bucket'] == 'near'
    assert matches[0]['score'] < 1


def test_invalid_target_address_cannot_be_masked_away():
    original = BODY + struct.pack('<I', 0x401000)
    target = BODY + struct.pack('<I', 0xDEADBEEF)
    score, relations, _ = work.compare(original, target, {len(BODY): 'dir32'},
                                     0x1000, 0x1000, FakeImage(original), FakeImage(target))
    assert score < 1 and relations == []


def test_different_string_targets_are_held_even_with_identical_code():
    original = BODY + struct.pack('<I', 0x401000)
    target = BODY + struct.pack('<I', 0x402000)
    a = FakeImage(original, {0x401000:'RoleAlpha'})
    b = FakeImage(target, {0x402000:'RoleBeta'})
    score, _, conflicts = work.compare(original, target, {len(BODY): 'dir32'}, 0x1000, 0x1000, a, b)
    assert score == 1 and conflicts
    matches, _ = work.search(original, {len(BODY):'dir32'}, b, a, 0x1000)
    assert matches[0]['bucket'] == 'string-conflict'


def test_decoding_does_not_find_calls_inside_mov_immediates():
    # E8 is an immediate byte, not an opcode; only the literal VA is eligible.
    body = bytes.fromhex('b8e8104000c3')
    fields, decoded = work.fields(body, 0x1000, FakeImage(body))
    assert decoded and fields == {1:'dir32'}


def test_stale_source_receipt_is_rejected(tmp_path):
    source=tmp_path/'a.cpp'; source.write_text('one')
    stamps=work.receipt([source]); source.write_text('two')
    with pytest.raises(ValueError, match='stale inputs'):
        work.validate_receipt(stamps)


def test_reverse_layout_mapping_never_uses_nested_reference(tmp_path):
    root=tmp_path/'bfme1'; donor=root/'donor'
    (root/'inputs/reference/zh').mkdir(parents=True)
    mapped=trial.mapped_path('reference/open-bfme-1/reference/zh', root, donor, {})
    assert mapped == (root/'inputs/reference/zh').resolve()
    with pytest.raises(ValueError, match='missing'):
        trial.mapped_path('reference/shims/not-present',root,donor,{})
    with pytest.raises(ValueError):
        trial.mapped_path('../escape',root,donor,{})


def test_explicit_mapping_and_quoted_flags_preserve_context(tmp_path):
    root=tmp_path/'bfme1'; donor=root/'donor'
    (root/'inputs/reference/shims/local').mkdir(parents=True)
    flags, includes=trial.flags_from('// cl: /O1 /MD /I"reference/shims/a b"', root, donor,
                                    {'reference/shims/a b':'inputs/reference/shims/local'})
    assert flags == ['-O1','-MD']
    assert includes == [(root/'inputs/reference/shims/local').resolve()]
    with pytest.raises(ValueError, match='compiler control'):
        trial.flags_from('// cl: /Fooutside.obj',root,donor,{})


def test_global_rewrite_preserves_literals_comments_and_refuses_ambiguity():
    text='// (*(int *)0x00401000)\nconst char *s="(*(int *)0x00401000)";\nint f() { return (*(int *)0x00401000); }\n'
    changed, declarations=globals_engine.safe_rewrite(text,{0x401000:['?TheCount@@3HA']})
    assert '// (*(int *)0x00401000)' in changed
    assert '"(*(int *)0x00401000)"' in changed
    assert 'return TheCount;' in changed and 'TheCount' in declarations
    unchanged, declarations=globals_engine.safe_rewrite(text,{0x401000:['?A@@3HA','?B@@3HA']})
    assert unchanged == text and declarations == {}


def test_global_rewrite_never_creates_vtable_aliases():
    text='unsigned table=0x00401000;\n'
    changed, declarations=globals_engine.safe_rewrite(text,{0x401000:['??_7Owner@@6B@']})
    assert changed == text and not declarations


def test_no_current_claims_is_not_permission_to_serve(monkeypatch):
    import eligibility
    import claims
    monkeypatch.setattr(eligibility,'load_rows',lambda:[])
    monkeypatch.setattr(eligibility,'open_dumps',lambda **kw:[])
    monkeypatch.setattr(eligibility,'finish_bodies',lambda **kw:[])
    monkeypatch.setattr(eligibility,'latest_verdicts',lambda:{})
    monkeypatch.setattr(claims,'fetch',lambda:False)
    with pytest.raises(ValueError, match='claims unavailable'):
        work.current_work([],False)
    assert work.current_work([],True) == []


def test_open_row_with_wrong_extent_is_not_served(monkeypatch):
    import eligibility
    import claims
    row={'target_rva':'0x1000','target_size':'20','name':'placeholder'}
    monkeypatch.setattr(eligibility,'load_rows',lambda:[row])
    monkeypatch.setattr(eligibility,'open_dumps',lambda **kw:[row])
    monkeypatch.setattr(eligibility,'finish_bodies',lambda **kw:[])
    monkeypatch.setattr(eligibility,'latest_verdicts',lambda:{})
    monkeypatch.setattr(eligibility,'stash',lambda r:None)
    monkeypatch.setattr(claims,'fetch',lambda:True)
    monkeypatch.setattr(claims,'_read_local',lambda:{})
    record=dict(rva=0x1000,size=21,bucket='exact-unique')
    assert not work.current_work([record])[0]['servable']


def test_existing_claim_prevents_serving_even_exact_match(monkeypatch):
    import eligibility
    import claims
    row={'target_rva':'0x1000','target_size':'20','name':'placeholder'}
    monkeypatch.setattr(eligibility,'load_rows',lambda:[row])
    monkeypatch.setattr(eligibility,'open_dumps',lambda **kw:[row])
    monkeypatch.setattr(eligibility,'finish_bodies',lambda **kw:[])
    monkeypatch.setattr(eligibility,'latest_verdicts',lambda:{})
    monkeypatch.setattr(eligibility,'stash',lambda r:None)
    monkeypatch.setattr(claims,'fetch',lambda:True)
    monkeypatch.setattr(claims,'_read_local',lambda:{0x1000:('sha',{'expires':1e30,'owner':'other'})})
    assert not work.current_work([dict(rva=0x1000,size=20,bucket='exact-unique')])[0]['servable']


@pytest.mark.parametrize('newline', [b'\n', b'\r\n'])
def test_global_failed_verification_restores_only_our_edit(tmp_path, monkeypatch, newline):
    import argparse
    import build
    import bfme2_repairs as repair
    monkeypatch.setattr(work, 'ROOT', tmp_path)
    path=tmp_path/'game/GameEngine/a.cpp'; path.parent.mkdir(parents=True)
    original=b'int f() { return (*(int *)0x00401000); }' + newline
    path.write_bytes(original)
    data=tmp_path/'targets/game/reverse/data_rows.csv'; data.parent.mkdir(parents=True)
    data.write_text('name,address,address_kind,status,source\n?TheCount@@3HA,0x00401000,va,matched,game/provider.cpp\n')
    monkeypatch.setattr(build,'load_function_rows',lambda:[{'source':'game/GameEngine/a.cpp','target_rva':'0x1000'}])
    monkeypatch.setattr(repair,'claim_rows',lambda rows:None)
    calls=[]
    def verify(source):
        calls.append(source)
        if len(calls)==3:
            raise ValueError('deliberate mismatch')
    monkeypatch.setattr(repair,'scoped_build',verify)
    with pytest.raises(ValueError,match='deliberate mismatch'):
        repair.globals_repair(argparse.Namespace(source='game/GameEngine/a.cpp',apply=True))
    assert path.read_bytes()==original
    assert calls==['game/GameEngine/a.cpp','game/provider.cpp','game/GameEngine/a.cpp']


def test_rehome_rejects_nonexact_home_without_repointing(tmp_path, monkeypatch):
    import argparse
    import build
    import bfme2_repairs as repair
    monkeypatch.setattr(work,'ROOT',tmp_path)
    for name in ('home.cpp','split.cpp'):
        p=tmp_path/'game/GameEngine'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('void f() {}')
    monkeypatch.setattr(build,'load_function_rows',lambda:[{'source':'game/GameEngine/split.cpp','name':'f'}])
    monkeypatch.setattr(repair,'scoped_build',lambda source:None)
    monkeypatch.setattr(build,'load_symbol_map',lambda:{})
    monkeypatch.setattr(build,'obj_path',lambda source:tmp_path/'home.obj')
    monkeypatch.setattr(build,'compile_function',lambda *args:{'unresolved':[],'bytes':b'a','target':b'b'})
    with pytest.raises(ValueError,match='does not exactly verify'):
        repair.rehome(argparse.Namespace(home='game/GameEngine/home.cpp',split='game/GameEngine/split.cpp',apply=False))


def test_landing_requires_identity_evidence_before_claiming(tmp_path,monkeypatch):
    import argparse
    import bfme2_repairs as repair
    monkeypatch.setattr(work,'ROOT',tmp_path)
    p=tmp_path/'game/GameEngine/a.cpp';p.parent.mkdir(parents=True);p.write_text('int f(){return 0;}')
    monkeypatch.setattr(repair,'claim_rows',lambda rows:pytest.fail('must not claim without evidence'))
    with pytest.raises(ValueError,match='nonempty identity'):
        repair.land(argparse.Namespace(source='game/GameEngine/a.cpp',evidence='missing.md'))


def test_partial_claim_failure_releases_only_newly_acquired_claims(monkeypatch):
    import claims
    import bfme2_repairs as repair
    released=[]
    monkeypatch.setattr(claims,'claim',lambda rows:claims.ClaimResult([0x1000],[0x2000],tokens={0x1000:'token'}))
    monkeypatch.setattr(claims,'release',lambda rows,**kw:released.append((rows,kw)))
    with pytest.raises(ValueError,match='claim every'):
        repair.claim_rows([{'target_rva':'0x1000'},{'target_rva':'0x2000'}])
    assert released==[([0x1000],{'tokens':{0x1000:'token'}})]


def test_compiled_object_change_refuses_match_before_search(tmp_path,monkeypatch):
    import argparse
    obj=tmp_path/'donor.obj';obj.write_bytes(b'old')
    manifest=tmp_path/'trial.json'
    manifest.write_text(json.dumps(dict(schema=work.SCHEMA,status='compiled',inputs={},object=str(obj),object_hash=work.digest(obj))))
    obj.write_bytes(b'changed')
    with pytest.raises(ValueError,match='object changed'):
        trial.match_trial(argparse.Namespace(trial=manifest,min_size=16))
