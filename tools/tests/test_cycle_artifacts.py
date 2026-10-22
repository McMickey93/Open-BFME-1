"""BFME1 bundle integrity/trust/freshness/store regression tests, synthetic only.

Acceptance cases adapted from BFME2 02518d74b1; no donor validity policy.
"""
import copy
import gzip
import io
import json
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cycle_fixture import synthetic_host, NOW, bundle, measured_run, rehash, rewrite_manifest, save_receipt
import closure_report as cr
import cycle_artifacts as ca
import link_cycle as lc
import link_cycle_context as context
import publish_cycle as pc


REAL_ANCESTRY = ca.ancestry


@pytest.fixture(autouse=True)
def reader_context(monkeypatch):
    # Unit tests use synthetic commits; actual git ancestry is exercised below.
    monkeypatch.setattr(ca, "ancestry", lambda *a: (True, 0, "synthetic ancestor"))
    monkeypatch.setattr(ca.time, "time", lambda: NOW)


@pytest.fixture
def frozen(tmp_path):
    return bundle(tmp_path)


def test_deterministic_bundle_bytes(tmp_path):
    run, _ = measured_run(tmp_path / "run")
    a = bundle(tmp_path / "a", run=run, first=True)
    b = bundle(tmp_path / "b", run=run, first=True)
    assert {p.name: p.read_bytes() for p in a.iterdir()} == {p.name: p.read_bytes() for p in b.iterdir()}
    assert set(p.name for p in a.iterdir()) == set(ca.MEMBERS + (ca.MANIFEST, ca.CYCLE_DIFF, ca.cycle_stamp.STAMP))
    assert ca.SCHEMA != "link-cycle-bundle/2"
    for p in a.glob("*.gz"):
        assert p.read_bytes()[4:8] == b"\0" * 4
    assert not (tmp_path / "run" / cr.ROOTS).exists()  # Builder never mutates the run.


