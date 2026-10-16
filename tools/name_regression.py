#!/usr/bin/env python3
"""Preserve descriptive names across edits and bank-to-source conversions.

Usage: name_regression.py OLD NEW (NEW may be ':' for the index).
Unlike name_oracle, this compares history, not the witness's class-name key.
It checks explicit identifier substitutions, unambiguous computable layouts,
and single-row symbol changes at the same ledger address. It does not infer
semantic identity from a successful byte match.
"""
import argparse
import csv
import difflib
import hashlib
import io
import json
import re
import subprocess
from collections import defaultdict
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path

import abi_view
import name_oracle as oracle
import layout_history

ROOT = Path(__file__).resolve().parents[1]
CORRECTIONS = 'targets/game/reverse/name_corrections.json'
SOURCE = ('.cpp', '.cc', '.cxx', '.c', '.h', '.hh', '.hpp', '.hxx')
# The MSVC inline-assembly emission directive, in both spellings, is a
# compiler directive and not a name an author chose. Reading it as an
# identifier lets a lifted `_emit 0E9h` body align the directive against a
# member of the native body that replaced it and report the directive as
# renamed. `0E9h` is a MASM literal, not C++, so the trailing `h` is part of
# the literal too: without that alternative the tokenizer split it into an
# identifier and reported it against a member the same way.
# Integer suffixes belong to the literal, not to an author-chosen name.
# In particular, replacing a callback address such as 0x004063BBu with a
# relocatable j_XXXXXXXX reference must not report a rename of identifier u.
# Keep standalone identifiers (including u and L) subject to the usual rule.
INTEGER_SUFFIX = r'(?:[uU](?:ll|LL|[lL])?|(?:ll|LL|[lL])[uU]?)?'
TOKEN = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_]\w*|0[xX][0-9a-fA-F]+' + INTEGER_SUFFIX + r'|\d+[0-9A-Fa-f]*[hH]|\d+' + INTEGER_SUFFIX + r'|[^\s]', re.S)
IDENT = re.compile(r'^[A-Za-z_]\w*$')
OPAQUE = re.compile(
    r'^(?:Rva[0-9a-f]{8}|(?:d|dup|j|sub|FUN)_[0-9a-f]{8}|'
    r'Gen_?[0-9a-f]{8}|Gen_t_[0-9a-f]{8}|'
    r'(?:rva|func|fn)_?[0-9a-f]{8}|'
    # Glo<VA>: a type or datum named after the global's address, as
    # rename_addressed_sources.py already reads it (Glo012F4B98Type).
    r'Glo[0-9a-f]{8}|'
    # unidentified_<address>: the address-derived spelling 35 game/ TUs
    # already use for a callee whose identity is unproven
    # (unidentified_00380ee0, re_attempts 59731).
    r'unidentified_[0-9a-f]{8}(?![0-9a-z])|'
    # Rva<address> with the image-base leading zeros dropped, as Apt TUs
    # name types after their class address (Rva8CB820StringPool for
    # 0x008CB820; owner-queue row 123, re_attempts 0x008AD100).
    r'Rva[0-9a-f]{6,7}(?![0-9a-f])|'
    # Owner ruling 2026-10-09: bfme*/Bfme* names are converter-invented
    # placeholders, as ilt_oracle, name_lane and ilt_guard already treat them.
    r'_?bfme)', re.I)
KEYWORDS = set('void bool char short int long float double signed unsigned const volatile static extern class struct public private protected return true false nullptr typedef typename auto Bool Byte Short UnsignedByte UnsignedShort WideChar Int UnsignedInt UnsignedInt32 Real Int64 UnsignedInt64 _emit __emit'
               # MSVC keywords: an attribute, calling convention, sized integer,
               # inline assembly or SEH block names no entity (`__declspec` aligned
               # against an ILT ?j_ row's name in ten 10-12 commits).
               ' __declspec __cdecl __stdcall __fastcall __thiscall __inline __forceinline'
               ' __int8 __int16 __int32 __int64 __asm __try __except __finally inline virtual'.split())
ADDRESS = re.compile(r'(?:rva|0x|(?:^|_)\s*)([0-9a-f]{8})(?![0-9a-f])', re.I)


# Unlike the witness oracle's broad work-queue heuristic, a historical gate
# must not classify m_fieldOfView or m_reservedCapacity as unnamed storage.
FIELD_OPAQUE = re.compile(
    r"^m_(?:(?:unk(?:nown)?|unmodelled|field|pad(?:ding)?|slack|slot|reserved|unused|opaque)"
    r"(?:_?(?:0x)?[0-9a-fA-F]+)?"
    r"|(?:bfme)?(?:dword|word|byte|bool|int|float|short|ptr|hash|string|str|val|value)"
    r"(?:_?(?:0x)?[0-9][0-9a-fA-F]*)?"
    r"|(?:at|f|bfme|p)(?:0x)?[0-9][0-9a-fA-F]*"
    r"|(?:0x)?[0-9][0-9a-fA-F]*"
    # Owner ruling 2026-10-09: m_bfme* fields are converter-invented, like
    # the bfme*/Bfme* names OPAQUE already covers.
    r"|bfme\w*)$"
)


def opaque(name):
    return bool(OPAQUE.match(name) or FIELD_OPAQUE.fullmatch(name))


# Rva<address> with the leading zeros dropped is opaque on the NEW side only.
# As an OLD name it is the type an Apt TU already uses, so renaming it away is
# checked like a descriptive name; _without_respellings accepts a rename to a
# name the base ledger backs or that keeps the address.
SHORT_RVA = re.compile(r'^Rva([0-9a-f]{6,7})(?![0-9a-f])', re.I)


def _short_rva(name):
    return bool(SHORT_RVA.match(name)) and not re.match(r'^Rva[0-9a-f]{8}', name, re.I)


def downgrade(old, new):
    return (old != new and bool(IDENT.fullmatch(old)) and old not in KEYWORDS
            and (_short_rva(old) or not opaque(old)) and opaque(new))


# `#pragma comment(linker, ...)` and friends name no identifier: a bank that
# reached a thunk through /alternatename and a source that calls it directly
# aligned `comment` against the thunk and reported a rename (2026-09-28).
PRAGMA = re.compile(r'^[ \t]*#[ \t]*pragma\b[^\n]*', re.M)


# MSVC's `__identifier("Name")` spells the identifier Name; read it as one
# token, or a rename of it aligns `__identifier` against the new name.
MS_IDENTIFIER = re.compile(r'\b__identifier\s*\(\s*"([A-Za-z_]\w*)"\s*\)')


def _normalize(text):
    return MS_IDENTIFIER.sub(r'\1', PRAGMA.sub('', text))


def tokens(text):
    return [t for t in TOKEN.findall(_normalize(text)) if not t.startswith(('//', '/*', '"', "'"))]


