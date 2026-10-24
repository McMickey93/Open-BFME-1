#!/usr/bin/env python3
"""Read-only BFME 2 donor discovery for BFME 1.

  python3 tools/bfme2_sweep.py linking --limit 20
  python3 tools/bfme2_sweep.py sources --limit 20
  python3 tools/bfme2_sweep.py linking --symbol NAME --json build/donor.json

Additional commands: scan, ranked, near, show, packets, compile, match,
globals, rehome, naming and land. Each has --help. Discovery never initializes submodules.
ranked/packets refresh shared claims unless --offline (inspection only).
compile writes private objects; globals/rehome require --apply to edit code
or rows and use BFME 1 scoped verification and claims.
"""
import argparse
import csv
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONOR = ROOT / 'inputs/reference/open-bfme-2'
GENERATED = ('Code/gen_', 'Code/masm_dumps/', 'game/gen_', 'game/masm_dumps/')
ROOTS = ('Code/GameEngine/', 'Code/GameEngineDevice/', 'Code/Libraries/')


def read_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        yield from csv.DictReader(handle)


def local_path(source):
    parts = Path(source.replace('\\', '/')).parts
    if '..' in parts or not source.startswith(ROOTS):
        return None
    return 'game/' + source[len('Code/'):]


def source_context(donor, source):
    mapped = local_path(source)
    path = donor / source
    # Missing, escaping or lifted sources are never offered as portable C++.
    if not mapped or path.suffix.lower() not in ('.cpp', '.c'):
        return None
    try:
        path.resolve().relative_to(donor.resolve())
        text = path.read_text(encoding='utf-8-sig')
    except (OSError, ValueError):
        return None
    if re.search(r'__declspec\s*\(\s*naked\s*\)|\b(?:__emit|_emit|__asm|_asm)\b', text):
        return None
    return {'source': source, 'local_path_hint': mapped,
            'compiler_directives': re.findall(r'^// cl:.*$', text, re.M),
            'stlport_marker': bool(re.search(r'^// stlport\b', text, re.M)),
            'includes': re.findall(r'^\s*#\s*include\s*([^\n]+)', text, re.M),
            'warning': 'Map and verify includes/flags locally; path correspondence is not identity.'}


def donor_index(donor):
    names, sources = defaultdict(list), defaultdict(list)
    for row in read_rows(donor / 'reverse/functions.csv'):
        if row['status'] == 'matched' and local_path(row['source']):
            names[row['name']].append(row)
            sources[row['source']].append(row)
    status_path = donor / 'reverse/link_status.csv'
    status = {r['source']: r['linked'] == 'yes' for r in read_rows(status_path)} if status_path.exists() else {}
    return names, sources, status


def linking(root, donor, names, status, symbol=None):
    context = {}
    output = []
    for item in read_rows(root / 'targets/game/reverse/link_queue.csv'):
        if symbol and item['name'] != symbol:
            continue
        providers = []
        for row in names.get(item['name'], []):
            source = row['source']
            if source not in context:
                context[source] = source_context(donor, source)
            if context[source] is None:
                continue
            providers.append(dict(context[source], name=row['name'], donor_rva=row['target_rva'],
                                  donor_size=row['target_size'], donor_census_link_clean=status.get(source)))
        if providers:
            output.append({'name': item['name'], 'kind': item['kind'],
                           'estimated_bytes': int(item['bytes_unlocked']),
                           'target_files': item['files'].split(';'), 'census': item['census'],
                           'providers': providers,
                           'checks': ['Read prior BFME 1 attempts and check current claims.',
                                      'Prove identity, layout and thunk/body distinction in BFME 1.',
                                      'Inspect provider/consumer definitions and donor repair history.',
                                      'Verify affected bytes and current linking; census estimates may be stale.']})
    return sorted(output, key=lambda r: (-r['estimated_bytes'], r['name']))


def sources(root, donor, donor_sources):
    local = defaultdict(list)
    for row in read_rows(root / 'targets/game/reverse/functions.csv'):
        local[row['source']].append(row)
    output = []
    for source, rows in sorted(donor_sources.items()):
        mapped = local_path(source)
        if mapped not in local:
            continue
        context = source_context(donor, source)
        if context:
            target_names = {r['name'] for r in local[mapped]}
            output.append(dict(context, donor_rows=len(rows), local_rows=len(local[mapped]),
                               shared_names=sorted(target_names & {r['name'] for r in rows}),
                               inspection_only=True,
                               checks=['Use eligibility.py for open-work decisions, not this inventory.',
                                       'Compare donor bodies/headers and prior attempts before adapting.',
                                       'Same filename or symbol is not identity or byte proof.']))
    return output


def revision(path):
    result = subprocess.run(['git', '-c', 'safe.directory=' + path.resolve().as_posix(),
                             '-C', str(path), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else 'unavailable'


def main():
    import sys
    advanced = {'scan', 'ranked', 'near', 'show', 'packets', 'compile', 'match', 'globals', 'rehome', 'land', 'naming'}
    if len(sys.argv) > 1 and sys.argv[1] in advanced:
        if sys.argv[1] in {'compile', 'match'}:
            import bfme2_trial as runner
        elif sys.argv[1] in {'globals', 'rehome', 'land', 'naming'}:
            import bfme2_repairs as runner
        else:
            import bfme2_workflow as runner
        return runner.main(sys.argv[1:])
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('lane', choices=('linking', 'sources'))
    ap.add_argument('--limit', type=int, default=20)
    ap.add_argument('--symbol', help='exact mangled blocker name (linking only)')
    ap.add_argument('--json', type=Path, help='save the displayed packet; no persistent discovery cache')
    args = ap.parse_args()
    if args.limit < 1 or (args.symbol and args.lane != 'linking'):
        ap.error('limit must be positive; --symbol requires linking')
    try:
        names, donor_sources, status = donor_index(DONOR)
        entries = (linking(ROOT, DONOR, names, status, args.symbol) if args.lane == 'linking'
                   else sources(ROOT, DONOR, donor_sources))
        payload = {'lane': args.lane, 'target_revision': revision(ROOT),
                   'donor_revision': revision(DONOR), 'total_leads': len(entries),
                   'warning': 'Live working-tree inspection. Not a verified immutable snapshot; no bytes recovered or linked.',
                   'entries': entries[:args.limit]}
        rendered = json.dumps(payload, indent=2)
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered + '\n', encoding='utf-8')
        print(rendered)
    except (OSError, KeyError, ValueError) as exc:
        ap.exit(2, f'bfme2_sweep: {exc}\nInitialize only inputs/reference/open-bfme-2 without recursion.\n')


if __name__ == '__main__':
    raise SystemExit(main())
