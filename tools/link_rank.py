#!/usr/bin/env python3
"""Rank link blockers by the matched bytes they keep from linking.

`link_check.py next` serves `sole` blockers only (a unit's single blocker), and
that view is near empty: most unlinked bytes sit in units with many blockers.
This reads the same census index (build/link_census/link_index.pkl, from
tools/link_census.py or the daily workflow's `link-census-index` artifact) and
reports the views Open-BFME-2's tools/link_rank.py used to drive its linking
pass:

  sole     blockers that are a unit's ONLY blocker, by that unit's bytes
  names    every blocking name by bytes shared out among the blockers of the
           units it blocks: what a fix moves overall
  near     units with at most --near blockers, largest first: the work list

Kinds: U unresolved, D duplicate strong definition, L COMDAT copy that is not
retail's body, S the kept definition is proven not retail's (wrong_selected),
A a hard-coded image address in the source.

  python3 tools/link_rank.py [--top N] [--near K] [--kind U|D|L|S|A] [--json PATH]
  python3 tools/link_rank.py --file SOURCE     one unit's blockers
  python3 tools/link_rank.py --class            names grouped by the class token in the mangled name

These are the blockers the last census recorded, not current link results;
check a candidate with tools/link_check.py --census-only before repairing it.
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import link_census as lc  # noqa: E402

GENERATED = ("game/gen_asm/", "game/gen_small/")


def blockers(index):
    """({source: {(kind, name)}}, {source: matched bytes}) from the census index."""
    sizes, seen = collections.Counter(), set()
    for row in lc.ledger():
        source = row["source"]
        if not source.lower().endswith((".c", ".cpp")):
            continue
        key = (source, row["target_rva"])
        if key not in seen:
            seen.add(key)
            sizes[source] += int(row["target_size"] or 0, 0)
    out = {}
    for source, entry in index["blockers"].items():
        found = {("U", s) for s in entry["unresolved"]}
        found |= {("D", s) for s in entry["duplicates"]}
        found |= {("L", s) for s in entry["losers"]}
        found |= {("S", s) for s in entry["wrong_selected"]}
        if entry["addresses"]:
            found.add(("A", ""))
        out[source] = found
    return out, sizes


def class_token(name):
    match = re.search(r"@([A-Za-z_]\w*)@@", name)
    return match.group(1) if match else name[:40]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--near", type=int, default=3)
    parser.add_argument("--kind", choices="UDLSA")
    parser.add_argument("--file")
    parser.add_argument("--json", help="write {source: [[kind, name], ...]} here")
    parser.add_argument("--class", dest="by_class", action="store_true",
                        help="group the names view by class token")
    args = parser.parse_args(argv)
    import link_check
    index = link_check.load_index()
    found, sizes = blockers(index)
    meta = index.get("meta", {})
    print(f"Census blockers: {meta.get('date', 'unknown')} at {meta.get('commit', 'unknown')}; "
          "current objects have not been checked.")
    if args.file:
        if args.file not in found:
            print(f"{args.file}: not in census; current link state unknown.")
            return 2
        names = sorted(found[args.file])
        print(f"{args.file}: {sizes[args.file]:,} matched bytes, "
              f"{'linked in census' if not names else f'{len(names)} blocker(s)'}")
        for kind, name in names:
            print(f"  {kind} {name}")
        return 0
    if args.json:
        Path(args.json).write_text(json.dumps({s: sorted(b) for s, b in found.items()}), encoding="utf-8")

    authored = {s: b for s, b in found.items() if not s.startswith(GENERATED)}
    linked = [s for s, b in authored.items() if not b]
    print(f"{len(linked):,} of {len(authored):,} authored units linked in census "
          f"({sum(sizes[s] for s in linked):,} of {sum(sizes[s] for s in authored):,} matched bytes)")
    absent = sum(not s.startswith(GENERATED) and s not in found for s in sizes)
    if absent:
        print(f"{absent:,} current matched unit(s) absent from the census; link state unknown.")

    def wanted(item):
        return args.kind is None or item[0] == args.kind

    def label(item):
        return f"{item[0]} {item[1] or '(source has a hard-coded image address)'}"

    sole, sole_units = collections.Counter(), collections.Counter()
    share, share_units = collections.Counter(), collections.Counter()
    by_count = collections.Counter()
    for source, items in authored.items():
        if not items:
            continue
        n = len(items)
        by_count["1" if n == 1 else "2-5" if n <= 5 else "6-20" if n <= 20 else "21+"] += sizes[source]
        if n == 1:
            item = next(iter(items))
            sole[item] += sizes[source]
            sole_units[item] += 1
        for item in items:
            share[item] += sizes[source] / n
            share_units[item] += 1
    print("unlinked matched bytes by blockers per unit: "
          + ", ".join(f"{k}: {by_count[k]:,}" for k in ("1", "2-5", "6-20", "21+")))

    print("\nsole blockers in census (what `link_check.py next` serves):")
    for item, value in [(i, v) for i, v in sole.most_common() if wanted(i)][:args.top]:
        print(f"  {value:8,} {sole_units[item]:4} units  {label(item)[:150]}")
    if args.by_class:
        classes, class_units = collections.Counter(), collections.Counter()
        for item, value in share.items():
            if wanted(item) and item[1]:
                classes[class_token(item[1])] += value
                class_units[class_token(item[1])] += share_units[item]
        print("\nblocking names by shared bytes, grouped by class token:")
        for cls, value in classes.most_common(args.top):
            print(f"  {int(value):8,} {class_units[cls]:5} unit-names  {cls}")
    else:
        print("\nblocking names by shared bytes:")
        for item, value in [(i, v) for i, v in share.most_common() if wanted(i)][:args.top]:
            print(f"  {int(value):8,} {share_units[item]:4} units  {label(item)[:150]}")
    print(f"\nunits within {args.near} blocker(s) of linking:")
    near = sorted((s for s, b in authored.items() if 0 < len(b) <= args.near and all(wanted(i) for i in b)),
                  key=lambda s: -sizes[s])
    for source in near[:args.top]:
        names = "; ".join(label(i)[:70] for i in sorted(authored[source]))
        print(f"  {sizes[source]:7,}  {source}  [{names}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