# A function-like macro's parameter names whatever argument the expansion
# supplies; it names no entity. Expanding such a macro by hand aligns the
# parameter against the argument it stood for (`NAME` -> Rva00065A40), which
# is not a rename. Only occurrences inside their own #define are exempt: an
# identifier with the same spelling elsewhere is still checked.
FUNCTION_MACRO = re.compile(
    r'^[ \t]*#[ \t]*define[ \t]+[A-Za-z_]\w*\(([^)]*)\)(?:\\\r?\n|[^\n])*', re.M)


def macro_parameter_positions(text):
    """Token indices (as tokens() numbers them) of parameters in their #define."""
    stripped = _normalize(text)
    spans = [(m.start(), m.end(), {p.strip() for p in m[1].split(',')})
             for m in FUNCTION_MACRO.finditer(stripped)]
    found, index = set(), 0
    for m in TOKEN.finditer(stripped):
        if m[0].startswith(('//', '/*', '"', "'")):
            continue
        if any(start <= m.start() < end and m[0] in params for start, end, params in spans):
            found.add(index)
        index += 1
    return found


FUNCTION_DECL_TAIL = {
    ';', '{', '=', ':', 'const', 'volatile', 'noexcept', 'override',
    'final', 'try', '->',
}
FUNCTION_PREFIX_BLOCKERS = {
    '(', '[', '{', '}', ';', ',', '=', 'return', 'if', 'while', 'for',
    'switch', 'case', 'throw', 'new', 'delete', 'sizeof', 'decltype',
    '?', '.', '&', '*', '+', '-', '!', '~', '#',
}


def _paren_pairs(values):
    stack = []
    pairs = {}
    for index, value in enumerate(values):
        if value == '(':
            stack.append(index)
        elif value == ')' and stack:
            pairs[stack.pop()] = index
    return pairs


def _declaration_prefix(values, name_index):
    """Return the tokens before a possible qualified function name.

    A qualified call such as `Owner::run()` has no return-type prefix, while a
    definition such as `void Owner::run()` does.  Keeping that distinction
    prevents the declaration pass from pairing arbitrary calls.
    """
    start = name_index
    while (start >= 3 and values[start - 2:start] == [':', ':']
           and IDENT.fullmatch(values[start - 3])):
        start -= 3
    boundary = start - 1
    while boundary >= 0 and values[boundary] not in (';', '{', '}', '(', '[', ']', ','):
        boundary -= 1
    return values[boundary + 1:start]



def _is_function_declaration(values, name_index, open_index, close_index):
    name = values[name_index]
    if not IDENT.fullmatch(name) or name in KEYWORDS or name == 'operator':
        return False
    if name_index + 1 != open_index:
        return False
    previous = values[name_index - 1] if name_index else ''
    if previous in FUNCTION_PREFIX_BLOCKERS:
        return False
    if previous == '>' and name_index >= 2 and values[name_index - 2] == '-':
        return False
    if previous == ':' and not (name_index >= 2 and values[name_index - 2] == ':'):
        return False
    if previous == ':':
        prefix = _declaration_prefix(values, name_index)
        if not prefix or any(value in FUNCTION_PREFIX_BLOCKERS for value in prefix):
            return False
    if close_index + 1 < len(values) and values[close_index + 1] not in FUNCTION_DECL_TAIL:
        return False
    return True


def _function_declarations(values):
    declarations = {}
    for open_index, close_index in _paren_pairs(values).items():
        name_index = open_index - 1
        if name_index >= 0 and _is_function_declaration(
                values, name_index, open_index, close_index):
            declarations[name_index] = (open_index, close_index)
    return declarations


@lru_cache(maxsize=8)
def _token_opcodes(old, new):
    # regressions() and _equal_token_alignment() align the same token lists;
    # without autojunk this is quadratic in repeated tokens (an __emit lift is
    # thousands of them), so compute it once per pair.
    return tuple(difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes())


def _equal_token_alignment(old, new):
    alignment = {}
    for tag, a, b, c, d in _token_opcodes(tuple(old), tuple(new)):
        if tag == 'equal':
            alignment.update({a + offset: c + offset for offset in range(b - a)})
    return alignment


def _templated_type_declaration(values, name_index):
    """Whether a class/struct name immediately follows a template prefix."""
    if name_index < 2 or values[name_index - 1] not in ('class', 'struct'):
        return False
    end = name_index - 2
    if values[end] != '>':
        return False
    depth = 0
    for index in range(end, -1, -1):
        if values[index] == '>':
            depth += 1
        elif values[index] == '<':
            depth -= 1
            if depth == 0:
                return index > 0 and values[index - 1] == 'template'
    return False


def _function_declaration_regressions(old, new, exempt=frozenset()):
    """Find only declaration names whose parameter boundaries remain aligned.

    The ordinary token pass intentionally handles equal-sized identifier
    substitutions.  This narrower pass covers a declaration when a return
    type, storage class, or calling convention also changes and makes the
    surrounding replacement unequal.  Exact parameter tokens plus aligned
    opening and closing parentheses are required; there is no name-only
    pairing across removed/added functions or overloads.
    """
    old_declarations = _function_declarations(old)
    new_declarations = _function_declarations(new)
    alignment = _equal_token_alignment(old, new)
    found = set()
    for old_name_index, (old_open, old_close) in old_declarations.items():
        if old_name_index in exempt:
            continue
        new_open = alignment.get(old_open)
        new_close = alignment.get(old_close)
        if new_open is None or new_close is None:
            continue
        if old[old_open:old_close + 1] != new[new_open:new_close + 1]:
            continue
        candidates = [
            new_name_index for new_name_index, (candidate_open, candidate_close)
            in new_declarations.items()
            if candidate_open == new_open and candidate_close == new_close
            and downgrade(old[old_name_index], new[new_name_index])
        ]
        if len(candidates) == 1:
            found.add((old[old_name_index], new[candidates[0]]))
    return found


def layouts(text):
    # Strip prose/literals before looking for declarations; offset annotations
    # remain in the original input to the established layout walker.
    masked = TOKEN.sub(lambda m: ' ' * len(m[0]) if m[0].startswith(('//', '/*', '"', "'")) else m[0], text)
    result = {}
    for decl in oracle.DECL.finditer(masked):
        rows, refused = oracle.outer_members(text, decl.end() - 1, bool(decl.group('base')))
        if not refused and rows:
            result[decl[1]] = {off: (member, span, array) for member, off, _, _, span, array in rows}
    return result


def _shapes(found):
    return {owner: {off: value[1:] for off, value in fields.items()}
            for owner, fields in found.items()}


def _demonstrable_carrier(owner, retained):
    """Whether `owner` demonstrably left its file and can have become a target.

    A type that is still declared in the NEW snapshot of its own file did not
    move: another file merely borrowed its layout, so pairing the two invents a
    rename -- and a member rename -- for a type that never left.  That is the
    only evidence that positively identifies a non-carrier, and the caller
    collects it from the new snapshot of the paired path, not from the text
    being compared.

    A shared layout is otherwise not evidence either way.  When an edit drops
    several old types at once and the new file carries one of their layouts,
    which one moved is undecidable here; suppressing the pairings because the
    layout is ambiguous would discard the genuine rename instead, which is the
    one defect a regression gate must not make.  Every candidate is therefore
    reported, and an evidence-backed correction in
    targets/game/reverse/name_corrections.json closes a false one.
    """
    return owner not in retained


