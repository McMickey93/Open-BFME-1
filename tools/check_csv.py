#!/usr/bin/env python3
"""Fast integrity check for targets/game/reverse/functions.csv, symbols.csv and data_rows.csv (<1s).

Catches the corruption classes that break the full gate long after the fact:
duplicate rows from union merges, two agents claiming overlapping bytes,
malformed rows, rows pointing at missing sources, and LF damage to the CRLF
ledgers. Run it before committing, after every merge/rebase, and in hooks.

Exit 0: both ledgers clean. Exit 1: every problem printed with the fix.
"""
if __name__ == "__main__":
    from target_guard import require_game_cli
    require_game_cli("check_csv.py")

import argparse
import collections
import csv
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger_io  # noqa: E402  (after the path insert that makes it importable)

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT / "targets/game/reverse" / "functions.csv"
SYMBOLS = ROOT / "targets/game/reverse" / "symbols.csv"
DELETED = ROOT / "targets/game/reverse" / "deleted_rows.csv"

# Union merge duplicates contiguous BLOCKS of records, not single lines, and the
# ledgers mix \r\r\n, \r\n and bare-LF terminators that add_match indexes by
# physical line. dedup_csv.py renormalises both files (~157k lines) and conflicts
# with every branch in flight, so it is the wrong repair for a post-merge
# duplicate -- it is for whole-file terminator damage, which is why the two
# checks below still name it.
DUP_FIX = ("Fix: drop the duplicate record(s) with tools/ledger_io.py keeping the "
           "first -- expect a contiguous block, not one line. Not dedup_csv: see "
           "a union merge duplicated the row; keep the first and drop the rest.")

# realcrc.cpp is linked twice in the retail exe, so these two symbols
# legitimately appear at two addresses each. Any other duplicate name is a bug.
ALLOWED_DUP_NAMES = {
    "?CRC_Memory@@YAKPBEKK@Z",
    "?CRC_String@@YAKPBDK@Z",
}

FUNCTIONS_HEADER = "name,export_rva,target_rva,target_size,source,status,notes"
SYMBOLS_HEADER = "name,address,notes"


def read_ledger(path, spec):
    """spec: None = working tree, "" = git index (staged), else a ref/SHA."""
    if spec is None:
        return path.read_bytes()
    rel = path.relative_to(ROOT).as_posix()
    if rel == "targets/game/reverse/functions.csv":
        import layout_history
        return layout_history.read_at(spec, rel, layout_history.OLD_LEDGER, root=ROOT)
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"{spec}:{rel}"],
                         capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"check_csv: cannot read {spec}:{rel}: "
                         f"{out.stderr.decode().strip()}")
    return out.stdout


def read_blobs(paths, spec):
    """Read one state's evidence in one Git process, retaining raw blob bytes.

    The batch protocol is length-framed: bodies can contain newlines or NULs.
    Never substitute the working tree for a missing index/commit object.
    """
    paths = list(paths)
    if spec is None:
        return {path: path.read_bytes() for path in paths}
    if not paths:
        return {}
    requests = [f"{spec}:{path.relative_to(ROOT).as_posix()}" for path in paths]
    if any("\n" in request or "\r" in request for request in requests):
        raise SystemExit("check_csv: newline in Git blob request")
    out = subprocess.run(["git", "-C", str(ROOT), "cat-file", "--batch"],
                         input=("\n".join(requests) + "\n").encode("utf-8"),
                         capture_output=True)
    if out.returncode:
        raise SystemExit(f"check_csv: git cat-file failed: "
                         f"{out.stderr.decode(errors='replace').strip()}")
    stream = io.BytesIO(out.stdout)
    blobs = {}
    for path, request in zip(paths, requests):
        header = stream.readline().rstrip(b"\n").split()
        if len(header) != 3 or header[1] != b"blob" or not header[2].isdigit():
            raise SystemExit(f"check_csv: cannot read {request}: "
                             f"{b' '.join(header).decode(errors='replace')}")
        size = int(header[2])
        blob = stream.read(size)
        if len(blob) != size or stream.read(1) != b"\n":
            raise SystemExit(f"check_csv: incomplete Git blob {request}")
        blobs[path] = blob
    if stream.read(1):
        raise SystemExit("check_csv: unexpected data after Git blob batch")
    return blobs


def known_sources(spec):
    """Sources a ledger row may legally reference for the given state.

    A row whose source exists on disk but is not in git is the worst failure
    class this tool guards: the row pushes fine locally and breaks every
    other clone ("references missing source file"). So worktree/staged modes
    require git-tracked (staged counts during a commit), and --ref mode
    requires presence in that commit's tree.
    """
    if spec:  # a ref/SHA
        out = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", spec],
                             capture_output=True, text=True)
        if out.returncode != 0:
            raise SystemExit(f"check_csv: git ls-tree {spec} failed: {out.stderr.strip()}")
        return set(out.stdout.splitlines())
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files"],
                             capture_output=True, text=True)
    if tracked.returncode != 0:
        raise SystemExit(f"check_csv: git ls-files failed: {tracked.stderr.strip()}")
    allowed = set(tracked.stdout.splitlines())
    staged = subprocess.run(["git", "-C", str(ROOT), "diff", "--cached", "--name-only",
                             "--diff-filter=ACMRT"], capture_output=True, text=True)
    if staged.returncode == 0:
        allowed.update(staged.stdout.splitlines())
    return allowed


