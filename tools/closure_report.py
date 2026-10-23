#!/usr/bin/env python3
"""Rank conditional unique-byte closure gains on a frozen BFME1 measured graph.

This is a ranking estimate, not a repair proof. Single-root gains are not
additive; joint-only gains stay in complete bounded blocker sets and joint_gain.
No compilation, census, link, ledger substitution or validity admission occurs.

  closure_report.py graph RUN_DIR --out DIR [--verify 25]
  closure_report.py show closure_roots.json[.gz]

The graph and every status row must reproduce the receipt's credit. Integrity
binding alone does not establish clean-run authority. Older replay reports retain the
label 'replayed, graph not receipt-bound'; rebuilding unbound legacy graphs is
intentionally unavailable here, since BFME2's replay uses different verdicts.

Pure interval/graph/ranking machinery adapted from Open-BFME-2 02518d74b1.
"""
import argparse
import bisect
import collections
import csv
import gzip
import hashlib
import io
import json
import os
import sys
from pathlib import Path

import link_cycle_context as context

SCHEMA = "bfme1-closure-report/1"
ALGORITHM = "conditional-single-address-gain/1"
GRAPH_SCHEMA = context.GRAPH_SCHEMA             # link_cycle.CLOSURE_GRAPH_SCHEMA
GRAPH_FILE = "closure_graph.json.gz"         # link_cycle.CLOSURE_GRAPH
ROOTS = "closure_roots.json"
BLOCKERS = "closure_blockers.csv"
FORBIDDEN = context.BAD_TARGETS                 # link_cycle.greatest_closure's bad_targets
SET_CAP = 6                                  # complete blocker sets are kept up to this size
OVER = None                                  # a blocker set larger than the cap
BLOCKER_COLUMNS = ("name", "source", "retail_rva", "size", "bucket", "reach", "roots", "scored", "witness")
BOUND = "measured graph, bound to the receipt"
REPLAYED = "replayed, graph not receipt-bound"
STATUS_COMPARED = ("name", "kind", "source", "retail_rva", "size", "linked_rva", "placed", "self_strict",
                   "closed_strict", "hardcoded", "failure_count", "failures")
LIMITS = (
    "conditional on the frozen graph of the measured commit (every edge and every other verdict unchanged): "
    "not a repair proof and not an expected net credit",
    "a root 'passing' means all of its own listed failures are gone, not one of them",
    "single-root scores omit joint-only gains and may overlap: do not add them; a row behind two or more roots is "
    "in no root's score",
    "fillers, stubs and targets the graph does not hold are listed as unscored and never ranked: they close nothing "
    "even when they pass",
    "a root is the node where a failure is recorded (a failing unit, twin or datum), not its cause or its repair "
    "site: one datum repair that clears data-back in many units at once is ranked by data_back_rank, not here",
    "placed real rows only; closed-strict rows that are not placed are a separate bucket (summary.buckets)",
    "a repair is done only when a later authoritative cycle shows the root gone and its beneficiaries closed",
)


class ReportError(Exception):
    """The report cannot be produced or read."""


# ---------------------------------------------------------------- spans

def row_spans(row):
    return row.get("credit_spans", [(row["rva"], row["rva"] + row["size"])])


def merge(spans):
    """Disjoint sorted [start, end) spans covering the union."""
    def flat(values):
        for value in values:
            if len(value) == 2 and all(isinstance(v, int) for v in value):
                yield value
            else:
                yield from flat(value)
    out = []
    for s, e in sorted(flat(spans)):
        if e <= s:
            continue
        if out and s <= out[-1][1]:
            if e > out[-1][1]:
                out[-1][1] = e
        else:
            out.append([s, e])
    return out


def total(merged):
    return sum(e - s for s, e in merged)


def unique_bytes(spans):
    return total(merge(spans))


def uncovered(spans, base, base_starts):
    """Bytes of the union of SPANS outside BASE (merged, with its starts)."""
    gain = 0
    for s, e in merge(spans):
        i = max(bisect.bisect_right(base_starts, s) - 1, 0)
        cur = s
        while i < len(base) and base[i][0] < e:
            bs, be = base[i]
            if be > cur:
                if bs > cur:
                    gain += bs - cur
                cur = max(cur, be)
            i += 1
        if cur < e:
            gain += e - cur
    return gain


# ---------------------------------------------------------------- the graph