@pytest.mark.parametrize("name", ca.MEMBERS + (ca.MANIFEST, ca.CYCLE_DIFF))
@pytest.mark.parametrize("attack", ["tamper", "missing"])
def test_every_member_tampered_or_missing(tmp_path, name, attack):
    d = bundle(tmp_path, first=True)
    p = d / name
    if attack == "missing":
        p.unlink()
    else:
        raw = bytearray(p.read_bytes())
        raw[len(raw) // 2] ^= 1
        p.write_bytes(raw)
    with pytest.raises(ca.BundleError):
        ca.validate(d)


@pytest.mark.parametrize("name", ca.MEMBERS + (ca.CYCLE_DIFF,))
def test_member_replaced_and_manifest_rehashed(tmp_path, name):
    d = bundle(tmp_path, first=True)
    if name.endswith(".gz"):
        raw = ca.read_member(d / name) + b"altered"
        pc.gzip_bytes(raw, d / name)
    else:
        (d / name).write_text("{}\n")
    rehash(d, name)
    with pytest.raises(ca.Problem):
        ca.validate(d)


def test_replaced_manifest_and_unlisted_extra(frozen, tmp_path):
    original = (frozen / ca.MANIFEST).read_bytes()
    other_run, _ = measured_run(tmp_path / "other", commit="b" * 40)
    other = bundle(tmp_path / "other-bundle", run=other_run)
    (frozen / ca.MANIFEST).write_bytes((other / ca.MANIFEST).read_bytes())
    with pytest.raises(ca.BundleError):
        ca.validate(frozen)
    (frozen / ca.MANIFEST).write_bytes(original)
    (frozen / "extra.txt").write_text("extra")
    with pytest.raises(ca.BundleError, match="directory members"):
        ca.validate(frozen)


@pytest.mark.parametrize("field", ["commit", "rules", "binding", "tool_digest", "headline", "measured", "instance"])
def test_manifest_repetition_disagreement(frozen, field):
    rewrite_manifest(frozen, lambda m: m.update({field: {"forged": True}}))
    with pytest.raises(ca.BundleError):
        ca.validate(frozen)


@pytest.mark.parametrize("field", ["commit", "receipt_core_sha256", "receipt_sha256", "rule_identity",
                                   "link_status_sha256", "graph", "blockers", "link_cycle_tool_digest"])
def test_graph_report_digest_and_identity_mismatch(frozen, field):
    doc = ca.read_json(frozen / ca.CLOSURE_ROOTS)
    doc[field] = {"wrong": True}
    pc.gzip_bytes(ca.dumps(doc).encode(), frozen / ca.CLOSURE_ROOTS)
    rehash(frozen, ca.CLOSURE_ROOTS)
    with pytest.raises(ca.BundleError):
        ca.validate(frozen)


@pytest.mark.parametrize("field", ["retail_sha256", "inputs", "objects_digest", "rule_identity", "tool_digest"])
def test_receipt_provenance_cannot_be_changed_by_rehashing(frozen, field):
    receipt = ca.read_json(frozen / ca.RECEIPT)
    receipt[field] = "forged"
    (frozen / ca.RECEIPT).write_text(ca.dumps(receipt))
    rehash(frozen, ca.RECEIPT)
    with pytest.raises(ca.BundleError):
        ca.validate(frozen)


def test_missing_semantic_dependency_refused_even_with_restamped_core(tmp_path):
    run, receipt = measured_run(tmp_path / "run")
    del receipt["tool_dependencies"]["build.py"]
    receipt["rule_identity"] = context.rule_identity(receipt["tool_dependencies"])
    receipt["tool_digest"] = context.digest(receipt["tool_dependencies"])
    save_receipt(run, receipt)
    with pytest.raises(ca.BundleError, match="dependency"):
        pc.make_bundle(run, tmp_path / "out", "test")


def test_old_rules_are_incompatible_not_tool_warning(frozen):
    b = ca.load_bundle(frozen)
    r = copy.deepcopy(b.receipt)
    r["rules"] = r["rule_identity"]["id"] = "bfme1-old-rule"
    fr = ca.freshness(r, now=NOW)
    assert ca.refusal(fr)[0] == "incompatible-rules"
    assert ca.refusal(fr, allow_stale=True)[0] == "incompatible-rules"


@pytest.mark.parametrize("offset,reason", [(24 * 3600 + 1, "stale"), (-601, "corrupt"), (-600, None),
                                           (24 * 3600, None)])
def test_stale_future_and_exact_limits(frozen, offset, reason):
    if reason:
        with pytest.raises(ca.Problem) as e:
            ca.serve(frozen, now=NOW + offset)
        assert e.value.reason == reason
    else:
        b, fr, _ = ca.serve(frozen, now=NOW + offset)
        assert fr["rules_match"] is True and b.authoritative is True


def test_stale_override_does_not_override_future(frozen):
    b, fr, lines = ca.serve(frozen, allow_stale=True, now=NOW + 90000)
    assert not b.authoritative and not fr["authoritative"]
    assert fr["stale"] and any(line.startswith("STALE") for line in lines)
    with pytest.raises(ca.Refused) as exc:
        ca.serve(frozen, allow_stale=True, now=NOW - 601)
    assert (exc.value.reason, exc.value.sub_reason) == ("corrupt", "future")


def test_unavailable_rank_is_explicit_and_not_empty_success(frozen):
    b = ca.load_bundle(frozen)
    doc = ca.read_json(b.rank_json)
    assert doc["status"] == "unavailable" and "typed DIR32" in doc["reason"]
    assert "addresses" not in doc
    with pytest.raises(ca.Unavailable):
        b.data_back_rank()
    with pytest.raises(ca.Unavailable):
        ca.serve(frozen, need_rank=True, now=NOW)
    doc.update(status="available", addresses=[])
    (frozen / ca.RANK_JSON).write_text(ca.dumps(doc))
    rehash(frozen, ca.RANK_JSON)
    with pytest.raises(ca.BundleError):
        ca.validate(frozen)


def test_atomic_install_concurrent_writers_and_immutable_reader(tmp_path):
    a = bundle(tmp_path / "a")
    run, _ = measured_run(tmp_path / "b-run", now=NOW + 100, commit="b" * 40)
    b = bundle(tmp_path / "b", run=run)
    store = tmp_path / "store"
    ca.install_local(a, store)
    resolved, _ = ca.resolve(store)
    old_bytes = (resolved / ca.RECEIPT).read_bytes()
    # Different and duplicate writers serialize. Every writer sees complete dirs.
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda d: ca.install_local(d, store), [a, b, a, b, a, b]))
    assert len(results) == 6
    doc = ca.read_pointer(store)
    assert len(doc["bundles"]) == 2
    assert doc["bundles"][0]["commit"] == "b" * 40
    assert (resolved / ca.RECEIPT).read_bytes() == old_bytes
    assert not list(store.glob(".partial-*"))
    assert ca.resolve(store)[0] != resolved
    ca.validate(resolved)


