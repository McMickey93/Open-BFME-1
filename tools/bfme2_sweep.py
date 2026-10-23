#!/usr/bin/env python3
"""Read-only BFME2 -> BFME1 retail donor discovery (never compile or land).

  scan --donor-root /path/to/Open-BFME-2
  ranked --all --limit 20
  near
  show '?symbol@@YAXXZ'
  packets

All addresses in ledgers/reports are RVAs. Image bases come from each PE.
Matched donor rows supply ledger-proven extents, not target boundaries or
identities. Relocations are inferred from decoded operands, not COFF proof.
Packets contain instructions only. The sole writes are scratch reports/packets
under build/bfme2_sweep. No donor policy, compiler flags or landing code is used.
"""
import argparse
import bisect
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import shlex
import struct
import subprocess
import sys
import time

import capstone as cs
from capstone import x86_const as x86

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build
import eligibility
import place_bodies as placement

OUT = build.ROOT / "build/bfme2_sweep"
MODELS = {"T1": "Luna Medium", "T2": "Sol Medium", "T3": "Sol High",
          "T4": "Sol High", "T5": "Astra High"}
NOTICE = ("Placement evidence never proves identity. BFME2 names/pins are leads only. "
          "BFME2 retail may fold names; BFME1 retail has no ICF: prove exactly one "
          "BFME1 identity. No ledgers, sources or pins are written.")
LIBRARY_NOTICE = ("Read BFME1 library provenance before copying library code, including "
                  "vendored release identity and GameSpy PROVENANCE.txt. BFME2 benchmark, "
                  "licensing, ICF and library claims are not BFME1 facts.")
GENERATED = ("Code/gen_", "Code/masm_dumps/", "game/gen_", "game/masm_dumps/")
LIFT = re.compile(r"__declspec\s*\(\s*naked\s*\)|\b_{1,2}emit\b|\b(?:_asm|__asm)\b")


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def donor_revision(root):
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()


def scratch(path):
    path = Path(path).resolve()
    if not path.is_relative_to(OUT.resolve()) or path == OUT.resolve():
        raise ValueError("output must be a file/directory below build/bfme2_sweep")
    return path


class Image(placement.Retail):
    """Phase 4's file-backed .text/ILT reader plus bounded data reads."""
    def __init__(self, path):
        super().__init__(path)
        self.data = self.path.read_bytes()
        if placement.sha256(self.data) != self.sha256:
            raise ValueError("image changed during discovery")
        optional = build.u32(self.data, 0x3C) + 24
        self.image_size = build.u32(self.data, optional + 56)
        table = optional + build.u16(self.data, optional - 4)
        self.sections = []
        for i in range(build.u16(self.data, optional - 18)):
            offset = table + i * 40
            size, rva, raw_size, raw = struct.unpack_from("<IIII", self.data, offset + 8)
            if raw + raw_size > len(self.data):
                raise ValueError("truncated PE section")
            self.sections.append((rva, raw_size, raw))

    def body(self, rva, size):
        for start, count, raw in self.sections:
            if size >= 0 and start <= rva and rva + size <= start + count:
                return self.data[raw + rva - start:raw + rva - start + size]
        return None

    def in_image(self, va):
        return self.image_base <= va < self.image_base + self.image_size

    def cstring(self, va):
        rva = va - self.image_base
        for start, count, raw in self.sections:
            if start <= rva < start + count:
                offset = raw + rva - start
                end = self.data.find(b"\0", offset, min(raw + count, offset + 256))
                value = self.data[offset:end] if end >= 0 else b""
                if len(value) >= 3 and all(32 <= b < 127 or b in (9, 10, 13) for b in value):
                    return value.decode("ascii")
        return None


def decoder():
    md = cs.Cs(cs.CS_ARCH_X86, cs.CS_MODE_32)
    md.detail = True
    return md