def regressions(before, after, retained=frozenset()):
    """Report descriptive names `after` replaced with placeholders.

    `retained` names the types still declared in the new snapshot of
    `before`'s own file; they did not move, so their layout is not a carrier.
    """
    found = set()
    old, new = tokens(before), tokens(after)
    if old == new:
        return []
    macro_parameters = macro_parameter_positions(before)
    # Moving a retained type before a new namespace can align its old
    # declaration with the namespace declaration. That is not a type rename.
    type_definition = re.compile(r'\b(?:class|struct)\s+([A-Za-z_]\w*)[^;{}]*\{')
    namespace_definition = re.compile(r'\bnamespace\s+([A-Za-z_]\w*)\s*\{')
    old_text, new_text = ' '.join(old), ' '.join(new)
    retained_types = (set(type_definition.findall(old_text)) &
                      set(type_definition.findall(new_text)))
    added_namespaces = (set(namespace_definition.findall(new_text)) -
                        set(namespace_definition.findall(old_text)))
    # Exact token alignment handles functions, locals and declarations even
    # when the surrounding class is not sizeable. Comments cannot preserve a name.
    for tag, a, b, c, d in _token_opcodes(tuple(old), tuple(new)):
        if tag == 'replace' and b - a == d - c:
            for offset, (x, y) in enumerate(zip(old[a:b], new[c:d])):
                old_pos, new_pos = a + offset, c + offset
                moved_type = (x in retained_types and y in added_namespaces and
                              old_pos > 0 and new_pos > 0 and
                              old[old_pos - 1] in ('class', 'struct') and
                              new[new_pos - 1] == 'namespace')
                # A bare MSVC attribute can align with a new sizeof operand.
                # Exempt this occurrence, not real identifiers named "naked".
                compiler_attribute = (
                    old_pos >= 2 and old_pos + 1 < len(old) and
                    old[old_pos - 2] in ('__declspec', '_declspec') and
                    old[old_pos - 1] == '(' and old[old_pos + 1] == ')')
                # A removed template helper can align with a newly added plain
                # class at the same location.  Its template prefix makes that
                # declaration pairing ambiguous; other uses and matching
                # layouts are still checked independently.
                template_mismatch = (
                    _templated_type_declaration(old, old_pos) !=
                    _templated_type_declaration(new, new_pos))
                # A destructor's name is its class's name. Aligning `~Owner`
                # with an ordinary identifier (a method `m` lined up with an
                # added `virtual ~Rva00802380Base()`) renames neither; two
                # destructors still pair, so a class rename is still caught.
                destructor_mismatch = (
                    (old_pos > 0 and old[old_pos - 1] == '~') !=
                    (new_pos > 0 and new[new_pos - 1] == '~'))
                if (downgrade(x, y) and not moved_type and
                        not compiler_attribute and not template_mismatch and
                        not destructor_mismatch and
                        old_pos not in macro_parameters):
                    found.add((x, y))
    found.update(_function_declaration_regressions(old, new, macro_parameters))
    left, right = layouts(before), layouts(after)
    left_shapes, right_shapes = _shapes(left), _shapes(right)
    for owner, members in left.items():
        shape = left_shapes[owner]
        if owner in right:
            candidates = [owner]
        else:
            candidates = [name for name, other in right_shapes.items()
                          if name not in left and other == shape]
            # Removing a local type during header adoption does not rename it
            # to an unrelated, already-present type with the same layout.
            # Never pick arbitrarily between two identical carrier layouts.
            if len(candidates) != 1:
                continue
            if not _demonstrable_carrier(owner, retained):
                continue
        target = candidates[0]
        if downgrade(owner, target):
            found.add((owner, target))
        for off, (name, span, array) in members.items():
            other = right[target].get(off)
            if other and other[1:] == (span, array) and downgrade(name, other[0]):
                found.add((name, other[0]))
    return sorted(found)


def git(root, *args):
    return subprocess.run(['git', *args], cwd=root, check=True, capture_output=True).stdout.decode('utf-8', 'replace')


def read(root, ref, path):
    spec = ':' + path if ref == ':' else ref + ':' + path
    exists = subprocess.run(['git', 'cat-file', '-e', spec], cwd=root, capture_output=True)
    if exists.returncode:
        return None
    return git(root, 'show', spec)


def read_many(root, ref, paths):
    """Read changed Git blobs in one framed request; missing paths stay explicit."""
    paths = sorted(set(paths))
    if not paths:
        return {}
    specs = [':' + path if ref == ':' else ref + ':' + path for path in paths]
    if any('\n' in spec or '\r' in spec for spec in specs):
        raise ValueError('newline in Git blob request')
    out = subprocess.run(['git', 'cat-file', '--batch'], cwd=root,
                         input=('\n'.join(specs) + '\n').encode(),
                         capture_output=True, check=True).stdout
    stream = io.BytesIO(out)
    values = {}
    for path in paths:
        header = stream.readline().rstrip(b'\n')
        if header.endswith(b' missing'):
            values[path] = None
            continue
        fields = header.split(b' ')
        if len(fields) != 3 or fields[1] != b'blob':
            raise ValueError(f'{ref}:{path}: unexpected Git object header {header!r}')
        size = int(fields[2])
        data = stream.read(size)
        if len(data) != size or stream.read(1) != b'\n':
            raise ValueError(f'{ref}:{path}: truncated Git blob batch')
        values[path] = data.decode('utf-8', 'replace')
    if stream.read(1):
        raise ValueError('extra Git blob batch data')
    return values


def diff_args(old, new):
    return ['--cached', old] if new == ':' else [old, new]


def ledger_diff(root, old, new):
    old_path = layout_history.path_at(old, 'targets/game/reverse/functions.csv',
                                       layout_history.OLD_LEDGER, root=root,
                                       allow_missing=True)
    new_path = layout_history.path_at('' if new == ':' else new,
                                       'targets/game/reverse/functions.csv',
                                       layout_history.OLD_LEDGER, root=root,
                                       allow_missing=True)
    if not old_path or not new_path or old_path == new_path:
        return git(root, 'diff', '--unified=0', '--no-renames',
                   *diff_args(old, new), '--', new_path or old_path or
                   'targets/game/reverse/functions.csv')
    before = csv.DictReader((read(root, old, old_path) or '').splitlines())
    after = csv.DictReader((read(root, new, new_path) or '').splitlines())
    def claims(rows):
        return [(r['name'], r['export_rva'], r['target_rva'], r['target_size'],
                 layout_history.canonical_source(r['source']), r['status'])
                for r in rows]
    if claims(before) != claims(after):
        raise ValueError('ledger relocation changed a function claim')
    return ''


