#!/usr/bin/env python3
"""Discovery-only masked placement of every function emitted by an existing TU object.

Examples (no compilation, subprocesses, ledger writes or landing):
  python3 tools/place_bodies.py game/path/Unit.cpp
  python3 tools/place_bodies.py --object game/path/Unit.cpp /path/to/Unit.obj --json

Positional sources use build.obj_path; --object explicitly pairs a source with an
already-built object, including one in another checkout. Object/source hashes are
reported, but their compile relationship and freshness are NOT established here.
The source label is not identity evidence. harvest owns compilation; locate owns
COFF function spans and masking. Neither tool's compiling/writing CLI is invoked.

A unique byte hit proves only candidate placement, never identity or boundaries.
Every result needs BFME1 identity validation, add_match and pin_consistency gates.
"""
import argparse
import bisect
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build
import eligibility
import locate
import one_identity
import pin_consistency

REL32 = 0x0014
C_NAME = re.compile(r"_[A-Za-z_]\w*(@\d+)?")
DENYLIST = build.ROOT / "targets/game/reverse/place_denylist.txt"
NOTICE = ("Candidate evidence only: a unique byte hit is placement evidence, never "
          "identity evidence. Validate identity and boundaries, then use BFME1 "
          "add_match and pin_consistency gates. No ledgers are written.")
NO_FOLD = ("Possible folded body / over-claim signal only: BFME1 retail has no "
           "identical-COMDAT folding; multiple names never prove a fold or permit a pin.")


def placeable(name):
    """BFME2's applicable spelling filter, without any admission policy."""
    return name.startswith("?") or C_NAME.fullmatch(name) is not None


def sha256(data):
    return hashlib.sha256(data).hexdigest()


class Retail:
    def __init__(self, path):
        self.path = Path(path)
        data = self.path.read_bytes()
        self.sha256 = sha256(data)
        pe = build.u32(data, 0x3C)
        if data[:2] != b"MZ" or data[pe:pe + 4] != b"PE\0\0":
            raise ValueError("not a PE image")
        optional = pe + 24
        if build.u16(data, pe + 4) != 0x14C or build.u16(data, optional) != 0x10B:
            raise ValueError("expected an i386 PE32 image")
        self.image_base = build.u32(data, optional + 28)
        section = next(s for s in build.pe_sections(data) if s["name"] == ".text")
        # pe_sections.size includes virtual zero-fill. Only search file-backed
        # .text, never the following section or bytes invented by the loader.
        table = optional + build.u16(data, pe + 20)
        raw_size = next(build.u32(data, table + i * 40 + 16)
                        for i in range(build.u16(data, pe + 6))
                        if data[table + i * 40:table + i * 40 + 8].rstrip(b"\0") == b".text")
        raw = section["raw_pointer"]
        if raw + raw_size > len(data):
            raise ValueError("truncated retail .text")
        self.text = data[raw:raw + raw_size]
        self.text_rva = section["rva"]
        _, entries = one_identity.link_table(self.text, self.text_rva)
        self.thunks = {slot: body for body, slots in entries.items() for slot in slots}

    def in_text(self, rva):
        return self.text_rva <= rva < self.text_rva + len(self.text)

    def body_of(self, rva):
        # Follow only the ILT slots proved by one_identity, never an arbitrary
        # E9 that might be a real tail-calling body or an instruction operand.
        seen = set()
        while rva in self.thunks:
            if rva in seen:
                raise ValueError("retail ILT cycle")
            seen.add(rva)
            rva = self.thunks[rva]
        return rva

    def call(self, rva, offset, addend):
        displacement = struct.unpack_from("<i", self.text, rva - self.text_rva + offset)[0]
        encoded = (rva + offset + 4 + displacement) & 0xFFFFFFFF
        return encoded, (encoded - addend) & 0xFFFFFFFF


