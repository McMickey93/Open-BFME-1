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
from cycle_fixture import NOW, bundle, measured_run, rehash, rewrite_manifest, save_receipt
import closure_report as cr
import cycle_artifacts as ca
import link_cycle as lc
import link_cycle_context as context
import publish_cycle as pc


@pytest.fixture
def frozen(tmp_path):
    return bundle(tmp_path)


def test_deterministic_bundle_bytes(tmp_path):
    run, _ = measured_run(tmp_path / "run")
    a = bundle(tmp_path / "a", run=run, first=True)
    b = bundle(tmp_path / "b", run=run, first=True)
    assert {p.name: p.read_bytes() for p in a.iterdir()} == {p.name: p.read_bytes() for p in b.iterdir()}
    assert set(p.name for p in a.iterdir()) == set(ca.MEMBERS + (ca.MANIFEST, ca.CYCLE_DIFF))
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
        pc.make_bundle(run, tmp_path / "out", "test", local_unpublished=True)


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
            ca.serve(frozen, local_unpublished=True, now=NOW + offset)
        assert e.value.reason == reason
    else:
        b, fr, _ = ca.serve(frozen, local_unpublished=True, now=NOW + offset)
        assert fr["rules_match"] is True and b.authoritative is False


def test_stale_override_does_not_override_future(frozen):
    _, fr, lines = ca.serve(frozen, local_unpublished=True, allow_stale=True, now=NOW + 90000)
    assert fr["stale"] and any(line.startswith("STALE") for line in lines)
    with pytest.raises(ca.BundleError):
        ca.serve(frozen, local_unpublished=True, allow_stale=True, now=NOW - 601)


def test_local_unpublished_never_authoritative_in_any_api(frozen, tmp_path, monkeypatch):
    assert ca.validate(frozen)["authoritative"] is False
    b, fr, lines = ca.serve(frozen, local_unpublished=True, now=NOW)
    b.evidence = {"immutable": True, "author": {"login": "test", "id": 1}}
    assert b.authoritative is False and b.authenticated is False
    assert fr["authenticated"] is False and fr["authoritative"] is False
    assert any("UNAUTHENTICATED" in line for line in lines)
    # Even a configured future allowlist and fabricated evidence cannot promote LOCAL.
    monkeypatch.setattr(ca, "PUBLISHERS", ({"login": "test", "id": 1},))
    with pytest.raises(ca.Refused) as e:
        ca.authenticate_local(b)
    assert e.value.reason == "unauthenticated"
    store = tmp_path / "store"
    m, pointer = ca.install_local(frozen, store, local_unpublished=True)
    assert not m["authenticated"] and pointer["latest_measurement"] is None
    assert pointer["latest_closure_ready"] is None
    status = ca.status(store, out=io.StringIO())
    assert all(not e["authoritative"] and not e["authenticated"] for e in status["bundles"])
    with pytest.raises(ca.Refused):
        ca.serve(store, now=NOW)
    assert ca.serve(store, local_unpublished=True, now=NOW)[0].authoritative is False


class NoNetwork:
    def run(self, *a, **kw):
        pytest.fail("deferred trust must refuse before network")
    json = run


@pytest.mark.parametrize("dry_run", [False, True])
def test_empty_allowlist_and_no_default_repo_refuse(frozen, tmp_path, dry_run):
    assert ca.PUBLISHERS == () and ca.DEFAULT_REPO is None
    assert ca.release_trust({}) == "publisher trust not configured"
    with pytest.raises(ca.Refused, match="publisher trust not configured") as e:
        ca.fetch("test/repo", tmp_path / "store", gh=NoNetwork())
    assert ca.exit_code(e.value) == 6
    with pytest.raises(ca.Refused, match="publisher trust not configured"):
        pc.publish(frozen, "test/repo", gh=NoNetwork(), dry_run=dry_run)
    assert not (tmp_path / "store").exists()


def test_unavailable_rank_is_explicit_and_not_empty_success(frozen):
    b = ca.load_bundle(frozen)
    doc = ca.read_json(b.rank_json)
    assert doc["status"] == "unavailable" and "typed DIR32" in doc["reason"]
    assert "addresses" not in doc
    with pytest.raises(ca.Unavailable):
        b.data_back_rank()
    with pytest.raises(ca.Unavailable):
        ca.serve(frozen, local_unpublished=True, need_rank=True, now=NOW)
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
    ca.install_local(a, store, local_unpublished=True)
    resolved, _ = ca.resolve(store, local_unpublished=True)
    old_bytes = (resolved / ca.RECEIPT).read_bytes()
    # Different and duplicate writers serialize. Every writer sees complete dirs.
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda d: ca.install_local(d, store, local_unpublished=True), [a, b, a, b, a, b]))
    assert len(results) == 6
    doc = ca.read_pointer(store)
    assert len(doc["bundles"]) == 2
    assert doc["bundles"][0]["commit"] == "b" * 40
    assert (resolved / ca.RECEIPT).read_bytes() == old_bytes
    assert not list(store.glob(".partial-*"))
    assert ca.resolve(store, local_unpublished=True)[0] != resolved
    ca.validate(resolved)