def source(path):
    # Generated files hold many unrelated placeholder bodies.  A ledger row
    # moving from one of them to authored C++ links the entire old file to the
    # new one, so comparing its declarations invents name regressions.
    return (not path.startswith('game/gen_small/') and
            path.startswith(('game/', 'inputs/reference/shims/', 'targets/game/reverse/attempts/')) and
            path.endswith(SOURCE))


def pairs(root, old, new, retained=None):
    """Return the (old path, new path, before, after) texts to compare.

    `retained` is an optional dict, filled in with the type names each old
    path still declares in the new snapshot; `regressions` needs them to tell a
    moved type from one that stayed behind.
    """
    args = diff_args(old, new)
    changes = []
    fields = git(root, 'diff', '--name-status', '-z', '-M1%', *args).split('\0')
    i = 0
    while i < len(fields) and fields[i]:
        status = fields[i]; i += 1
        count = 2 if status.startswith(('R', 'C')) else 1
        changes.append((status, fields[i:i + count]))
        i += count
    paths = {path for status, names in changes if status not in ('R100', 'C100')
             for path in names}
    source_paths = {path for path in paths if source(path)}
    old_paths = source_paths | {names[0] for status, names in changes
                                if status.startswith(('R', 'C')) and status not in ('R100', 'C100')
                                and source(names[1])}
    snapshots = {(old, path): value for path, value in read_many(root, old, old_paths).items()}
    snapshots.update({(new, path): value for path, value in read_many(root, new, source_paths).items()})
    @lru_cache(maxsize=None)
    def snapshot(ref, path):
        return snapshots.get((ref, path)) if (ref, path) in snapshots else read(root, ref, path)
    left, right = {}, {}
    ids = {}
    for path in paths:
        if not source(path):
            continue
        for ref, dest in ((old, left), (new, right)):
            text = snapshot(ref, path)
            if text is not None:
                dest[path] = text
        ids[path] = {int(m[1], 16) for m in ADDRESS.finditer(Path(path).stem)}
    # Read only changed ledger rows, never the complete ledger. These link
    # semantic filenames and functions whose source carries no address token.
    delta = ledger_diff(root, old, new)
    # Prefetch every blob the loops below ask for in one framed `git cat-file
    # --batch` per ref. Reading them one by one spawned two git processes per
    # file, and a range touching a few thousand ledger rows spent minutes in
    # process startup alone. The lookups themselves are unchanged.
    def prefetch(ref, wanted):
        missing = {p for p in wanted if (ref, p) not in snapshots}
        snapshots.update({(ref, p): v for p, v in read_many(root, ref, missing).items()})
    delta_paths = {old: set(), new: set()}
    for line in delta.splitlines():
        if not line.startswith(('+', '-')) or line.startswith(('+++', '---')):
            continue
        row = next(csv.reader([line[1:]]), [])
        if len(row) >= 6 and source(row[4]):
            delta_paths[new if line[0] == '+' else old].add(row[4])
    prefetch(old, delta_paths[old])
    prefetch(new, delta_paths[new])
    for line in delta.splitlines():
        if not line.startswith(('+', '-')) or line.startswith(('+++', '---')):
            continue
        row = next(csv.reader([line[1:]]), [])
        if len(row) < 6 or not source(row[4]):
            continue
        try:
            rva = int(row[2], 16)
        except ValueError:
            continue
        path = row[4]
        ids.setdefault(path, set()).add(rva)
        ref, dest = (new, right) if line[0] == '+' else (old, left)
        text = snapshot(ref, path)
        if text is not None:
            dest[path] = text
    # A bank may remain in place while a conversion is prepared. Compare it
    # too; deletion and git's rename similarity heuristic are not prerequisites.
    old_banks = set(git(root, 'ls-tree', '-r', '--name-only', old, '--',
                        'reverse/attempts/', 'targets/game/reverse/attempts/').splitlines())
    wanted_banks = set()
    for path in right:
        for rva in ids.get(path, ()):
            bank = f'targets/game/reverse/attempts/0x{rva:08x}.cpp'
            wanted_banks.add(bank if bank in old_banks else 'reverse/' + bank[len('targets/game/reverse/') :])
    prefetch(old, wanted_banks & old_banks)
    for path in list(right):
        for rva in ids.get(path, ()):
            bank = f'targets/game/reverse/attempts/0x{rva:08x}.cpp'
            old_bank = bank if bank in old_banks else 'reverse/' + bank[len('targets/game/reverse/') :]
            if old_bank not in old_banks:
                continue
            text = snapshot(old, old_bank)
            if text is not None:
                left[old_bank] = text
                ids.setdefault(old_bank, set()).add(rva)
    linked = {(p, p) for p in left.keys() & right.keys()}
    # Git-detected moves cover address-free files without a ledger edit.
    for status, names in changes:
        if status.startswith(('R', 'C')) and status not in ('R100', 'C100') and source(names[1]):
            before = snapshot(old, names[0])
            after = snapshot(new, names[1])
            if before is not None and after is not None:
                left[names[0]] = before
                right[names[1]] = after
                linked.add(tuple(names))
    prefetch(new, {a for a in left if a.startswith('game/')})
    by_rva = defaultdict(set)
    for path in right:
        for rva in ids.get(path, ()):
            by_rva[rva].add(path)
    for a in left:
        targets = {b for rva in ids.get(a, ()) for b in by_rva[rva] if a != b}
        if not targets:
            continue
        # Rehoming one row out of a retained game/ TU does not move its other
        # declarations. Comparing that unchanged whole source to the new file
        # invents unrelated renames; the same-RVA ledger check still runs.
        if a.startswith('game/') and snapshot(new, a) == left[a]:
            continue
        linked.update((a, b) for b in targets)
    if retained is not None:
        retained.update(retained_types(root, new, right, left))
    return [(a, b, left[a], right[b]) for a, b in sorted(linked)]


def retained_types(root, new, right, paths):
    """Type names each paired OLD path still declares in the NEW snapshot.

    A type still declared in its own file did not move into the file it is
    being compared with, so its layout is not a carrier there.  This is the
    only positive evidence available at the pairing boundary: the two texts
    handed to `regressions` are different files, and only the new snapshot of
    the OLD path says which types stayed behind.  Only measured definitions count: comments, literals and forward declarations
    cannot prove that a layout stayed behind. Only `game/` is read; a banked
    attempt body is stale evidence, not a definition that survived.
    """
    wanted = {path for path in paths if path.startswith('game/')}
    texts = {path: right[path] for path in wanted if path in right}
    missing = wanted - set(texts)
    if missing:
        texts.update({path: text for path, text
                      in read_many(root, new, missing).items()
                      if text is not None})
    return {path: frozenset(layouts(text))
            for path, text in texts.items()}