def test_local_install_never_replaces(frozen, tmp_path):
    store = tmp_path / "store"
    ca.install_local(frozen, store)
    before = (store / ca.POINTER).read_bytes()
    rewrite_manifest(frozen, lambda m: m.update(producer="other producer"))
    with pytest.raises(ca.BundleError, match="immutable installed manifest"):
        ca.install_local(frozen, store)
    assert (store / ca.POINTER).read_bytes() == before


def test_pointer_read_once_during_refresh(frozen, tmp_path, monkeypatch):
    store = tmp_path / "store"
    ca.install_local(frozen, store)
    original = ca.read_pointer
    calls = []
    def read_once(path):
        calls.append(path)
        doc = original(path)
        (Path(path) / ca.POINTER).write_text("corrupt future pointer")
        return doc
    monkeypatch.setattr(ca, "read_pointer", read_once)
    b, _, _ = ca.serve(store, now=NOW)
    assert b.commit == "a" * 40 and len(calls) == 1


def test_failure_reasons_and_exit_codes(frozen, tmp_path):
    assert ca.EXIT == {"corrupt": 1, "unavailable": 2, "empty": 3, "stale": 4,
                       "incompatible-rules": 5, "not-authoritative": 6, "no-closure-report": 7}
    for reason, code in ca.EXIT.items():
        problem = ca.Refused("test", reason)
        assert ca.exit_code(problem) == code and f"[reason={reason}]" in ca.describe(problem)
    with pytest.raises(ca.Unavailable):
        ca.serve(tmp_path / "missing")
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ca.Empty):
        ca.serve(empty)
    # Required-member profile refuses a legacy bundle without reports with the
    # routing reason, while integrity validation still rejects the profile.
    rewrite_manifest(frozen, lambda m: [m["members"].pop(k) for k in (ca.CLOSURE_ROOTS, ca.CLOSURE_BLOCKERS)])
    with pytest.raises(ca.Refused) as e:
        ca.serve(frozen, need_closure=True)
    assert e.value.reason == "no-closure-report"
    with pytest.raises(ca.BundleError):
        ca.validate(frozen)


def test_empty_measurement_refuses(tmp_path):
    run, _ = measured_run(tmp_path / "run", empty=True)
    with pytest.raises(ca.Empty):
        bundle(tmp_path, run=run)


def test_semantic_change_refuses_unrelated_change_only_warns(frozen, tmp_path):
    root = tmp_path / "checkout"
    shutil.copytree(ca.ROOT / "tools", root / "tools", ignore=shutil.ignore_patterns("tests", "__pycache__"))
    assert ca.local_rules(root) == ca.local_rules()
    (root / "tools/fleet_unrelated.py").write_text("# daily fleet edit\n")
    _, fr, lines = ca.serve(frozen, now=NOW, root=root)
    assert fr["rules_match"] is True and fr["tool_digest_matches"] is False
    assert any(line.startswith("WARNING: tool digest") for line in lines)
    p = root / "tools/build.py"
    p.write_bytes(p.read_bytes() + b"\n# semantic provider changed\n")
    with pytest.raises(ca.Refused) as e:
        ca.serve(frozen, now=NOW, root=root)
    assert e.value.reason == "incompatible-rules"


