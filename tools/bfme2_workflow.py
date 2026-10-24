"""BFME 1 donor binary search, private compilation and evidence packets.

Adapted from BFME 2's bfme1_sweep/zh_sweep workflow. Discovery is deliberately
separate from identity, boundary and relocation verification by add_match.py.
"""
import argparse
import collections
import hashlib
import json
import re
import shlex
import struct
import subprocess
import sys
import uuid
from pathlib import Path

import bfme2_sweep as donor_tool

ROOT = donor_tool.ROOT
DONOR = donor_tool.DONOR
OUT = ROOT / 'build/bfme2_sweep'
SCHEMA = 1


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def inputs():
    import build
    return [build.EXE, DONOR / 'baselines/bfme2/workshop-vanilla-1.06/files/game.dat',
            ROOT / 'targets/game/reverse/functions.csv', DONOR / 'reverse/functions.csv']


def receipt(paths):
    return {str(p.resolve()): digest(p) for p in paths}


def validate_receipt(stamps):
    for path, expected in stamps.items():
        if not Path(path).is_file() or digest(Path(path)) != expected:
            raise ValueError(f'stale inputs: {path}; rerun scan or compile/match')


class Image:
    def __init__(self, path):
        import build
        self.data = path.read_bytes()
        self.sections = build.pe_sections(self.data)
        pe = struct.unpack_from('<I', self.data, 0x3c)[0]
        self.base = struct.unpack_from('<I', self.data, pe + 24 + 28)[0]
        self.size = struct.unpack_from('<I', self.data, pe + 24 + 56)[0]
        section = next(s for s in self.sections if s['name'] == '.text')
        self.rva = section['rva']
        self.text = self.data[section['raw_pointer']:section['raw_pointer'] + section['size']]

    def body(self, rva, size):
        at = rva - self.rva
        if at < 0 or at + size > len(self.text):
            raise ValueError('body is not wholly inside .text')
        return self.text[at:at + size]

    def in_text(self, rva):
        return self.rva <= rva < self.rva + len(self.text)

    def in_image(self, va):
        return self.base <= va < self.base + self.size

    def string(self, va):
        import build
        try:
            at = build.rva_to_file_offset(self.sections, va - self.base)
            end = self.data.index(b'\0', at, at + 256)
            value = self.data[at:end]
            return value.decode('ascii') if len(value) >= 4 and all(32 <= b < 127 for b in value) else None
        except (ValueError, IndexError):
            return None


def fields(body, rva, image):
    """Only decoded operand fields, never arbitrary four-byte sliding windows."""
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    out = {}
    consumed = 0
    for ins in md.disasm(body, rva):
        consumed += ins.size
        pos = ins.address - rva
        raw = ins.bytes
        if (raw[0] in (0xe8, 0xe9) or raw[:1] == b'\x0f' and len(raw) > 1 and 0x80 <= raw[1] <= 0x8f):
            if ins.imm_size == 4:
                off = pos + ins.imm_offset
                dest = (rva + off + 4 + struct.unpack_from('<i', body, off)[0]) & 0xffffffff
                if image.in_text(dest):
                    out[off] = 'rel32'
        else:
            for off, size in ((ins.disp_offset, ins.disp_size), (ins.imm_offset, ins.imm_size)):
                if size == 4 and image.in_image(struct.unpack_from('<I', body, pos + off)[0]):
                    out[pos + off] = 'dir32'
    return out, consumed == len(body)


def compare(body, window, relocations, donor_rva, target_rva, donor_image, target_image):
    """Return stable-byte similarity and evidence; masked fields need both sides valid."""
    if len(window) != len(body):
        return 0, [], []
    holes = set()
    relations, conflicts = [], []
    for off, kind in relocations.items():
        if off < 0 or off + 4 > len(body):
            raise ValueError('relocation outside body')
        a = struct.unpack_from('<I', body, off)[0]
        b = struct.unpack_from('<I', window, off)[0]
        if kind == 'rel32':
            a = (donor_rva + off + 4 + struct.unpack_from('<i', body, off)[0]) & 0xffffffff
            b = (target_rva + off + 4 + struct.unpack_from('<i', window, off)[0]) & 0xffffffff
            valid = donor_image.in_text(a) and target_image.in_text(b)
        else:
            valid = donor_image.in_image(a) and target_image.in_image(b)
            sa, sb = donor_image.string(a), target_image.string(b)
            if sa and sb and sa != sb:
                conflicts.append({'offset': off, 'donor': sa, 'target': sb})
        if valid:
            holes.update(range(off, off + 4))
            relations.append({'offset': off, 'kind': kind, 'donor': a, 'target': b})
    stable = [i for i in range(len(body)) if i not in holes]
    score = sum(body[i] == window[i] for i in stable) / len(stable) if len(stable) >= 8 else 0
    return score, relations, conflicts


