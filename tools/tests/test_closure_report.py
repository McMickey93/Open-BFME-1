"""Synthetic BFME1 closure ranking; pure cases adapted from BFME2 02518d74b1."""
import copy
import csv
import gzip
import io
import json
import random
import sys
import types
from functools import partial
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import closure_report as cr
import link_cycle as lc
import link_cycle_context as context

source_closure = partial(lc.greatest_closure, bad_targets=context.BAD_TARGETS)

def U(n):
    return ("unit", n)


def row(node, rva, size, self_strict=True, placed=True, real=True):
    return {"node": node, "name": f"f{node[1]}_{rva:X}", "source": f"game/{node[1]}.cpp", "rva": rva, "size": size,
            "real": real, "placed": placed, "self_strict": self_strict}


def describe(n):
    ident = ":".join(str(x) for x in n)
    return {"id": ident, "kind": n[0], "group": GROUPS.get(n, ident), "name": ident, "failures": [f"why-{ident}"]}


GROUPS = {}


def graph():
    """u1 fails alone; u2 and u3 wait only for u1; u4 waits for u1 and the failed datum d;
    u5 waits only for a filler; u6 reaches an unknown target; u7 is closed; u8 fails and
    also reaches the failed datum, so its own row is not gained by fixing u8."""
    d, fill, twin = ("datum", (9, 0x900, 4)), ("fill", 0x700), ("twin", 0x50, 0x100)
    ok = {U(1): False, U(2): True, U(3): True, U(4): True, U(5): True, U(6): True, U(7): True, U(8): False,
          d: False, twin: False}
    edges = {U(2): {U(1)}, U(3): {U(2)}, U(4): {U(1), d}, U(5): {fill}, U(6): {("eh", 0x33)}, U(8): {d},
             U(7): set(), U(1): {twin}}
    rows = [row(U(1), 0x100, 10, self_strict=False), row(U(2), 0x200, 20), row(U(3), 0x300, 30),
            row(U(4), 0x400, 40), row(U(5), 0x500, 50), row(U(6), 0x600, 60), row(U(7), 0x700, 70),
            row(U(8), 0x800, 80, self_strict=False), row(U(3), 0x300, 30, placed=False),
            row(U(7), 0x7F0, 8, placed=False), row(U(2), 0x200, 20, real=False)]
    return ok, edges, rows


def test_gain_is_beneficiaries_plus_own_rows_and_two_roots_score_for_neither():
    GROUPS.clear()
    GROUPS.update({U(1): "0x00000100", ("twin", 0x50, 0x100): "0x00000100"})    # one address, two failed nodes
    ok, edges, rows = graph()
    body, blockers = cr.analyze(ok, edges, rows, describe)
    s = body["summary"]
    assert s["credit_unique_bytes"] == 70
    by_root = {e["root"]: e for e in body["roots"]}
    one = by_root["0x00000100"]
    assert [n["id"] for n in one["nodes"]] == ["twin:80:256", "unit:1"]
    assert (one["beneficiary_rows"], one["beneficiary_bytes"]) == (2, 50)      # u2 and u3; u4 also needs the datum
    assert (one["direct_rows"], one["direct_bytes"]) == (1, 10)
    assert one["conditional_gain_bytes"] == 60 and one["scored"] is True
    assert (one["affected_rows"], one["affected_bytes"]) == (3, 90)            # u4 reaches it too: affected, not gained
    assert one["failures"] == ["why-twin:80:256", "why-unit:1"]
    assert set(by_root) == {"0x00000100"}                                      # u8 and the datum gain nothing alone
    assert [e["root"] for e in body["unscored"]] == ["leaf:eh:51", "leaf:fill:1792"]
    assert body["unscored"][1]["sole_blocked_bytes"] == 50 and body["unscored"][1]["scored"] is False
    assert s["buckets"] == {"closed-strict-unplaced": {"rows": 1, "unique_bytes": 8},
                            "closure-blocked": {"rows": 5, "unique_bytes": 200},
                            "failing": {"rows": 2, "unique_bytes": 90}}
    assert s["closure_blocked_reach"] == {"one scored root": {"rows": 2, "unique_bytes": 50},
                                          "one unscored leaf": {"rows": 2, "unique_bytes": 110},
                                          "two or more": {"rows": 1, "unique_bytes": 40}}
    assert s["closure_blocked_by_blocker_set_size"] == {"1": {"rows": 4, "unique_bytes": 160},
                                                        "2": {"rows": 1, "unique_bytes": 40}, "cap": cr.SET_CAP}
    assert s["roots_with_no_beneficiary"] == 0 and "sum_conditional_gain_bytes" not in s
    table = {r["name"]: r for r in blockers}
    assert table["f3_300"]["witness"] == "unit:3 > unit:2 > unit:1" and table["f3_300"]["roots"] == "0x00000100"
    # the COMPLETE blocker set of a row behind two roots is kept, not collapsed to "2+"
    assert (table["f4_400"]["reach"], table["f4_400"]["roots"], table["f4_400"]["scored"]) == (
        "2", "0x00000100;datum:(9, 2304, 4)", 1)
    assert (table["f5_500"]["reach"], table["f5_500"]["roots"], table["f5_500"]["scored"]) == (
        "1", "leaf:fill:1792", 0)
    assert table["f8_800"]["bucket"] == "failing" and table["f8_800"]["roots"] == "datum:(9, 2304, 4);unit:8"
    assert "f7_700" not in table                                               # credited rows are not blockers


