#!/usr/bin/env python3
"""Remove union-merge duplicate runs from targets/game/reverse/re_attempts.log.

Approved by the project lead 2026-10-16. The log is union-merged, and rebases
across commits that rewrote line endings re-added whole blocks of rows. A
DUPLICATE RUN is a maximal run of two or more consecutive rows that exactly
(CR-insensitively) repeats an earlier contiguous block of the log; its first
occurrence is kept and the run is deleted. A single repeated row is left in
place (it may be a legitimate re-record) and only listed.

find_runs() is the one definition: check_csv's append-only guard recomputes it
to admit the one dedupe commit and nothing else. The claim is one-shot: it
names the git blob id of the log it dedupes (trailer `Re-Attempts-Dedupe: <N>
runs base=<blob>`, and BFME_RE_ATTEMPTS_DEDUPE='<N> runs base=<blob>' for its
pre-commit), so it can never admit a deletion from a later log.

  python3 tools/re_attempts_dedupe.py              report runs and single repeats
  python3 tools/re_attempts_dedupe.py --write      rewrite the log without the runs
  python3 tools/re_attempts_dedupe.py --report F   also write the single repeats to F
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
LOG = ROOT / "targets/game/reverse/re_attempts.log"


def split_lines(raw):
    """Lines split on LF only, terminators kept (the last may have none); a CR
    inside a row is content, not a line break."""
    parts = raw.split(b"\n")
    return [part + b"\n" for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


def plain(line):
    return line.rstrip(b"\r\n")


def find_runs(lines):
    """(runs, singles): runs = [(start, length, earlier_start)] of maximal
    duplicate runs (0-based line indexes); singles = [(index, earlier_index)]
    of lone repeated rows. Lines are compared without their terminators;
    empty lines never take part."""
    keys = [plain(line) for line in lines]
    seen = {}                    # key -> earlier indexes
    runs, singles = [], []
    i = 0
    while i < len(keys):
        key = keys[i]
        earlier = seen.get(key, []) if key else []
        best, best_at = 0, None
        for k in earlier:
            m = 0
            while (i + m < len(keys) and k + m < i and keys[i + m] and keys[k + m] == keys[i + m]):
                m += 1
            if m > best:
                best, best_at = m, k
        if best >= 2:
            runs.append((i, best, best_at))   # deleted rows add no new positions
            i += best
            continue
        if earlier:
            singles.append((i, earlier[0]))
        if key:
            seen.setdefault(key, []).append(i)
        i += 1
    return runs, singles


def dedupe(raw):
    """(new raw, runs, singles): RAW without its duplicate runs."""
    lines = split_lines(raw)
    runs, singles = find_runs(lines)
    drop = set()
    for start, length, _ in runs:
        drop.update(range(start, start + length))
    return b"".join(line for i, line in enumerate(lines) if i not in drop), runs, singles


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report")
    args = ap.parse_args(argv)
    raw = LOG.read_bytes()
    new, runs, singles = dedupe(raw)
    removed = sum(length for _, length, _ in runs)
    print(f"re_attempts_dedupe: {len(runs)} duplicate run(s), {removed} row(s); "
          f"{len(singles)} single repeated row(s) kept")
    if args.report:
        lines = split_lines(raw)
        with open(args.report, "w", encoding="utf-8") as out:
            out.write("line\tfirst_seen_line\trow\n")
            for i, k in singles:
                out.write(f"{i + 1}\t{k + 1}\t{plain(lines[i]).decode('utf-8', 'replace')}\n")
    if args.write and runs:
        import check_csv
        LOG.write_bytes(new)
        print(f"Re-Attempts-Dedupe: {len(runs)} runs base={check_csv.git_blob_id(raw)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
