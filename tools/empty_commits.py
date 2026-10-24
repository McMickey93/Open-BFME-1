#!/usr/bin/env python3
"""Refuse outgoing commits that change no file (pre-push).

WHY. A seat that keeps re-landing work already on master ends up with nothing left
to change, and when its script forces the commit through anyway (`--allow-empty`, a
cherry-pick or rebase told to keep empty commits) it pushes an empty commit every
cooldown. 57 reached master on 2026-10-08..12: "Link MetaEvent (819B): own
TheMetaMap in MetaEvent.cpp with its data row" landed as 277bfd21a8 and then 14 more
times with no content (a9ec33cb68 ... 6ede5559ca). Every gate passes such a commit,
since it changes no file, and replay_check.py only reports. This is the one replay
that is certain: a commit with exactly one parent and that parent's tree.

  python3 tools/empty_commits.py --range REMOTE_SHA LOCAL_SHA

Prints the empty commits and exits 1 when there is one, else exits 0. Merges and
root commits are not judged, nor are commits origin/master already has (a branch
being brought up to master carries the old ones, and nobody can remove those).
Exit 2: git could not be read, and the hook fails closed.
"""
import argparse
import subprocess
import sys

SEP = "\x1f"
SHOWN = 20
REMEDY = "git rebase --no-keep-empty --no-ff origin/master"
REMEDY_MERGES = "git rebase --no-keep-empty --no-ff --rebase-merges origin/master"
UPSTREAM = "refs/remotes/origin/master"


def git(*args, input=None):
    got = subprocess.run(["git", *args], input=input, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    if got.returncode:
        raise RuntimeError(f"git {' '.join(args[:2])}: {got.stderr.strip() or got.returncode}")
    return got.stdout


def outgoing(base, tip):
    """[[sha, tree, parents, subject]] of base..tip less what origin/master has, newest first.
    NUL-separated records: a subject may hold any line separator (U+2028), and a
    log.showSignature setting must not add lines of its own."""
    known = subprocess.run(["git", "rev-parse", "-q", "--verify", UPSTREAM], capture_output=True).returncode == 0
    out = git("log", "-z", "--no-show-signature", f"--format=%H{SEP}%T{SEP}%P{SEP}%s", f"{base}..{tip}",
              *([f"^{UPSTREAM}"] if known else []))
    return [record.split(SEP, 3) for record in out.split("\0") if record]


def empty_commits(rows):
    """[(sha, subject)] of outgoing() rows with one parent and that parent's tree."""
    tree = {sha: t for sha, t, _, _ in rows}
    single = [(sha, t, parents, subject) for sha, t, parents, subject in rows if len(parents.split()) == 1]
    outside = sorted({parents for _, _, parents, _ in single if parents not in tree})
    if outside:
        out = git("cat-file", "--batch-check=%(objectname)", input="".join(f"{p}^{{tree}}\n" for p in outside))
        for parent, line in zip(outside, out.split("\n")):
            if line and not line.endswith(" missing"):
                tree[parent] = line.strip()
    return [(sha, subject) for sha, t, parent, subject in single if tree.get(parent) == t]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--range", nargs=2, metavar=("BASE", "TIP"), required=True)
    args = ap.parse_args(argv)
    sys.stderr.reconfigure(errors="backslashreplace")       # a subject the console cannot encode
    try:
        rows = outgoing(*args.range)
        found = empty_commits(rows)
    except (RuntimeError, OSError) as e:
        print(f"empty_commits: {e}", file=sys.stderr)
        return 2
    if not found:
        return 0
    print(f"empty_commits: {len(found)} outgoing commit(s) change no file:", file=sys.stderr)
    for sha, subject in found[:SHOWN]:
        print(f"  {sha[:10]} {subject}", file=sys.stderr)
    if len(found) > SHOWN:
        print(f"  ... and {len(found) - SHOWN} more", file=sys.stderr)
    print("Work that is already on master leaves nothing to commit, so there is nothing to push for it.",
          file=sys.stderr)
    if any(len(parents.split()) > 1 for _, _, parents, _ in rows):
        print("Remove the empty commits and push again. This range holds merge commits, which a plain\n"
              "rebase would flatten; this keeps them but redoes each merge, so check any conflict you\n"
              "resolved by hand:\n"
              f"  {REMEDY_MERGES}", file=sys.stderr)
    else:
        print("Remove the empty commits and push again. This rebases your commits onto origin/master:\n"
              f"  {REMEDY}", file=sys.stderr)
    print("A script that made them is re-landing work that already landed: fetch and look at origin/master\n"
          "before retrying, and never force the commit with --allow-empty, --keep-redundant-commits or\n"
          "--empty=keep.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
