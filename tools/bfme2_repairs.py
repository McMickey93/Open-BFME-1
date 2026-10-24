"""Scoped BFME 1 global-reference and row-rehoming repairs.

No census or full rebuild is started. --apply uses existing scoped verifiers;
default mode reports a patch or verified move plan without modifying sources.
"""
import argparse
import csv
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

import bfme2_workflow as work


def scoped_build(source):
    result = subprocess.run([sys.executable, str(work.ROOT / 'tools/build.py'), source], cwd=work.ROOT)
    if result.returncode:
        raise ValueError(f'scoped verification failed: {source}')


def source_path(value):
    path = (work.ROOT / value).resolve()
    if not path.is_relative_to((work.ROOT / 'game').resolve()) or path.suffix not in ('.cpp', '.c'):
        raise ValueError('repair source must be a non-generated game C/C++ unit')
    if any(part.startswith('gen_') or part == 'masm_dumps' for part in path.parts):
        raise ValueError('generated source cannot be repaired by this helper')
    return path


def claim_rows(rows):
    import claims
    result = claims.claim(sorted({int(r['target_rva'], 16) for r in rows}))
    if result.refused or not result.claimed:
        if result.claimed:
            claims.release(result.claimed, tokens=result.tokens)
        raise ValueError('could not claim every affected row; no repair applied')


def globals_repair(args):
    import build
    import bfme2_globals as engine
    path = source_path(args.source)
    index, providers = {}, {}
    data_path = work.ROOT / 'targets/game/reverse/data_rows.csv'
    for row in work.donor_tool.read_rows(data_path):
        if row['status'] != 'matched' or not engine.declare(row['name']):
            continue
        address = int(row['address'], 0)
        if row['address_kind'] == 'rva':
            address += work.Image(build.EXE).base
        index.setdefault(address, []).append(row['name'])
        providers[row['name']] = row['source']
    original = path.read_bytes()
    text = original.decode('utf-8-sig')
    changed, declarations = engine.safe_rewrite(text, index)
    if not declarations:
        print('No unambiguous typed global rewrite backed by the BFME 1 data ledger.')
        return
    print(''.join(difflib.unified_diff(text.splitlines(True), changed.splitlines(True),
                                     fromfile=args.source, tofile=args.source + ' (proposed)')))
    if not args.apply:
        return
    rows = [r for r in build.load_function_rows() if r['source'] == args.source]
    if not rows:
        raise ValueError('no matched source rows to claim/verify')
    claim_rows(rows)
    scoped_build(args.source)
    for provider in sorted({providers[s] for names in index.values() for s in names
                            if engine.declare(s)[0] in declarations}):
        scoped_build(provider)
    if path.read_bytes() != original:
        raise ValueError('source changed during preflight')
    proposed = changed.encode('utf-8')
    path.write_bytes(proposed)
    try:
        scoped_build(args.source)
    except BaseException:
        # Restore only if our proposed contents are still present.
        if path.read_bytes() == proposed:
            path.write_bytes(original)
        raise
    print('Applied and byte-verified; run link_check.py for the current provider/consumer verdict.')


def rehome(args):
    import build
    home, split = source_path(args.home), source_path(args.split)
    if home == split:
        raise ValueError('home and split must differ')
    rows = [r for r in build.load_function_rows() if r['source'] == args.split]
    if not rows:
        raise ValueError('split source owns no function rows')
    if args.apply:
        affected = rows + [r for r in build.load_function_rows() if r['source'] == args.home]
        claim_rows(affected)
    scoped_build(args.home)
    scoped_build(args.split)
    symbols = build.load_symbol_map()
    obj = build.obj_path(home)
    before = {str(home): work.digest(home), str(split): work.digest(split)}
    for row in rows:
        proof = build.compile_function(dict(row, source=args.home), symbols, obj)
        if proof['unresolved'] or proof['bytes'] != proof['target']:
            raise ValueError(f'home does not exactly verify {row["name"]}')
    print(json.dumps({'home': args.home, 'split': args.split, 'verified_rows': len(rows),
                      'next': 'add_match.py --replace-existing through normal gates; no source deletion by this helper'}))
    if not args.apply:
        return
    work.validate_receipt(before)
    for row in rows:
        command = [sys.executable, 'tools/add_match.py', row['name'], row['target_rva'],
                   row['target_size'], args.home, '--replace-existing', '--model', args.model,
                   '--notes', (row.get('notes') or '') + '; verified home copy from ' + args.split]
        result = subprocess.run(command, cwd=work.ROOT)
        if result.returncode:
            raise ValueError('rehome stopped; inspect already verified moves before retrying')
    print('Rows repointed through add_match.py. Inspect the emptied split TU before removing it; no automatic deletion.')