def _symbol_names(symbol):
    """Extract plain method and immediate-owner names from an MSVC symbol."""
    if symbol.startswith(('??0', '??1')):
        owner = symbol[3:].split('@', 1)[0]
        return ('', owner if IDENT.fullmatch(owner) else '')
    if not symbol.startswith('?') or symbol.startswith('??') or '@@' not in symbol:
        return ()
    head = symbol[1:].split('@@', 1)[0].split('@')
    return tuple(part if IDENT.fullmatch(part) else '' for part in head[:2])


def _symbol_name_pairs(old_symbol, new_symbol):
    """Every (old, new) name part of two symbols of one declaration shape;
    otherwise the method and immediate owner, by position."""
    found = symbol_pairs(old_symbol, new_symbol)
    if found is not None and (declaration_shape(old_symbol) == declaration_shape(new_symbol)
                              or not old_symbol.startswith('?')):
        return found
    return list(zip(_symbol_names(old_symbol), _symbol_names(new_symbol)))


def _function_row(row):
    if len(row) < 6:
        return None
    try:
        return row[0], int(row[2], 16), int(row[3])
    except ValueError:
        return None


def _symbol_row(row):
    if len(row) < 2 or row[0] == 'name':
        return None
    try:
        return row[0], int(row[1], 16), 0
    except ValueError:
        return None


def _data_row(row):
    if len(row) < 4 or row[0] == 'name':
        return None
    try:
        return (row[0], int(row[1], 16) - (IMAGE_BASE if row[2] == 'va' else 0),
                int(row[3] or 0))
    except ValueError:
        return None


def _paired_rows(delta, parse):
    """(removed, added) changed rows paired 1:1: the same (address, size)
    first, then the same start address among the rest. Never by overlap: a
    retirement that corrects a false-tail start is routine work."""
    removed, added = [], []
    for line in delta.splitlines():
        if not line.startswith(('+', '-')) or line.startswith(('+++', '---')):
            continue
        row = parse(next(csv.reader([line[1:]]), []))
        if row is not None:
            (added if line[0] == '+' else removed).append((row, line[1:]))
    out = []
    for key in (lambda r: (r[0][1], r[0][2]), lambda r: r[0][1]):
        left, right = defaultdict(list), defaultdict(list)
        for item in removed:
            left[key(item)].append(item)
        for item in added:
            right[key(item)].append(item)
        used = set()
        for k in left.keys() & right.keys():
            # A many-to-many ledger edit has no safe name pairing.
            used.update(id(x) for x in left[k] + right[k])
            if len(left[k]) == 1 and len(right[k]) == 1:
                out.append((left[k][0], right[k][0]))
        removed = [x for x in removed if id(x) not in used]
        added = [x for x in added if id(x) not in used]
    return out


def ledger_symbol_regressions(root, old, new):
    """Catch a ledger-only rename of the same physical body or datum."""
    sides = [(FUNCTIONS, ledger_diff(root, old, new), _function_row)]
    for path, parse in ((SYMBOLS, _symbol_row), (DATA_ROWS, _data_row)):
        sides.append((path, git(root, 'diff', '--unified=0', '--no-renames',
                                *diff_args(old, new), '--', path), parse))
    found = []
    for path, delta, parse in sides:
        for ((old_symbol, _, _), before), ((new_symbol, _, _), after) in _paired_rows(delta, parse):
            for old_name, new_name in _symbol_name_pairs(old_symbol, new_symbol):
                if downgrade(old_name, new_name):
                    found.append(Finding(path, path, old_name, new_name,
                                         digest(before), digest(after)))
    return sorted(found, key=lambda f: (f.before_sha256, f.old_name, f.new_name))


@dataclass(frozen=True)
class Finding:
    old_path: str
    new_path: str
    old_name: str
    new_name: str
    before_sha256: str
    after_sha256: str


DIR32_RECORD = 'targets/game/reverse/dir32_addresses.csv'
SYMBOLS = 'targets/game/reverse/symbols.csv'
FUNCTIONS = 'targets/game/reverse/functions.csv'
DATA_ROWS = 'targets/game/reverse/data_rows.csv'
ILT_TOKEN = re.compile(r'^\??j_([0-9A-Fa-f]{8})(?:@@YAXXZ)?$')
IMAGE_BASE = 0x400000


def _bare(name):
    """`?Foo@Bar@@..` -> Foo, `_Foo` -> Foo, `Foo` -> Foo."""
    head = name[1:].split('@', 1)[0] if name.startswith('?') else (
        name[1:] if name.startswith('_') else name)
    return head if IDENT.fullmatch(head) else None


def _ilt_respellings(root, old, new):
    """(old, j_XXXXXXXX) pairs that respell a DIR32-recorded stand-in to the
    canonical `?j_` ILT row at the very address the stand-in was recorded at.

    A `?j_XXXXXXXX@@YAXXZ` row is a thunk's canonical identity (AGENTS.md),
    not an invented placeholder; naming the recorded address by its ledger row
    loses nothing. Only an exact address match counts.
    """
    recorded = {}
    for row in csv.DictReader(io.StringIO(read(root, old, DIR32_RECORD) or '')):
        try:
            va = int(row['va'], 16)
        except (KeyError, TypeError, ValueError):
            continue
        bare = _bare(row.get('name') or '')
        if bare:
            recorded.setdefault(bare, set()).add(va - IMAGE_BASE)
    # A symbols.csv pin records its stand-in at an RVA the same way
    # (?destroy@ProductionPrerequisiteDestructorShim pinned at 0x753450,
    # the ?j_00753450 row; re_attempts 28c943e424).
    for row in csv.DictReader(io.StringIO(read(root, old, SYMBOLS) or '')):
        if _is_view(row):
            continue
        try:
            rva = int(row['address'], 16)
        except (KeyError, TypeError, ValueError):
            continue
        bare = _bare(row.get('name') or '')
        if bare:
            recorded.setdefault(bare, set()).add(rva)
    ilt = set()
    for line in (read(root, new, 'targets/game/reverse/functions.csv') or '').splitlines():
        if not line.startswith('?j_'):
            continue
        cols = line.split(',')
        try:
            rva = int(cols[2], 16)
        except (IndexError, ValueError):
            continue
        # Ledger ?j_ names spell the address in either case (?j_0000955c,
        # re_attempts 59148); the address, not its case, is the identity. The
        # address fixes the name whatever signature the row declares
        # (?j_0000fd1c@@YAXPAVGameWindow@@_N@Z, d30e390803).
        if cols[0].lower().startswith(f'?j_{rva:08x}@@'):
            ilt.add(rva)
    return recorded, ilt


def _is_view(row):
    """An abi-view= pin (tools/abi_view.py): a compilation view, never a
    recorded name, so it pre-authorises no rename and settles nothing."""
    return abi_view.is_view(','.join([row.get('notes') or ''] + (row.get(None) or [])))