def test_local_install_requires_flag_and_never_replaces(frozen, tmp_path):
    store = tmp_path / "store"
    with pytest.raises(ca.Refused):
        ca.install_local(frozen, store)
    ca.install_local(frozen, store, local_unpublished=True)
    before = (store / ca.POINTER).read_bytes()
    rewrite_manifest(frozen, lambda m: m.update(producer="other producer"))
    with pytest.raises(ca.BundleError, match="immutable installed manifest"):
        ca.install_local(frozen, store, local_unpublished=True)
    assert (store / ca.POINTER).read_bytes() == before


def test_pointer_read_once_during_refresh(frozen, tmp_path, monkeypatch):
    store = tmp_path / "store"
    ca.install_local(frozen, store, local_unpublished=True)
    original = ca.read_pointer
    calls = []
    def read_once(path):
        calls.append(path)
        doc = original(path)
        (Path(path) / ca.POINTER).write_text("corrupt future pointer")
        return doc
    monkeypatch.setattr(ca, "read_pointer", read_once)
    b, _, _ = ca.serve(store, local_unpublished=True, now=NOW)
    assert b.commit == "a" * 40 and len(calls) == 1


def test_failure_reasons_and_exit_codes(frozen, tmp_path):
    assert ca.EXIT == {"corrupt": 1, "unavailable": 2, "empty": 3, "stale": 4,
                       "incompatible-rules": 5, "unauthenticated": 6, "no-closure-report": 7}
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
        ca.serve(frozen, need_closure=True, local_unpublished=True)
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
    _, fr, lines = ca.serve(frozen, local_unpublished=True, now=NOW, root=root)
    assert fr["rules_match"] is True and fr["tool_digest_matches"] is False
    assert any(line.startswith("WARNING: tool digest") for line in lines)
    p = root / "tools/build.py"
    p.write_bytes(p.read_bytes() + b"\n# semantic provider changed\n")
    with pytest.raises(ca.Refused) as e:
        ca.serve(frozen, local_unpublished=True, now=NOW, root=root)
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


class SyntheticRelease:
    """In-memory GitHub transport; no external account or service."""
    def __init__(self, directory):
        self.files = {p.name: p.read_bytes() for p in directory.iterdir()}
        manifest = ca.read_json(directory / ca.MANIFEST)
        self.commit, self.tag = manifest["commit"], manifest["tag"]
        self.release = {"id": 37, "tag_name": self.tag, "draft": False, "prerelease": True,
                        "immutable": True, "author": {"login": "synthetic-bfme1", "id": 37},
                        "target_commitish": self.commit,
                        "assets": [{"name": n, "state": "uploaded", "size": len(raw),
                                    "digest": "sha256:" + ca.hashlib.sha256(raw).hexdigest()}
                                   for n, raw in sorted(self.files.items())]}
        self.tag_target = self.commit

    def run(self, args):
        if args[:2] == ["release", "download"]:
            dest = Path(args[args.index("--dir") + 1])
            for n, raw in self.files.items():
                (dest / n).write_bytes(raw)
            return ""
        if args[:2] == ["release", "verify"]:
            return "verified"
        raise AssertionError(args)

    def json(self, args):
        if args[:4] == ["api", "--paginate", "--slurp", "repos/synthetic/repo/releases?per_page=100"]:
            return [[self.release]]
        if args[0] == "api" and "/git/ref/tags/" in args[1]:
            return {"object": {"type": "commit", "sha": self.tag_target}}
        raise AssertionError(args)


@pytest.fixture
def synthetic_release(frozen, monkeypatch):
    # Only tests can configure trust. The production allowlist stays empty.
    monkeypatch.setattr(ca, "PUBLISHERS", ({"login": "synthetic-bfme1", "id": 37},))
    rewrite_manifest(frozen, lambda m: m.update(publication="release"))
    return SyntheticRelease(frozen)


def test_dormant_authentication_code_path(tmp_path, synthetic_release):
    gh = synthetic_release
    store = tmp_path / "store"
    m, _, pointer = ca.fetch("synthetic/repo", store, gh=gh, now=NOW)
    b, fr, _ = ca.serve(store, now=NOW)
    assert b.authenticated and b.authoritative
    assert pointer["latest_measurement"] == ca.bundle_id(m["tag"])
    assert fr["authenticated"] and fr["authoritative"]
    assert ca.authenticate_local(b)["author"]["id"] == 37
    # A changed authenticated manifest is no longer evidence-backed, even if
    # the edit leaves the self-consistent member/receipt identities untouched.
    rewrite_manifest(b.dir, lambda m: m.update(producer="forged label"))
    with pytest.raises(ca.Refused) as e:
        ca.serve(b.dir, now=NOW)
    assert e.value.reason == "unauthenticated"