def test_new_rules_old_report_cannot_be_rebound(tmp_path):
    run, receipt = measured_run(tmp_path / "run")
    roots, table, _ = cr.from_graph(run)
    (run / cr.ROOTS).write_bytes(roots)
    (run / cr.BLOCKERS).write_bytes(table)
    receipt["tool_dependencies"]["build.py"] = "f" * 64
    receipt["rule_identity"] = context.rule_identity(receipt["tool_dependencies"])
    receipt["tool_digest"] = context.digest(receipt["tool_dependencies"])
    save_receipt(run, receipt)
    with pytest.raises(ca.BundleError, match="closure report"):
        bundle(tmp_path, run=run)


@pytest.mark.parametrize("name", ca.MEMBERS + (ca.MANIFEST,))
def test_symlink_members_refused(frozen, tmp_path, name):
    path = frozen / name
    outside = tmp_path / ("outside-" + name)
    path.rename(outside)
    path.symlink_to(outside)
    with pytest.raises(ca.BundleError):
        ca.validate(frozen)


def test_legacy_presplit_rules_require_a_new_measurement(tmp_path):
    run, r = measured_run(tmp_path / "run")
    r["rule_identity"].pop("measurement_files")
    r["rule_identity"]["implementation_sha256"] = context.digest(r["tool_dependencies"])
    save_receipt(run, r)
    with pytest.raises(ca.Refused) as e:
        pc.validate_run(run)
    assert e.value.reason == "incompatible-rules"


def test_unknown_local_rules_never_served(frozen, tmp_path):
    with pytest.raises(ca.Refused) as e:
        ca.serve(frozen, root=tmp_path / "no-tools", now=NOW)
    assert e.value.reason == "incompatible-rules"


def test_closure_selection_respects_five_older_limit():
    mine = ca.local_rules()
    bad = dict(mine, id="other-rule")
    entries = [{"id": str(i), "closure_report": True, "rules_tuple": bad, "authoritative": True}
               for i in range(7)]
    doc = {"bundles": entries}
    entries[5]["rules_tuple"] = mine
    assert ca.closure_choice(doc) == ("5", True)
    entries[5]["rules_tuple"] = bad
    entries[6]["rules_tuple"] = mine
    assert ca.closure_choice(doc) == ("0", False)


def test_historical_dependency_set_is_incompatible_not_corrupt(tmp_path):
    _, r = measured_run(tmp_path / "run")
    # A historical semantic closure may differ, but must still digest exactly
    # its declared providers. Today's set is only a compatibility comparison.
    r["rule_identity"]["measurement_files"].remove("progress.py")
    r["rule_identity"]["implementation_sha256"] = context.digest({
        n: r["tool_dependencies"][n] for n in r["rule_identity"]["measurement_files"]})
    lc.stamp_cores(r)
    ca.check_receipt(r)
    assert ca.refusal(ca.freshness(r, now=NOW))[0] == "incompatible-rules"


def test_clean_local_run_accepted_through_bundle_store_and_status(frozen, tmp_path):
    # Neither a manifest nor a CLI switch needs to claim authority.
    assert "authoritative" not in ca.validate(frozen)
    rewrite_manifest(frozen, lambda m: m.update(authoritative=False))
    from cycle_fixture import host_stamp
    host_stamp(frozen, ca.cycle_stamp.configured_keys()[0])
    b, fr, lines = ca.serve(frozen, now=NOW)
    assert b.authoritative and fr["authoritative"]
    assert any("AUTHORITATIVE: clean local run" in line for line in lines)
    store = tmp_path / "store"
    m, pointer = ca.install_local(frozen, store, now=NOW)
    assert pointer["latest_measurement"] == ca.bundle_id(m["tag"])
    assert ca.serve(store, now=NOW)[0].authoritative
    doc = ca.status(store, now=NOW, out=io.StringIO())
    assert all(e["authoritative"] for e in doc["bundles"])