def scorable(n, ok, forbidden=FORBIDDEN):
    """A node whose passing can close something: held by the graph, failed, not a filler or stub."""
    return n in ok and not ok[n] and n[0] not in forbidden


def reverse_edges(edges):
    rev = collections.defaultdict(set)
    for n, ts in edges.items():
        for t in ts:
            rev[t].add(n)
    return rev


def blockers_of(ok, edges, forbidden=FORBIDDEN):
    """Every blocker: failed nodes, and edge targets that are forbidden or unknown to the graph.
    A filler or stub that nothing reaches blocks nothing and is not one."""
    out = {n for n, v in ok.items() if not v}
    for ts in edges.values():
        for t in ts:
            if t[0] in forbidden or t not in ok:
                out.add(t)
    return out


def propagate(blockers, rev, group, cap=SET_CAP):
    """{node: frozenset of groups | OVER} for every node that is, or reaches, a blocker: the
    complete set of blocker groups it reaches when that has at most CAP members, else OVER.
    A node absent from the result reaches none: it is closed."""
    state = {n: frozenset((group(n),)) for n in blockers}
    work = collections.deque(state)
    queued = set(state)
    while work:
        n = work.popleft()
        queued.discard(n)
        incoming = state[n]
        for parent in rev.get(n, ()):
            old = state.get(parent, frozenset())
            if old is OVER:
                continue
            new = OVER if incoming is OVER else old | incoming
            if new is not OVER and len(new) > cap:
                new = OVER
            if new is OVER or len(new) != len(old):
                state[parent] = new
                if parent not in queued:
                    work.append(parent)
                    queued.add(parent)
    return state


def reference_closure(ok, edges, bad_targets=FORBIDDEN):
    """link_cycle.greatest_closure, copied so that a report can be checked in a checkout
    whose link_cycle is not the run's: nodes that are ok and reach only ok nodes (cycles
    optimistic); an edge to a filler, a stub or a node the graph does not hold closes nothing.
    tools/tests/test_closure_report.py holds it equal to link_cycle's on random graphs."""
    closed = {n for n in ok if ok[n]}
    for n in list(closed):
        if any(t[0] in bad_targets or t not in ok for t in edges.get(n, ())):
            closed.discard(n)
    rev = reverse_edges(edges)
    work = [n for n in ok if n not in closed]
    while work:
        t = work.pop()
        for n in rev.get(t, ()):
            if n in closed:
                closed.discard(n)
                work.append(n)
    return closed


def distances(blockers, rev):
    """{node: edges on a shortest path to a blocker} for every node that reaches one."""
    dist = {n: 0 for n in blockers}
    work = collections.deque(blockers)
    while work:
        n = work.popleft()
        for parent in rev.get(n, ()):
            if parent not in dist:
                dist[parent] = dist[n] + 1
                work.append(parent)
    return dist


def witness(n, dist, edges, ident, limit=12):
    """The ids along a shortest path from N to its nearest blocker, ' > ' joined; among
    equally near next nodes the one with the smallest id, so two runs agree."""
    ids = [ident(n)]
    while dist[n] and len(ids) <= limit:
        n = min((t for t in edges.get(n, ()) if dist.get(t) == dist[n] - 1), key=ident)
        ids.append(ident(n))
    if dist[n]:
        ids.append("...")
    return " > ".join(ids)


