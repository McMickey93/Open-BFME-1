"""Review-2 admission boundaries with real temporary Git histories; no native tools."""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import comdat_families as comdat
import cycle_source
import link_cycle as lc
import repair_queue as rq
from test_comdat_families import census, NAME
from test_cycle_review2_admission import initialize, commit


@pytest.mark.parametrize("digests,homes,ambiguous", [
    (["good", "good"], {0x60000}, False),
    (["good", "other"], {0x60000}, True),
    (["good", "good"], {0x60000, 0x60010}, True),
])
def test_provider_requires_one_body_home(digests, homes, ambiguous):
    index = census()
    index["objects"].append("another.obj")
    index["comdat"][NAME] = [(0, "bad", "wrong"), (1, digests[0], "retail"), (3, digests[1], "retail")]
    family = comdat.analyze(index, {}, homes={NAME: homes})["families"][0]
    assert family["ambiguous_provider"] is ambiguous
    assert family["servable"] is not ambiguous
    assert (family["canonical_provider"] is None) is ambiguous
    if ambiguous:
        assert family["status"] == "ambiguous provider — needs analysis"


def test_homes_deduplicate_addresses_without_ignoring_distinct_homes(tmp_path):
    ledger = tmp_path / "targets/game/reverse/functions.csv"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("name,source,status,target_rva,target_size,notes\n" +
                      "".join(f"{NAME},game/a.cpp,matched,{rva},6,\n"
                              for rva in ("0x60000", "0x00060000", "0x60010")))
    assert comdat.retail_homes(tmp_path, {NAME})[NAME] == {0x60000, 0x60010}


@pytest.fixture
def history(tmp_path):
    initialize(tmp_path)
    sources = ["game/root.cpp", "game/dep.cpp", "game/leaf.cpp", "game/unrelated.cpp"]
    for source in sources:
        path = tmp_path / source
        path.parent.mkdir(exist_ok=True)
        path.write_text("int f() { return 2; }\n")
    header = tmp_path / "game/shared.h"
    header.write_text("#define VALUE 2\n")
    reverse = tmp_path / "targets/game/reverse"
    reverse.mkdir(parents=True)
    (reverse / "functions.csv").write_text(
        "name,source,status,target_rva,target_size,notes\n" +
        "".join(f"{name},{source},matched,0x{rva:08X},6,\n"
                for name, source, rva in zip(("root", "dep", "leaf", "unrelated"), sources,
                                             (0x60000, 0x60100, 0x60200, 0x70000))))
    (reverse / "symbols.csv").write_text("name,address,notes\nleaf,0x00460200,original\n")
    (reverse / "data_rows.csv").write_text(
        "name,address,address_kind,size,source,status\nleaf,0x00060200,rva,4,game/leaf.cpp,matched\n")
    measured = commit(tmp_path, ["game", "targets"], "measured")
    nodes = [("unit", str(i)) for i in range(3)]
    rows = [dict(node=n, rva=0x60000 + i * 0x100, source=sources[i]) for i, n in enumerate(nodes)]
    descriptions = {n: {"source": row["source"], "retail_rva": f"0x{row['rva']:08X}"}
                    for n, row in zip(nodes, rows)}
    graph = ({n: False for n in nodes}, {nodes[i]: {nodes[(i + 1) % 3]} for i in range(3)},
             rows, descriptions.__getitem__)
    item = {"target_rva": "0x00060000", "source": sources[0], "function": "root"}
    return tmp_path, measured, item, graph


@pytest.mark.parametrize("change,stale", [
    ("root.cpp", True), ("dep.cpp", True), ("leaf.cpp", True), ("shared.h", True),
    ("unrelated.cpp", False), ("root-row", True), ("leaf-row", True),
    ("unrelated-row", False), ("symbols.csv", True), ("data_rows.csv", True),
    ("unchanged", False),
])
def test_source_dependency_and_narrow_ledger_currency(history, change, stale):
    root, measured, item, graph = history
    if change.endswith((".cpp", ".h")):
        path = root / "game" / change
        path.write_text(path.read_text().replace("2", "1"))
    elif change.endswith("-row"):
        path = root / "targets/game/reverse/functions.csv"
        path.write_text(path.read_text().replace(change.removesuffix("-row") + ",game/",
                                                 "renamed,game/"))
    elif change != "unchanged":
        path = root / "targets/game/reverse" / change
        path.write_text(path.read_text().replace("original", "changed").replace(
            "rva,4,", "rva,8,"))
    if change != "unchanged":
        commit(root, [str(path.relative_to(root))], change)
    kept, skipped = rq.current_bundle_items([item], measured, root=root, graph=graph)
    assert bool(skipped) is stale
    assert bool(kept) is not stale
    if stale:
        assert skipped[0]["reason"] == "stale"
        assert "changed since measurement" in skipped[0]["stale_reason"]


