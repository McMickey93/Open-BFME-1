"""Donor discovery must not confuse source leads with transferable identities."""
import csv
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bfme2_sweep as sweep


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_path_translation_rejects_generated_and_escape_paths():
    assert sweep.local_path('Code/GameEngine/A.cpp') == 'game/GameEngine/A.cpp'
    for path in ['Code/gen_small/a.cpp', 'Code/masm_dumps/a.asm', '../Code/GameEngine/a.cpp',
                 'Code/GameEngine/../../outside.cpp', '/Code/GameEngine/a.cpp']:
        assert sweep.local_path(path) is None


def test_link_packets_use_symbol_not_equal_rva_and_preserve_all_providers(tmp_path):
    root, donor = tmp_path/'local', tmp_path/'donor'
    provider = 'Code/GameEngine/A.cpp'
    path = donor/provider
    path.parent.mkdir(parents=True)
    path.write_text('// cl: /Ireference/open-bfme-1/Code\nint a() { return 1; }')
    write_csv(root/'targets/game/reverse/link_queue.csv', [
        dict(name='realName', kind='duplicates', bytes_unlocked='120', files='game/A.cpp;game/B.cpp', census='old'),
        dict(name='otherName', kind='unresolved', bytes_unlocked='500', files='game/C.cpp', census='old')])
    row = dict(name='realName', source=provider, target_rva='0x99', target_size='6')
    result = sweep.linking(root, donor, {'realName': [row,dict(row, target_rva='0x100')]}, {})
    assert len(result) == 1 and len(result[0]['providers']) == 2
    assert result[0]['target_files'] == ['game/A.cpp', 'game/B.cpp']
    assert result[0]['providers'][0]['donor_census_link_clean'] is None
    assert result[0]['providers'][0]['local_path_hint'] == 'game/GameEngine/A.cpp'
    assert result[0]['providers'][0]['compiler_directives']
    assert sweep.linking(root, donor, {'realName':[row]}, {}, 'otherName') == []


def test_lifted_missing_and_escaped_sources_are_not_served(tmp_path):
    path = tmp_path/'Code/GameEngine/lift.cpp'
    path.parent.mkdir(parents=True)
    path.write_text('__declspec(naked) void a() { __emit 0xc3; }')
    assert sweep.source_context(tmp_path, 'Code/GameEngine/lift.cpp') is None
    assert sweep.source_context(tmp_path, 'Code/GameEngine/missing.cpp') is None
    assert sweep.source_context(tmp_path, 'Code/GameEngine/../../outside.cpp') is None


def test_corresponding_sources_are_inspection_only_not_eligibility(tmp_path):
    root, donor = tmp_path/'local', tmp_path/'donor'
    source='Code/GameEngine/A.cpp'
    path=donor/source
    path.parent.mkdir(parents=True)
    path.write_text('int a() { return 1; }')
    write_csv(root/'targets/game/reverse/functions.csv', [dict(source='game/GameEngine/A.cpp', name='localOnly')])
    result=sweep.sources(root, donor, {source:[dict(name='donorOnly')]})
    assert len(result)==1 and result[0]['inspection_only']
    assert result[0]['shared_names']==[]
    assert 'eligibility.py' in result[0]['checks'][0]