def analyze(ok, edges, rows, describe, *, forbidden=FORBIDDEN, affected=True, cap=SET_CAP):
    """(body, blocker_rows) of the closure report.

    ok, edges   link_cycle.closure_graph's.
    rows        [{"node", "name", "source", "rva", "size", "real", "placed", "self_strict"}], one per ledger row.
    describe    node -> {"id", "kind", "group", ...}: a deterministic id, and the retail-address group the
                node's failure is repaired at; further keys are copied into the report.
    """
    cache = {}

    def desc(n):
        if n not in cache:
            cache[n] = describe(n)
        return cache[n]

    def ident(n):
        return desc(n)["id"]

    def group(n):
        return desc(n)["group"] if scorable(n, ok, forbidden) else "leaf:" + desc(n)["id"]

    rev = reverse_edges(edges)
    blockers = blockers_of(ok, edges, forbidden)
    state = propagate(blockers, rev, group, cap)
    single = propagate(blockers, rev, lambda n: n, 1)
    dist = distances(blockers, rev)
    members = collections.defaultdict(list)
    for n in blockers:
        members[group(n)].append(n)

    live = [r for r in rows if r["real"] and r["placed"]]
    span = row_spans
    credited = merge(span(r) for r in live if r["self_strict"] and r["node"] not in state)
    starts = [s for s, _ in credited]
    credit = total(credited)
    gain_rows = collections.defaultdict(lambda: {"beneficiary": [], "direct": []})
    out_rows = []
    buckets = collections.defaultdict(list)
    reach_spans = collections.defaultdict(list)
    joint_only_spans = []
    by_size = collections.defaultdict(list)
    for r in live:
        if r["self_strict"] and r["node"] not in state:
            continue
        st = state[r["node"]]
        bucket = "closure-blocked" if r["self_strict"] else "failing"
        buckets[bucket].append(span(r))
        one = next(iter(st)) if st is not OVER and len(st) == 1 else None
        scored = one is not None and not one.startswith("leaf:")
        if one is not None:                       # a failing row of a unit that reaches nothing else: its own root
            gain_rows[one]["beneficiary" if r["self_strict"] else "direct"].append(r)
        reach = f">{cap}" if st is OVER else str(len(st))
        if st is not OVER and len(st) > 1 and not any(g.startswith("leaf:") for g in st):
            joint_only_spans.append(span(r))
        if r["self_strict"]:
            reach_spans["one scored root" if scored else "one unscored leaf" if one is not None
                        else "two or more"].append(span(r))
            by_size[reach].append(span(r))
        out_rows.append({"name": r["name"], "source": r["source"], "retail_rva": "0x%08X" % r["rva"],
                         "size": r["size"], "bucket": bucket, "reach": reach,
                         "roots": "" if st is OVER else ";".join(sorted(st)),
                         "scored": "" if st is OVER else int(not any(g.startswith("leaf:") for g in st)),
                         "witness": witness(r["node"], dist, edges, ident)})
    out_rows.sort(key=lambda r: (r["retail_rva"], r["name"], r["source"], r["size"]))
    buckets["closed-strict-unplaced"] = [span(r) for r in rows if r["real"] and not r["placed"] and r["self_strict"]
                                         and r["node"] not in state]

    aff = {}
    if affected:                                  # self-strict open rows that reach the root at all
        open_by_node = collections.defaultdict(list)
        for r in live:
            if r["self_strict"] and r["node"] in state:
                open_by_node[r["node"]].append(r)
        for g in gain_rows:
            if g.startswith("leaf:"):
                continue
            seen = set(members[g])
            work = list(seen)
            while work:
                for parent in rev.get(work.pop(), ()):
                    if parent not in seen:
                        seen.add(parent)
                        work.append(parent)
            hit = [r for n in seen for r in open_by_node.get(n, ())]
            aff[g] = (len(hit), unique_bytes(span(r) for r in hit))

    roots, unscored = [], []
    for g, rs in gain_rows.items():
        ben, direct = rs["beneficiary"], rs["direct"]
        nodes = sorted((dict(desc(n)) for n in members[g]), key=lambda d: d["id"])
        for d in nodes:
            d.pop("group", None)
        entry = {"root": g, "nodes": nodes,
                 "beneficiary_rows": len(ben), "beneficiary_bytes": unique_bytes(span(r) for r in ben)}
        if g.startswith("leaf:"):
            entry.update(scored=False, sole_blocked_bytes=entry.pop("beneficiary_bytes"),
                         sole_blocked_rows=entry.pop("beneficiary_rows"))
            if entry["sole_blocked_rows"]:
                unscored.append(entry)
            continue
        entry.update(scored=True, direct_rows=len(direct), direct_bytes=unique_bytes(span(r) for r in direct),
                     conditional_gain_bytes=uncovered([span(r) for r in ben + direct], credited, starts),
                     failures=sorted({f for d in nodes for f in d.get("failures", ())}),
                     verified=None)
        if g in aff:
            entry["affected_rows"], entry["affected_bytes"] = aff[g]
        if entry["conditional_gain_bytes"]:
            roots.append(entry)
    roots.sort(key=lambda e: (-e["conditional_gain_bytes"], e["root"]))
    unscored.sort(key=lambda e: (-e["sole_blocked_bytes"], e["root"]))

    by_kind = collections.defaultdict(list)       # node-level cross-check: one failed NODE, no grouping
    for r in live:
        st = single.get(r["node"])
        if r["self_strict"] and st:
            (n,) = st
            by_kind[n[0]].append((n, span(r)))
    cross = {k: {"roots": len({n for n, _ in v}), "sole_blocked_bytes": unique_bytes(s for _, s in v)}
             for k, v in sorted(by_kind.items())}
    scored_groups = {g for g in members if not g.startswith("leaf:")}
    count = (lambda table: {k: {"rows": len(v), "unique_bytes": unique_bytes(v)} for k, v in sorted(table.items())})
    body = {
        "summary": {
            "credit_unique_bytes": credit,
            "joint_only": {"candidate_unique_bytes": uncovered(joint_only_spans, credited, starts),
                           "non_additive": True,
                           "definition": "rows behind multiple scored roots; excludes overflow and unscored leaves; "
                                         "not a gain for any particular packet; use joint_gain for chosen roots"},
            "buckets": count(buckets),
            "closure_blocked_reach": count(reach_spans),
            "closure_blocked_by_blocker_set_size": dict(count(by_size), cap=cap),
            "blockers": len(blockers), "scored_roots": len(scored_groups),
            "scored_roots_with_gain": len(roots),
            "roots_with_no_beneficiary": sum(1 for e in roots if not e["beneficiary_rows"]),
            "unscored_leaves_solely_blocking": len(unscored),
            "single_node_cross_check": cross,
        },
        "roots": roots,
        "unscored": unscored,
    }
    return body, out_rows