def search(body, relocations, target, donor_image, donor_rva, cap=8192):
    holes = {i for off in relocations for i in range(off, off + 4)}
    runs, start = [], None
    for i in range(len(body) + 1):
        if i < len(body) and i not in holes:
            if start is None:
                start = i
        elif start is not None:
            runs.append((i - start, start))
            start = None
    candidates, truncated = set(), False
    anchors = []
    for length, off in sorted(runs, reverse=True)[:3]:
        if length >= 6:
            width = min(length, 12)
            for anchor in sorted({off, off + (length - width) // 2, off + length - width}):
                anchors.append((anchor, width))
    for off, width in anchors:
        needle = body[off:off + width]
        at = target.text.find(needle)
        while at >= 0:
            candidate = at - off
            if 0 <= candidate <= len(target.text) - len(body):
                candidates.add(candidate)
            if len(candidates) >= cap:
                truncated = True
                break
            at = target.text.find(needle, at + 1)
        if truncated:
            break
    matches = []
    for pos in sorted(candidates):
        window = target.text[pos:pos + len(body)]
        score, relations, conflicts = compare(body, window, relocations, donor_rva,
                                               target.rva + pos, donor_image, target)
        if score >= .90:
            matches.append(dict(rva=target.rva + pos, size=len(body), score=score,
                                relations=relations, string_conflicts=conflicts))
    exact_count = sum(m['score'] == 1 for m in matches)
    for match in matches:
        match['bucket'] = ('truncated' if truncated else 'string-conflict' if match['string_conflicts'] else
                           'exact-unique' if match['score'] == 1 and exact_count == 1 else
                           'exact-multi' if match['score'] == 1 else 'near')
    return matches, truncated


def scan(args):
    paths = inputs() + [Path(__file__), ROOT / 'tools/bfme2_sweep.py']
    before = receipt(paths)
    target, donor_image = Image(paths[0]), Image(paths[1])
    source_stamps, contexts, records, seen = {}, {}, [], set()
    aliases = collections.defaultdict(set)
    for alias_row in donor_tool.read_rows(paths[3]):
        aliases[int(alias_row['target_rva'], 16)].add(alias_row['name'])
    used = 0
    for row in donor_tool.read_rows(paths[3]):
        source = row['source']
        size, rva = int(row['target_size']), int(row['target_rva'], 16)
        if row['status'] != 'matched' or size < args.min_size or size > args.max_size:
            continue
        if args.source and source != args.source:
            continue
        if source not in contexts:
            contexts[source] = donor_tool.source_context(DONOR, source)
        if not contexts[source] or (source, rva, row['name']) in seen:
            continue
        seen.add((source, rva, row['name']))
        source_stamps[str((DONOR / source).resolve())] = digest(DONOR / source)
        try:
            body = donor_image.body(rva, size)
        except ValueError:
            continue
        relocs, decoded = fields(body, rva, donor_image)
        if not decoded:
            continue
        matches, truncated = search(body, relocs, target, donor_image, rva, args.candidate_cap)
        for match in matches:
            records.append(dict(match, name=row['name'], source=source, donor_rva=rva,
                                donor_aliases=sorted(aliases[rva])))
        used += 1
        if used % 100 == 0:
            print(f'scan: {used} donor bodies, {len(records)} placements', file=sys.stderr, flush=True)
        if args.limit and used >= args.limit:
            break
    validate_receipt(before)
    validate_receipt(source_stamps)
    payload = dict(schema=SCHEMA, inputs=dict(before, **source_stamps), bodies_scanned=used,
                   exhaustive=False, scope='anchor search; near matches may be missed; identity unverified', records=records)
    write_json(OUT / 'binary.json', payload)
    print(json.dumps({'bodies_scanned': used, 'placements': len(records),
                      'buckets': dict(collections.Counter(r['bucket'] for r in records))}))


def current_work(records, offline=False):
    import eligibility
    import claims
    rows = eligibility.load_rows()
    verdicts = eligibility.latest_verdicts()
    # Banked dumps are already included by open_dumps. Re-running finish_bodies
    # here scanned every bank a second time for no additional eligible RVAs.
    opened = {eligibility.rva_of(r) for r in eligibility.open_dumps(rows=rows, latest=verdicts, include_carved=True)}
    known = {eligibility.rva_of(r): r for r in rows}
    if not offline and not claims.fetch():
        raise ValueError('shared claims unavailable; use --offline for inspection only')
    live = {} if offline else {r: info for r, (_, info) in claims.live(claims._read_local()).items()}
    result = []
    for record in records:
        rva = record['rva']
        row = known.get(rva)
        item = dict(record, target_row=row, eligible=rva in opened,
                    claim_state='unknown' if offline else live.get(rva),
                    latest_verdict=verdicts.get(rva))
        # Discovery at unknown boundaries stays an inspection lead, never auto-served.
        item['servable'] = (not offline and rva in opened and rva not in live
                            and row is not None and int(row['target_size']) == record['size']
                            and record['bucket'] not in ('truncated', 'string-conflict', 'exact-multi', 'object-exact-multi')
                            and len(record.get('donor_aliases', [])) <= 1)
        result.append(item)
    return result


def load_binary(path=None):
    value = json.loads((path or OUT / 'binary.json').read_text(encoding='utf-8'))
    if value['schema'] != SCHEMA:
        raise ValueError('sweep schema changed; rerun scan')
    validate_receipt(value['inputs'])
    return value


def packets(args):
    payload = load_binary(args.matches)
    records = payload['records']
    if args.command == 'ranked':
        records = [r for r in records if r['bucket'] in ('exact-unique', 'object-exact-unique')]
    if args.command == 'near':
        records = [r for r in records if r['bucket'] == 'near']
    if args.rva is not None:
        records = [r for r in records if r['rva'] == args.rva]
    records = current_work(records, args.offline)
    records.sort(key=lambda r: (not r['servable'], -r['size'], -r['score'], r['rva']))
    selected = records[:args.limit] if args.limit else records
    # Do not expose naming hints as independent votes; these packets are evidence work.
    for item in selected:
        import eligibility
        item['banked_source'] = str((eligibility.stash(item['rva']) or ('', 0))[0])
        item['donor_context'] = donor_tool.source_context(DONOR, item['source'])
        token = f"0x{item['rva']:08x}"
        evidence = ROOT / 'targets/game/reverse/attempt_support'
        item['prior_evidence'] = [p.relative_to(ROOT).as_posix() for p in evidence.glob(token + '*')]
        item['instructions'] = ['Inspect donor revision, callers, literals and boundary evidence.',
                                'Reconcile layout, ABI, imports and thunk/body names.',
                                'Claim via claims.py before recovery; do not auto-land this packet.',
                                'Land through add_match.py and normal byte/link gates only.']
    if args.command == 'packets':
        for item in selected:
            key = hashlib.sha256((item['source'] + item['name']).encode()).hexdigest()[:12]
            write_json(OUT / 'packets' / f"{item['rva']:08x}-{key}.json", dict(inputs=payload['inputs'], **item))
    validate_receipt(payload['inputs'])
    print(json.dumps({'inspection_only': args.offline, 'total': len(records), 'entries': selected}, indent=2, default=str))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('scan')
    p.add_argument('--source')
    p.add_argument('--min-size', type=int, default=16)
    p.add_argument('--max-size', type=int, default=4000)
    p.add_argument('--limit', type=int, default=0)
    p.add_argument('--candidate-cap', type=int, default=8192)
    for name in ('ranked', 'near', 'show', 'packets'):
        p = sub.add_parser(name)
        p.add_argument('--rva', type=lambda s: int(s, 0))
        p.add_argument('--limit', type=int, default=20)
        p.add_argument('--offline', action='store_true')
        p.add_argument('--matches', type=Path, help='compile/match output instead of binary scan')
    args = ap.parse_args(argv)
    try:
        if args.command == 'scan':
            if args.min_size < 8 or args.max_size < args.min_size or args.limit < 0 or args.candidate_cap < 2:
                raise ValueError('invalid search bounds')
            scan(args)
        else:
            packets(args)
    except (OSError, ValueError, KeyError) as error:
        ap.exit(2, f'bfme2_sweep: {error}\n')


if __name__ == '__main__':
    main(sys.argv[1:])