def tombstones(raw=None):
    """(name, rva) pairs deleted on purpose -> why. See targets/game/reverse/deleted_rows.csv.

    functions.csv merges with git's union driver, which cannot express a
    deletion: any branch forked before the delete puts the row back with no
    conflict. Without this, a proven-wrong row silently returns to master.
    """
    if raw is None:
        if not DELETED.exists():
            return {}
        raw = DELETED.read_bytes()
    out = {}
    for row in csv.reader(io.StringIO(raw.decode("utf-8", errors="replace"))):
        if not row or not row[0].strip() or row[0].startswith("#") or row[0] == "name":
            continue
        if len(row) < 2:
            continue
        try:
            out[(row[0], int(row[1], 16))] = row[2] if len(row) > 2 else ""
        except ValueError:
            continue
    return out


def function_keys(raw):
    """Semantic (name, RVA) keys in one functions.csv state."""
    keys = set()
    for row in csv.reader(io.StringIO(raw.decode("utf-8", errors="replace"))):
        if len(row) < 3 or row[0] == "name":
            continue
        try:
            keys.add((row[0], int(row[2], 16)))
        except ValueError:
            continue
    return keys


def check_removed_rows(before, after, deleted, problems):
    """A staged functions.csv deletion is durable only with its tombstone.

    Comparing semantic keys permits duplicate cleanup and same-key metadata
    rewrites, while catching every identity/address retirement a union merge
    could otherwise reverse after the commit lands.
    """
    missing = sorted(function_keys(before) - function_keys(after) - set(deleted))
    for name, rva in missing:
        problems.append(
            f"functions.csv removes {name} @ 0x{rva:08X} without a staged "
            "targets/game/reverse/deleted_rows.csv tombstone. A union merge will resurrect it; "
            "stage the transaction's tombstone with the ledger change.")


def check_row_extents(before, after, problems):
    """A row the commit adds or moves must not start mid-body or span padding.

    See tools/row_extent.py; rows already in HEAD are not re-judged.
    """
    import row_extent
    old, new = row_extent.parse_rows(before), row_extent.parse_rows(after)
    if not row_extent.changed_rows(old, new):
        return
    import build
    ghidra = ROOT / "targets/game/reverse/ghidra_functions.csv"
    sizes = row_extent.load_ghidra(ghidra)
    try:
        image, sections = build.exe_image()
    except OSError:  # check() reports the missing image per row
        index = row_extent.CallIndex({}, set(), set())
    else:
        index = row_extent.load_index(ghidra, image, sections, build.read_target_bytes,
                                      ROOT / "build/row_extent_index.pkl")
    problems.extend(row_extent.check(old, new, sizes, build.read_target_bytes, index))


# ABI/codegen scaffold rows (approved by the project lead 2026-10-16): the
# source invents a class hierarchy only to drive codegen (e.g. opaque
# Va<addr>Subobject bases that pin vftable names to addresses). The tag pair
# says so machine-readably; tools/progress.py reports such rows apart.
SCAFFOLD_KEYS = {"abi-scaffold": {"yes"}, "semantic-hierarchy": {"unresolved"}}


def notes_keys(notes):
    """{key: value} for every `key=value` field of a ;-separated notes cell."""
    out = {}
    for field in notes.split(";"):
        key, sep, value = field.strip().partition("=")
        if sep and re.fullmatch(r"[a-z][a-z0-9-]*", key):
            out.setdefault(key, value)
    return out


def scaffold_problems(notes, source, status):
    """Why a row's abi-scaffold tags are malformed (empty list when fine)."""
    keys = notes_keys(notes)
    present = [k for k in SCAFFOLD_KEYS if k in keys]
    if not present:
        return []
    out = [f"{k}={keys[k]} is not one of {sorted(SCAFFOLD_KEYS[k])}" for k in present
           if keys[k] not in SCAFFOLD_KEYS[k]]
    if len(present) != len(SCAFFOLD_KEYS):
        out.append("abi-scaffold=yes and semantic-hierarchy=unresolved go together")
    if status != "matched" or source.startswith(("game/gen_asm/", "game/gen_small/")):
        out.append("an abi-scaffold tag belongs on a matched, hand-written row")
    return out


RE_ATTEMPTS_REL = "targets/game/reverse/re_attempts.log"


def read_re_attempts(spec):
    """re_attempts.log's bytes in the chosen state (None = working tree, "" =
    index, else a ref), or None when that state has no log. A log that exists
    but cannot be read fails loudly: an unread log must not pass as empty."""
    if spec is None:
        path = ROOT / RE_ATTEMPTS_REL
        return path.read_bytes() if path.exists() else None
    exists = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{spec}:{RE_ATTEMPTS_REL}"],
                            capture_output=True)
    if exists.returncode != 0:
        return None
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"{spec}:{RE_ATTEMPTS_REL}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"check_csv: cannot read {spec}:{RE_ATTEMPTS_REL}: {out.stderr.decode().strip()}")
    return out.stdout