def closed_nodes(ok, edges, forbidden=FORBIDDEN):
    """The nodes this module holds closed: must equal link_cycle.greatest_closure(ok, edges)."""
    state = propagate(blockers_of(ok, edges, forbidden), reverse_edges(edges), lambda n: n, 1)
    return {n for n, v in ok.items() if v and not any(t in state for t in edges.get(n, ()))}


def credit_of(ok, edges, rows, forced=(), closure=reference_closure):
    """The credit of the graph with the FORCED nodes passing, by CLOSURE."""
    forced = {n for n in forced if scorable(n, ok)}
    table = dict(ok)
    table.update((n, True) for n in forced)
    closed = closure(table, edges)
    return unique_bytes(row_spans(r) for r in rows
                        if r["real"] and r["placed"] and r["node"] in closed
                        and (r["self_strict"] or r["node"] in forced))


def forced_gain(ok, edges, rows, nodes, closure=reference_closure):
    """credit(graph with NODES passing) - credit(graph), by CLOSURE run twice: the
    independent check of a root's conditional_gain_bytes, and the joint gain of several
    roots' nodes (joint_gain)."""
    return credit_of(ok, edges, rows, nodes, closure) - credit_of(ok, edges, rows, (), closure)


def joint_gain(graph, roots):
    """The exact gain on the frozen GRAPH (load_graph) of every failed node at ROOTS (retail
    address groups, as closure_blockers.csv spells them) passing together. For scoring a
    reviewed packet; nothing in this tool enumerates or ranks sets."""
    ok, edges, rows, describe = graph
    want = set(roots)
    nodes = [n for n in ok if scorable(n, ok) and describe(n)["group"] in want]
    return forced_gain(ok, edges, rows, nodes)


# ---------------------------------------------------------------- the measured graph

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read_bytes(path):
    data = Path(path).read_bytes()
    return gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data