def volatile_fields(body, image, rva):
    """Only decoded four-byte address/branch operands may be masked.

    Internal branch displacements stay fixed. No unaligned dword scanning:
    `add ecx,0x120` and an E8 byte inside a pointer must retain their meaning.
    Undecoded bytes remain fixed, including embedded jump tables.
    """
    fields = {}
    for ins in decoder().disasm(body, rva):
        offset = ins.address - rva
        branch = ins.group(cs.CS_GRP_CALL) or ins.group(cs.CS_GRP_JUMP)
        if branch and ins.imm_size == 4 and ins.operands[0].type == x86.X86_OP_IMM:
            target = ins.operands[0].imm & 0xFFFFFFFF
            if image.in_text(target) and not rva <= target < rva + len(body):
                fields[offset + ins.imm_offset] = "rel32"
        elif ins.imm_size == 4:
            slot = offset + ins.imm_offset
            if image.in_image(struct.unpack_from("<I", body, slot)[0]):
                fields[slot] = "dir32"
        if ins.disp_size == 4 and any(
                op.type == x86.X86_OP_MEM and op.mem.base == 0 and op.mem.index == 0
                for op in ins.operands):
            slot = offset + ins.disp_offset
            if image.in_image(struct.unpack_from("<I", body, slot)[0]):
                fields[slot] = "dir32"
    return fields


def agreed_fields(body, fields, window, donor_rva, target_rva, donor, target):
    agreed = {}
    for offset, kind in fields.items():
        if kind == "dir32":
            valid = target.in_image(struct.unpack_from("<I", window, offset)[0])
        else:
            dest = (target_rva + offset + 4 + struct.unpack_from("<i", window, offset)[0]) & 0xFFFFFFFF
            valid = target.in_text(dest)
        if valid:
            agreed[offset] = kind
    return agreed


def compare(body, fields, window):
    holes = {i for off in fields for i in range(off, off + 4)}
    diffs = [{"offset": i, "donor": a, "target": b}
             for i, (a, b) in enumerate(zip(body, window)) if i not in holes and a != b]
    fixed = len(body) - len(holes)
    return (1 - len(diffs) / fixed if fixed else 0), diffs


def exact_hits(target, body, fields):
    # Reuse Phase 4's uncapped all-overlapping masked search. That helper
    # trims COFF padding; here the donor ledger's FULL extent must agree.
    relocs = [(off, placement.REL32 if kind == "rel32" else 6, "")
              for off, kind in fields.items()]
    _, hits, reason = placement.masked_hits(target, body, relocs)
    return [rva for rva in hits if (window := target.body(rva, len(body))) is not None
            and compare(body, fields, window)[0] == 1], reason