# `<N> runs base=<blob>`: the claim is bound to the one log it dedupes (the git
# blob id of the base re_attempts.log), so it can never be reused on a later log.
DEDUPE_CLAIM = r"(\d+)[ \t]+runs?[ \t]+base=([0-9a-f]{40})"
DEDUPE_TRAILER_RE = re.compile(r"^Re-Attempts-Dedupe:[ \t]*" + DEDUPE_CLAIM + r"[ \t]*$", re.MULTILINE)
DEDUPE_ENV_RE = re.compile(r"^[ \t]*" + DEDUPE_CLAIM + r"[ \t]*$")


def git_blob_id(raw):
    """The git blob id of RAW (what `git hash-object` prints)."""
    import hashlib
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


def re_attempts_dedupe_claim(ref=None):
    """(runs, base blob id) a commit claims to dedupe from re_attempts.log, or
    None: the `Re-Attempts-Dedupe: <N> runs base=<blob>` trailer of REF's
    message (--ref), or BFME_RE_ATTEMPTS_DEDUPE='<N> runs base=<blob>' for the
    pre-commit of that one commit (--staged, which cannot see the message)."""
    if ref:
        message = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%B", ref],
                                 capture_output=True, text=True).stdout
        found = DEDUPE_TRAILER_RE.search(message)
    else:
        found = DEDUPE_ENV_RE.match(os.environ.get("BFME_RE_ATTEMPTS_DEDUPE") or "")
    return (int(found.group(1)), found.group(2)) if found else None


def check_re_attempts_range(base, tip, problems):
    """The append-only rule for EVERY commit in BASE..TIP, each against its first
    parent with its own trailer, so a deletion below the pushed tip is caught."""
    commits = subprocess.run(["git", "-C", str(ROOT), "rev-list", "--reverse", "--first-parent",
                              f"{base}..{tip}", "--", RE_ATTEMPTS_REL],
                             capture_output=True, text=True)
    if commits.returncode != 0:
        raise SystemExit(f"check_csv: cannot list {base}..{tip}: {commits.stderr.strip()}")
    for commit in commits.stdout.split():
        found = []
        check_re_attempts_append_only(read_re_attempts(f"{commit}^"), read_re_attempts(commit), found,
                                      dedupe_claim=re_attempts_dedupe_claim(commit),
                                      ledger=ledger_keys_at(commit))
        problems.extend(f"{commit[:10]}: {p}" for p in found)


ADD_MATCH_LANDED = b"landed-by=add_match "


def matched_ledger_keys(functions_raw):
    """{(name, rva, size)} of the matched functions.csv rows in FUNCTIONS_RAW."""
    keys = set()
    if not functions_raw:
        return keys
    text = functions_raw.decode("utf-8", "replace") if isinstance(functions_raw, bytes) else functions_raw
    for row in csv.DictReader(io.StringIO(text, newline="")):
        if row.get("status") != "matched":
            continue
        try:
            keys.add((row["name"], int(row["target_rva"], 16), int(row["target_size"])))
        except (KeyError, TypeError, ValueError):
            continue
    return keys


def ledger_keys_at(commit):
    """matched_ledger_keys of functions.csv at COMMIT, or None when the commit
    has no ledger (then no landed row can be judged against it)."""
    rel = "targets/game/reverse/functions.csv"
    shown = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{rel}"], capture_output=True)
    if shown.returncode != 0:
        return None
    return matched_ledger_keys(shown.stdout)


def add_match_landing(line):
    """(name, rva, size) of a `landed` row add_match wrote, else None."""
    fields = line.rstrip(b"\r").split(b"\t")
    if len(fields) < 5 or fields[3] != b"landed" or not fields[4].startswith(ADD_MATCH_LANDED):
        return None
    try:
        return fields[0].decode("utf-8", "replace"), int(fields[1], 16), int(fields[2])
    except ValueError:
        return None