def _recorded_components(root, ref):
    """Name component -> RVAs where a symbols.csv pin or DIR32 record (a
    candidate, AGENTS.md) spells it as the method/datum or its owner."""
    out = defaultdict(set)
    for path, column, base in ((SYMBOLS, 'address', 0), (DIR32_RECORD, 'va', IMAGE_BASE)):
        for row in csv.DictReader(io.StringIO(read(root, ref, path) or '')):
            if path == SYMBOLS and _is_view(row):
                continue
            try:
                rva = int(row[column], 16) - base
            except (KeyError, TypeError, ValueError):
                continue
            name = row.get('name') or ''
            parts = set(_symbol_names(name)) | {_bare(name)}
            for part in parts - {'', None}:
                out[part].add(rva)
    return out


ILT_TARGET = re.compile(r'target=(?:0x([0-9A-Fa-f]{8})|FUN_([0-9A-Fa-f]{8}))')


def _ledger_rows_by_rva(root, ref):
    """RVA -> ledger names (functions.csv and data_rows.csv), and the ILT
    rows' recorded jump targets (RVA -> target RVA)."""
    names, targets = defaultdict(list), {}
    for line in (read(root, ref, 'targets/game/reverse/functions.csv') or '').splitlines():
        cols = line.split(',')
        try:
            rva = int(cols[2], 16)
        except (IndexError, ValueError):
            continue
        names[rva].append(cols[0])
        if cols[0].lower() == f'?j_{rva:08x}@@yaxxz':
            m = ILT_TARGET.search(line)
            if m:
                targets[rva] = int(m.group(1), 16) if m.group(1) else int(m.group(2), 16) - IMAGE_BASE
    for row in csv.DictReader(io.StringIO(read(root, ref, 'targets/game/reverse/data_rows.csv') or '')):
        try:
            rva = int(row['address'], 16) - (IMAGE_BASE if row.get('address_kind') == 'va' else 0)
        except (KeyError, TypeError, ValueError):
            continue
        names[rva].append(row.get('name') or '')
    return names, targets


def _is_pin_respelling(finding, recorded, names, targets):
    """A name known only as a pin/DIR32 record at address A, respelled to a
    component of the ledger row at A (or, for an ILT pin, at the ILT row's
    recorded target), as callees.py prints it. The ledger row is that address's
    identity; a name the ledger row itself spells is never dropped here."""
    # In a decorated name a class/struct/union/enum type carries a one-letter
    # code (URva00080600Value@@); the identifier still ends at '@'.
    # A constructor, destructor or other special member spells its class
    # right after ??<digit> or ??_<letter> (??0AIGuardMachine@@).
    word = lambda n: re.compile(r'(?:(?<![A-Za-z0-9_])|(?<=[^A-Za-z0-9_][UVTW])'
                                r'|(?<=\?\?[0-9])|(?<=\?\?_[A-Za-z]))'
                                + re.escape(n) + r'(?![A-Za-z0-9_])')
    new, old = word(finding.new_name), word(finding.old_name)
    embedded = re.match(r'(?:Rva|Glo|Gen_?|(?:d|dup|j|sub|FUN)_)([0-9A-Fa-f]{8})(?![0-9A-Fa-f])',
                        finding.new_name, re.I)
    for rva in recorded.get(finding.old_name, ()):
        places = [rva] + ([targets[rva]] if rva in targets else [])
        rows = [n for a in places for n in names.get(a, [])]
        if not rows or any(old.search(n) for n in rows):
            continue
        if any(new.search(n) for n in rows):
            return True
        # An address-derived placeholder naming that very ledger body
        # (Rva00080600Tree for the 0x00080600 row) is honest (AGENTS.md). An
        # ILT's own address is named only by its ?j_ row (test_respelling_
        # recorded_standin_to_bfme_or_rva_still_fails).
        bodies = {a for a in places
                  if not any(ILT_TOKEN.match(n) for n in names.get(a, []))}
        if embedded and opaque(finding.new_name) and int(embedded.group(1), 16) in (
                bodies | {a + IMAGE_BASE for a in bodies}):
            return True
    return False


# A word followed by an embedded 6-8 hex-digit address (`forward4125F0`,
# dc77a7e650). The tail starts with a digit and holds at least three digits.
ADDRESS_TAIL = re.compile(r'^[A-Za-z_]*[a-z_]((?=(?:[A-Fa-f]*[0-9]){3})[0-9][0-9A-Fa-f]{5,7})$')


def _ledger_names_by_rva(root, ref):
    out = defaultdict(list)
    for line in (read(root, ref, 'targets/game/reverse/functions.csv') or '').splitlines():
        cols = line.split(',')
        try:
            out[int(cols[2], 16)].append(cols[0])
        except (IndexError, ValueError):
            continue
    return out


def _is_address_respelling(finding, ledger):
    """The old name encodes address A and the new name is part of the decorated
    name of the ledger row at A (RVA, or VA - image base)."""
    m = ADDRESS_TAIL.match(finding.old_name)
    if not m:
        return False
    a = int(m.group(1), 16)
    names = ledger.get(a, []) + (ledger.get(a - IMAGE_BASE, []) if a >= IMAGE_BASE else [])
    return any(re.search(r'(?<![A-Za-z0-9_])' + re.escape(finding.new_name) + r'(?![A-Za-z0-9_])', n)
               for n in names)


def _is_ilt_respelling(finding, recorded, ilt):
    m = ILT_TOKEN.match(finding.new_name)
    if not m:
        return False
    rva = int(m.group(1), 16)
    return rva in ilt and rva in recorded.get(_bare(finding.old_name) or '', ())


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _without_respellings(candidates, root, old, new):
    """`candidates` less the ILT, pin and address respellings check() accepts."""
    if any(ILT_TOKEN.match(f.new_name) for f in candidates):
        recorded, ilt = _ilt_respellings(root, old, new)
        candidates = [f for f in candidates if not _is_ilt_respelling(f, recorded, ilt)]
    # The exemptions read the BASE ledger: a row renamed in the same change
    # cannot certify its own respelling.
    if candidates:
        recorded = _recorded_components(root, old)
        if any(f.old_name in recorded for f in candidates):
            names, targets = _ledger_rows_by_rva(root, old)
            _add_base_pins(root, old, candidates, recorded, names)
            candidates = [f for f in candidates
                          if not _is_pin_respelling(f, recorded, names, targets)]
    if any(ADDRESS_TAIL.match(f.old_name) for f in candidates):
        ledger = _ledger_names_by_rva(root, old)
        candidates = [f for f in candidates if not _is_address_respelling(f, ledger)]
    if any(_short_rva(f.old_name) for f in candidates):
        candidates = _without_short_rva_respellings(candidates, root, old)
    return candidates


def _add_base_pins(root, old, candidates, recorded, names):
    """Where the base has no functions.csv or data_rows.csv row at a recorded
    address A, its symbols.csv pins at A and A - image base stand in for the
    row (5ec282b785), less any pin that spells an old name."""
    olds = [re.compile(r'(?<![A-Za-z0-9_])' + re.escape(f.old_name) + r'(?![A-Za-z0-9_])')
            for f in candidates]
    wanted = {a for f in candidates for a in recorded.get(f.old_name, ()) if not names.get(a)}
    if not wanted:
        return
    pins = defaultdict(list)
    for row in csv.DictReader(io.StringIO(read(root, old, SYMBOLS) or '')):
        if _is_view(row):
            continue
        name = row.get('name') or ''
        try:
            rva = int(row['address'], 16)
        except (KeyError, TypeError, ValueError):
            continue
        if not any(o.search(name) for o in olds):
            pins[rva].append(name)
    for a in wanted:
        names[a].extend(pins.get(a, []) + (pins.get(a - IMAGE_BASE, []) if a >= IMAGE_BASE else []))