@pytest.mark.parametrize("attack,sub_reason", [
    ("dirty-start", "dirty-start"), ("dirty-end", "dirty-end"),
    ("allow_dirty", "diagnostic"), ("allow_stale_cache", "diagnostic"),
    ("measure_only", "diagnostic"), ("snapshot", "diagnostic"), ("remeasure", "diagnostic"),
    ("warm-stale", "diagnostic"), ("missing-start", "missing-evidence"),
    ("missing-end", "missing-evidence"), ("missing-options", "missing-evidence"),
    ("receipt-denies", "receipt-not-authoritative"), ("compile-failed", "compile-failed")])
def test_authority_claim_cannot_override_run_evidence(tmp_path, attack, sub_reason):
    run, r = measured_run(tmp_path / "run")
    if attack.startswith("dirty-"):
        r["checkout_" + attack.split("-")[1]]["dirty"] = True
    elif attack.startswith("missing-"):
        del r[{"missing-start": "checkout_start", "missing-end": "checkout_end",
               "missing-options": "run_options"}[attack]]
    elif attack == "receipt-denies":
        r["authoritative"] = False
    elif attack == "compile-failed":
        r["compile_failed"] = ["f.cpp"]
    elif attack == "warm-stale":
        r["warm_start"]["stale"] = True
    else:
        r["run_options"][attack] = True
    save_receipt(run, r)
    d = bundle(tmp_path, run=run)
    rewrite_manifest(d, lambda m: m.update(authoritative=True))
    assert not ca.load_bundle(d).authoritative
    with pytest.raises(ca.Refused) as exc:
        ca.serve(d, now=NOW)
    assert (exc.value.reason, exc.value.sub_reason) == ("not-authoritative", sub_reason)
    assert ca.exit_code(exc.value) == 6


def test_authority_and_store_pointer_claims_are_recomputed(frozen, tmp_path, monkeypatch):
    store = tmp_path / "store"
    ca.install_local(frozen, store, now=NOW)
    b = ca.serve(store, now=NOW)[0]
    # The pointer still claims authority after local origin/master changes.
    monkeypatch.setattr(ca, "ancestry", lambda *a: (False, None, "another line"))
    assert not b.authoritative
    with pytest.raises(ca.Refused) as exc:
        ca.serve(store, now=NOW)
    assert exc.value.sub_reason == "non-ancestor"
    doc = ca.status(store, now=NOW, out=io.StringIO())
    assert doc["latest_measurement"] is None
    assert not doc["bundles"][0]["authoritative"]


@pytest.mark.parametrize("condition,sub_reason", [("ancestor", None), ("non-ancestor", "non-ancestor"),
    ("unknown-commit", "ancestry-unknown"), ("missing-ref", "ancestry-unknown"),
    ("git-failed", "ancestry-unknown"), ("not-checkout", "ancestry-unknown")])