def check_re_attempts_append_only(base, new, problems, dedupe_claim=None, ledger=None):
    """re_attempts.log only grows: its old lines stay, in order, and lines are
    appended after them (approved by the project lead 2026-10-16). Compared
    with CR-at-EOL ignored, so the one-time LF normalisation passes, but a
    union merge that re-adds rows (a rebase across that normalisation
    duplicates every line whose ending changed) does not. A kept line may
    lose its CR, never gain one; an appended line must be LF and must not
    repeat a line already in the log."""
    if base is None or new is None:
        return
    # A claim applies only to the log it names and only when the log changed: a
    # claim on any other base (reused, or a stale environment variable) is not
    # an exemption, so the ordinary append-only rules below judge the commit.
    if dedupe_claim is not None and new != base and dedupe_claim[1] == git_blob_id(base):
        # The one sanctioned deletion (approved by the project lead 2026-10-16):
        # exactly the union-merge duplicate runs tools/re_attempts_dedupe.py
        # finds in the base, nothing more and nothing less.
        import re_attempts_dedupe
        expected, runs, _singles = re_attempts_dedupe.dedupe(base)
        if not runs or dedupe_claim[0] != len(runs) or new != expected:
            problems.append(f"{RE_ATTEMPTS_REL}: the commit claims a dedupe of {dedupe_claim[0]} run(s), but "
                            f"the log is not the base with exactly its {len(runs)} duplicate run(s) removed "
                            "(tools/re_attempts_dedupe.py --write)")
        return
    base_lines = base.split(b"\n")
    new_lines = new.split(b"\n")
    tail_base = base_lines.pop() if base_lines else b""
    tail_new = new_lines.pop() if new_lines else b""
    if tail_base:
        base_lines.append(tail_base)               # last line without newline
    plain = lambda line: line[:-1] if line.endswith(b"\r") else line
    if ledger is not None:
        # The one deletion a landing may take back: `git revert` of a landing
        # commit removes add_match's `landed` row together with its ledger row.
        # A landed row whose (name, rva, size) is no longer a matched row may
        # leave the log; every other line stays append-only.
        survivors = collections.Counter(plain(line) for line in new_lines + [tail_new])
        kept = []
        for line in base_lines:
            key = add_match_landing(line)
            if key is not None and key not in ledger and not survivors[plain(line)]:
                continue
            kept.append(line)
        base_lines = kept
    n = len(base_lines)
    if len(new_lines) + (1 if tail_new else 0) < n:
        problems.append(f"{RE_ATTEMPTS_REL}: {n - len(new_lines)} line(s) removed; the log is append-only")
        return
    for i in range(n):
        old_line = base_lines[i]
        new_line = new_lines[i] if i < len(new_lines) else tail_new
        if plain(new_line) != plain(old_line):
            problems.append(f"{RE_ATTEMPTS_REL}: line {i + 1} differs from the committed log; the log is "
                            "append-only (a union-merged rebase re-adds rows: rebase with -X renormalize "
                            "(git pull --rebase -X renormalize); do not strip CRs from a rebased log)")
            return
        if new_line.endswith(b"\r") and not old_line.endswith(b"\r"):
            problems.append(f"{RE_ATTEMPTS_REL}: line {i + 1} gained a CRLF ending")
            return
    appended = new_lines[n:] + ([tail_new] if tail_new and len(new_lines) >= n else [])
    for k, line in enumerate(appended, n + 1):
        if line.endswith(b"\r"):
            problems.append(f"{RE_ATTEMPTS_REL}: appended line {k} ends in CRLF; the log is LF-only. "
                            "Rebase with -X renormalize (git pull --rebase -X renormalize); do not strip "
                            "CRs from a rebased log")
            return
    if ledger is not None:
        # add_match writes `landed` after its scoped build; if the full gate
        # then fails and the ledger is reverted, the row must not ride into a
        # commit that does not carry the matched row it records.
        for k, line in enumerate(appended, n + 1):
            key = add_match_landing(line)
            if key is not None and key not in ledger:
                problems.append(f"{RE_ATTEMPTS_REL}: appended line {k} records add_match landing "
                                f"{key[0]} @ 0x{key[1]:08X}/{key[2]}B, but functions.csv in this commit "
                                "has no matched row with that name, rva and size; drop the line "
                                "with the reverted landing")
                return
    # Union duplication re-adds whole runs of rows. A single repeated row can be
    # a coincidence (the log already holds 4,948 rows written more than once),
    # so only two or more consecutive appended rows that repeat two consecutive
    # rows of the log are refused.
    pairs = {(plain(a), plain(b)) for a, b in zip(base_lines, base_lines[1:]) if a and b}
    for k in range(len(appended) - 1):
        pair = (plain(appended[k]), plain(appended[k + 1]))
        if pair[0] and pair[1] and pair in pairs:
            problems.append(f"{RE_ATTEMPTS_REL}: appended lines {n + k + 1}-{n + k + 2} repeat a run of "
                            "existing rows (union-merge duplication): rebase with -X renormalize "
                            "(git pull --rebase -X renormalize); do not strip CRs from a rebased log")
            return