def graph_from_doc(doc):
    """(ok, edges, rows, describe) of a closure-graph document (link_cycle.closure_graph_doc)."""
    if not isinstance(doc, dict) or doc.get("schema") != GRAPH_SCHEMA:
        raise ReportError(f"closure graph schema {doc.get('schema') if isinstance(doc, dict) else None!r}, expected "
                          f"{GRAPH_SCHEMA!r}")
    if tuple(doc.get("bad_targets") or ()) != FORBIDDEN:
        raise ReportError(f"closure graph bad_targets {doc.get('bad_targets')!r}: not this tool's closure rule")
    if doc.get("rules") != context.RULES:
        raise ReportError("closure graph rules are not BFME1's")
    info = doc["nodes"]
    if any(not isinstance(v.get("ok"), bool) or v.get("kind") not in ("unit", "twin", "datum", "eh", *FORBIDDEN)
           or v.get("kind") != k.split(":", 1)[0]
           for k, v in info.items()):
        raise ReportError("invalid node verdict or kind")
    dump_units = set()
    for r in doc["rows"]:
        if len(r) != 8:
            raise ReportError("invalid graph row width")
        name, kind, source, rva, size, key, placed, strict = r
        if key not in info or info[key]["kind"] != "unit" or not isinstance(rva, int) or rva < 0 \
                or not isinstance(size, int) or size <= 0 or placed not in (0, 1) or strict not in (0, 1):
            raise ReportError("invalid graph row extent, flags or unit")
        if kind == "real" and context.source_kind({"source": source}) != "real":
            raise ReportError("generated/assembly source cannot be real credit")
        # BFME1 progress.source_lane governs dependencies even when their
        # functional kind is gen-funclet/import/alias, including via libraries.
        if (kind in ("generated", "asm") or context.source_kind({"source": source}) in ("generated", "asm")
                or set(info[key].get("provenance", ())) & {"generated", "dump", "asm"}):
            dump_units.add(key)
    if any(t in dump_units for ts in doc["edges"].values() for t in ts):
        raise ReportError("graph contains a generated/assembly source closure dependency")
    if any(k not in info for k in doc["edges"]):
        raise ReportError("edge source is absent from measured nodes")

    def node(key):
        return (info[key]["kind"] if key in info else key.split(":", 1)[0], key)
    ok = {node(k): bool(v["ok"]) for k, v in info.items()}
    edges = {node(k): {node(t) for t in ts} for k, ts in doc["edges"].items()}
    padding = context.validate_padding(doc.get("padding", []))
    rows = [{"credit_spans": context.credit_spans(rva, size, padding), "name": name, "kind": kind, "source": source, "rva": rva, "size": size, "node": node(key),
             "real": kind == "real", "placed": bool(placed), "self_strict": bool(strict)}
            for name, kind, source, rva, size, key, placed, strict in doc["rows"]]

    def describe(n):
        d = info.get(n[1])
        if d is None:                             # an edge target the graph does not hold
            parts = n[1].split(":")
            ident = parts[0] + ":" + ":".join(("0x%08X" % int(p)) if p.lstrip("-").isdigit() else p for p in parts[1:])
            return {"id": ident, "kind": n[0], "group": ident}
        rva = d.get("rva")
        where = None if rva is None else ("0x%08X" % rva if rva >= 0 else "-0x%08X" % -rva)
        if n[0] == "unit":
            ident = f"unit:{where}:{d['name']}"
        elif n[0] == "twin":
            ident = "twin:%s:%s@0x%08X" % (where, d.get("name") or "?", d["linked"])
        elif n[0] == "datum":
            ident = "datum:%s:%d:%s@0x%08X" % (where, d["size"], d["name"], d["linked"])
        else:
            ident = n[0] + ":" + ":".join("0x%08X" % int(p) for p in n[1].split(":")[1:])
        out = {"id": ident, "kind": n[0], "group": where if rva is not None and rva >= 0 else ident,
               "failures": list(d.get("failures") or ())}
        for key in ("name", "source", "sources", "include_proofs", "object", "size"):
            if d.get(key) not in (None, ""):
                out[key] = d[key]
        # One witnessed include map per TU, shared by all its code/data
        # nodes. Do not duplicate the full header inventory for every body.
        sources = set(d.get("sources", [])) | ({d["source"]} if d.get("source") else set())
        proofs = {s: doc["include_proofs"][s] for s in sorted(sources) if s in doc.get("include_proofs", {})}
        if proofs:
            out["include_proofs"] = proofs
        if where is not None:
            out["retail_rva"] = where
        return out
    return ok, edges, rows, describe


def load_graph(path, want_sha256=None):
    """(ok, edges, rows, describe) of closure_graph.json.gz; with WANT_SHA256 the file must
    be the one a receipt names (closure_graph_sha256)."""
    try:
        raw = Path(path).read_bytes()
    except OSError as e:
        raise ReportError(f"{path}: no closure graph ({e})") from None
    if want_sha256 is not None and sha256_bytes(raw) != want_sha256:
        raise ReportError(f"{path}: sha256 {sha256_bytes(raw)[:16]} is not the receipt's closure_graph_sha256 "
                          f"{str(want_sha256)[:16]}: not the graph that run measured")
    try:
        doc = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    except (OSError, EOFError, ValueError) as e:
        raise ReportError(f"{path}: not a readable closure graph ({e})") from None
    try:
        return graph_from_doc(doc)
    except (KeyError, TypeError, ValueError, IndexError) as e:
        raise ReportError(f"{path}: malformed closure graph ({e})") from None