def stream_rows(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


class RowIndex:
    """Interval lookup that preserves nested/overlapping ledger claims."""
    def __init__(self, rows):
        self.rows = sorted(rows, key=lambda r: int(r["target_rva"], 16))
        self.starts, self.ends = [], []
        for row in self.rows:
            start = int(row["target_rva"], 16)
            self.starts.append(start)
            self.ends.append(max(self.ends[-1] if self.ends else 0,
                                 start + int(row["target_size"])))

    def overlaps(self, rva, size):
        index = bisect.bisect_left(self.starts, rva + size) - 1
        rows = []
        while index >= 0 and self.ends[index] > rva:
            row = self.rows[index]
            if self.starts[index] + int(row["target_size"]) > rva:
                rows.append(row)
            index -= 1
        return rows


def donor_rows(root, minimum):
    """Matched clean source and a positive ledger extent; no generator/dump TUs.

    Reject an entire TU containing asm conservatively: no source parser here
    can establish which ledger body an anonymous inline assembly spray owns.
    Vendored sources are real donors, but their release notes remain leads.
    """
    texts, hashes, rows, excluded = {}, {}, [], Counter()
    for row in stream_rows(root / "reverse/functions.csv"):
        source = row.get("source", "")
        if (row.get("status") != "matched" or not source.startswith("Code/")
                or source.startswith(GENERATED) or "gen-" in row.get("notes", "")
                or "identity=generated" in row.get("notes", "")
                or Path(source).suffix.lower() not in (".c", ".cpp", ".cc", ".cxx")):
            excluded["non-source-row"] += 1
            continue
        try:
            rva, size = int(row["target_rva"], 16), int(row["target_size"])
        except (ValueError, KeyError, TypeError):
            excluded["unproven-extent"] += 1
            continue
        if size < minimum:
            excluded["below-minimum"] += 1
            continue
        path = (root / source).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            excluded["missing-source"] += 1
            continue
        if source not in texts:
            raw = path.read_bytes()
            texts[source] = raw.decode("utf-8", "replace")
            hashes[str(path)] = placement.sha256(raw)
        if LIFT.search(texts[source]):
            excluded["assembly-source"] += 1
            continue
        rows.append(dict(name=row["name"], donor_rva=rva, size=size, source=source,
                         donor_notes=row.get("notes", ""), extent_basis="BFME2 matched ledger"))
    return rows, hashes, dict(excluded)


def donor_names(root, image):
    names = defaultdict(set)
    for row in stream_rows(root / "reverse/functions.csv"):
        if row.get("status") == "matched" and placement.placeable(row["name"]):
            names[image.body_of(int(row["target_rva"], 16))].add(row["name"])
    for row in stream_rows(root / "reverse/symbols.csv"):
        if placement.placeable(row["name"]):
            names[image.body_of(int(row["address"], 16))].add(row["name"])
    return names


def near_windows(target, body, fields, named_rvas, cap):
    """Search several fixed anchors plus same-name BFME1 ledger leads.

    Bounded near search is explicitly incomplete; it never establishes unique
    placement. Exact search is uncapped. An anchor may hit interior bytes:
    only existing target extents or INT3 padded starts survive below.
    """
    positions = set(named_rvas)
    runs = placement.locate.hole_free_segments(len(body), list(fields))
    runs = sorted(runs, key=lambda p: p[1] - p[0], reverse=True)[:3]
    truncated = False
    for start, end in runs:
        for left, right in ((start, end), (start, (start + end) // 2), ((start + end) // 2, end)):
            if right - left < placement.locate.MIN_NEEDLE:
                continue
            cursor, count = 0, 0
            while (found := target.text.find(body[left:right], cursor)) >= 0:
                positions.add(target.text_rva + found - left)
                cursor, count = found + 1, count + 1
                if count >= cap:
                    truncated = True
                    break
    return positions, truncated


def layout_diff(body, window, fields, rva):
    """Positive instruction evidence only; a byte diff alone is not ABI proof."""
    a, b = list(decoder().disasm(body, rva)), list(decoder().disasm(window, rva))
    if len(a) != len(b):
        return []
    evidence = []
    for left, right in zip(a, b):
        if left.address != right.address or left.id != right.id or left.size != right.size:
            continue
        off = left.address - rva
        if left.mnemonic.startswith("ret") and left.op_str != right.op_str:
            evidence.append({"offset": off, "kind": "stack-cleanup", "donor": left.op_str,
                             "target": right.op_str})
        if len(left.operands) != len(right.operands):
            continue
        for x, y in zip(left.operands, right.operands):
            if (x.type == y.type == x86.X86_OP_MEM and x.mem.base == y.mem.base
                    and x.mem.index == y.mem.index and x.mem.scale == y.mem.scale
                    and x.mem.base not in (0, x86.X86_REG_ESP, x86.X86_REG_EBP)
                    and x.mem.disp != y.mem.disp and off + left.disp_offset not in fields):
                evidence.append({"offset": off, "kind": "member-displacement",
                                 "donor": x.mem.disp, "target": y.mem.disp})
    return evidence


def work_state(rva, size, rows, latest):
    """Delegate retirement, landed source and dump admission to eligibility."""
    if eligibility.retired(rva, latest):
        return "retired"
    overlaps = [r for r in rows if int(r["target_rva"], 16) < rva + size
                and rva < int(r["target_rva"], 16) + int(r["target_size"])]
    starts = {int(r["target_rva"], 16) for r in overlaps}
    if eligibility.landed_at(starts, rows=overlaps, root=build.ROOT):
        return "closed"
    dumps = eligibility.open_dumps(rows=overlaps, latest=latest)
    if not overlaps or (dumps and len(dumps) == len(overlaps)
                        and all(int(r["target_rva"], 16) == rva
                                and int(r["target_size"]) == size for r in dumps)):
        return "open"
    return "boundary-review"


def tier_for(record, hit):
    if hit["layout_disagreement"]:
        return "T5"
    if not hit["exact"] or any(s["agreement"] != "matched" for s in hit["strings"]):
        return "T4"
    if len(record["donor_names"]) > 1:
        return "T3"
    if (record["placement"] == "unique" and hit["identity_evidence"]
            and not hit["other_identities"] and not hit["callee_conflicts"]
            and not hit["extent_conflict"]):
        return "T1"
    return "T2"


def scan(donor_root, *, minimum=20, near_threshold=0.90, near_cap=4096):
    if minimum < 1 or not 0 < near_threshold <= 1 or near_cap < 1:
        raise ValueError("invalid scan thresholds")
    root = Path(donor_root).resolve()
    donor_path = root / "baselines/bfme2/workshop-vanilla-1.06/files/game.dat"
    donor, target = Image(donor_path), Image(build.EXE)
    rows, source_hashes, excluded = donor_rows(root, minimum)
    inputs = [donor_path, build.EXE, root / "reverse/functions.csv", root / "reverse/symbols.csv",
              build.FUNCTIONS, build.SYMBOLS, Path(__file__), Path(placement.__file__),
              Path(eligibility.__file__)]
    fingerprints = {str(p.resolve()): digest(p) for p in inputs}
    fingerprints.update(source_hashes)
    aliases = donor_names(root, donor)
    # Retain only name->RVA/size leads for the requested donors, not full rows.
    wanted = {r["name"] for r in rows}
    named, boundaries = defaultdict(set), defaultdict(set)
    for row in stream_rows(build.FUNCTIONS):
        rva, size = int(row["target_rva"], 16), int(row["target_size"])
        boundaries[rva].add(size)
        if row["name"] in wanted:
            named[row["name"]].add(rva)
    starts, prefix_ends = sorted(boundaries), []
    for start in starts:
        prefix_ends.append(max(prefix_ends[-1] if prefix_ends else 0,
                               start + max(boundaries[start])))
    records, names, points, spans = [], set(wanted), set(), []
    started = time.monotonic()
    print(f"bfme2_sweep: {len(rows)} clean donors; searching BFME1 .text", file=sys.stderr, flush=True)
    for index, row in enumerate(rows, 1):
        if index % 500 == 0:
            print(f"  {index}/{len(rows)} donors ({time.monotonic() - started:.0f}s)",
                  file=sys.stderr, flush=True)
        body = donor.body(row["donor_rva"], row["size"])
        if body is None or not donor.in_text(row["donor_rva"]) or not donor.in_text(row["donor_rva"] + row["size"] - 1):
            excluded["outside-file-text"] = excluded.get("outside-file-text", 0) + 1
            continue
        fields = volatile_fields(body, donor, row["donor_rva"])
        raw_hits, reason = exact_hits(target, body, fields)
        hits = []
        for rva in raw_hits:
            window = target.body(rva, row["size"])
            agreed = agreed_fields(body, fields, window, row["donor_rva"], rva, donor, target)
            if len(agreed) == len(fields):
                hits.append((rva, window, agreed, 1.0, []))
        placement_status = "unique" if len(hits) == 1 else "multiple" if hits else "none"
        truncated = False
        if not hits:
            windows, truncated = near_windows(target, body, fields, named[row["name"]], near_cap)
            for rva in sorted(windows):
                window = target.body(rva, row["size"])
                if window is None or not target.in_text(rva) or not target.in_text(rva + row["size"] - 1):
                    continue
                pos = rva - target.text_rva
                padded = pos >= 2 and target.text[pos - 2:pos] == b"\xcc\xcc"
                if rva not in boundaries and not padded:
                    continue
                # A start strictly inside any recorded body is never a new boundary.
                before = bisect.bisect_left(starts, rva) - 1
                if before >= 0 and prefix_ends[before] > rva:
                    continue
                agreed = agreed_fields(body, fields, window, row["donor_rva"], rva, donor, target)
                score, diffs = compare(body, agreed, window)
                if near_threshold <= score < 1:
                    hits.append((rva, window, agreed, score, diffs))
            hits.sort(key=lambda h: (-h[3], h[0]))
        record = dict(row, placement=placement_status, search_reason=reason,
                      donor_names=sorted(aliases[donor.body_of(row["donor_rva"]) ] | {row["name"]}),
                      near_search_truncated=truncated, hits=[])
        records.append(record)
        for rva, window, agreed, score, diffs in hits:
            calls, strings, dir32 = [], [], []
            for offset, kind in sorted(agreed.items()):
                if kind == "rel32":
                    dest_a = (row["donor_rva"] + offset + 4 + struct.unpack_from("<i", body, offset)[0]) & 0xFFFFFFFF
                    dest_b = (rva + offset + 4 + struct.unpack_from("<i", window, offset)[0]) & 0xFFFFFFFF
                    leads = sorted(aliases[donor.body_of(dest_a)])
                    calls.append(dict(offset=offset, donor_rva=dest_a, target_rva=dest_b,
                                      donor_names=leads))
                    names.update(leads)
                    points.add(dest_b)
                else:
                    va_a, va_b = struct.unpack_from("<I", body, offset)[0], struct.unpack_from("<I", window, offset)[0]
                    dir32.append(dict(offset=offset, donor_va=va_a, target_va=va_b,
                                      donor_rva=va_a - donor.image_base, target_rva=va_b - target.image_base))
                    sa, sb = donor.cstring(va_a), target.cstring(va_b)
                    if sa is not None or sb is not None:
                        strings.append(dict(offset=offset, donor=sa, target=sb,
                                            agreement="matched" if sa is not None and sa == sb else "conflict"))
            hit = dict(rva=rva, size=row["size"], exact=score == 1, similarity=round(score, 6),
                       diff_count=len(diffs), diff_summary=diffs[:64], diff_truncated=len(diffs) > 64,
                       calls=calls, dir32=dir32, strings=strings,
                       layout_disagreement=layout_diff(body, window, agreed, rva) if diffs else [])
            record["hits"].append(hit)
            points.add(rva)
            spans.append((rva, rva + row["size"]))
    evidence = placement.Evidence(target, names, points, spans)
    # Source-based target identities must remain tied to their source snapshots.
    for row in evidence.rows:
        path = build.ROOT / row["source"]
        key = str(path.resolve())
        if key not in fingerprints and path.is_file():
            fingerprints[key] = digest(path)
    latest = eligibility.latest_verdicts()
    row_index, overlap_cache, work_cache = RowIndex(evidence.rows), {}, {}
    for record in records:
        for hit in record["hits"]:
            rva = hit["rva"]
            hit["callee_conflicts"] = []
            for call in hit["calls"]:
                known = {name: sorted(evidence.addresses(name)) for name in call["donor_names"]
                         if evidence.addresses(name)}
                matched = [name for name, addresses in known.items()
                           if target.body_of(call["target_rva"]) in {target.body_of(a) for a in addresses}]
                call.update(known_target_rvas=known, matching_names=matched,
                            agreement="matched" if matched else "conflict" if known else "unknown")
                call["ledger_rvas"] = {name: sorted(evidence.known[name]) for name in call["donor_names"]
                                       if evidence.known[name]}
                call["candidate_pin_rvas"] = {name: sorted(evidence.pins[name]) for name in call["donor_names"]
                                              if evidence.pins[name]}
                for label, addresses in (("ledger", call["ledger_rvas"]), ("pin", call["candidate_pin_rvas"])):
                    agrees = any(target.body_of(a) == target.body_of(call["target_rva"])
                                 for values in addresses.values() for a in values)
                    call[f"{label}_agreement"] = "matched" if agrees else "conflict" if addresses else "unknown"
                if call["agreement"] == "conflict":
                    hit["callee_conflicts"].append(call["offset"])
            key = (rva, hit["size"])
            if key not in overlap_cache:
                overlap_cache[key] = row_index.overlaps(*key)
            hit["target_rows"] = overlap_cache[key]
            hit["boundary_evidence"] = [{"rva": int(r["target_rva"], 16), "size": int(r["target_size"]),
                                          "status": r["status"], "name": r["name"]} for r in hit["target_rows"]]
            hit["extent_conflict"] = any(int(r["target_rva"], 16) != rva
                                          or int(r["target_size"]) != hit["size"]
                                          for r in hit["target_rows"])
            hit["identity_evidence"] = [dict(kind="same-decorated-symbol", name=r["name"],
                                               source=r["source"], rva=rva)
                                        for r in hit["target_rows"]
                                        if r["name"] == record["name"] and placement.placeable(r["name"])
                                        and (r["name"], r["target_rva"]) in evidence.identity_keys
                                        and int(r["target_rva"], 16) == rva
                                        and int(r["target_size"]) == hit["size"]]
            hit["other_identities"] = evidence.conflicts(record["name"], rva)
            if key not in work_cache:
                work_cache[key] = work_state(rva, hit["size"], hit["target_rows"], latest)
            hit["work_status"] = work_cache[key]
            hit["tier"] = tier_for(record, hit)
            hit["suggested_model"] = MODELS[hit["tier"]]
            hit["blocked_by"] = []
            for condition, blocker in [
                    (hit["callee_conflicts"], "callee-conflict (identity/ABI requires review)"),
                    (hit["other_identities"], "other-BFME1-identity"),
                    (hit["extent_conflict"], "conflicting-target-extent"),
                    (not hit["identity_evidence"], "unproven-BFME1-identity"),
                    (not hit["boundary_evidence"], "unproven-BFME1-extent"),
                    (len(record["donor_names"]) > 1, "multiple-donor-names"),
                    (record["placement"] == "multiple", "multiple-target-placements"),
                    (any(s["agreement"] != "matched" for s in hit["strings"]), "different-string"),
                    (hit["tier"] in ("T4", "T5"), "source-repair")]:
                if condition:
                    hit["blocked_by"].append(blocker)
    return dict(schema="bfme1-bfme2-sweep-v1", notice=NOTICE, library_notice=LIBRARY_NOTICE,
                address_kind="RVA", donor_root=str(root), donor_revision=donor_revision(root),
                donor_image_base=donor.image_base, target_image_base=target.image_base,
                target_root=str(build.ROOT.resolve()), fingerprints=fingerprints,
                configuration=dict(minimum=minimum, near_threshold=near_threshold, near_cap=near_cap,
                                   exact_search="uncapped", minimum_fixed_run=placement.locate.MIN_NEEDLE,
                                   decoder=f"capstone-{cs.__version__}", near_search="same-size anchored windows"),
                excluded=excluded, records=records)


def counts(report):
    hits = [h for r in report["records"] for h in r["hits"]]
    return dict(donors=len(report["records"]), placements=dict(Counter(r["placement"] for r in report["records"])),
                tiers={t: sum(h["tier"] == t for h in hits) for t in MODELS},
                open_tiers={t: sum(h["tier"] == t and h["work_status"] == "open" for h in hits) for t in MODELS})


def load_report(path):
    report = json.loads(Path(path).read_text(encoding="utf-8"))
    if report.get("schema") != "bfme1-bfme2-sweep-v1" or report["target_root"] != str(build.ROOT.resolve()):
        raise ValueError("incompatible report; rerun scan in this checkout")
    for name, expected in report["fingerprints"].items():
        if not Path(name).is_file() or digest(name) != expected:
            raise ValueError(f"input changed: {name}; rerun scan")
    latest = eligibility.latest_verdicts()
    work_cache = {}
    for row in report["records"]:
        for hit in row["hits"]:
            key = (hit["rva"], hit["size"])
            if key not in work_cache:
                work_cache[key] = work_state(*key, hit["target_rows"], latest)
            hit["work_status"] = work_cache[key]
    return report


def ranked(report, *, include_closed=False, near_only=False):
    entries = [(r, h) for r in report["records"] for h in r["hits"]
               if (include_closed or h["work_status"] == "open")
               and (not near_only or h["tier"] in ("T4", "T5"))]
    return sorted(entries, key=lambda e: (e[1]["tier"], -e[1]["similarity"], -e[0]["size"],
                                         e[1]["rva"], e[0]["name"]))


def packet_text(report, record, hit):
    name, rva, size = record["name"], hit["rva"], hit["size"]
    # Mapping is a suggested official-tree destination, never a copied file.
    destination = "game/" + record["source"].removeprefix("Code/")
    q = shlex.quote
    commands = [f"python3 tools/claims.py claim 0x{rva:08X}",
                f"python3 tools/callees.py 0x{rva:08X} {size}",
                f"python3 tools/pin_consistency.py --symbol {q(name)}",
                f"python3 tools/add_match.py {q(name)} 0x{rva:08X} {size} {q(destination)} --model '<actual-worker-model>'",
                "python3 tools/pin_consistency.py --check"]
    text = [f"{hit['tier']} | {hit['suggested_model']} (suggestion only) | {name}", NOTICE,
            LIBRARY_NOTICE, f"BFME2 revision: {report['donor_revision']}",
            f"BFME2 source: {record['source']} | RVA 0x{record['donor_rva']:08X} | {size} bytes",
            f"BFME1 candidate: RVA 0x{rva:08X} | extent {size} bytes | {hit['work_status']}",
            f"Placement: {record['placement']} | masked similarity {hit['similarity']:.6f}",
            "The candidate extent comes from BFME2. Re-prove BFME1 boundaries before landing.",
            "T3 requires exactly one independently proven BFME1 identity; never import folded aliases.",
            "T4/T5 require source repair and byte verification; the donor is not ready to land.",
            "Resolve identity first. If unproven, use an address-derived name, not the donor name.",
            "If a row exists, choose the appropriate --replace-rva/--replace-existing only after reviewing it.",
            "Do not overwrite a closed body, retire another identity, or invent pins from this packet.",
            "Evidence:", json.dumps(dict(donor_names=record["donor_names"], hit=hit), indent=2),
            "BFME1 commands (instructions only; run after identity/boundary/provenance review):",
            *commands, "Donor translation unit (contains the source body; preserve relevant headers/context):"]
    source = Path(report["donor_root"]) / record["source"]
    text.append(source.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(text) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    scan_parser = sub.add_parser("scan")
    scan_parser.add_argument("--donor-root", type=Path, required=True)
    scan_parser.add_argument("--min-size", type=int, default=20)
    scan_parser.add_argument("--near-threshold", type=float, default=0.90)
    scan_parser.add_argument("--near-cap", type=int, default=4096)
    scan_parser.add_argument("--output", type=Path, default=OUT / "match.json")
    for command in ("ranked", "near", "packets", "show"):
        p = sub.add_parser(command)
        p.add_argument("--report", type=Path, default=OUT / "match.json")
        p.add_argument("--all", action="store_true", help="include closed/retired/boundary-review candidates")
        if command == "show":
            p.add_argument("selector", help="decorated name, donor source path or BFME1 0xRVA")
        elif command == "packets":
            p.add_argument("--output", type=Path, default=OUT / "packets")
        else:
            p.add_argument("--limit", type=int, default=20)
            p.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            output = scratch(args.output)
            report = scan(args.donor_root, minimum=args.min_size,
                          near_threshold=args.near_threshold, near_cap=args.near_cap)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
            print(json.dumps(counts(report), indent=2))
            print(f"Scratch report: {output}")
        else:
            report = load_report(args.report)
            entries = ranked(report, include_closed=args.all or args.command == "show", near_only=args.command == "near")
            if args.command == "show":
                entries = [(r, h) for r, h in entries if args.selector in
                           (r["name"], r["source"], f"0x{h['rva']:08X}", f"0x{h['rva']:08x}")]
                if not entries:
                    raise ValueError("no candidate matches selector")
                for r, h in entries:
                    print(packet_text(report, r, h))
            elif args.command == "packets":
                output = scratch(args.output)
                output.mkdir(parents=True, exist_ok=True)
                for r, h in entries:
                    token = hashlib.sha256((r["source"] + r["name"]).encode()).hexdigest()[:16]
                    path = scratch(output / f"{h['tier']}_{h['rva']:08X}_{token}.txt")
                    path.write_text(packet_text(report, r, h), encoding="utf-8")
                print(f"Wrote {len(entries)} scratch packets to {output}")
            else:
                selected = entries[:max(0, args.limit)]
                if args.json:
                    print(json.dumps(dict(counts=counts(report), entries=[dict(record=r, hit=h) for r, h in selected]), indent=2))
                else:
                    print(json.dumps(counts(report)))
                    for r, h in selected:
                        print(f"{h['tier']} {h['suggested_model']:12} 0x{h['rva']:08X} {h['size']:5}B "
                              f"{h['work_status']:15} {h['similarity']:.4f} {r['name']} | {r['source']}")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"bfme2_sweep: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