def check_functions(raw, problems, sources_ok, deleted=None):
    deleted = tombstones() if deleted is None else deleted
    if b"\r\n" not in raw[:200]:
        problems.append("functions.csv: CRLF line endings were lost (file is LF). "
                        "Restore from git and use binary-safe edits (tools/dedup_csv.py "
                        "or tools/add_match.py), not csv.writer defaults.")
        # keep checking the content anyway
    text = raw.decode("utf-8", errors="replace")
    rows = list(csv.reader(io.StringIO(text)))
    if not rows or ",".join(rows[0]) != FUNCTIONS_HEADER:
        problems.append(f"functions.csv: bad header (expected '{FUNCTIONS_HEADER}')")
        return
    header_count = sum(1 for r in rows if ",".join(r) == FUNCTIONS_HEADER)
    if header_count > 1:
        problems.append(f"functions.csv: header appears {header_count} times "
                        "(bad merge). " + DUP_FIX)

    seen_exact = set()
    by_rva = {}
    by_name = {}
    matched_ranges = []
    for i, r in enumerate(rows[1:], start=2):
        if len(r) != 7:
            problems.append(f"functions.csv line {i}: {len(r)} fields, expected 7: {r[:2]}...")
            continue
        name, export_rva, target_rva, target_size, source, status, _notes = r
        if not name:
            problems.append(f"functions.csv line {i}: empty name")
            continue
        if export_rva:
            try:
                int(export_rva, 16)
            except ValueError:
                problems.append(f"functions.csv line {i} ({name}): bad export_rva '{export_rva}'")
        if not target_rva:
            problems.append(f"functions.csv line {i} ({name}): empty target_rva")
            continue
        try:
            rva = int(target_rva, 16)
        except ValueError:
            problems.append(f"functions.csv line {i} ({name}): bad target_rva '{target_rva}'")
            continue
        try:
            size = int(target_size) if target_size else 0
        except ValueError:
            problems.append(f"functions.csv line {i} ({name}): bad target_size '{target_size}'")
            continue
        if status not in ("matched", "unmatched"):
            problems.append(f"functions.csv line {i} ({name}): bad status '{status}'")
        if status == "matched" and size <= 0:
            problems.append(f"functions.csv line {i} ({name}): matched with target_size {size}")
        if not source:
            problems.append(f"functions.csv line {i} ({name}): empty source")
        elif source not in sources_ok:
            hint = ("file exists on disk but is NOT tracked by git — `git add` it"
                    if (ROOT / source).exists()
                    else "a commit added rows without adding the file")
            problems.append(f"functions.csv line {i} ({name}): source not in git: {source} ({hint})")

        if (name, rva) in deleted:
            problems.append(f"functions.csv line {i}: {name} @ {target_rva} was deleted on "
                            f"purpose and has come back (a union merge from a branch that "
                            f"forked before the delete). Reason it was deleted: "
                            f"{deleted[(name, rva)]}. Drop the row again, or — if you can "
                            f"byte-prove it — remove its line from targets/game/reverse/deleted_rows.csv "
                            f"in the same commit.")

        # Keyed on the parsed address: the ledger spells it three ways
        # (0x0015B830, 0x0015b830, 0x1005), and a union merge or a hand edit can
        # land the same claim twice under two of them.
        key = (name, rva)
        if key in seen_exact:
            problems.append(f"functions.csv line {i}: exact duplicate row for {name} @ {target_rva}. "
                            + DUP_FIX)
        seen_exact.add(key)

        problems.extend(f"functions.csv line {i} ({name}): {why}"
                        for why in scaffold_problems(_notes, source, status))
        rva = int(target_rva, 16)
        gen_row = _notes.lstrip().startswith("gen-")
        if rva in by_rva and by_rva[rva][0] != name:
            prev_name, prev_size, prev_gen = by_rva[rva]
            if prev_size != size:
                problems.append(f"functions.csv: two names claim target_rva {target_rva} with "
                                f"different sizes: {prev_name} ({prev_size}B) and {name} ({size}B). "
                                "Byte-verify decides which is real.")
            elif gen_row != prev_gen:
                # A gen-* placeholder sharing an exact range with a real identity
                # is not an alias group — the placeholder is the same function under
                # a synthetic name and must yield (union merges land both sides
                # silently; this is the only gate that can see it).
                problems.append(f"functions.csv: {name} and {prev_name} claim the same range "
                                f"at {target_rva} but exactly one is a gen-* placeholder. "
                                "Retract the placeholder row and tombstone it in "
                                "targets/game/reverse/deleted_rows.csv.")
            # same (rva, size), same kind: an alias group. Retail has no ICF, so at
            # most one name is right; identity_guard ratchets the count down.
        by_rva.setdefault(rva, (name, size, gen_row))

        if name in by_name and by_name[name] != rva and name not in ALLOWED_DUP_NAMES:
            problems.append(f"functions.csv: {name} claims two addresses: "
                            f"0x{by_name[name]:08X} and 0x{rva:08X}. One is wrong.")
        by_name.setdefault(name, rva)

        if status == "matched":
            matched_ranges.append((rva, rva + size, name))

    matched_ranges.sort()
    for (a_start, a_end, a_name), (b_start, b_end, b_name) in zip(matched_ranges, matched_ranges[1:]):
        if b_start < a_end:
            if a_start == b_start and a_end == b_end:
                continue  # alias group: one range, several names; identity_guard counts these
            problems.append(f"functions.csv: matched ranges overlap: {a_name} "
                            f"[0x{a_start:08X}-0x{a_end:08X}) and {b_name} @ 0x{b_start:08X}. "
                            "The full gate will refuse to patch. Byte-verify decides which is real.")
    return len([r for r in rows[1:] if len(r) == 7])


