"""Round-2 snapshot/candidate tests in temporary repositories only."""
import sys

import pytest

from test_cycle_review2_admission import initialize, commit, git
from test_cycle_review2_currency import history
from test_cycle_review2_evidence import ImageCase, F, DATA, RDATA, dword, lc
import closure_report as cr
import cycle_source
import repair_queue as rq


@pytest.mark.parametrize("suffix", [".h", ".hxx", ".hh", ".ipp"])
def test_header_only_repairs_stale_candidates_for_all_cpp_header_suffixes(history, suffix):
    root, _, item, graph = history
    header = root / ("game/settings" + suffix)
    header.write_text("#define VALUE 2\n")
    source = root / "game/root.cpp"
    source.write_text('#include "settings' + suffix + '"\nint root() { return VALUE; }\n')
    measured = commit(root, [str(header.relative_to(root)), "game/root.cpp"], "measured header use")
    header.write_text("#define VALUE 1\n")
    commit(root, [str(header.relative_to(root))], "repair in header only")
    kept, skipped = rq.current_bundle_items([item], measured, root=root, graph=graph)
    print({"header": header.name, "kept": len(kept), "skipped": skipped})
    assert not kept and skipped[0]["reason"] == "stale", "valid C++ include extension omitted from currency"


def test_new_untracked_earlier_header_stales_measured_candidate(history):
    root, _, item, graph = history
    fallback = root / "game/include/settings.h"
    fallback.parent.mkdir()
    fallback.write_text("#define VALUE 2\n")
    source = root / "game/root.cpp"
    source.write_text('#include "settings.h"\nint root() { return VALUE; }\n')
    measured = commit(root, ["game/include/settings.h", "game/root.cpp"], "header from include search path")
    # Source-adjacent quoted includes win over /Igame/include; this is exactly
    # the change build.search_inventory already treats as invalidating a TU.
    (root / "game/settings.h").write_text("#define VALUE 1\n")
    kept, skipped = rq.current_bundle_items([item], measured, root=root, graph=graph)
    print({"untracked_header": "game/settings.h", "kept": len(kept), "skipped": skipped})
    assert not kept, "untracked earlier include repaired the body but stale candidate is still served"


def test_data_only_dependency_repair_stales_measured_candidate(tmp_path, monkeypatch):
    initialize(tmp_path)
    case = ImageCase(tmp_path, monkeypatch)
    raw = b"\xa1" + bytes(4) + b"\xc3"
    obj = case.object("root.obj", [(".text", raw, [(1, "_g", lc.DIR32)])],
                      [("_root", 1, 0, lc.EXTERNAL), ("_g", 0, 0, lc.EXTERNAL)])
    data = case.object("data.obj", [(".data", dword(2), [])], [("_g", 1, 0, lc.EXTERNAL)])
    case.row(obj, "_root", F, 6, source="game/root.cpp")
    case.public(obj, "_root", F)
    case.public(data, "_g", DATA)
    case.put(F, raw, retail=raw)
    case.ptr(F + 1, DATA)
    case.R[F + 1:F + 5] = dword(lc.BASE + RDATA)
    case.put(DATA, dword(2))
    case.R[RDATA:RDATA + 4] = dword(1)
    (tmp_path / "game").mkdir()
    (tmp_path / "game/root.cpp").write_text("extern int g; int root() { return g; }\n")
    source = tmp_path / "game/data.cpp"
    source.write_text("int g = 2;\n")
    reverse = tmp_path / "targets/game/reverse"
    reverse.mkdir(parents=True)
    (reverse / "functions.csv").write_text(
        "name,source,status,target_rva,target_size,notes\n_root,game/root.cpp,matched,0x60000,6,\n")
    (reverse / "data_rows.csv").write_text(
        "name,address,address_kind,size,source,status\n_g,0x81000,rva,4,game/data.cpp,matched\n")
    measured = commit(tmp_path, ["game", "targets"], "before data repair")
    result, _ = case.measure()
    assert result["credit_unique_bytes"] == 0
    graph = cr.load_graph(tmp_path / "measurement" / cr.GRAPH_FILE)
    source.write_text("int g = 1;\n")
    commit(tmp_path, ["game/data.cpp"], "repair the failed datum")
    item = {"function": "_root", "target_rva": "0x00060000", "source": "game/root.cpp"}
    kept, skipped = rq.current_bundle_items([item], measured, root=tmp_path, graph=graph)
    print({"scope": [sorted(s) for s in rq.candidate_scope(item, graph)],
           "kept": len(kept), "skipped": skipped})
    assert not kept, "measured datum has no defining source in candidate dependency scope"


def test_snapshot_filters_and_checkout_hooks_cannot_seed_exported_build(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / "payload.txt").write_text("input\n")
    (repo / ".gitattributes").write_text("payload.txt filter=seed\n")
    hook = repo / ".git/hooks/post-checkout"
    hook.write_text("#!/bin/sh\nmkdir -p build/match\ntouch build/match/hook.obj\n")
    hook.chmod(0o755)
    git(repo, "config", "filter.seed.smudge", "mkdir -p build/match; touch build/match/filter.obj; cat")
    sha = commit(repo, ["payload.txt", ".gitattributes"], "hook and filter fixture")
    monkeypatch.setattr(lc, "ROOT", repo)
    monkeypatch.delenv("BFME_CYCLE_EXPECTED_SEMANTIC", raising=False)
    monkeypatch.setattr(cycle_source, "command", lambda *a: [sys.executable, "-I", "-S", "-c", "pass"])
    snapshot = lc.export_snapshot(sha, tmp_path / "snapshots")
    assert list((snapshot / "build").iterdir()) == []
    assert not (repo / "build/match/hook.obj").exists()
    # Git archive may invoke a configured smudge filter. Its output is confined
    # to the source repo here; none of that build cache enters the snapshot.
    assert (repo / "build/match/filter.obj").exists()


def test_snapshot_rejects_build_files_created_by_its_preparation_helper(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / "source.cpp").write_text("int x;\n")
    sha = commit(repo, ["source.cpp"], "fixture")
    monkeypatch.setattr(lc, "ROOT", repo)
    monkeypatch.delenv("BFME_CYCLE_EXPECTED_SEMANTIC", raising=False)
    code = "from pathlib import Path; Path('build/poison.obj').write_bytes(b'preseeded')"
    monkeypatch.setattr(cycle_source, "command", lambda *a: [sys.executable, "-I", "-S", "-c", code])
    with pytest.raises(SystemExit, match="empty snapshot build"):
        lc.export_snapshot(sha, tmp_path / "snapshots")