def object_functions(path):
    """Reuse locate's executable-section spans; retain co-located symbol aliases."""
    path = Path(path)
    before = path.read_bytes()
    if build.u16(before, 0) != 0x14C:
        raise ValueError(f"{path}: expected i386 COFF")
    symbols = build.read_object_symbols(before)
    keys = {s["name"]: (s["section"], s["value"])
            for s in symbols if s["section"] > 0}
    aliases = collections.defaultdict(set)
    for name, key in keys.items():
        aliases[key].add(name)
    functions = []
    for name, span, relocs in locate.object_functions(path):
        for alias in sorted(aliases[keys[name]]):
            functions.append((alias, span, relocs))
    if path.read_bytes() != before:
        raise ValueError(f"{path}: object changed during discovery; retry after its owner finishes")
    return functions, {"path": str(path.resolve()), "sha256": sha256(before),
                       "size": len(before), "compile_provenance": "unverified"}


def masked_hits(retail, span, relocs):
    """All overlapping hits, using locate's longest fixed run and mask helpers."""
    # Trimming padding must not remove the high byte of a relocation addend.
    size = max(len(span.rstrip(b"\xcc")),
               max((off + build.RELOC_WIDTH.get(kind, 0) for off, kind, _ in relocs), default=0))
    body = span[:size]
    holes = []
    for offset, kind, _ in relocs:
        if kind not in (0x0006, REL32):
            raise ValueError(f"unsupported relocation 0x{kind:04X}")
        if offset < 0 or offset + 4 > len(body):
            raise ValueError("relocation crosses function span")
        holes.append(offset)
    segments = locate.hole_free_segments(len(body), holes)
    start, end = max(segments, key=lambda s: s[1] - s[0], default=(0, 0))
    if end - start < locate.MIN_NEEDLE:
        return body, [], "weak-pattern"
    needle = body[start:end]
    pattern = locate.masked(body, holes, len(body))
    cursor, hits = 0, []
    while True:
        found = retail.text.find(needle, cursor)
        if found < 0:
            break
        cursor = found + 1
        pos = found - start
        if (pos >= 0 and pos + len(body) <= len(retail.text)
                and locate.masked(retail.text[pos:pos + len(body)], holes, len(body)) == pattern):
            hits.append(retail.text_rva + pos)
    return body, hits, None


def identity_source(row):
    """Delegate generated/dump/lift/assembly and identity classification to BFME1."""
    return (pin_consistency.names_identity(row) and not eligibility.is_dump_row(row)
            and not row["source"].startswith(one_identity.NOT_EVIDENCE))


class Evidence:
    def __init__(self, retail, names, points, spans):
        self.retail = retail
        points = sorted(points | {retail.body_of(p) for p in points})
        point_set = set(points)
        intervals = []
        for start, end in sorted(spans + [(p, p + 1) for p in points]):
            if intervals and start <= intervals[-1][1]:
                intervals[-1] = (intervals[-1][0], max(end, intervals[-1][1]))
            else:
                intervals.append((start, end))
        ends = [end for _, end in intervals]
        rows = []
        # Stream the ledger and retain just this scan's names/addresses/extents;
        # never load functions.csv, exports.csv or Ghidra's inventory wholesale.
        with build.FUNCTIONS.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                rva = int(row["target_rva"], 16)
                i = bisect.bisect_right(ends, rva)
                if (row["name"] in names or (i < len(intervals)
                        and intervals[i][0] < rva + int(row["target_size"]))):
                    rows.append(row)
        self.rows = rows
        identity_rows = [r for r in rows if identity_source(r)]
        self.owners = one_identity.real_names_by_address(identity_rows)
        # Use the existing pin guard's identity owner API as well as the
        # one_identity real-name check. Neither is an admission bypass.
        _, _, guard_owners = pin_consistency.load_ledger(identity_rows)
        for rva, owners in guard_owners.items():
            self.owners[rva].update(owners)
        self.known = collections.defaultdict(set)
        for row in identity_rows:
            self.known[row["name"]].add(int(row["target_rva"], 16))
        self.pins = collections.defaultdict(set)
        routes = pin_consistency.load_routes()
        with build.SYMBOLS.open(encoding="utf-8", newline="") as handle:
            for raw_row in csv.DictReader(handle):
                # pin_exemption expects the pin guard's normalised row form:
                # empty notes and unquoted-comma overflow are meaningful here.
                row = pin_consistency._norm(raw_row, ("name", "address", "notes"))
                address = int(row["address"], 16)
                if row["name"] in names:
                    self.pins[row["name"]].add(address)
                # Routing/view pins do not claim a second identity. Ordinary
                # pins remain candidates, but conservatively block a rival pin.
                body = retail.body_of(address)
                if body not in point_set:
                    continue
                own = pin_consistency.own_components(row["name"])
                explicit_alias = (pin_consistency.ALIAS_TOKEN.search(own)
                                  or pin_consistency.INVENTED_TOKEN.search(own))
                if ((row["name"], address) not in routes
                        and not pin_consistency.pin_exemption(row)
                        and not explicit_alias):
                    # The pin guard's explicit alias tokens are pure to read.
                    # Its additional hex-tail heuristic needs a disk-writing
                    # known-start cache; leave those pins conservatively owning
                    # their address here and let the real gate decide later.
                    self.owners[body].add(row["name"])

    def addresses(self, name):
        return self.known[name] | self.pins[name]

    def conflicts(self, name, address):
        return sorted(self.owners.get(self.retail.body_of(address), set()) - {name})

    def overlaps(self, rva, size):
        return [{"name": r["name"], "rva": int(r["target_rva"], 16),
                 "size": int(r["target_size"]), "identity_source": identity_source(r)}
                for r in self.rows if r["status"] == "matched"
                and int(r["target_rva"], 16) < rva + size
                and rva < int(r["target_rva"], 16) + int(r["target_size"])]