def test_blocker_sets_are_complete_up_to_the_cap_and_marked_truncated_beyond_it():
    GROUPS.clear()
    bad = [U(n) for n in range(1, 9)]
    ok = dict.fromkeys(bad, False)
    ok.update({U(20): True, U(21): True, U(22): True})
    edges = {U(20): set(bad[:cr.SET_CAP]), U(21): set(bad[:cr.SET_CAP + 1]), U(22): {U(21), U(20)}}
    rows = [row(U(20), 0x2000, 8), row(U(21), 0x2100, 8), row(U(22), 0x2200, 8)]
    body, blockers = cr.analyze(ok, edges, rows, describe)
    table = {r["name"]: r for r in blockers}
    assert table["f20_2000"]["reach"] == str(cr.SET_CAP)
    assert table["f20_2000"]["roots"].split(";") == [f"unit:{n}" for n in range(1, cr.SET_CAP + 1)]
    for name in ("f21_2100", "f22_2200"):                                      # truncated: said so, never guessed
        assert (table[name]["reach"], table[name]["roots"], table[name]["scored"]) == (f">{cr.SET_CAP}", "", "")
    assert body["summary"]["closure_blocked_by_blocker_set_size"][f">{cr.SET_CAP}"] == {"rows": 2, "unique_bytes": 16}
    assert cr.blockers_csv(blockers).decode().splitlines()[0] == ",".join(cr.BLOCKER_COLUMNS)


def test_single_root_scores_omit_joint_gains_and_may_overlap():
    """Astra: two zero-gain roots can jointly unlock a row; two gains over overlapping bytes
    do not add. joint_gain scores a chosen set exactly; nothing here ranks sets."""
    GROUPS.clear()
    ok = {U(1): False, U(2): False, U(3): True}
    edges = {U(3): {U(1), U(2)}}
    rows = [row(U(3), 0x300, 100)]
    body, blockers = cr.analyze(ok, edges, rows, describe)
    assert body["roots"] == [] and blockers[0]["roots"] == "unit:1;unit:2"
    g = (ok, edges, rows, describe)
    assert cr.joint_gain(g, ["unit:1"]) == 0 == cr.joint_gain(g, ["unit:2"])
    assert cr.joint_gain(g, blockers[0]["roots"].split(";")) == 100
    ok = {U(1): False, U(2): False}
    rows = [row(U(1), 0x100, 16, self_strict=False), row(U(2), 0x108, 16, self_strict=False)]
    body, _ = cr.analyze(ok, {}, rows, describe)
    assert [e["conditional_gain_bytes"] for e in body["roots"]] == [16, 16]
    assert cr.joint_gain((ok, {}, rows, describe), ["unit:1", "unit:2"]) == 24
    assert "do not add them" in " ".join(cr.LIMITS)


def test_gain_subtracts_bytes_already_credited():
    GROUPS.clear()
    ok = {U(1): False, U(2): True, U(3): True}
    rows = [row(U(1), 0x100, 16, self_strict=False), row(U(2), 0x108, 16), row(U(3), 0x100, 12)]
    body, _ = cr.analyze(ok, {U(2): {U(1)}}, rows, describe)
    (e,) = body["roots"]
    assert (e["direct_bytes"], e["beneficiary_bytes"]) == (16, 16)
    assert e["conditional_gain_bytes"] == 12                                   # [0x100,0x118) less [0x100,0x10C)
    assert cr.forced_gain(ok, {U(2): {U(1)}}, rows, [U(1)], source_closure) == 12


