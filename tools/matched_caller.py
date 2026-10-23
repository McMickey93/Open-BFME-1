#!/usr/bin/env python3
"""Matched-caller evidence: callee names proven by byte-identical callers. Dry run only.

A caller copy whose bytes equal retail's at its ledger home, everywhere outside its
relocation fields, reproduces retail's code. Each REL32 relocation in it then
says "the function this source calls by name N is the one retail calls at T".
When the ledger's only rows at T (or at the body an incremental-link stub at T
jumps to) carry a placeholder name, and N has no row anywhere, N is a candidate
real name for that body.

A caller's author can still have guessed N: the bytes match whatever the callee
is called. So a proposal is graded by independent corroboration, never by one
caller alone:

  oracle     the ILT oracle CONFIRMS N at the body (tools/ilt_oracle.py)
  multi      two or more distinct real-named, ledger-homed caller bodies name N
             at T, its identifiers occur in vendored upstream source, the
             agreement is not just an existing pin, and the oracle does not
             CONTRADICT N there
  single     one independent caller only (written to singles.json, never proposed)

Refused outright (each written to refusals.json with its reason):
  - a caller copy whose other relocations do not land where the ledger says
    (RetailTruth._judge "wrong"): its home may be a template twin;
  - a ?ji_ import thunk row: map the import instead;
  - a callee name that matched callers resolve to more than one body;
  - a callee name the ledger already places elsewhere (row name or object-symbol=);
  - any caller names a different callee at the same body (conflict);
  - N already has a ledger row, or a pin at an address that is neither T, the
    body, nor an ILT stub of it (the inlined-wrapper case: ~StringBase pinned at
    0x5E490 while retail callers land on releaseBuffer at 0x887940);
  - N is a placeholder or invented name (ilt_oracle.tier) or the rows at the
    body include a real or invented name (that is a two-real-names dispute);
  - the oracle CONTRADICTS N at the body;
  - the caller copy has fewer than MIN_CODE bytes outside relocations (a
    vtable or pointer table "matches" any home, so it proves nothing).

    python3 tools/matched_caller.py [--objects build/match] [--out build/matched_caller]

Reads the census index (link_check.load_index), the ledger and the retail image;
writes only under --out. Nothing here renames a row: proposals go through
add_match.py --correct-identity or the operator's name corrections.
"""
import argparse
import collections
import concurrent.futures
import csv
import json
import multiprocessing
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import link_census  # noqa: E402
import link_check  # noqa: E402
from ilt_oracle import oracle as ilt, tier  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MIN_CODE = 8
GENERATED = ("game/gen_asm/", "game/gen_small/", "game/masm_dumps/")
# whole identifier parts only: "getOverallBestWinStreak" is not a "Twin" (review round 2)
STAND_IN = re.compile(r"(Dummy|Shim|StandIn|Stand_In|Surrogate|Twin|Placeholder)(?=[A-Z_0-9@]|$)")
UPSTREAM = (ROOT / "inputs/reference/CnC_Generals_Zero_Hour", ROOT / "inputs/vendor")
# access letters that the ILT hash cannot tell apart (review 2026-10-23: QAE/IAE 6%, MAE/UAE 29%)
ACCESS_GROUPS = ("AIQ", "EMU", "CKS")


def access_variants(name):
    """The callee with each other access letter, and YA<->YG for free functions.

    The access code follows the '@@' that ends the qualified name; in a template
    name earlier '@@' close template arguments, so every candidate position is
    tried (over-generating only makes the twin check stricter)."""
    out = []
    for m in re.finditer(r"@@(?=([A-Z])([A-Z]))", name):
        letter, cv = m.group(1), m.group(2)
        at = m.end()
        group = next((g for g in ACCESS_GROUPS if letter in g), None)
        if group and (cv in "AB" or group == "CKS"):
            out += [name[:at] + other + name[at + 1:] for other in group if other != letter]
        if letter == "Y" and cv in "AG":
            out.append(name[:at + 1] + ("G" if cv == "A" else "A") + name[at + 2:])
    return [v for v in dict.fromkeys(out) if v != name]


def tail_variants(name, span=3):
    """Single-letter type-code swaps in the last `span` characters: the ILT hash is nearly
    blind there (review round 2: 57/158 confirm at 3 from the end, ~0 from 4 on)."""
    out = []
    for i in range(max(0, len(name) - span), len(name)):
        if name[i].isupper():
            out += [name[:i] + c + name[i + 1:] for c in "DEFGHIJKMNO_" if c != name[i]]
    return out


_UPSTREAM_MEMO = {}


def upstream_declares(name):
    """True when the callee's class and member identifiers both occur in vendored upstream source."""
    m = re.match(r"^\?(\?[0-9A-Z_]?)?([A-Za-z_]\w*)@(?:\?\$)?([A-Za-z_]\w*)@", name)
    if not m:
        return False
    idents = {m.group(3)} | ({m.group(2)} if not m.group(1) else set())
    for ident in idents:
        if ident not in _UPSTREAM_MEMO:
            hit = subprocess.run(["rg", "-l", "-m1", "-w", "-F", ident, *map(str, UPSTREAM)],
                                 capture_output=True, text=True).stdout.strip()
            _UPSTREAM_MEMO[ident] = bool(hit)
        if not _UPSTREAM_MEMO[ident]:
            return False
    return True