def status_rows(path):
    """link_status.csv rows (plain or gzip) as dicts."""
    text = read_bytes(path).decode("utf-8")
    return list(csv.DictReader(io.StringIO(text, newline="")))


def check_rows(rows, closed, status, columns=("name", "kind", "source", "retail_rva", "size", "placed", "self_strict",
                                               "closed_strict")):
    """Every row of the graph against link_status.csv on COLUMNS, as multisets; ReportError
    naming how many differ. `rows` may carry further link_status columns (the replay's)."""
    def mine(r):
        full = {"name": r["name"], "kind": r["kind"], "source": r["source"], "retail_rva": "0x%08X" % r["rva"],
                "size": str(r["size"]), "placed": str(int(r["placed"])), "self_strict": str(int(r["self_strict"])),
                "closed_strict": str(int(r["self_strict"] and r["node"] in closed))}
        full.update(r.get("status") or {})
        return tuple(full[c] for c in columns)
    got = collections.Counter(mine(r) for r in rows)
    want = collections.Counter(tuple(r[c] for c in columns) for r in status)
    if got != want:
        off = sum(((got - want) + (want - got)).values())
        some = sorted((got - want).elements())[:2] + sorted((want - got).elements())[:2]
        raise ReportError(f"{off} row record(s) differ from link_status.csv on {', '.join(columns)} (e.g. "
                          f"{some}): an unreproduced graph is not attributed")
    return len(status)


def report(graph, receipt, status, binding, verify=25, log=None):
    """(roots bytes, blockers bytes, facts): check GRAPH against the receipt's credit and
    every row of STATUS, analyse it, and re-prove the top VERIFY roots by a forced closure."""
    ok, edges, rows, describe = graph
    # BFME1 progress.real_split weights must also agree for conditional gains,
    # including open rows; equal closed totals do not prove equal byte credit.
    padding = context.validate_padding((receipt.get("series") or {}).get("padding", []))
    if any(row_spans(r) != context.credit_spans(r["rva"], r["size"], padding) for r in rows):
        raise ReportError("graph nonpadding weights differ from receipt")
    closed = reference_closure(ok, edges)
    if closed_nodes(ok, edges) != closed:
        raise ReportError("this module's one-pass closure is not the reference closure")
    credit = unique_bytes(row_spans(r) for r in rows
                          if r["real"] and r["placed"] and r["self_strict"] and r["node"] in closed)
    want = (receipt.get("series") or {}).get("credit_unique_bytes")
    if credit != want:
        raise ReportError(f"the graph credits {credit}, the receipt {want}: an unreproduced graph is not attributed")
    columns = binding["row_columns"]
    binding = {k: v for k, v in binding.items() if k != "row_columns"}
    compared = check_rows(rows, closed, status, columns)
    body, blocker_rows = analyze(ok, edges, rows, describe)
    if body["summary"]["credit_unique_bytes"] != credit:
        raise ReportError("the report's credit is not the graph's")
    by_group = collections.defaultdict(list)
    for n in ok:
        if scorable(n, ok):
            by_group[describe(n)["group"]].append(n)
    checked = 0
    for e in body["roots"][:max(verify, 0)]:
        got = forced_gain(ok, edges, rows, by_group[e["root"]])
        if got != e["conditional_gain_bytes"]:
            raise ReportError(f"root {e['root']}: gain {e['conditional_gain_bytes']} but forcing its nodes to pass "
                              f"and re-running the closure gives {got}")
        e["verified"] = "forced-closure"
        checked += 1
    if log:
        log(f"credit {credit} and {compared} link_status rows reproduced; {checked} root(s) re-proved by a forced "
            "closure")
    binding = dict(binding, commit=receipt["commit"], receipt_core_sha256=receipt.get("core_sha256"),
                   link_status_sha256=(receipt.get("series") or {}).get("link_status_sha256"),
                   link_cycle_tool_digest=receipt.get("tool_digest"), rules=receipt.get("rules"),
                   rule_identity=receipt.get("rule_identity"),
                   tool={"path": "tools/closure_report.py",
                         "text_sha256": sha256_bytes(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))})
    binding["checks"] = dict(binding.get("checks") or {}, credit_reproduced=credit,
                             link_status_rows_reproduced=compared, roots_verified_by_forced_closure=checked,
                             graph_nodes=len(ok), graph_edges=sum(len(v) for v in edges.values()))
    roots, table = document(body, blocker_rows, binding)
    return roots, table, {"credit": credit, "roots": len(body["roots"])}