def discover(inputs, *, minimum=20, denylist=DENYLIST):
    """Return a JSON-compatible candidate report; every filesystem operation reads."""
    if minimum < 1:
        raise ValueError("minimum body size must be positive")
    retail = Retail(build.EXE)
    denylist = Path(denylist)
    content = denylist.read_bytes() if denylist.exists() else b""
    denied = sorted({line.strip() for line in content.decode("utf-8").splitlines()
                     if line.strip() and not line.lstrip().startswith("#")})
    report = {"schema": "bfme1-place-bodies-v1", "evidence": "candidate",
              "notice": NOTICE, "fold_notice": NO_FOLD,
              "required_gates": ["identity validation", "add_match", "pin_consistency"],
              "address_kind": "RVA", "image_base": retail.image_base,
              "baseline": {"path": str(retail.path), "sha256": retail.sha256,
                           "text_rva": retail.text_rva, "text_size": len(retail.text)},
              "configuration": {"minimum_body_size": minimum,
                                "minimum_fixed_run": locate.MIN_NEEDLE,
                                "denylist": str(denylist), "denylist_sha256": sha256(content),
                                "denied_names": denied},
              "objects": [], "bodies": [], "possible_pins": [], "refused_pins": []}
    names, points, spans = set(), set(), []
    for source, obj in inputs:
        source_path = (build.ROOT / source).resolve()
        source = source_path.relative_to(build.ROOT.resolve())
        functions, metadata = object_functions(obj)
        metadata.update(source=source.as_posix(), source_sha256=sha256(source_path.read_bytes()))
        report["objects"].append(metadata)
        for name, span, relocs in functions:
            entry = {"evidence": "candidate", "name": name, "source": source.as_posix(),
                     "object": metadata["path"], "size": len(span), "hits": [],
                     "candidate_rva": None, "possible_folded_body": False}
            report["bodies"].append(entry)
            if not placeable(name) or name in denied:
                entry["status"] = "denied" if name in denied else "excluded-symbol"
                continue
            try:
                body, hits, reason = masked_hits(retail, span, relocs)
            except ValueError as exc:
                entry.update(status="unsupported-body", reason=str(exc))
                continue
            entry["size"] = len(body)
            if len(body) < minimum:
                entry["status"] = "below-minimum"
                continue
            entry["status"] = reason or ("unique-hit" if len(hits) == 1 else
                                          "multiple-hits" if hits else "no-hit")
            entry["relocations"] = [{"offset": o, "kind": k, "name": s} for o, k, s in relocs]
            names.add(name)
            for rva in hits:
                hit = {"rva": rva, "va": retail.image_base + rva, "callees": []}
                points.add(rva)
                spans.append((rva, rva + len(body)))
                for offset, kind, symbol in relocs:
                    if kind != REL32:
                        continue
                    addend = struct.unpack_from("<i", body, offset)[0]
                    encoded, target = retail.call(rva, offset, addend)
                    # Only branch relocations are callee evidence. Nonzero
                    # addends are retained explicitly; no interior-target pin.
                    branch = (offset > 0 and body[offset - 1] in (0xE8, 0xE9)) or (
                        offset > 1 and body[offset - 2] == 0x0F and 0x80 <= body[offset - 1] <= 0x8F)
                    hit["callees"].append({"name": symbol, "offset": offset,
                                           "encoded_rva": encoded, "rva": target,
                                           "addend": addend, "branch": branch})
                    names.add(symbol)
                    points.add(target)
                entry["hits"].append(hit)
    evidence = Evidence(retail, names, points, spans)
    candidates = []
    for entry in report["bodies"]:
        for hit in entry["hits"]:
            matched, conflicts = [], []
            for call in hit["callees"]:
                known = evidence.addresses(call["name"])
                call["known_rvas"] = sorted(known)
                call["agreement"] = "unknown"
                if known and call["branch"]:
                    agrees = retail.body_of(call["rva"]) in {retail.body_of(a) for a in known}
                    call["agreement"] = "matched" if agrees else "conflict"
                    (matched if agrees else conflicts).append(call)
            hit.update(matched_callees=matched, conflicting_callees=conflicts,
                       other_identities=evidence.conflicts(entry["name"], hit["rva"]),
                       overlapping_rows=evidence.overlaps(hit["rva"], entry["size"]))
        viable = [h for h in entry["hits"] if not h["conflicting_callees"]]
        if len(viable) == 1:
            entry["candidate_rva"] = viable[0]["rva"]
            entry["placement_basis"] = "unique-byte-hit" if len(entry["hits"]) == 1 else "callee-filtered"
            entry["blocked_by"] = []
            if viable[0]["other_identities"]:
                entry["blocked_by"].append("other-identity")
            # A scanned assembly/generated TU cannot provide caller identities.
            probe = dict(name=entry["name"], status="matched", source=entry["source"], notes="",
                         target_rva=f"0x{entry['candidate_rva']:08X}")
            if not identity_source(probe):
                entry["blocked_by"].append("non-identity-source")
            if any(r["rva"] != entry["candidate_rva"] or r["size"] != entry["size"]
                   for r in viable[0]["overlapping_rows"]):
                entry["blocked_by"].append("overlapping-extent")
            candidates.append(entry)
    by_address = collections.defaultdict(set)
    for entry in candidates:
        by_address[entry["candidate_rva"]].add(entry["name"])
    for entry in candidates:
        shared = by_address[entry["candidate_rva"]] - {entry["name"]}
        if shared or "other-identity" in entry["blocked_by"]:
            entry["possible_folded_body"] = True
            entry["fold_note"] = NO_FOLD
        if shared:
            entry["blocked_by"].append("multiple-emitted-names")
    # Discovery placements can contradict one another; never use the resulting
    # pins recursively to bootstrap more placements or identity evidence.
    proposed = collections.defaultdict(set)
    for entry in candidates:
        proposed[entry["name"]].add(retail.body_of(entry["candidate_rva"]))
    for entry in candidates:
        hit = next(h for h in entry["hits"] if h["rva"] == entry["candidate_rva"])
        for call in hit["callees"]:
            if (call["branch"] and proposed.get(call["name"])
                    and proposed[call["name"]] != {retail.body_of(call["rva"])}):
                entry["blocked_by"].append("conflicting-candidate-callee")
                call["agreement"] = "conflicting-candidate"
                hit["matched_callees"] = [c for c in hit["matched_callees"] if c is not call]
                hit["conflicting_callees"].append(call)
    pins = collections.defaultdict(list)
    for entry in candidates:
        if entry["blocked_by"]:
            continue
        hit = next(h for h in entry["hits"] if h["rva"] == entry["candidate_rva"])
        for call in hit["callees"]:
            if call["branch"]:
                pins[call["name"]].append((call, entry))
    for name, sites in sorted(pins.items()):
        targets = {c["rva"] for c, _ in sites}
        pin = {"evidence": "candidate", "name": name, "candidate_rvas": sorted(targets),
               "call_sites": [{"caller": e["name"], "caller_rva": e["candidate_rva"],
                               "offset": c["offset"], "object": e["object"]} for c, e in sites]}
        reasons = []
        if len(targets) != 1:
            reasons.append("conflicting-call-sites")
        if any(c["addend"] for c, _ in sites):
            reasons.append("nonzero-relocation-addend")
        if any(not retail.in_text(a) for a in targets):
            reasons.append("outside-retail-text")
        owners = sorted({o for a in targets for o in evidence.conflicts(name, a)})
        if owners:
            reasons.append("other-identity")
            pin["other_identities"] = owners
        rivals = sorted({other for a in targets for other in by_address.get(retail.body_of(a), set())
                         if other != name})
        if rivals:
            reasons.append("other-candidate-name")
            pin["other_candidate_names"] = rivals
        if any(any(r["rva"] < a < r["rva"] + r["size"]
                   for r in evidence.overlaps(a, 1)) for a in targets):
            reasons.append("interior-of-existing-body")
        if not placeable(name):
            reasons.append("excluded-symbol")
        if name in denied:
            reasons.append("denied")
        if reasons:
            pin["reasons"] = reasons
            report["refused_pins"].append(pin)
        elif not evidence.addresses(name) and name not in proposed:
            pin["rva"] = next(iter(targets))
            report["possible_pins"].append(pin)
    # Detect replacement after the scan too; metadata alone is never evidence
    # that a concurrently compiled object's bytes remained the same.
    for obj in report["objects"]:
        if sha256(Path(obj["path"]).read_bytes()) != obj["sha256"]:
            raise ValueError(f"{obj['path']}: object changed during discovery")
    return report


