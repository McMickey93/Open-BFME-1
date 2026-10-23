"""Independent review-2 admission/queue counterexamples; synthetic inputs only."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
import comdat_families
import cycle_source
import link_census as census
import link_cycle as lc
import protected_paths


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          text=True, capture_output=True).stdout.strip()


def initialize(root):
    root.mkdir(exist_ok=True)
    git(root, "init", "-q")
    git(root, "config", "user.name", "Review fixture")
    git(root, "config", "user.email", "review@example.invalid")


def commit(root, paths, message):
    git(root, "add", "--", *paths)
    git(root, "-c", "core.hooksPath=.githooks", "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


def test_new_measurement_verifiers_must_be_protected(tmp_path, monkeypatch):
    paths = ["tools/link_cycle.py", "tools/link_cycle_context.py", "tools/cycle_source.py",
             "tools/cycle_launch.py", "tools/cycle_stamp.py", "tools/cycle_artifacts.py",
             "tools/closure_report.py", "tools/publish_cycle.py", "tools/cycle_diff.py"]
    covered = protected_paths.protected(paths)
    initialize(tmp_path)
    tool = tmp_path / "tools/link_cycle.py"
    source = tmp_path / "game/f.cpp"
    tool.parent.mkdir()
    source.parent.mkdir()
    tool.write_text("def measured_credit(): return 0\n")
    source.write_text("int f() { return 1; }\n")
    commit(tmp_path, ["tools/link_cycle.py", "game/f.cpp"], "fixture original verifier")
    tool.write_text("def measured_credit(): return 1000000\n")
    source.write_text("int f() { return 2; }\n")
    git(tmp_path, "add", "--", "tools/link_cycle.py", "game/f.cpp")
    message = tmp_path / "message"
    message.write_text("ordinary body change, no verifier declaration\n")
    monkeypatch.chdir(tmp_path)
    verdict = protected_paths.check_staged(message)
    print("protected new measurement paths:", covered, "; staged guard exit:", verdict)
    assert set(covered) == set(paths), "new credit/signing policy can change with no Verifier-Change declaration"
    assert verdict != 0


def test_shared_decorated_name_cannot_prove_a_single_template_provider():
    name = "?reserve@?$Vector@H@@QAEXI@Z"
    truth = census.RetailTruth.__new__(census.RetailTruth)
    truth.image = b"\xb8\x01\0\0\0\xc3" + bytes(10) + b"\xb8\x02\0\0\0\xc3"
    truth.sections = [{"name": ".text", "rva": 0x60000, "size": len(truth.image), "raw_pointer": 0}]
    truth.ledger = {name: {0x60000, 0x60010}}
    truth.pinned, truth.shared, truth._cache = {}, set(), {}
    symbol = {"name": name, "section": 1, "value": 0, "storage": 2}
    verdicts = [truth.verdict(symbol, bytes([0xB8, value, 0, 0, 0, 0xC3]), [], str(value), 6)
                for value in (1, 2, 3)]
    objects = ["one.obj", "two.obj", "wrong.obj"]
    index = {"meta": {"commit": "synthetic"}, "objects": objects,
             "comdat": {name: [(i, str(i), verdict) for i, verdict in enumerate(verdicts)]},
             "strong": {}, "selection": {"exceptions": {}, "owners": {name: {"one.obj", "two.obj"}}},
             "blockers": {"game/" + obj + ".cpp": {
                 "object": obj, "linked": i < 2, "losers": [] if i < 2 else [name],
                 "unresolved": [], "duplicates": [], "wrong_selected": [], "addresses": 0}
                 for i, obj in enumerate(objects)}}
    report = comdat_families.analyze(index, {"game/wrong.obj.cpp": [(0x70000, 0x70040)]})
    family = report["families"][0]
    print(json.dumps({"verdicts": verdicts, "servable": family["servable"],
                      "provider": family["canonical_provider"], "selected": family["selected_verdict"]}))
    assert not family["servable"], "two distinct body homes were treated as one proven provider"


def test_archive_snapshot_must_not_import_cached_objects(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    initialize(repo)
    (repo / "build/match").mkdir(parents=True)
    obj = repo / "build/match/game_f.obj"
    lc.write_coff(obj, [(".text", 0x60101020, b"\x31\xc0\xc3", 2)], [("_f", 1, 0, lc.EXTERNAL)])
    sidecar = obj.with_suffix(".deps.json")
    sidecar.write_text('{"source":"preseeded input receipt"}')
    sha = commit(repo, [str(p.relative_to(repo)) for p in (obj, sidecar)], "fixture cache payload")
    monkeypatch.setattr(lc, "ROOT", repo)
    monkeypatch.delenv("BFME_CYCLE_EXPECTED_SEMANTIC", raising=False)
    # Only the generated-case-shim helper is inert; git archive/extraction and
    # all of export_snapshot's own admission checks run normally.
    monkeypatch.setattr(cycle_source, "command", lambda *a: [sys.executable, "-I", "-S", "-c", "pass"])
    snapshot = lc.export_snapshot(sha, tmp_path / "snapshots")
    imported = snapshot / obj.relative_to(repo)
    print("fresh exported snapshot imported cached object:", imported.exists())
    assert not imported.exists(), "fresh measurement starts with contributor-supplied cached COFF"


def test_snapshot_build_symlink_must_not_reuse_external_cache(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    initialize(repo)
    external = tmp_path / "external-cache"
    external.mkdir()
    (external / "poison.obj").write_bytes(b"external cache, not part of git archive")
    (repo / "build").symlink_to(external, target_is_directory=True)
    sha = commit(repo, ["build"], "fixture external build cache")
    monkeypatch.setattr(lc, "ROOT", repo)
    monkeypatch.delenv("BFME_CYCLE_EXPECTED_SEMANTIC", raising=False)
    monkeypatch.setattr(cycle_source, "command", lambda *a: [sys.executable, "-I", "-S", "-c", "pass"])
    snapshot = lc.export_snapshot(sha, tmp_path / "snapshots")
    print("snapshot build resolves outside export:", (snapshot / "build").resolve())
    assert not (snapshot / "build").is_symlink(), "immutable export reuses an external mutable build tree"


def test_preseeded_object_has_no_source_to_object_proof(tmp_path, monkeypatch):
    root = tmp_path / "repository"
    initialize(root)
    source = root / "game/f.cpp"
    source.parent.mkdir(parents=True)
    source.write_text("int f() { return 2; }\n")
    obj = root / "build/match/game_f.obj"
    obj.parent.mkdir(parents=True)
    lc.write_coff(obj, [(".text", 0x60101020, b"\xb8\x01\0\0\0\xc3", 2)], [("_f", 1, 0, lc.EXTERNAL)])
    monkeypatch.setattr(build, "ROOT", root)
    monkeypatch.setattr(lc, "ROOT", root)
    monkeypatch.setattr(census, "ROOT", root)
    command, environment = ["inert-compiler", "-c"], {}
    # Native compiler discovery is replaced; no successful compile is claimed
    # by this test. The object returns 1; the source says 2.
    monkeypatch.setattr(build, "compiler_command", lambda *a: (command, environment))
    monkeypatch.setattr(build, "_cmd_fingerprint", lambda *a: "synthetic-command")
    inventory = build.search_inventory(source, command, environment)
    build._write_deps_sidecar(source, obj, "synthetic-command", "", True, command, environment, inventory, [])
    sha = commit(root, ["game/f.cpp", "build/match/game_f.obj", "build/match/game_f.deps.json"],
                 "fixture input-only cache certificate")
    monkeypatch.delenv("BFME_CYCLE_EXPECTED_SEMANTIC", raising=False)
    monkeypatch.setattr(cycle_source, "command", lambda *a: [sys.executable, "-I", "-S", "-c", "pass"])
    root = lc.export_snapshot(sha, tmp_path / "snapshots")
    source, obj = root / "game/f.cpp", root / "build/match/game_f.obj"
    for module in (build, lc, census):
        monkeypatch.setattr(module, "ROOT", root)
    monkeypatch.setattr(census, "_object_sources", lambda rows: {obj: source})
    out = root / "build/link_cycle"
    out.mkdir()
    accepted = build.compile_is_current(source, obj)
    assert not accepted, "input-only sidecar certifies arbitrary COFF without a witnessed compile"
    # The corrected export strips the object, so provenance must refuse it too.
    with pytest.raises(SystemExit, match="not current"):
        lc.provenance([], [obj], lc.Objects([obj]), out, receipts=None)


def test_shadow_must_not_select_a_root_changed_since_measurement(tmp_path, monkeypatch):
    """A still-fresh ancestor bundle must not prove today's work is still broken."""
    import pickle
    from types import SimpleNamespace
    import router_shadow as shadow
    import cycle_artifacts as ca

    initialize(tmp_path)
    source = tmp_path / "game/root.cpp"
    source.parent.mkdir()
    source.write_text("int root() { return 2; }\n")
    ledger = tmp_path / "targets/game/reverse/functions.csv"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("name,source,status,target_rva,target_size,notes\n"
                      "root,game/root.cpp,matched,0x00060000,6,\n")
    old = commit(tmp_path, ["game/root.cpp", "targets/game/reverse/functions.csv"], "before repair")
    source.write_text("int root() { return 1; }\n")
    new = commit(tmp_path, ["game/root.cpp"], "retail-equivalent repair")
    git(tmp_path, "update-ref", "refs/remotes/origin/master", new)
    assert ca.ancestry(old, tmp_path)[:2] == (True, 1)
    view = {"items": [{"target_rva": "0x00060000", "function": "root", "source": "game/root.cpp",
                       "conditional_gain_bytes": 6}], "proof": {"0x00060000": 6}, "joint_only": {},
            "status": [{"retail_rva": "0x00060000", "name": "root", "source": "game/root.cpp",
                        "placed": "1", "self_strict": "0", "closed_strict": "0"}],
            "metadata": {"authoritative": True, "commit": old, "freshness": {"behind": 1}}}
    index = tmp_path / "index.pkl"
    index.write_bytes(pickle.dumps({"meta": {"commit": old}, "objects": [], "blockers": {},
                                   "comdat": {}, "strong": {}}))
    monkeypatch.setattr(shadow, "ROOT", tmp_path)
    # An unchanged, fresh, signed ancestor bundle is allowed by the owner policy.
    # Stub only its transport, remote leases and the unrelated legacy selector.
    monkeypatch.setattr(shadow, "bundle_view", lambda path: view)
    monkeypatch.setattr(shadow, "claim_snapshot", lambda: ({}, {"status": "remote-read-only"}))
    monkeypatch.setattr(shadow, "old_choice", lambda *a: None)
    monkeypatch.setattr(shadow.link_check, "queue_rows", lambda *a: [])
    monkeypatch.setattr(shadow.comdat, "source_intervals", lambda *a: {})
    for name in ("busy_rvas", "recent_run_rvas", "unlocked_rvas"):
        monkeypatch.setattr(shadow.eligibility, name, lambda *a: set())
    for name in ("latest_verdicts", "attempt_counts"):
        monkeypatch.setattr(shadow.eligibility, name, lambda *a: {})
    monkeypatch.setattr(shadow.eligibility.re_log, "latest_records", lambda: {})
    output = tmp_path / "shadow.jsonl"
    records = shadow.run(SimpleNamespace(output=output, bundle=tmp_path, index=index, donors=None,
                                        count=1, lanes=["closure"]))
    record = records[0]
    print(json.dumps({"old_commit": old, "current_commit": new, "choice": record["new_choice"],
                      "violations": record["violations"]}))
    assert record["new_choice"] is None, "already-repaired root is proposed without a stale-work violation"


def test_control_changed_transitive_header_invalidates_cache(tmp_path, monkeypatch):
    from test_build_include_inventory import _fixture
    source, obj, _, header, _, _ = _fixture(tmp_path, monkeypatch)
    assert build.compile_is_current(source, obj)
    header.write_text("#define PACKET_RANGE 99\n")
    assert not build.compile_is_current(source, obj)


def test_control_baseline_growth_requires_repair_not_a_trailer(monkeypatch):
    path = "targets/game/reverse/full_gate_baseline.txt"
    monkeypatch.setattr(protected_paths, "blob", lambda revision, _: "old\n" if revision == "old" else "old\nnew\n")
    assert protected_paths.growth(["old"], "new", {path}, {path}) == [(path, ["new"])]