_TRUTH = None


def _init():
    global _TRUTH
    _TRUTH = link_census.RetailTruth(link_census.ledger())


def code_body(target):
    """The body a REL32 target reaches: an ILT stub's jump target, else itself."""
    return _TRUTH._stub(target) or target


def scan_object(job):
    """[(caller, home, source, callee, target, body)] for one object's matched copies."""
    path, source = job
    t = _TRUTH
    out = []
    try:
        data = Path(path).read_bytes()
    except OSError:
        return out
    for sym, body, relocs, digest, size in link_census._comdat_sections(data):
        if body is None:
            continue
        name = sym["name"]
        home = t.ledger.get(link_census._normal(name)) or t.pinned.get(link_census._normal(name))
        if not home or len(home) != 1:
            continue
        start = next(iter(home)) - sym["value"]
        retail = t._read(start, size)
        if retail is None:
            continue
        relocs = link_census.bind_weak_relocations(relocs, None, t)
        covered = sum(2 if kind == 0x000A else 4 for _, kind, _ in relocs)
        if size - covered < MIN_CODE:
            continue
        mask = bytearray(body)
        for where, kind, _ in relocs:
            width = 2 if kind == 0x000A else 4
            mask[where:where + width] = retail[where:where + width]
        if bytes(mask) != retail:
            continue
        # equal bytes do not place the copy: a template twin differs only in its
        # call targets, so every relocation must also land where the ledger says
        if t._judge(start, sym, body, relocs, size) == "wrong":
            continue
        by_pin = link_census._normal(name) not in t.ledger
        for where, kind, ref in relocs:
            if kind != t.REL32 or ref["storage"] != link_census.EXTERNAL or ref.get("content") is not None:
                continue
            addend = struct.unpack_from("<i", body, where)[0]
            value = struct.unpack_from("<i", retail, where)[0]
            target = start + where + 4 + value - addend
            out.append((name, start, source, ref["name"], target, code_body(target), by_pin))
    return out


def build_object_symbol(row):
    m = re.search(r"object-symbol=([^;]+)", row.get("notes") or "")
    return m.group(1) if m else None


