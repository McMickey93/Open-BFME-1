"""Private donor compilation and COFF placement using BFME 1's compiler APIs."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

import bfme2_sweep as donor_tool
import bfme2_workflow as work


def mapped_path(value, root, donor, mappings):
    value = value.replace('\\', '/').strip('"')
    if Path(value).is_absolute() or '..' in Path(value).parts:
        raise ValueError(f'absolute or parent-relative include requires an explicit normalized mapping: {value}')
    for before, after in sorted(mappings.items(), key=lambda pair: -len(pair[0])):
        if value == before or value.startswith(before.rstrip('/') + '/'):
            result = root / after / value[len(before):].lstrip('/')
            break
    else:
        prefix = 'reference/open-bfme-1/'
        if value.startswith(prefix):
            tail = value[len(prefix):]
            for old, new in (('reference/', 'inputs/reference/'), ('Code/', 'game/'),
                             ('vendor/', 'inputs/vendor/'), ('build/toolchains/', 'inputs/toolchains/')):
                if tail.startswith(old):
                    tail = new + tail[len(old):]
                    break
            result = root / tail
        elif value.startswith('vendor/'):
            result = root / 'inputs' / value
        else:
            result = donor / value
    result = result.resolve()
    if not any(result.is_relative_to(base.resolve()) for base in (root, donor)):
        raise ValueError(f'include mapping escapes the repositories: {result}')
    if not result.is_dir():
        raise ValueError(f'include directory missing: {value} -> {result}; supply --map JSON')
    if (donor / 'reference/open-bfme-1').resolve() in result.parents or result == (donor / 'reference/open-bfme-1').resolve():
        raise ValueError('nested BFME 1 reference is forbidden')
    return result


def flags_from(text, root, donor, mappings):
    directives = re.findall(r'^// cl:(.*)$', text, re.M)
    if len(set(directives)) > 1:
        raise ValueError('conflicting compiler directives')
    # Preserve quoted compiler arguments as single tokens (including /I"a b").
    tokens = re.findall(r'(?:[^\s"]|"[^"]*")+', directives[0] if directives else '')
    flags, includes = [], []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith(('/I', '-I')):
            path = token[2:]
            if not path:
                i += 1
                if i >= len(tokens):
                    raise ValueError('missing /I argument')
                path = tokens[i]
            includes.append(mapped_path(path, root, donor, mappings))
        else:
            # Output/forced-input/PCH flags or response files must not redirect trials.
            if token.startswith('@') or re.match(r'(?i)^[-/](?:F[AIoepd]|Y[cu]|link)', token):
                raise ValueError(f'unsupported donor compiler control: {token}')
            flags.append('-' + token[1:] if token.startswith('/') else token)
        i += 1
    return flags, includes


def compile_trial(args):
    import build
    source = work.DONOR / args.source
    if donor_tool.source_context(work.DONOR, args.source) is None:
        raise ValueError('donor is missing, generated, lifted or outside supported roots')
    mappings = json.loads(args.map.read_text()) if args.map else {}
    if not isinstance(mappings, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in mappings.items()):
        raise ValueError('--map must be a JSON object of string path prefixes')
    text = source.read_text(encoding='utf-8-sig')
    flags, includes = flags_from(text, work.ROOT, work.DONOR, mappings)
    folder = work.OUT / 'trials' / uuid.uuid4().hex
    folder.mkdir(parents=True)
    # Rebase quoted includes to resolved originals. Their own relative includes
    # retain donor context. Any nested-reference dependency is rejected by trace.
    def include(match):
        name = match.group(1)
        found = next((p / name for p in [source.parent] + includes if (p / name).is_file()), None)
        if found is None:
            raise ValueError(f'quoted include unresolved: {name}')
        resolved = found.resolve()
        forbidden = (work.DONOR / 'reference/open-bfme-1').resolve()
        if resolved == forbidden or forbidden in resolved.parents:
            raise ValueError(f'nested-reference include: {name}')
        return '#include "' + resolved.as_posix() + '"'
    staged = folder / source.name
    rewritten = re.sub(r'^\s*#\s*include\s*"([^"\n]+)"', include, text, flags=re.M)
    rewritten = re.sub(r'^// cl:.*$', '', rewritten, flags=re.M)
    # build.compiler_command supplies BFME 1's defaults; append donor settings
    # explicitly so quoting never passes through build.py's legacy split().
    staged.write_text(rewritten, encoding='utf-8')
    obj = folder / 'donor.obj'
    command, env = build.compiler_command(staged, obj)
    command = command[:-2] + flags + ['-I' + str(p) for p in includes] + ['-showIncludes'] + command[-2:]
    env.pop('CL', None)
    env.pop('_CL_', None)
    # Compiler host/SDK inputs are BFME 1's, never copied compiler overrides.
    stamps = work.receipt([source, work.ROOT / 'tools/build.py', work.ROOT / 'tools/bfme2_trial.py',
                           build.DEFAULT_VC71_ROOT / 'Vc7/bin/cl.exe'])
    completed = subprocess.run(command, cwd=work.ROOT, env=env, capture_output=True, text=True, errors='replace')
    log = completed.stdout + completed.stderr
    (folder / 'compile.log').write_text(log, encoding='utf-8')
    dependencies = []
    forbidden = (work.DONOR / 'reference/open-bfme-1').resolve()
    for line in log.splitlines():
        if 'including file:' in line:
            value = build._host_path(line.split('including file:', 1)[1].strip())
            if value and Path(value).is_file():
                path = Path(value).resolve()
                if path == forbidden or forbidden in path.parents:
                    raise ValueError(f'compile reached forbidden nested reference: {path}')
                dependencies.append(path)
    # A failed compile is an inspectable outcome, never cached as a success.
    status = 'compiled' if completed.returncode == 0 and obj.is_file() else 'failed'
    if status == 'compiled' and '#include' in text and not dependencies:
        raise ValueError('compiler emitted no dependency trace; cannot establish trial inputs')
    work.validate_receipt(stamps)
    stamps.update(work.receipt(dependencies + [staged]))
    if status == 'compiled' and dependencies:
        # Trace once, then prove the same complete dependency set stays stable
        # across a second compile. A post-hoc header hash alone is insufficient.
        second = subprocess.run(command, cwd=work.ROOT, env=env, capture_output=True, text=True, errors='replace')
        (folder / 'compile.log').write_text(second.stdout + second.stderr, encoding='utf-8')
        if second.returncode:
            raise ValueError('second dependency-stability compile failed')
        second_deps = set()
        for line in (second.stdout + second.stderr).splitlines():
            if 'including file:' in line:
                value = build._host_path(line.split('including file:', 1)[1].strip())
                if value:
                    second_deps.add(str(Path(value).resolve()))
        if second_deps != {str(p) for p in dependencies}:
            raise ValueError('header dependency set changed during trial')
        work.validate_receipt(stamps)
    payload = dict(schema=work.SCHEMA, status=status, returncode=completed.returncode,
                   source=args.source, object=str(obj), object_hash=work.digest(obj) if obj.is_file() else None,
                   command=command, include_dirs=[str(p) for p in includes],
                   dependencies=[str(p) for p in dependencies], inputs=stamps,
                   compiler_environment={k:env.get(k, '') for k in ('INCLUDE', 'LIB')})
    work.write_json(folder / 'trial.json', payload)
    print(json.dumps({'trial': str(folder / 'trial.json'), 'status': status,
                      'log': str(folder / 'compile.log')}, indent=2))
    return 0 if status == 'compiled' else 1


def match_trial(args):
    import build
    import zh_sweep
    trial = json.loads(args.trial.read_text())
    if trial['schema'] != work.SCHEMA or trial['status'] != 'compiled':
        raise ValueError('trial did not compile with this schema')
    work.validate_receipt(trial['inputs'])
    obj = Path(trial['object'])
    if work.digest(obj) != trial['object_hash']:
        raise ValueError('compiled trial object changed')
    target = work.Image(build.EXE)
    target_hash = work.digest(build.EXE)
    records = []
    for name, body, relocs in zh_sweep.carve(obj.read_bytes()):
        if len(body) < args.min_size:
            continue
        if any(kind not in (6, 20) or off < 0 or off + 4 > len(body) for off, kind, _ in relocs):
            continue
        masked, holes = zh_sweep.mask(body, relocs)
        matches = []
        for at in sorted(zh_sweep.placements(target.text, body, masked, holes)):
            score = zh_sweep.alignment(target.text[at:at + len(body)], masked, holes)
            if score >= .9:
                matches.append(dict(rva=target.rva + at, size=len(body), score=score))
        count = sum(m['score'] == 1 for m in matches)
        for m in matches:
            m.update(name=name, source=trial['source'], donor_rva=None,
                     bucket='object-exact-unique' if m['score'] == 1 and count == 1 else
                     'object-exact-multi' if m['score'] == 1 else 'near',
                     relocations=relocs, identity_verified=False)
            records.append(m)
    work.validate_receipt(trial['inputs'])
    if work.digest(build.EXE) != target_hash:
        raise ValueError('retail image moved during match')
    match_inputs = dict(trial['inputs'], **{str(build.EXE.resolve()):target_hash, str(obj.resolve()):trial['object_hash']})
    work.write_json(args.trial.parent / 'match.json', dict(schema=work.SCHEMA, inputs=match_inputs,
                    target_hash=target_hash, records=records,
                    warning='COFF relocation-masked placements; require boundary, identity and full relocation verification.'))
    print(json.dumps({'placements': len(records), 'buckets': dict(__import__('collections').Counter(r['bucket'] for r in records))}))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('compile')
    p.add_argument('source')
    p.add_argument('--map', type=Path, help='JSON donor include prefix -> BFME 1 root-relative directory')
    p = sub.add_parser('match')
    p.add_argument('trial', type=Path)
    p.add_argument('--min-size', type=int, default=16)
    args = ap.parse_args(argv)
    try:
        if args.command == 'compile':
            return compile_trial(args)
        if args.min_size < 8:
            raise ValueError('minimum size must be at least 8')
        match_trial(args)
    except (OSError, ValueError, KeyError) as error:
        ap.exit(2, f'bfme2_sweep: {error}\n')
    return 0