def _without_short_rva_respellings(candidates, root, old):
    """Drop a rename of a short Rva<address> name to one that keeps the
    address, or that a BASE functions.csv, symbols.csv or data_rows.csv name
    spells as a whole word or a decorated type (PAUBfmeStringPool3AF0@@)."""
    text = None
    keep = []
    for f in candidates:
        m = SHORT_RVA.match(f.old_name) if _short_rva(f.old_name) else None
        if m:
            address = int(m.group(1), 16)
            spelled = re.search(r'(?:(?<![0-9A-Fa-f])|(?<=Rva)|(?<=_))0*([0-9A-Fa-f]{6,8})(?![0-9A-Fa-f])', f.new_name)
            if spelled and int(spelled.group(1), 16) == address:
                continue
            if text is None:
                text = '\n'.join(line.split(',', 1)[0]
                                 for path in (FUNCTIONS, SYMBOLS, DATA_ROWS)
                                 for line in (read(root, old, path) or '').splitlines()
                                 if not (path == SYMBOLS and abi_view.is_view(line.split(',', 2)[2]
                                                                               if line.count(',') >= 2 else '')))
            if re.search(r'(?:(?<![A-Za-z0-9_])|(?<=[UVTW]))' + re.escape(f.new_name)
                         + r'(?![A-Za-z0-9_])', text):
                continue
        keep.append(f)
    return keep


class _Unread(Exception):
    """A decorated name in a shape _NameReader does not parse."""


_SIMPLE_NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*@')
_PRIMITIVE_TYPES = frozenset('CDEFGHIJKMNOXZ')


class _NameReader:
    """Reads an MSVC decorated name: the identifiers of its scope, the class,
    struct, union and enum names its types and template arguments spell, and
    its declaration shape -- operator or named, member/static/free, return
    and parameter types with every name abstracted (`C`, template arguments
    kept) and back-references resolved. Raises _Unread on anything else:
    function and member pointers, arrays, thunks, nested and special names.

    Name back-references follow MSVC's numbering as LLVM's demangler reads
    it: the first ten distinct names, a template instantiation counted as one
    name and its arguments read with names of their own; the symbol's own
    name counts unless it is a template (GPT-6.1-Sol, round 3: Box<int>::f
    (Box<int>*) and Crate<float>::g(Crate<float>*) must not read alike)."""

    def __init__(self, text):
        self.s, self.i, self.scope, self.types = text, 0, [], []
        self.names = []            # back-reference table: (key, identifier, shape)

    def peek(self, n=0):
        at = self.i + n
        return self.s[at] if at < len(self.s) else '\0'

    def take(self):
        char = self.peek()
        if char == '\0':
            raise _Unread
        self.i += 1
        return char

    def memorize(self, key, identifier, shape):
        if len(self.names) < 10 and all(key != known for known, _, _ in self.names):
            self.names.append((key, identifier, shape))

    def simple(self, into, memorize=True):
        found = _SIMPLE_NAME.match(self.s, self.i)
        if not found:
            raise _Unread
        name = found.group(0)[:-1]
        into.append(name)
        self.i = found.end()
        if memorize:
            self.memorize(name, name, '')
        return name

    def fragment(self, into, memorize_template=True):
        """One scope component; its shape is a template's argument shapes."""
        if self.peek().isdigit():
            at = int(self.take())
            if at >= len(self.names):
                raise _Unread
            _, name, shape = self.names[at]
            into.append(name)
            return shape
        if self.s.startswith('?$', self.i):
            start, outer, self.names = self.i, self.names, []
            self.i += 2
            name = self.simple(into)
            shape = '<' + self.template_arguments() + '>'
            self.names = outer
            if memorize_template:
                self.memorize(self.s[start:self.i], name, shape)
            return shape
        if self.peek() == '?':
            raise _Unread
        self.simple(into)
        return ''

    def qualified(self, into, first=None):
        shape = [first] if first is not None else []
        while self.peek() != '@':
            shape.append(self.fragment(into))
        self.take()
        # every component keeps its slot: B<int>::A is not D::C<int> (GPT-6.1-Sol, round 4)
        return '::'.join(shape)

    def template_arguments(self):
        shapes = []
        while self.peek() != '@':
            if self.s.startswith('$0', self.i):
                self.i += 2
                shapes.append('$0' + self.number())
            elif self.s.startswith('$$C', self.i):       # a cv-qualified type argument
                self.i += 3
                shapes.append('$$C' + self.cv() + self.type())
            elif self.peek() == '$':
                raise _Unread
            else:
                shapes.append(self.type())
        self.take()
        return ','.join(shapes)

    def number(self):
        start = self.i
        if self.peek() == '?':
            self.i += 1
        if self.peek().isdigit():
            self.i += 1
            return self.s[start:self.i]
        while self.peek() in 'ABCDEFGHIJKLMNOP':
            self.i += 1
        if self.take() != '@':
            raise _Unread
        return self.s[start:self.i]

    def cv(self):
        char = self.take()
        if char not in 'ABCD':
            raise _Unread
        return char

    def type(self):
        char = self.take()
        if char in _PRIMITIVE_TYPES or char.isdigit():
            return char
        if char == '_':
            return '_' + self.take()
        if char == '?':
            return '?' + self.cv() + self.type()
        if char in 'PQRSAB':
            if self.peek() in '68':
                raise _Unread
            return char + self.cv() + self.type()
        if char in 'VUT':
            return 'C' + self.qualified(self.types)
        if char == 'W' and self.peek().isdigit():
            self.i += 1
            return 'W' + self.qualified(self.types)
        raise _Unread

    def parameters(self):
        """Parameter shapes, a back-reference replaced by the parameter it
        repeats (MSVC numbers the parameters whose encoding is longer than
        one letter), so `(Foo*, Foo*)` and `(Bar*, Baz*)` read alike."""
        if self.peek() == 'X':
            self.i += 1
            return ('X',)
        shapes, table = [], []
        while self.peek() not in '@Z\0':
            start = self.i
            shape = self.type()
            if len(shape) == 1 and shape.isdigit():
                if int(shape) >= len(table):
                    raise _Unread
                shape = table[int(shape)]
            elif self.i - start > 1 and len(table) < 10:
                table.append(shape)
            shapes.append(shape)
        if self.peek() == 'Z':
            shapes.append('...')
        return tuple(shapes)

    def encoding(self):
        lead = self.take()
        if lead in '01234':
            return ('data' + lead, self.type())
        if lead in 'ABEFIJMNQRUV':
            kind = 'member'
            self.cv()                                   # `this` const-ness: not a call's shape
        elif lead in 'CDKLST':
            kind = 'static'
        elif lead in 'YZ':
            kind = 'free'
        else:
            raise _Unread
        convention = self.take()                        # read here, where a template scope has ended
        if self.peek() == '@':
            self.i += 1
            returns = '@'                               # a constructor or destructor
        else:
            returns = self.type()
        return (kind, convention, returns, self.parameters())

    def read(self):
        """(scope, types, shape)."""
        if self.s.startswith('??') and not self.s.startswith('??$'):
            width = 1 if self.peek(2) != '_' else 2 if self.peek(3) != '_' else 3
            form, self.i = 'operator ' + self.s[2:2 + width], 2 + width
            scope = self.qualified(self.scope)
        else:
            form, self.i = 'named', 1
            # the symbol's own name: a simple name is memorized, a template is not
            scope = self.qualified(self.scope, self.fragment(self.scope, memorize_template=False))
        return self.scope, self.types, (form, scope) + self.encoding()