def readable(report):
    lines = [report["notice"], report["fold_notice"],
             f"RVA addresses; ImageBase=0x{report['image_base']:08X}; "
             f"minimum={report['configuration']['minimum_body_size']}; "
             f"fixed-run={report['configuration']['minimum_fixed_run']}; "
             f"denylist={report['configuration']['denylist']} "
             f"({len(report['configuration']['denied_names'])} names)"]
    for obj in report["objects"]:
        lines.append(f"CANDIDATE OBJECT {obj['path']} sha256={obj['sha256']} "
                     f"source={obj['source']}; compile provenance unverified")
    for entry in report["bodies"]:
        candidate = entry["candidate_rva"]
        lines.append(f"CANDIDATE {entry['name']} {entry['size']}B {entry['status']} "
                     f"hits={len(entry['hits'])} " + (f"RVA=0x{candidate:08X}" if candidate is not None else "unplaced"))
        if entry.get("blocked_by"):
            lines.append("  withheld: " + ", ".join(entry["blocked_by"]))
        if entry.get("reason"):
            lines.append("  " + entry["reason"])
        if entry["possible_folded_body"]:
            lines.append("  " + entry["fold_note"])
        for hit in entry["hits"]:
            lines.append(f"  hit RVA=0x{hit['rva']:08X} VA=0x{hit['va']:08X}")
            for call in hit["callees"]:
                lines.append(f"    {call['agreement']} callee {call['name']} "
                             f"RVA=0x{call['rva']:08X} +0x{call['offset']:X}")
    for key, label in (("possible_pins", "POSSIBLE PIN"), ("refused_pins", "REFUSED PIN")):
        for pin in report[key]:
            lines.append(f"CANDIDATE {label} {pin['name']} "
                         + ",".join(f"0x{a:08X}" for a in pin["candidate_rvas"])
                         + (" " + ",".join(pin["reasons"]) if "reasons" in pin else ""))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", help="source TUs with existing build.obj_path objects")
    parser.add_argument("--object", nargs=2, action="append", default=[], metavar=("SOURCE", "OBJECT"),
                        help="read an explicit existing TU object; never compile")
    parser.add_argument("--min", "--min-size", type=int, default=20, dest="minimum")
    parser.add_argument("--denylist", type=Path, default=DENYLIST)
    parser.add_argument("--json", action="store_true", help="emit candidate JSON to stdout")
    args = parser.parse_args(argv)
    inputs = [(s, build.obj_path(build.ROOT / s)) for s in args.sources] + args.object
    if not inputs:
        parser.error("provide a source or --object SOURCE OBJECT")
    try:
        report = discover(inputs, minimum=args.minimum, denylist=args.denylist)
    except (OSError, ValueError, IndexError, KeyError, StopIteration, struct.error) as exc:
        parser.exit(2, f"place_bodies: {exc}\n")
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else readable(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