def check_symbols(raw, problems):
    # Rows may be 2-field (name,address — the form docs/matching.md tells agents
    # to append) or 3-field with notes. A name may legitimately appear at several
    # addresses: build.py's load_symbol_map treats them all as REL32 resolution
    # candidates. Only exact duplicates and malformed rows are errors.
    #
    # The file must carry ONE terminator, and this is where that is caught. It is
    # merge=union, so a pin differing from its twin by a single \r is a distinct
    # line to the merge driver and lands twice; a duplicate pin is legal, so
    # nothing downstream notices, while the same mixing in functions.csv trips
    # the duplicate-name rule above. ledger_io.uniform_terminator refuses to
    # append to a mixed file — that stops every writer, in a session that did not
    # cause it. 66 LF pins reached master this way and blocked landing until they
    # were repaired by hand.
    census = ledger_io.terminator_census(raw)
    if len(census) > 1:
        spelling = {b"\n": "LF", b"\r\n": "CRLF", b"\r\r\n": "CRCRLF"}
        odd = min(census.items(), key=lambda item: len(item[1]))
        problems.append(
            f"symbols.csv mixes line terminators: {len(odd[1])} "
            f"{spelling.get(odd[0], repr(odd[0]))} line(s) in a file that is otherwise "
            f"{spelling.get(max(census, key=lambda t: len(census[t])), '?')} "
            f"(line {odd[1][0]}{', ...' if len(odd[1]) > 1 else ''}). It is union-merged, "
            "so the odd lines duplicate every pin they carry on the next rebase. "
            "Fix: python3 tools/dedup_csv.py")
    text = raw.decode("utf-8", errors="replace")
    rows = list(csv.reader(io.StringIO(text)))
    if not rows or ",".join(rows[0]) != SYMBOLS_HEADER:
        problems.append(f"symbols.csv: bad header (expected '{SYMBOLS_HEADER}')")
        return
    seen_exact = set()
    for i, r in enumerate(rows[1:], start=2):
        if not r or (len(r) == 1 and not r[0]):
            continue
        if len(r) < 2:
            problems.append(f"symbols.csv line {i}: {len(r)} fields, expected at least 2: {r}...")
            continue
        # >3 fields happens when notes contain commas; the gate only reads
        # name and address, so that is fine.
        name, address = r[0], r[1]
        if not name or not address:
            problems.append(f"symbols.csv line {i}: empty name or address")
            continue
        try:
            addr = int(address, 16)
        except ValueError:
            problems.append(f"symbols.csv line {i} ({name}): bad address '{address}'")
            continue
        # Short addresses are only inconsistent zero-padding and parse fine, but
        # more than eight hex digits cannot be a 32-bit RVA in any spelling, so
        # it is always a typo — three such rows reached the ledger before this
        # check existed, each one digit too long and silently parsing correctly.
        if len(address.removeprefix("0x").removeprefix("0X")) > 8:
            problems.append(f"symbols.csv line {i} ({name}): address '{address}' has "
                            f"more than 8 hex digits; write it as 0x{addr:08X}")
        if (name, addr) in seen_exact:
            problems.append(f"symbols.csv line {i}: exact duplicate row for {name}. "
                            + DUP_FIX)
        seen_exact.add((name, addr))
    return len(rows) - 1


ATTEMPTS_DIR = "targets/game/reverse/attempts/"
ATTEMPT_NAME = re.compile(r"^0x[0-9a-f]{8}\.cpp$")
ATTEMPT_LIMIT = 64 * 1024


def _attempt_paths(spec, sources_ok=None):
    """Stash files as they exist in the state being gated, never on disk.

    A working-tree scan would fail an unrelated `--ref` push over a stray
    uncommitted file, so this reads the same source of truth known_sources does.
    """
    if sources_ok is None:
        sources_ok = known_sources(spec)
    return sorted(p for p in sources_ok
                  if p.startswith(ATTEMPTS_DIR) and p != ATTEMPTS_DIR)