def _read_name(symbol):
    if not symbol.startswith('?'):
        return None
    try:
        return _NameReader(symbol).read()
    except _Unread:
        return None


def mangled_identifiers(symbol):
    """(scope, types): the identifiers a decorated name spells -- its scope
    innermost first (a method, then its owners; an operator, constructor or
    destructor has only owners), then the class/struct/union/enum names of
    its types and template arguments in order. A C name is its bare name.
    None when the name is in a shape _NameReader does not parse."""
    if not symbol.startswith('?'):
        bare = _bare(symbol)
        return ([bare], []) if bare else None
    found = _read_name(symbol)
    return None if found is None else found[:2]


def declaration_shape(symbol):
    """What a call must declare to call `symbol`, with every name abstracted:
    (operator code or 'named', scope template shapes, member/static/free or
    dataN, calling convention letter, return type, parameter types). Two
    names of one shape differ only in their names.
    None for a C name or a decorated name _NameReader does not parse."""
    found = _read_name(symbol)
    return None if found is None else found[2]


def symbol_pairs(old, new):
    """The (old, new) identifiers a source renames to respell a call from the
    decorated or C name `old` to `new`, scope with scope and type with type
    (`??RCodecState@@QBE_NH@Z` -> `??RBfmeThingJT@@...` renames CodecState
    to BfmeThingJT). None when either name cannot be read or the two do not
    line up (another number of scope or type names): no preflight then."""
    left, right = mangled_identifiers(old), mangled_identifiers(new)
    if left is None or right is None:
        return None
    pairs = set()
    for a, b in zip(left, right):
        if len(a) != len(b):
            return None
        pairs.update((x, y) for x, y in zip(a, b) if x != y)
    return sorted(pairs)


def refused_respellings(pairs, root=None, ref='HEAD'):
    """The (old, new) identifier pairs check() refuses as descriptive-to-
    placeholder when a source renames old to new and the ledger stays at
    `ref`: downgrade(), less the ILT, pin and address respellings. A preflight
    for link_check.py near; the hook still runs, and name_corrections.json
    (exact files and digests) is not consulted."""
    candidates = [Finding('', '', a, b, '', '') for a, b in sorted(set(pairs)) if downgrade(a, b)]
    if not candidates:
        return set()
    root = root or ROOT
    return {(f.old_name, f.new_name) for f in _without_respellings(candidates, root, ref, ref)}


def check(root, old, new):
    raw = read(root, new, CORRECTIONS)
    corrections = json.loads(raw) if raw else []
    if not isinstance(corrections, list):
        raise ValueError(f'{CORRECTIONS} must contain a list')
    findings = []
    accepted = 0
    retained = {}
    candidates = []
    for a, b, before, after in pairs(root, old, new, retained):
        found = regressions(before, after, retained.get(a, frozenset()))
        if found and a != b and a.startswith('game/'):
            # One row moved out of a game/ source that stays in the tree: the
            # whole old file is compared with the new one, so every name the
            # old file still uses would read as renamed (InGameUI against a
            # bridge helper, 2026-09-28). A name the file still carries was not
            # lost. Banks are excluded: one kept beside its conversion must
            # still be held to its names.
            kept = read(root, new, a)
            names = set(tokens(kept)) if kept is not None else set()
            found = [(x, y) for x, y in found if x not in names]
        if found and a != b and '/attempts/' in a:
            # A bank stays paired with every later edit of the source its
            # address names. A pair the OLD snapshot of that source already
            # shows against the same bank landed (and was checked) earlier;
            # this change did not introduce it (Rva003E5A50InfoCallback.cpp
            # against attempts/0x003e5a50.cpp, re_attempts 58887).
            # Token alignment shifts with unrelated insertions, so the same
            # earlier loss can pair differently; key it on the old name: a
            # bank name the old snapshot already reported as lost against
            # this bank, or no longer spelled at all, was not lost by this
            # change.
            landed = read(root, old, b)
            if landed is not None:
                earlier = {x for x, _ in regressions(before, landed, retained.get(a, frozenset()))}
                carried = set(tokens(landed))
                found = [(x, y) for x, y in found if x not in earlier and x in carried]
        candidates.extend(Finding(a, b, x, y, digest(before), digest(after)) for x, y in found)
    candidates.extend(ledger_symbol_regressions(root, old, new))
    for finding in _without_respellings(candidates, root, old, new):
        allowed = False
        for entry in corrections:
            if not isinstance(entry, dict):
                raise ValueError(f'{CORRECTIONS}: correction must be an object')
            if all(entry.get(k) == v for k, v in vars(finding).items()):
                evidence = entry.get('evidence', '')
                reason = entry.get('reason', '')
                # An exact, reviewable correction, not a count baseline or
                # reusable allowlist. Its evidence must exist in this snapshot.
                if (not isinstance(evidence, str) or not isinstance(reason, str)
                        or not evidence.startswith(('docs/', 'targets/game/reverse/'))
                        or '..' in Path(evidence).parts or not reason.strip()
                        or not (read(root, new, evidence) or '').strip()):
                    raise ValueError(f'{CORRECTIONS}: correction needs tracked evidence and a reason')
                allowed = True
                accepted += 1
                break
        if not allowed:
            findings.append(finding)
    return findings, accepted


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('old')
    parser.add_argument('new')
    args = parser.parse_args(argv)
    try:
        findings, accepted = check(ROOT, args.old, args.new)
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f'name_regression: {exc}')
        return 1
    for f in findings:
        print(f'  {f.old_path} -> {f.new_path}: {f.old_name} -> {f.new_name}')
    print(f'name_regression: {len(findings)} descriptive-to-placeholder regression(s), {accepted} documented correction(s)')
    if findings:
        print('Preserve the established name, or document an evidence-backed identity correction; see docs/naming_evidence.md.')
    return bool(findings)


if __name__ == '__main__':
    raise SystemExit(main())