def land(args):
    path = source_path(args.source)
    evidence = (work.ROOT / args.evidence).resolve()
    if not evidence.is_relative_to((work.ROOT / 'targets/game/reverse').resolve()) or not evidence.is_file() or not evidence.read_text(encoding='utf-8').strip():
        raise ValueError('landing needs nonempty identity/boundary evidence under targets/game/reverse/')
    if args.rva < 0 or args.size < 1:
        raise ValueError('invalid extent')
    claim_rows([{'target_rva': hex(args.rva)}])
    command = [sys.executable, 'tools/add_match.py', args.name, hex(args.rva), str(args.size),
               args.source, '--model', args.model, '--notes', 'bfme2 donor evidence: ' + args.evidence]
    if args.replace_existing:
        command.append('--replace-existing')
    result = subprocess.run(command, cwd=work.ROOT)
    if result.returncode:
        raise ValueError('normal add_match verification rejected the landing')
    print('Verified row landed locally; claim remains held until publication. No commit or push performed.')


def naming(args):
    import name_lane
    source = source_path(args.source)
    donor_source = args.donor_source or 'Code/' + args.source[len('game/'):]
    context = work.donor_tool.source_context(work.DONOR, donor_source)
    if context is None:
        raise ValueError('donor source missing, generated or lifted; specify --donor-source if relocated')
    local = name_lane.declared(args.source, source.read_text(encoding='utf-8-sig'))
    donor_names = name_lane.declared(donor_source, (work.DONOR / donor_source).read_text(encoding='utf-8-sig'))
    print(json.dumps({'target': args.source, 'donor_revision':work.donor_tool.revision(work.DONOR),
                      'donor': context, 'local_placeholders': [(k,n) for k,n in local if name_lane.weak(k,n)],
                      'donor_declarations': donor_names,
                      'warning': 'Evidence review only. No votes submitted, role mappings or canonical names inferred. Do not show these hints to blind voting sessions.'}, indent=2))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('globals')
    p.add_argument('source')
    p.add_argument('--apply', action='store_true')
    p = sub.add_parser('rehome')
    p.add_argument('--home', required=True)
    p.add_argument('--split', required=True)
    p.add_argument('--apply', action='store_true')
    p.add_argument('--model', default='')
    p = sub.add_parser('land')
    p.add_argument('--source', required=True)
    p.add_argument('--name', required=True)
    p.add_argument('--rva', required=True, type=lambda value:int(value,0))
    p.add_argument('--size', required=True, type=int)
    p.add_argument('--evidence', required=True)
    p.add_argument('--model', required=True)
    p.add_argument('--replace-existing', action='store_true')
    p = sub.add_parser('naming')
    p.add_argument('--source', required=True)
    p.add_argument('--donor-source')
    args = ap.parse_args(argv)
    try:
        if args.command == 'land':
            land(args)
        elif args.command == 'naming':
            naming(args)
        elif args.command == 'globals':
            globals_repair(args)
        else:
            if args.apply and not args.model:
                raise ValueError('--model required when applying rehome')
            rehome(args)
    except (OSError, ValueError, KeyError) as error:
        ap.exit(2, f'bfme2_sweep: {error}\n')
    return 0