def check_attempts(spec, problems, *, functions_raw=None, sources_ok=None):
    """Validate banked near-miss bodies under targets/game/reverse/attempts/.

    A stash is evidence handed to the next agent, so a malformed one is worse
    than none: it gets served at a score nobody measured. Absent directory means
    nothing banked yet, which is the normal state and passes. ``functions_raw``
    and ``sources_ok`` are the already-loaded bytes and source set for this
    exact working-tree, index, or committed-ref state when called by ``main``.
    ``None`` preserves the standalone helper's state-specific reads.
    """
    paths = _attempt_paths(spec, sources_ok)
    if not paths:
        return 0
    import re_log

    matched = {}
    if functions_raw is None:
        functions_raw = read_ledger(FUNCTIONS, spec)
    for row in csv.reader(io.StringIO(functions_raw.decode(
            "utf-8", errors="replace"))):
        if len(row) == 7 and row[5] == "matched":
            # A stash is named by the canonical lowercase address, whatever
            # spelling the ledger row uses for it.
            try:
                address = f"0x{int(row[2], 16):08x}"
            except ValueError:
                continue
            matched.setdefault(address, []).append((row[0], row[4]))

    blobs = read_blobs((ROOT / rel for rel in paths
                        if ATTEMPT_NAME.match(rel[len(ATTEMPTS_DIR):])), spec)
    lines_by_path = {
        path: blob.decode("utf-8", errors="replace").splitlines()
        for path, blob in blobs.items()
    }
    # A source can back several banked addresses. Read each source once from
    # the same index/commit as its bank, rather than launching git show for
    # every claim. Missing blobs still fail closed through read_blobs.
    source_paths = {
        ROOT / source
        for path, lines in lines_by_path.items()
        if len(lines) >= 2 and re_log._STASH_SCORE.match(lines[1])
        for _, source in matched.get(path.stem, [])
        if Path(source).suffix.lower() not in (".asm", ".s", ".lib")
    }
    source_blobs = read_blobs(sorted(source_paths), spec)
    for rel in paths:
        name = rel[len(ATTEMPTS_DIR):]
        if not ATTEMPT_NAME.match(name):
            problems.append(
                f"{rel}: name must be the lowercase rva it banks, e.g. "
                f"0x000c8220.cpp — serving looks the stash up by address.")
            continue
        blob = blobs[ROOT / rel]
        if len(blob) > ATTEMPT_LIMIT:
            problems.append(f"{rel}: {len(blob)} bytes, over {ATTEMPT_LIMIT}. "
                            f"That is not one function body; delete it.")
        lines = lines_by_path[ROOT / rel]
        if len(lines) < 2 or not re_log._STASH_SCORE.match(lines[1]):
            problems.append(
                f"{rel}: line 2 must read '// partial score=<0..1> date=<iso>'. "
                f"An unreadable score cannot be ranked; rewrite or delete it.")
            continue
        rva = name[:-len(".cpp")]
        claims = matched.get(rva, [])
        # A stash on a matched rva is an orphan ONLY when real C++ already owns
        # it. Every dump candidate is matched by construction -- a naked
        # transcription lands byte-verified -- and converting those is exactly
        # what a stash is for, so the dump lane must survive this check.
        for sym, source in claims:
            # Same two-part test progress.py uses to route a row to its `dump`
            # lane: an .asm/.lib row is retail re-encoded by extension alone,
            # and a .cpp row is one when its body is a naked/__emit lift.
            if Path(source).suffix.lower() in (".asm", ".s", ".lib"):
                continue
            text = source_blobs[ROOT / source].decode("utf-8", errors="replace")
            if "__declspec(naked)" in text or "_emit" in text:
                continue
            problems.append(
                f"{rel}: {rva} already has real C++ at {source} ({sym}). "
                f"It landed — delete the stash.")
            break
    return len(paths)


# Orphans that already exist: 6 .cpp under game/ own no matched row, the oldest
# added 2026-08-03. They fail build.py's verify_source_claims, but that runs only
# in the FULL gate -- which no commit or push hook invokes -- so they accumulated
# silently for weeks while every routine gate stayed green. This is a ratchet,
# not a clean-up: it cannot fail the fleet today, and it refuses the 7th.
# It may only ever be LOWERED, never raised to get green. Five of the six have
# since been claimed or removed; leaving the number at 6 let five new orphans in.
ORPHAN_BASELINE = 0


def worldbuilder_claims(spec, sources_ok):
    import target_hooks

    owned = {path for path in sources_ok if path.startswith(target_hooks.OWNED)}
    if not owned:
        return set()
    if not {target_hooks.CONFIG, target_hooks.LEDGER} <= sources_ok:
        raise ValueError("WorldBuilder sources require a target configuration and ledger")
    if spec is not None:
        # The target validator reads disk; it may exempt only this snapshot's claims.
        snapshot = ":" if spec == "" else spec
        sources = target_hooks._sources(ROOT, snapshot, sources_ok)
        dependencies = owned | sources | target_hooks._donor_paths(ROOT, snapshot, sources_ok)
        dependencies.add(target_hooks.CONFIG)
        dependencies.add("inputs/baselines/bfme1/workshop-vanilla-1.03/files/worldbuilder.exe")
        target_hooks._clean(ROOT, snapshot, dependencies)
    return target_hooks.validated_worldbuilder_sources(ROOT)


def read_data_rows(spec):
    """data_rows.csv at `spec` (b"" when that state has none)."""
    path = ROOT / "targets/game/reverse" / "data_rows.csv"
    if spec is None:
        return path.read_bytes() if path.exists() else b""
    rel = "targets/game/reverse/data_rows.csv"
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"{spec}:{rel}"], capture_output=True)
    return out.stdout if out.returncode == 0 else b""


def data_row_sources(raw):
    """Sources owning a matched data row (tools/data_rows.py): a data-only TU."""
    import data_rows
    try:
        return {row["source"] for _, row in data_rows.parse(raw) if row.get("status") == "matched"}
    except ValueError:
        return set()