def test_every_gain_and_every_blocker_set_equals_link_cycles_closure():
    """600 random graphs (failed, unknown and filler nodes, shared addresses, overlapping
    rows): each gain equals link_cycle.greatest_closure run with the root's nodes passing;
    the closed set, the credit and this module's reference closure are link_cycle's; and each
    row's blocker set is exactly the blockers it reaches (or is marked beyond the cap)."""
    rng = random.Random(7)
    positive = sets = 0
    for _ in range(600):
        nodes = [(rng.choice(["unit"] * 6 + ["datum", "twin", "fill", "stub", "dump"]), i) for i in range(rng.randint(3, 30))]
        ok = {n: rng.random() < 0.7 for n in nodes if n[0] not in context.BAD_TARGETS and rng.random() < 0.95}
        edges = {n: {rng.choice(nodes) for _ in range(rng.randint(0, 3))} for n in nodes if n in ok}
        rows = []
        for n in nodes:
            if n[0] == "unit" and n in ok:
                for _ in range(rng.randint(1, 2)):
                    rows.append({"node": n, "name": f"r{len(rows)}", "source": "s", "rva": rng.randint(0, 60) * 4,
                                 "size": rng.randint(1, 12), "real": rng.random() < 0.9,
                                 "placed": rng.random() < 0.85, "self_strict": ok[n] or rng.random() < 0.5})

        def group(n):
            return "g%d" % (n[1] // 2)

        def desc(n):
            return {"id": "%s:%03d" % n, "kind": n[0], "group": group(n)}
        cap = rng.randint(1, 4)
        body, table = cr.analyze(ok, edges, rows, desc, cap=cap)
        closed = source_closure(ok, edges)
        assert cr.closed_nodes(ok, edges) == closed == cr.reference_closure(ok, edges)
        assert body["summary"]["credit_unique_bytes"] == lc.unique_bytes(
            [(r["rva"], r["rva"] + r["size"]) for r in rows
             if r["real"] and r["placed"] and r["self_strict"] and r["node"] in closed])
        got = {e["root"]: e["conditional_gain_bytes"] for e in body["roots"]}
        groups = {}
        for n in ok:
            if cr.scorable(n, ok):
                groups.setdefault(group(n), []).append(n)
        assert set(got) <= set(groups)
        for g, members in groups.items():
            want = cr.forced_gain(ok, edges, rows, members, source_closure)
            assert got.get(g, 0) == want
            positive += want > 0
        blockers = cr.blockers_of(ok, edges)
        by_name = {r["name"]: r for r in table}
        for r in rows:
            if r["name"] not in by_name:
                continue
            seen, work = {r["node"]}, [r["node"]]
            while work:
                for t in edges.get(work.pop(), ()):
                    if t not in seen:
                        seen.add(t)
                        work.append(t)
            reach = sorted({group(n) if cr.scorable(n, ok) else "leaf:" + desc(n)["id"] for n in seen & blockers})
            out = by_name[r["name"]]
            if len(reach) > cap:
                assert (out["reach"], out["roots"]) == (f">{cap}", "")
            else:
                assert (out["reach"], out["roots"]) == (str(len(reach)), ";".join(reach))
                sets += len(reach) > 1
    assert positive > 300 and sets > 300


def _measure_state():
    """A finished measure, as link_cycle.closure_graph leaves it: two units (one failing, one
    with a hard-coded row), a certified and a rejected twin, three datums, an EH thunk."""
    units = [{"id": 0, "head": "?a@@YAXXZ"}, {"id": 1, "head": None}, {"id": 2, "head": "?c@@YAXXZ"}]
    recs = [{"row": {"name": "?a@@YAXXZ", "kind": "real", "source": "game/a.cpp", "rva": 0x1000, "size": 16},
             "unit": units[0], "measured": True, "fails": [], "placed": 1},
            {"row": {"name": "?a2@@YAXXZ", "kind": "real", "source": "game/a.cpp", "rva": 0x0F00, "size": 8},
             "unit": units[0], "measured": True, "fails": ["data-back:_g", "data-back:_g"], "placed": 1},
            {"row": {"name": "?b@@YAXXZ", "kind": "gen-funclet", "source": "game/b.cpp", "rva": 0x2000, "size": 4},
             "unit": units[1], "measured": False, "fails": [], "placed": 0},
            {"row": {"name": "?c@@YAXXZ", "kind": "real", "source": "game/c.cpp", "rva": 0x3000, "size": 32},
             "unit": units[2], "measured": True, "fails": [], "placed": 1}]
    hard = {id(recs[3]): "hardcoded address"}
    d1, d2, d3 = (0x9000, 0x8000, 4), (0x9100, -0x10, 8), (0x9200, 0x8200, 4)
    m = types.SimpleNamespace(
        twins={(0x500, 0x1000): (True, "certified"), (0x600, 0x3000): (False, "bytes"), (0x700, 0x4000): (True, "ok")},
        twin_fails={(0x600, 0x3000): ["bytes", "extent differs"]},
        dnodes={d1: {"name": "_g", "fails": ["data-content"]}, d2: {"name": "_h", "fails": []},
                d3: {"name": "_k", "fails": []}},
        eh_nodes={0x77: {"fails": []}, 0x78: {"fails": []}, 0x79: {"fails": ["catch type unverified"]}},
        sym_at=lambda a: (a, f"_sym{a:X}", "o.obj", a + 1) if a != 0x700 else None)
    ok = {("unit", 0): False, ("unit", 1): False, ("unit", 2): False, ("twin", 0x500, 0x1000): True,
          ("twin", 0x600, 0x3000): False, ("twin", 0x700, 0x4000): False, ("datum", d1): False, ("datum", d2): False,
          ("datum", d3): True, ("eh", 0x77): False, ("eh", 0x78): True, ("eh", 0x79): False}
    edges = {("unit", 0): {("datum", d1), ("twin", 0x500, 0x1000), ("fill", 0x5000)}, ("unit", 2): {("eh", 0x77)},
             ("twin", 0x500, 0x1000): {("datum", d2), ("stub",)}, ("unit", 1): set()}
    return m, recs, hard, ok, edges


def test_link_cycles_graph_emit_reads_the_measure_and_changes_nothing(tmp_path):
    m, recs, hard, ok, edges = _measure_state()
    before = copy.deepcopy((recs, ok, edges, m.twins, m.twin_fails, m.dnodes, m.eh_nodes)), dict(hard)
    doc = lc.closure_graph_doc(m, recs, hard, ok, edges)
    assert (copy.deepcopy((recs, ok, edges, m.twins, m.twin_fails, m.dnodes, m.eh_nodes)), dict(hard)) == before   # read only
    assert doc["schema"] == lc.CLOSURE_GRAPH_SCHEMA == cr.GRAPH_SCHEMA and lc.CLOSURE_GRAPH == cr.GRAPH_FILE
    n = doc["nodes"]
    assert n["unit:0"] == {"kind": "unit", "ok": False, "name": "?a@@YAXXZ", "rva": 0x0F00, "source": "game/a.cpp",
                           "failures": ["data-back:_g"]}
    assert n["unit:1"]["failures"] == ["unmeasured"] and n["unit:1"]["name"] == "?b@@YAXXZ"
    assert n["unit:2"]["failures"] == ["shift:hardcoded address"]
    assert n["twin:1536:12288"]["failures"] == ["bytes", "extent differs"]
    assert n["twin:1792:16384"] == {"kind": "twin", "ok": False, "failures": ["shift"], "rva": 0x4000,
                                    "linked": 0x700, "name": "", "object": ""}   # certified, failed its shift check
    assert n["twin:1280:4096"]["failures"] == [] and n["twin:1280:4096"]["name"] == "_sym500"
    assert n["datum:36864:32768:4"]["failures"] == ["data-content"]             # its shift check was never asked
    assert n["datum:37120:-16:8"]["failures"] == ["shift"] and n["eh:119"]["failures"] == ["shift"]
    assert n["eh:120"] == {"kind": "eh", "ok": True, "failures": []}
    assert n["eh:121"]["failures"] == ["catch type unverified"]
    assert doc["edges"] == {"twin:1280:4096": ["datum:37120:-16:8", "stub"],
                            "unit:0": ["datum:36864:32768:4", "fill:20480", "twin:1280:4096"], "unit:2": ["eh:119"]}
    assert doc["rows"][0] == ["?a2@@YAXXZ", "real", "game/a.cpp", 0x0F00, 8, "unit:0", 1, 0]
    assert [r[7] for r in doc["rows"]] == [0, 1, 0, 1] and doc["rows"][2][6] == 0
    # the same measure writes the same bytes, whatever order its dicts and sets happen to have
    shuffled = dict(reversed(list(ok.items()))), {k: set(sorted(v, key=str, reverse=True)) for k, v in
                                                  reversed(list(edges.items()))}
    lc.write_closure_graph(tmp_path / "a.gz", doc)
    lc.write_closure_graph(tmp_path / "b.gz", lc.closure_graph_doc(m, list(reversed(recs)), hard, *shuffled))
    assert (tmp_path / "a.gz").read_bytes() == (tmp_path / "b.gz").read_bytes()
    # and tools/closure_report.py reads it back as link_cycle's own closure
    g_ok, g_edges, rows, describe_node = cr.load_graph(tmp_path / "a.gz", lc.sha256(tmp_path / "a.gz"))
    assert {k[1] for k in cr.reference_closure(g_ok, g_edges)} == {lc.node_key(k) for k in
                                                                    source_closure(ok, edges)}
    assert describe_node(("unit", "unit:0"))["group"] == "0x00000F00"
    assert describe_node(("datum", "datum:37120:-16:8"))["group"].startswith("datum:-0x00000010")   # no address
    assert describe_node(("fill", "fill:20480")) == {"id": "fill:0x00005000", "kind": "fill",
                                                    "group": "fill:0x00005000"}


def test_document_binds_the_blockers_table_and_is_deterministic(tmp_path):
    GROUPS.clear()
    ok, edges, rows = graph()
    binding = {"commit": "c" * 40, "receipt_core_sha256": "d" * 64, "link_status_sha256": "e" * 64,
               "graph": {"bound": False, "label": cr.REPLAYED, "sha256": "f" * 64}}
    a = cr.document(*cr.analyze(ok, edges, rows, describe), binding)
    b = cr.document(*cr.analyze(ok, edges, list(reversed(rows)), describe), binding)
    assert a == b
    doc = json.loads(a[0])
    assert doc["schema"] == cr.SCHEMA and doc["algorithm"] == cr.ALGORITHM and doc["commit"] == "c" * 40
    assert doc["blockers"]["sha256"] == cr.sha256_bytes(a[1]) and doc["limits"] == list(cr.LIMITS)
    assert doc["blockers"]["set_cap"] == cr.SET_CAP and "truncated" in doc["blockers"]["roots_column"]
    (tmp_path / "r.json.gz").write_bytes(gzip.compress(a[0]))
    assert cr.load_roots(tmp_path / "r.json.gz") == doc
    (tmp_path / "other.json").write_text(json.dumps(dict(doc, algorithm="some-other-ranking/9")))
    with pytest.raises(cr.ReportError, match="this checkout reads"):
        cr.load_roots(tmp_path / "other.json")
    (tmp_path / "anon.json").write_text(json.dumps(dict(doc, graph={"bound": True, "label": cr.REPLAYED})))
    with pytest.raises(cr.ReportError, match="does not say where its graph came from"):
        cr.load_roots(tmp_path / "anon.json")




def measured_run(tmp_path, *, dump_kind=None):
    """A small frozen run, with verdicts and credit from BFME1's closure oracle."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    nodes = {f"unit:{i}": {"kind": "unit", "ok": i > 2, "rva": i * 0x1000,
                            "name": name, "source": f"game/{name}.cpp", "failures": [] if i > 2 else ["wrong-copy"]}
             for i, name in enumerate(("A", "B", "P", "C"), 1)}
    rows = [[n["name"], "real", n["source"], n["rva"], 20 if key == "unit:1" else 10,
             key, 1, int(n["ok"])] for key, n in nodes.items()]
    edges = {"unit:3": ["unit:1"]}
    if dump_kind:
        source = "game/gen_asm/d_5.asm" if dump_kind == "generated" else "game/masm_dumps/D.asm"
        nodes["unit:5"] = {"kind": "unit", "ok": True, "name": "D", "rva": 0x5000,
                           "source": source, "failures": []}
        rows.append(["D", dump_kind, source, 0x5000, 100, "unit:5", 1, 1])
        edges["unit:3"].append("dump:5")
    doc = {"schema": context.GRAPH_SCHEMA, "rules": context.RULES, "bad_targets": list(context.BAD_TARGETS),
           "nodes": nodes, "edges": edges, "rows": rows}
    graph = cr.graph_from_doc(doc)
    ok, es, rs, _ = graph
    closed = source_closure(ok, es)
    status = [{"name": r["name"], "kind": r["kind"], "source": r["source"],
               "retail_rva": f"0x{r['rva']:08X}", "size": str(r["size"]), "placed": str(int(r["placed"])),
               "self_strict": str(int(r["self_strict"])),
               "closed_strict": str(int(r["self_strict"] and r["node"] in closed))} for r in rs]
    with (tmp_path / "link_status.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(status[0]))
        writer.writeheader()
        writer.writerows(status)
    lc.write_closure_graph(tmp_path / cr.GRAPH_FILE, doc)
    deps = {"link_cycle.py": "synthetic-test"}
    receipt = {"commit": "a" * 40, "rules": context.RULES, "rule_identity": context.rule_identity(deps),
               "tool_dependencies": deps, "tool_digest": context.digest(deps),
               "closure_graph_sha256": lc.sha256(tmp_path / cr.GRAPH_FILE),
               "series": {"credit_unique_bytes": cr.credit_of(ok, es, rs),
                          "link_status_sha256": lc.sha256(tmp_path / "link_status.csv"),
                          "closure_graph_sha256": lc.sha256(tmp_path / cr.GRAPH_FILE)}}
    save_receipt(tmp_path, receipt)
    return tmp_path, doc, receipt


def save_receipt(run, receipt):
    lc.stamp_cores(receipt)
    (run / "receipt.json").write_text(json.dumps(receipt))


def bind_changed_graph(run, doc, receipt):
    lc.write_closure_graph(run / cr.GRAPH_FILE, doc)
    receipt["closure_graph_sha256"] = receipt["series"]["closure_graph_sha256"] = lc.sha256(run / cr.GRAPH_FILE)
    save_receipt(run, receipt)


def test_measured_graph_rows_credit_binding_and_deterministic_cli(tmp_path, capsys):
    run, _, receipt = measured_run(tmp_path / "run")
    first = cr.from_graph(run)
    assert first == cr.from_graph(run)
    roots, blockers, facts = first
    doc = json.loads(roots)
    assert facts == {"credit": 10, "roots": 2}
    assert {r["root"]: r["conditional_gain_bytes"] for r in doc["roots"]} == {"0x00001000": 30, "0x00002000": 10}
    assert doc["blockers"]["sha256"] == cr.sha256_bytes(blockers)
    assert doc["graph"] == {"bound": True, "label": cr.BOUND, "sha256": receipt["closure_graph_sha256"]}
    assert doc["checks"]["link_status_rows_reproduced"] == 4
    assert all(r["verified"] == "forced-closure" for r in doc["roots"])
    out = tmp_path / "reports"
    assert cr.main(["graph", str(run), "--out", str(out)]) == 0
    assert (out / cr.ROOTS).read_bytes() == roots
    assert (out / cr.BLOCKERS).read_bytes() == blockers
    assert cr.main(["show", str(out / cr.ROOTS)]) == 0
    assert "root A -> 30 potentially unlocked bytes" in capsys.readouterr().out
    # Phase 2 compressed members can use deterministic gzip without changing JSON/CSV.
    (run / "link_status.csv.gz").write_bytes(gzip.compress((run / "link_status.csv").read_bytes(), mtime=0))
    (run / "link_status.csv").unlink()
    assert cr.from_graph(run) == first


def test_equal_verdicts_cannot_hide_changed_edges(tmp_path):
    run, doc, _ = measured_run(tmp_path / "run")
    before = cr.graph_from_doc(doc)
    doc["edges"]["unit:3"].append("unit:2")
    after = cr.graph_from_doc(doc)
    assert source_closure(*before[:2]) == source_closure(*after[:2])
    assert cr.credit_of(*before[:3]) == cr.credit_of(*after[:3])
    assert cr.analyze(*before)[0]["roots"] != cr.analyze(*after)[0]["roots"]
    lc.write_closure_graph(run / cr.GRAPH_FILE, doc)
    with pytest.raises(cr.ReportError, match="not the graph that run measured"):
        cr.from_graph(run)
    out = tmp_path / "out"
    assert cr.main(["graph", str(run), "--out", str(out)]) == 1
    assert not out.exists()


@pytest.mark.parametrize("tamper", ["row", "credit", "status", "receipt", "rules", "profile", "dependencies"])
def test_refuses_tampered_measurement(tmp_path, tamper):
    run, doc, receipt = measured_run(tmp_path / "run")
    expected = ""
    if tamper == "row":
        doc["rows"][2][4] -= 1  # Open row: leaves credit and verdicts unchanged.
        bind_changed_graph(run, doc, receipt)
        expected = "row record.*differ"
    elif tamper == "credit":
        receipt["series"]["credit_unique_bytes"] += 1
        save_receipt(run, receipt)
        expected = "graph credits"
    elif tamper == "status":
        with (run / "link_status.csv").open("a") as f:
            f.write("forged\n")
        expected = "not the file the receipt hashed"
    elif tamper == "receipt":
        receipt["commit"] = "b" * 40
        (run / "receipt.json").write_text(json.dumps(receipt))
        expected = "core digest"
    else:
        if tamper == "rules":
            receipt["rules"] = "link-cycle-2"
        elif tamper == "profile":
            receipt["rule_identity"]["profile"] = dict(context.PROFILE, fold_exemptions=["retail-truth-4"])
        else:
            receipt["tool_dependencies"]["build.py"] = "changed"
        save_receipt(run, receipt)
        expected = "rule identity"
    with pytest.raises(cr.ReportError, match=expected):
        cr.from_graph(run)


@pytest.mark.parametrize("dump_kind", ["generated", "asm"])
def test_generated_and_assembly_dependencies_cannot_unlock_source(tmp_path, dump_kind):
    run, doc, receipt = measured_run(tmp_path / "run", dump_kind=dump_kind)
    roots, _, _ = cr.from_graph(run)
    result = json.loads(roots)
    assert {r["root"]: r["conditional_gain_bytes"] for r in result["roots"]} == {"0x00001000": 20, "0x00002000": 10}
    assert cr.joint_gain(cr.graph_from_doc(doc), ["0x00001000", "0x00002000", "dump:5"]) == 30
    # A BFME2-style source graph lacking BFME1 dump exclusion is refused.
    doc["edges"]["unit:3"][-1] = "unit:5"
    bind_changed_graph(run, doc, receipt)
    with pytest.raises(cr.ReportError, match="generated/assembly source closure"):
        cr.from_graph(run)


@pytest.mark.parametrize("shape", ["chain", "cycle", "diamond"])
def test_explicit_dependency_shapes(shape):
    GROUPS.clear()
    ok = {U(1): False, U(2): True, U(3): True, U(4): True}
    edges = {U(2): {U(1)}, U(3): {U(2)}, U(4): {U(3)}}
    if shape == "cycle":
        edges[U(1)] = {U(4)}
    elif shape == "diamond":
        edges = {U(2): {U(1)}, U(3): {U(1)}, U(4): {U(2), U(3)}}
    rows = [row(n, i * 100, 10, self_strict=good) for i, (n, good) in enumerate(ok.items(), 1)]
    body, _ = cr.analyze(ok, edges, rows, describe)
    assert body["roots"][0]["conditional_gain_bytes"] == 40
    assert cr.forced_gain(ok, edges, rows, [U(1)], source_closure) == 40


def test_duplicate_addresses_and_unplaced_rows_do_not_add_gain():
    GROUPS.clear()
    ok = {U(1): False, U(2): True}
    rows = [row(U(1), 0x100, 20, self_strict=False)] * 2 + [row(U(2), 0x100, 20), row(U(2), 0x110, 20),
                                                               row(U(2), 0x1000, 5000, placed=False)]
    body, _ = cr.analyze(ok, {U(2): {U(1)}}, rows, describe)
    assert body["roots"][0]["conditional_gain_bytes"] == 36


@pytest.mark.parametrize("leaf", [("fill", 1), ("stub",), ("dump", 1), ("unknown", 3)])
def test_leaves_never_score_even_when_explicitly_forced(leaf):
    GROUPS.clear()
    ok, edges, rows = {U(1): True}, {U(1): {leaf}}, [row(U(1), 0x100, 100)]
    body, _ = cr.analyze(ok, edges, rows, describe)
    assert body["roots"] == []
    assert cr.forced_gain(ok, edges, rows, [leaf]) == 0


def test_joint_only_output_is_separate_and_explicitly_non_additive():
    GROUPS.clear()
    g = ({U(1): False, U(2): False, U(3): True}, {U(3): {U(1), U(2)}}, [row(U(3), 0x100, 30)], describe)
    body, table = cr.analyze(*g)
    assert body["roots"] == []
    assert body["summary"]["joint_only"]["candidate_unique_bytes"] == 30
    assert body["summary"]["joint_only"]["non_additive"] is True
    assert table[0]["roots"] == "unit:1;unit:2"
    assert cr.joint_gain(g, ["unit:1", "unit:2"]) == 30


def test_legacy_replay_reports_keep_unbound_label(tmp_path):
    assert cr.main(["replay", str(tmp_path), "--out", str(tmp_path / "out")]) == 1
    assert not (tmp_path / "out").exists()
    run, _, receipt = measured_run(tmp_path / "run")
    receipt.pop("closure_graph_sha256")
    receipt["series"].pop("closure_graph_sha256")
    save_receipt(run, receipt)
    with pytest.raises(cr.ReportError, match="names no closure_graph_sha256.*replayed, graph not receipt-bound"):
        cr.from_graph(run)


@pytest.mark.parametrize("dump_kind", [None, "generated", "asm", "library"])
def test_measure_emits_the_final_bfme1_source_graph_and_data_back(tmp_path, monkeypatch, dump_kind):
    """Exercise measure's integration on in-memory images and finished records; no linker."""
    from collections import Counter
    real = {"name": "f", "kind": "real", "source": "game/f.cpp", "rva": 0x1000, "size": 4}
    other = {"name": "g", "kind": dump_kind or "real", "source":
             "game/gen_asm/d.asm" if dump_kind == "generated" else
             "inputs/vendor/example/example.lib" if dump_kind == "library" else
             "game/masm_dumps/D.asm" if dump_kind else "game/g.cpp",
             "rva": 0x1100, "size": 4}
    units = [{"id": i, "head": r["name"], "rows": [r]} for i, r in enumerate((real, other))]
    recs = [{"row": r, "unit": u, "measured": True, "placed": 1, "linked": r["rva"], "fails": [],
             "edges": {("unit", 1)} if i == 0 else set(), "masked": set(), "rels": [], "unpinned": False}
            for i, (r, u) in enumerate(zip((real, other), units))]
    m = types.SimpleNamespace(run=lambda: recs, twins={}, dnodes={}, eh=Counter(), import_equiv=0, ilt_routes=Counter(),
                              back={0x5000: {0x4100, 0x4000}})
    checks = []
    sh = types.SimpleNamespace(code=lambda *a: checks.append(a), summary=lambda: {"checked": True})
    monkeypatch.setattr(lc, "Measure", lambda *a: m)
    monkeypatch.setattr(lc, "Shifted", lambda *a: sh)
    monkeypatch.setattr(lc, "pe_view", lambda p: (None, bytes(0x3000), {".text": (0x1000, 0x2000)}, {}))
    monkeypatch.setattr(lc, "zz_names", lambda p: ({}, []))
    (tmp_path / "base.map").write_text("")
    result = lc.measure(tmp_path, units, [], types.SimpleNamespace(by_base={}), bytes(0x3000),
                        {".text": (0x1000, 0x2000)}, {}, {}, True, lc.SHIFT_BASE)
    assert len(checks) == 2  # Graph emission did not repeat shift verdicts.
    assert result["data_back"] == {"address_kind": "rva", "collisions": [
        {"retail_rva": 0x5000, "linked_rvas": [0x4000, 0x4100]}]}
    assert result["credit_unique_bytes"] == (4 if dump_kind == "library" else 0 if dump_kind else 8)
    graph = cr.load_graph(tmp_path / cr.GRAPH_FILE, result["closure_graph_sha256"])
    ok, edges, rows, describe_node = graph
    closed = source_closure(ok, edges)
    assert cr.check_rows(rows, closed, cr.status_rows(tmp_path / "link_status.csv")) == 2
    assert cr.credit_of(ok, edges, rows) == result["credit_unique_bytes"]
    deps = {"measurement": "synthetic"}
    receipt = {"commit": "a" * 40, "rules": context.RULES, "rule_identity": context.rule_identity(deps),
               "tool_dependencies": deps, "tool_digest": context.digest(deps), "series": result,
               "closure_graph_sha256": result["closure_graph_sha256"]}
    identity = lc.write_receipt(tmp_path, receipt)
    roots, table, facts = cr.from_graph(tmp_path)
    assert facts["credit"] == result["credit_unique_bytes"]
    archived = tmp_path / "measurements" / identity["tag"]
    assert cr.from_graph(archived) == (roots, table, facts)