def test_unknown_measured_commit_is_never_served(history):
    root, _, item, graph = history
    kept, skipped = rq.current_bundle_items([item], "f" * 40, root=root, graph=graph)
    assert not kept
    assert skipped[0]["reason"] == "stale"
    assert "cannot compare" in skipped[0]["stale_reason"]


def test_uncommitted_relevant_ledger_edit_also_stales_candidate(history):
    root, measured, item, graph = history
    ledger = root / "targets/game/reverse/functions.csv"
    ledger.write_text(ledger.read_text().replace("root,game/", "changed,game/"))
    kept, skipped = rq.current_bundle_items([item], measured, root=root, graph=graph)
    assert not kept and skipped[0]["reason"] == "stale"


def test_data_back_ranking_is_a_protected_verifier():
    import protected_paths
    assert protected_paths.protected(["tools/data_back_rank.py"]) == ["tools/data_back_rank.py"]


@pytest.mark.parametrize("closure", [False, True])
def test_bundle_queue_uses_shared_candidate_currency(history, monkeypatch, closure):
    import closure_report as cr
    root, measured, item, graph = history
    path = root / "game/dep.cpp"
    path.write_text("int repaired_dependency;\n")
    commit(root, ["game/dep.cpp"], "dependency repaired")
    b = SimpleNamespace(commit=measured, receipt={"closure_graph_sha256": "unused"},
                        closure_graph=root / "unused", link_status=root / "unused",
                        dir=root, tag="fixture")
    monkeypatch.setattr(rq, "ROOT", root)
    monkeypatch.setattr(rq.cycle_artifacts(), "serve", lambda *a, **kw: (b, {"authoritative": True}, []))
    monkeypatch.setattr(rq, "bundle_note", lambda *a: "fixture bundle")
    monkeypatch.setattr(rq, "cycle_items", lambda *a: [item])
    monkeypatch.setattr(rq, "closure_queue", lambda *a: ([item], [], {}))
    monkeypatch.setattr(cr, "load_graph", lambda *a: graph)
    monkeypatch.setattr(rq, "eligible_link_items", lambda items: items)
    result = rq._bundle_queue(root, closure=closure)
    assert not result["items"]
    assert result["skipped_candidates"][0]["reason"] == "stale"
    assert "game/dep.cpp" in result["notes"][1]


def test_export_strips_nested_cache_links_and_preserves_external_cache(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    initialize(root)
    external = tmp_path / "cache"
    external.mkdir()
    (external / "object.obj").write_bytes(b"cache")
    (root / "build").mkdir()
    (root / "build/match").symlink_to(external, target_is_directory=True)
    sha = commit(root, ["build"], "archived nested cache")
    monkeypatch.setattr(lc, "ROOT", root)
    monkeypatch.setattr(cycle_source, "command", lambda *a: [sys.executable, "-I", "-S", "-c", "pass"])
    snapshot = lc.export_snapshot(sha, tmp_path / "snapshots")
    assert list((snapshot / "build").iterdir()) == []
    assert (external / "object.obj").read_bytes() == b"cache"
    # A launcher cannot reuse outputs created in a previous run.
    (snapshot / "build/old.obj").write_bytes(b"old compile")
    monkeypatch.setenv("BFME_CYCLE_EXPECTED_SEMANTIC", "launcher")
    with pytest.raises(SystemExit, match="empty snapshot build"):
        lc.export_snapshot(sha, tmp_path / "snapshots")


def test_existing_snapshot_build_symlink_refused(tmp_path):
    external = tmp_path / "external"
    external.mkdir()
    (external / "object.obj").write_bytes(b"unchanged")
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (snapshot / "build").symlink_to(external, target_is_directory=True)
    with pytest.raises(SystemExit, match="local directory"):
        lc.snapshot_build_dir(snapshot)
    assert (external / "object.obj").read_bytes() == b"unchanged"