def ledger_maps():
    rows_at, row_names, pins = collections.defaultdict(list), set(), collections.defaultdict(set)
    rvas = link_census.RetailTruth._rvas
    with (ROOT / "targets/game/reverse/functions.csv").open(newline="") as fh:
        for row in csv.DictReader(fh):
            row_names.add(row["name"])
            if row["target_rva"]:
                rows_at[int(row["target_rva"], 16)].append(row)
    with (ROOT / "targets/game/reverse/symbols.csv").open(newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                pins[row["name"]].add(frozenset(rvas(int(row["address"], 16))))
            except ValueError:
                pass
    return rows_at, row_names, pins


def judge(callee, body, target, calls, rows_at, row_names, pins, ilt_check):
    """(grade, reasons) for proposing `callee` as the name of `body`."""
    reasons = []
    if any(r["name"].startswith("?ji_") for r in rows_at.get(body, [])):
        return "refused", ["import thunk (?ji_): map the import, do not rename"]
    rows = [r for r in rows_at.get(body, []) if not r["name"].startswith("?j_")]
    if not rows:
        return "refused", ["no ledger row at the body"]
    tiers = {tier(r["name"]) for r in rows}
    if tiers != {"placeholder"}:
        return "refused", ["rows at the body include a non-placeholder name: " + ", ".join(sorted(tiers))]
    if tier(callee) != "real":
        return "refused", [f"callee name is {tier(callee)}"]
    if STAND_IN.search(callee):
        return "refused", ["callee name is a stand-in (Dummy/Shim/Surrogate/...)"]
    if any(build_object_symbol(r) == callee for r in rows):
        return "refused", ["callee only repeats the row's own object-symbol= (circular)"]
    if callee in row_names:
        return "refused", ["callee already has a ledger row"]
    known = _TRUTH.ledger.get(link_census._normal(callee), set())
    if any(code_body(a) != body and a != target for a in known):
        return "refused", ["callee already placed elsewhere by the ledger (row or object-symbol)"]
    # a pin is consistent when either of its readings (RVA, or VA minus the base) reaches the body
    stray = [p for p in pins.get(callee, ()) if not any(a in (body, target) or code_body(a) == body for a in p)]
    if stray:
        return "refused", ["callee pinned elsewhere: " + ", ".join(hex(min(p)) for p in stray)]
    verdict = ilt_check(callee, body)
    if verdict == "CONTRADICTED":
        return "refused", ["ILT oracle contradicts the callee at the body"]
    pinned_here = any(code_body(a) == body or a in (body, target) for p in pins.get(callee, ()) for a in p)
    lineage = ["name already pinned at this body (pin lineage)"] if pinned_here else []
    if verdict == "CONFIRMED":
        twins = [v for v in access_variants(callee) if ilt_check(v, body) == "CONFIRMED"]
        if twins:
            return "single", ["ILT oracle confirms, but so does another access/convention: " + ", ".join(twins)] + lineage
        tails = [v for v in tail_variants(callee) if ilt_check(v, body) == "CONFIRMED"]
        if tails and "_STL@" not in callee:
            # STLport names: template arguments and size_t fix the trailing types
            return "single", ["ILT oracle confirms, but a trailing type swap also fits: " + ", ".join(tails[:3])] + lineage
        return "oracle", ["ILT oracle confirms; no access, convention or trailing-type variant fits"] + lineage
    settled = {c["home"] for c in calls if not c["by_pin"] and tier(c["caller"]) == "real"}
    if len(settled) >= 2 and upstream_declares(callee) and not pinned_here:
        return "multi", [f"{len(settled)} distinct real-named, ledger-homed caller bodies; "
                         "identifiers occur in vendored upstream source"]
    why = (f"{len(settled)} settled caller bodies" if len(settled) < 2 else
           "identifiers not found in upstream source" if not upstream_declares(callee) else
           "agreement may only reflect an existing pin")
    return "single", [why] + lineage


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--objects", default="build/match", help="census-commit object directory")
    ap.add_argument("--out", default="build/matched_caller")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args(argv)
    index = link_check.load_index()
    obj_source = {e["object"]: s for s, e in index["blockers"].items()}
    jobs = [(str(ROOT / args.objects / o), obj_source[o]) for o in index["objects"]
            if o in obj_source and not obj_source[o].startswith(GENERATED) and (ROOT / args.objects / o).exists()]
    with concurrent.futures.ProcessPoolExecutor(args.workers, mp_context=multiprocessing.get_context("spawn"),
                                                initializer=_init) as pool:
        found = [c for part in pool.map(scan_object, jobs, chunksize=32) for c in part]
    _init()
    rows_at, row_names, pins = ledger_maps()
    o = ilt()

    def ilt_check(name, body):
        return o.check(name, body)[0]

    by_body = collections.defaultdict(list)
    bodies_of = collections.defaultdict(set)
    for caller, home, source, callee, target, body, by_pin in found:
        by_body[body].append({"caller": caller, "home": hex(home), "source": source,
                              "callee": callee, "target": hex(target), "by_pin": by_pin})
        bodies_of[link_census._normal(callee)].add(body)
    proposals, refused, conflicts, refusals = [], collections.Counter(), [], []
    for body, calls in by_body.items():
        names = {c["callee"] for c in calls}
        current = [r["name"] for r in rows_at.get(body, []) if not r["name"].startswith("?j_")]
        if len(names) > 1:
            if current and all(tier(n) == "placeholder" for n in current):
                conflicts.append({"body": hex(body), "rows": current, "callees": sorted(names)})
            continue
        callee = next(iter(names))
        if callee in current:
            continue                              # already named that way
        if len(bodies_of[link_census._normal(callee)]) > 1:
            refused["callee name reaches several bodies"] += 1
            refusals.append({"body": hex(body), "rows": current, "callee": callee,
                             "why": "callee name reaches several bodies: " + ", ".join(
                                 hex(b) for b in sorted(bodies_of[link_census._normal(callee)]))})
            continue
        grade, why = judge(callee, body, int(calls[0]["target"], 16), calls, rows_at, row_names, pins, ilt_check)
        if grade == "refused":
            refused[why[0].split(":")[0]] += 1
            refusals.append({"body": hex(body), "rows": current, "callee": callee, "why": why[0]})
            continue
        proposals.append({"body": hex(body), "rows": current, "callee": callee, "grade": grade, "why": why,
                          "distinct_callers": len({c["home"] for c in calls}),
                          "caller_sources": len({c["source"] for c in calls}), "callers": calls})
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "conflicts.json").write_text(json.dumps(conflicts, indent=1))
    (out / "refusals.json").write_text(json.dumps(refusals, indent=1))
    singles = [p for p in proposals if p["grade"] == "single"]
    proposals = [p for p in proposals if p["grade"] != "single"]
    (out / "proposals.json").write_text(json.dumps(proposals, indent=1))
    (out / "singles.json").write_text(json.dumps(singles, indent=1))
    with (out / "proposals.tsv").open("w") as fh:
        fh.write("grade\tbody\tcurrent_rows\tproposed_name\tcaller_bodies\n")
        for p in sorted(proposals, key=lambda p: (p["grade"], p["body"])):
            fh.write(f"{p['grade']}\t{p['body']}\t{';'.join(p['rows'])}\t{p['callee']}\t"
                     f"{len({c['home'] for c in p['callers']})}\n")
    grades = collections.Counter(p["grade"] for p in proposals + singles)
    print(f"callers scanned: {len(jobs)} objects, {len(found)} matched REL32 calls, {len(by_body)} bodies")
    print(f"proposals: {dict(grades)}; conflicts (placeholder bodies with disagreeing callers): {len(conflicts)}")
    print("refused:", dict(refused.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