@pytest.mark.parametrize("attack,reason", [("author", "unauthenticated"), ("mutable", "unauthenticated"),
    ("tag", "unauthenticated"), ("target", "unauthenticated"), ("digest", "corrupt"),
    ("no-digest", "unauthenticated"), ("size", "corrupt"), ("extra", "corrupt"),
    ("duplicate", "corrupt"), ("local", "unauthenticated")])
def test_release_authentication_rejections_leave_no_install(tmp_path, synthetic_release, attack, reason):
    gh = synthetic_release
    r = gh.release
    if attack == "author":
        r["author"]["id"] += 1
    elif attack == "mutable":
        r["immutable"] = False
    elif attack == "tag":
        gh.tag_target = "b" * 40
    elif attack == "target":
        r["target_commitish"] = "b" * 40
    elif attack in ("digest", "no-digest"):
        r["assets"][0]["digest"] = "sha256:" + "0" * 64 if attack == "digest" else None
    elif attack == "size":
        r["assets"][0]["size"] += 1
    elif attack == "extra":
        gh.files["extra"] = b"extra"
    elif attack == "duplicate":
        r["assets"].append(copy.deepcopy(r["assets"][0]))
    else:
        manifest = json.loads(gh.files[ca.MANIFEST])
        manifest["publication"] = "local-unpublished"
        raw = ca.dumps(manifest).encode()
        gh.files[ca.MANIFEST] = raw
        a = next(a for a in r["assets"] if a["name"] == ca.MANIFEST)
        a.update(size=len(raw), digest="sha256:" + ca.hashlib.sha256(raw).hexdigest())
    store = tmp_path / "store"
    with pytest.raises(ca.Problem) as e:
        ca.install(gh, "synthetic/repo", r, store, now=NOW)
    assert e.value.reason == reason
    assert not (store / ca.bundle_id(gh.tag)).exists()
    assert not list(store.glob(".partial-*"))


def test_mutable_test_install_stays_unauthenticated(tmp_path, synthetic_release):
    gh = synthetic_release
    gh.release["immutable"] = False
    store = tmp_path / "store"
    m = ca.install(gh, "synthetic/repo", gh.release, store, allow_mutable=True, now=NOW)
    b = ca.load_bundle(store / ca.bundle_id(m["tag"]) / "bundle")
    assert b.authenticated is False and b.authoritative is False
    with pytest.raises(ca.Refused):
        ca.serve(b.dir, now=NOW)


@pytest.mark.parametrize("contents", [[], {"assets": []}, {"schema": ca.EVIDENCE_SCHEMA, "assets": {"bad": []}}])
def test_malformed_evidence_refuses(tmp_path, synthetic_release, contents):
    gh = synthetic_release
    store = tmp_path / "store"
    m = ca.install(gh, "synthetic/repo", gh.release, store, now=NOW)
    d = store / ca.bundle_id(m["tag"])
    (d / ca.EVIDENCE).write_text(ca.dumps(contents))
    b = ca.load_bundle(d / "bundle")
    assert b.authenticated is False
    with pytest.raises(ca.Refused):
        ca.authenticate_local(b)


def test_legacy_presplit_rules_require_a_new_measurement(tmp_path):
    run, r = measured_run(tmp_path / "run")
    r["rule_identity"].pop("measurement_files")
    r["rule_identity"]["implementation_sha256"] = context.digest(r["tool_dependencies"])
    save_receipt(run, r)
    with pytest.raises(ca.Refused) as e:
        pc.validate_run(run, local_unpublished=True)
    assert e.value.reason == "incompatible-rules"


def test_ancestry_is_informational(frozen, monkeypatch):
    monkeypatch.setattr(ca, "ancestry", lambda *a: (False, None, "not an ancestor"))
    b, fr, _ = ca.serve(frozen, local_unpublished=True, now=NOW)
    assert fr["ancestor"] is False and not b.authoritative


def test_unknown_local_rules_never_served(frozen, tmp_path):
    with pytest.raises(ca.Refused) as e:
        ca.serve(frozen, local_unpublished=True, root=tmp_path / "no-tools", now=NOW)
    assert e.value.reason == "incompatible-rules"


def test_closure_selection_respects_five_older_limit():
    mine = ca.local_rules()
    bad = dict(mine, id="other-rule")
    entries = [{"id": str(i), "closure_report": True, "authenticated": True, "rules_tuple": bad}
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