def test_actual_local_git_ancestry_required(tmp_path, monkeypatch, condition, sub_reason):
    import subprocess
    root = tmp_path / "repo"
    root.mkdir()
    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()
    git("init", "-q")
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", "first")
    first = git("rev-parse", "HEAD")
    git("update-ref", "refs/remotes/origin/master", first)
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", "second")
    second = git("rev-parse", "HEAD")
    assert REAL_ANCESTRY(first, root)[0] is True
    commit = first
    if condition == "non-ancestor":
        commit = second
    elif condition == "unknown-commit":
        commit = "f" * 40
    elif condition == "missing-ref":
        git("update-ref", "-d", "refs/remotes/origin/master")
    elif condition == "not-checkout":
        root = tmp_path
    elif condition == "git-failed":
        original = ca._git
        monkeypatch.setattr(ca, "_git", lambda root, *args: None if args[0] == "merge-base" else original(root, *args))
    run, _ = measured_run(tmp_path / "run", commit=commit)
    d = bundle(tmp_path, run=run)
    monkeypatch.setattr(ca, "ancestry", REAL_ANCESTRY)
    # Rules are checked from the consuming checkout; isolate git policy here.
    monkeypatch.setattr(ca, "local_rules", lambda *a: ca.rules_of(ca.read_json(d / ca.RECEIPT)))
    if condition == "ancestor":
        b, fr, _ = ca.serve(d, root=root, now=NOW)
        assert b.authoritative and fr["ancestor"] is True
        return
    with pytest.raises(ca.Refused) as exc:
        ca.serve(d, root=root, now=NOW)
    assert (exc.value.reason, exc.value.sub_reason) == ("not-authoritative", sub_reason)
    if condition == "unknown-commit":
        assert "git fetch origin" in str(exc.value)


def test_receipt_core_rejects_changed_cleanliness_without_restamping(tmp_path):
    run, r = measured_run(tmp_path / "run")
    r["checkout_end"]["dirty"] = True
    (run / ca.RECEIPT).write_text(ca.dumps(r))
    with pytest.raises(ca.BundleError, match="core_sha256"):
        bundle(tmp_path, run=run)


def test_removed_remote_trust_surface_has_no_remaining_references():
    import re
    names = ("link_cycle_context", "link_cycle", "closure_report", "cycle_artifacts",
             "publish_cycle", "cycle_diff", "data_back_rank", "repair_queue")
    # Grep the production surface; split removed tokens so this guard doesn't
    # itself reintroduce the obsolete API names into a repository text search.
    patterns = ("PUB" + "LISHERS", "publisher" + "_ok", "release" + "_trust", "release" + "_problem",
                "RELEASE" + "_TRUST", "--allow-" + "mutable", "unauth" + "enticated",
                "--local-" + "unpublished", r"\bGh(?:Error)?\b", r"\bgh\b", "Git" + "Hub",
                "authenticate" + "_local", "list_" + "releases", "tag_" + "commit",
                r"\brelease\b", r"\bpublishers?\b", r"\bauthenticat\w*\b")
    for name in names:
        source = (ca.ROOT / "tools" / (name + ".py")).read_text()
        for pattern in patterns:
            assert not re.search(pattern, source), (name, pattern)
    # Only the local lifecycle commands remain in either CLI.
    import ast
    for module, expected in ((ca, {"status", "install", "validate", "inspect"}),
                             (pc, {"validate", "bundle"})):
        tree = ast.parse(Path(module.__file__).read_text())
        commands = {node.args[0].value for node in ast.walk(tree) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute) and node.func.attr == "add_parser"}
        assert commands == expected


def test_loaded_bundle_rechecks_integrity_before_claiming_authority(frozen):
    b = ca.serve(frozen, now=NOW)[0]
    assert b.authoritative
    (frozen / ca.LINK_STATUS).write_bytes(b"changed after load")
    assert not b.authoritative


def test_diagnostic_store_pointer_cannot_promote_a_bundle(tmp_path):
    run, r = measured_run(tmp_path / "run")
    r["run_options"]["allow_stale_cache"] = True
    save_receipt(run, r)
    d = bundle(tmp_path, run=run)
    store = tmp_path / "store"
    _, pointer = ca.install_local(d, store, now=NOW)
    entry = pointer["bundles"][0]
    assert pointer["latest_measurement"] is None
    entry["authoritative"] = True
    pointer["latest_measurement"] = entry["id"]
    pointer["latest_closure_ready"] = entry["id"]
    (store / ca.POINTER).write_text(ca.dumps(pointer))
    for closure in (False, True):
        with pytest.raises(ca.Refused) as exc:
            ca.serve(store, need_closure=closure, now=NOW)
        assert (exc.value.reason, exc.value.sub_reason) == ("not-authoritative", "diagnostic")