def check_orphans(spec, problems, *, functions_raw=None, sources_ok=None, data_raw=None):
    """Refuse a NEW game/*.cpp that owns no matched row.

    A source with no row is presence pretending to be progress: nothing compiles
    it, nothing verifies it, and the only check that catches it is one the
    workflow never runs. Counting rather than listing keeps this a few lines and
    keeps the existing backlog someone else's to clear. ``functions_raw`` and
    ``sources_ok`` are the state-specific values already loaded by ``main``;
    omitted values retain the standalone helper's reads.
    """
    claimed = set()
    if functions_raw is None:
        functions_raw = read_ledger(FUNCTIONS, spec)
    for row in csv.reader(io.StringIO(functions_raw.decode(
            "utf-8", errors="replace"))):
        if len(row) == 7 and row[5] == "matched":
            claimed.add(row[4])
    if sources_ok is None:
        sources_ok = known_sources(spec)
    # a data-only TU owns its globals in data_rows.csv (tools/data_rows.py)
    claimed.update(data_row_sources(read_data_rows(spec) if data_raw is None else data_raw))
    try:
        claimed.update(worldbuilder_claims(spec, sources_ok))
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        problems.append(f"WorldBuilder source ownership is invalid: {error}")
    # No generated-tree exemption: game/gen_asm/ dumps are .asm, and a game/gen_small/
    # TU emptied by a repoint (5c065afaba) broke every full gate while this check,
    # which skipped game/gen_small/, stayed green.
    orphans = sorted(
        path for path in sources_ok
        if path.startswith("game/") and path.endswith(".cpp")
        and path not in claimed)
    if len(orphans) > ORPHAN_BASELINE:
        problems.append(
            f"{len(orphans)} game/*.cpp own no matched row, over the "
            f"{ORPHAN_BASELINE} already known. Byte-match one function in your "
            f"new file or delete it -- source presence is not progress. "
            f"Never raise ORPHAN_BASELINE to get green; it only goes down. "
            f"Orphans: {', '.join(orphans)}")
    return len(orphans)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    where = parser.add_mutually_exclusive_group()
    where.add_argument("--staged", action="store_true",
                       help="validate the git-staged ledgers instead of the working tree")
    where.add_argument("--ref", metavar="REF",
                       help="validate the ledgers as committed at REF")
    where.add_argument("--re-attempts-range", nargs=2, metavar=("BASE", "TIP"),
                       help="only re_attempts.log's append-only rule, for every commit in BASE..TIP "
                            "(pre-push: a deletion below the pushed tip)")
    args = parser.parse_args()
    if args.re_attempts_range:
        problems = []
        check_re_attempts_range(*args.re_attempts_range, problems)
        if problems:
            print(f"check_csv: {len(problems)} problem(s):", file=sys.stderr)
            for p in problems:
                print(f"  - {p}", file=sys.stderr)
            raise SystemExit(1)
        print(f"check_csv: OK ({RE_ATTEMPTS_REL} append-only over "
              f"{args.re_attempts_range[0]}..{args.re_attempts_range[1]})")
        return

    spec = "" if args.staged else args.ref  # None -> working tree
    problems = []
    functions_raw = read_ledger(FUNCTIONS, spec)
    deleted = tombstones(read_ledger(DELETED, spec))
    # All three state-sensitive checks need the same source membership. Resolve
    # it once, after selecting the mode: working-tree (None), index (""), and a
    # committed ref each have different authoritative files. Never cache this
    # set across invocations or modes.
    sources_ok = known_sources(spec)
    n_funcs = check_functions(functions_raw, problems, sources_ok, deleted)
    if args.staged:
        head_functions = read_ledger(FUNCTIONS, "HEAD")
        check_removed_rows(head_functions, functions_raw, deleted, problems)
        check_row_extents(head_functions, functions_raw, problems)
    n_syms = check_symbols(read_ledger(SYMBOLS, spec), problems)
    if args.staged or args.ref:
        base_spec = "HEAD" if args.staged else f"{args.ref}^"
        has_base = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "-q", "--verify", base_spec],
                                  capture_output=True).returncode == 0
        if has_base:
            check_re_attempts_append_only(read_re_attempts(base_spec), read_re_attempts(spec), problems,
                                          dedupe_claim=re_attempts_dedupe_claim(args.ref),
                                          ledger=matched_ledger_keys(functions_raw))
    check_attempts(spec, problems, functions_raw=functions_raw,
                   sources_ok=sources_ok)
    data_raw = read_data_rows(spec)
    n_data = 0
    if data_raw:
        import data_rows
        n_data = data_rows.check(data_raw, problems, sources_ok)
    n_orphans = check_orphans(spec, problems, functions_raw=functions_raw,
                              sources_ok=sources_ok, data_raw=data_raw)

    if problems:
        print(f"check_csv: {len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        raise SystemExit(1)
    print(f"check_csv: OK (functions.csv {n_funcs} rows, symbols.csv {n_syms} rows"
          + (f", data_rows.csv {n_data} rows" if n_data else "")
          + (f", {n_orphans} known row-less source(s))" if n_orphans else ")"))


if __name__ == "__main__":
    main()