def from_graph(run_dir, verify=25, log=None):
    """The report of a run whose measure wrote the graph: RUN_DIR holds receipt.json,
    link_status.csv and closure_graph.json.gz, and the receipt names the graph's sha256."""
    run = Path(run_dir)
    try:
        receipt = json.loads((run / "receipt.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ReportError(f"{run}: no readable receipt.json ({e})") from None
    import link_cycle as lc
    dependencies = receipt.get("tool_dependencies") or {}
    if receipt.get("rules") != context.RULES \
            or receipt.get("rule_identity") != context.rule_identity(dependencies) \
            or receipt.get("tool_digest") != context.digest(dependencies):
        raise ReportError("incompatible or inconsistent BFME1 rule identity")
    if receipt.get("core_sha256") != lc.digest_of(lc.receipt_core(receipt)):
        raise ReportError("receipt core digest differs")
    if lc.receipt_canon_core(receipt) is not None and receipt.get("core_canon_sha256") != lc.digest_of(lc.receipt_canon_core(receipt)):
        raise ReportError("receipt canonical core digest differs")
    want = receipt.get("closure_graph_sha256")
    if want != (receipt.get("series") or {}).get("closure_graph_sha256"):
        raise ReportError("receipt graph digests disagree")
    if not want:
        raise ReportError(f"{run / 'receipt.json'} names no closure_graph_sha256: this run was measured before "
                          "link_cycle wrote its graph (legacy diagnostics must retain the label "
                          f"'{REPLAYED}')")
    status_path = run / "link_status.csv"
    if not status_path.exists():
        status_path = run / "link_status.csv.gz"
    if sha256_bytes(read_bytes(status_path)) != (receipt.get("series") or {}).get("link_status_sha256"):
        raise ReportError(f"{status_path} is not the file the receipt hashed")
    graph = load_graph(run / GRAPH_FILE, want)
    return report(graph, receipt, status_rows(status_path),
                  {"source": "graph", "receipt_sha256": lc.sha256(run / "receipt.json"),
                   "graph": {"bound": True, "label": BOUND, "sha256": want},
                   "authority": "integrity-bound report; bundle authority requires clean-run and reader policy checks",
                   "row_columns": ("name", "kind", "source", "retail_rva", "size", "placed", "self_strict",
                                   "closed_strict")}, verify, log)


# ---------------------------------------------------------------- files

def blockers_csv(rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(BLOCKER_COLUMNS)
    for r in rows:
        w.writerow([r[c] for c in BLOCKER_COLUMNS])
    return buf.getvalue().encode("utf-8")


def document(body, blocker_rows, binding):
    """(closure_roots.json bytes, closure_blockers.csv bytes): the roots file binds the run
    (BINDING: commit, receipt core, link_status hash, where the graph came from) and the
    blockers file's hash."""
    table = blockers_csv(blocker_rows)
    doc = {"schema": SCHEMA, "algorithm": ALGORITHM,
           "definition": "conditional_gain_bytes(root) = credit(graph with every failed node at the root's retail "
                         "address passing) - credit(graph), in unique retail bytes, on the frozen closure graph of "
                         "the measured commit: beneficiaries (placed real self-strict open rows whose every "
                         "reachable blocker is this root) plus the root's own failing placed real rows when the root "
                         "reaches no other blocker, less bytes already credited",
           "limits": list(LIMITS),
           "blockers": {"file": BLOCKERS, "sha256": sha256_bytes(table), "rows": len(blocker_rows),
                        "columns": list(BLOCKER_COLUMNS), "set_cap": SET_CAP,
                        "roots_column": f"the complete set of roots and leaves the row reaches, ';' joined, when it "
                                        f"has at most {SET_CAP} members; empty with reach '>{SET_CAP}' beyond that "
                                        "(truncated)"},
           **binding, **body}
    return (json.dumps(doc, indent=1, sort_keys=True) + "\n").encode("utf-8"), table


def load_roots(path):
    """The roots document (plain or gzip); ReportError when it is not one this code reads."""
    try:
        doc = json.loads(read_bytes(path).decode("utf-8"))
    except (OSError, ValueError, EOFError) as e:
        raise ReportError(f"{path}: not a readable closure report ({e})") from None
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA or doc.get("algorithm") != ALGORITHM:
        raise ReportError(f"{path}: schema {doc.get('schema') if isinstance(doc, dict) else None!r}, algorithm "
                          f"{doc.get('algorithm') if isinstance(doc, dict) else None!r}; this checkout reads "
                          f"{SCHEMA!r}, {ALGORITHM!r}")
    graph = doc.get("graph") or {}
    if graph.get("label") not in (BOUND, REPLAYED) or bool(graph.get("bound")) != (graph.get("label") == BOUND):
        raise ReportError(f"{path}: does not say where its graph came from ({graph.get('label')!r})")
    return doc


def root_line(e):
    """(name, source) a root is best known by: its first unit node, else its first node."""
    nodes = e.get("nodes") or [{}]
    best = next((d for d in nodes if d.get("kind") == "unit"), nodes[0])
    return best.get("name") or best.get("id") or e["root"], best.get("source") or ""


def render(doc, limit=10, out=None):
    out = out or sys.stdout
    s = doc["summary"]
    print("Ranking estimate on a frozen graph; not a repair proof. Single-root scores are non-additive.", file=out)
    print(f"closure roots of {doc.get('commit', '?')[:12]} (credit {s['credit_unique_bytes']:,} B): "
          f"{s['scored_roots_with_gain']} scored root(s) with a gain, {s['roots_with_no_beneficiary']} of them with "
          f"no beneficiary; graph: {doc['graph']['label']}", file=out)
    for k, v in s["buckets"].items():
        print(f"  bucket {k}: {v['rows']} rows, {v['unique_bytes']:,} B", file=out)
    for k, v in s["closure_blocked_reach"].items():
        print(f"  closure-blocked rows behind {k}: {v['rows']} rows, {v['unique_bytes']:,} B", file=out)
    sizes = {k: v for k, v in s["closure_blocked_by_blocker_set_size"].items() if k != "cap"}
    print("  closure-blocked bytes by blocker-set size: "
          + ", ".join(f"{k}: {v['unique_bytes']:,}" for k, v in sorted(sizes.items(), key=lambda kv: (len(kv[0]), kv[0]))),
          file=out)
    for e in doc["roots"][:limit]:
        name, source = root_line(e)
        print(f"  root {name[:80]} -> {e['conditional_gain_bytes']:,} potentially unlocked bytes", file=out)
        print(f"         {source or '(no unit)'}: {len(e['failures'])} failure(s) {'; '.join(e['failures'])[:150]}",
              file=out)
        print(f"         beneficiaries {e['beneficiary_rows']} rows {e['beneficiary_bytes']} B; direct "
              f"{e['direct_rows']} rows {e['direct_bytes']} B; {len(e['nodes'])} node(s)"
              + (f"; verified {e['verified']}" if e.get("verified") else ""), file=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("graph", help="the report of a run whose measure wrote closure_graph.json.gz")
    g.add_argument("run_dir", help="holds receipt.json, link_status.csv and closure_graph.json.gz")
    r = sub.add_parser("replay", help="refuse legacy replay; older reports remain explicitly unbound")
    r.add_argument("snapshot", help="the link_cycle snapshot (holds build/link_cycle)")
    for p in (g, r):
        p.add_argument("--out", required=True, help="directory for closure_roots.json and closure_blockers.csv")
        p.add_argument("--verify", type=int, default=25, help="roots re-proved by a forced closure (default 25)")
    s = sub.add_parser("show", help="print a closure_roots.json")
    s.add_argument("roots")
    s.add_argument("--limit", type=int, default=10)
    args = ap.parse_args(argv)
    log = (lambda line: print(f"closure_report: {line}", file=sys.stderr, flush=True))
    try:
        if args.cmd == "show":
            render(load_roots(args.roots), args.limit)
            return 0
        if args.cmd == "replay":
            raise ReportError(f"legacy replay is unavailable; old reports must remain labelled '{REPLAYED}'")
        roots, table, facts = from_graph(args.run_dir, args.verify, log)
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        for name, data in ((BLOCKERS, table), (ROOTS, roots)):
            tmp = out / (name + ".partial")
            tmp.write_bytes(data)
            os.replace(tmp, out / name)
        label = BOUND if args.cmd == "graph" else REPLAYED
        print(f"closure report of credit {facts['credit']} ({label}): {facts['roots']} scored root(s) with a gain; "
              f"wrote {out / ROOTS} and {out / BLOCKERS}")
        return 0
    except (ReportError, OSError, ValueError, KeyError, TypeError) as e:
        print(f"closure_report: refused: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
