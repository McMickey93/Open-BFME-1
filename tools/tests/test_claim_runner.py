"""Manual claim runner: strict inputs, trusted context, real local Git fencing."""
import json
import shlex
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import claim_runner
import claims
from test_claims import hosts, _git

OWNER = "github:example:bfme1:cpp-loop-1"


def inputs(**overrides):
    return {"GITHUB_ACTOR": "Example", "GITHUB_TRIGGERING_ACTOR": "Example",
            "CLAIM_ACTION": "claim", "CLAIM_SEAT": "cpp-loop-1",
            "CLAIM_RVAS": "0x00000100", "CLAIM_TOKENS": "", **overrides}


def test_inputs_derive_owner_and_normalize_only_valid_rvas():
    assert claim_runner.request(inputs(CLAIM_RVAS="0x00000aBc, 0x00000100")) == (
        "claim", [0x100, 0xABC], OWNER, {})


@pytest.mark.parametrize("values", [
    {"CLAIM_ACTION": "prune"}, {"CLAIM_ACTION": "claim; echo injected"},
    {"CLAIM_SEAT": "../other"}, {"CLAIM_SEAT": "seat\nother"},
    {"CLAIM_SEAT": "a" * 33}, {"GITHUB_TRIGGERING_ACTOR": "AnotherWriter"},
    {"CLAIM_RVAS": ""}, {"CLAIM_RVAS": "0x00000000"},
    {"CLAIM_RVAS": "0x00000100 0x00000100"},
    {"CLAIM_RVAS": "0x00000100; curl attacker"},
    {"CLAIM_RVAS": "refs/heads/master"}, {"CLAIM_RVAS": "0x100"},
    {"CLAIM_RVAS": " ".join(f"0x{i:08X}" for i in range(1, 7))},
    {"CLAIM_TOKENS": "{}"},
])
def test_invalid_input_is_rejected(values):
    with pytest.raises(ValueError):
        claim_runner.request(inputs(**values))


@pytest.mark.parametrize("action", ["renew", "release"])
def test_mutations_require_exact_token_map(action):
    token = "a" * 40
    env = inputs(CLAIM_ACTION=action, CLAIM_TOKENS=json.dumps({"0x00000100": token}))
    assert claim_runner.request(env) == (action, [0x100], OWNER, {0x100: token})
    for bad in ("", "[]", "{}", '{"0x00000100":"short"}',
                '{"0x00000100":42}', json.dumps({"0x00000200": token}),
                '{"0x00000100":"' + token + '","0x00000100":"' + token + '"}'):
        with pytest.raises(ValueError):
            claim_runner.request({**env, "CLAIM_TOKENS": bad})


def context(**changes):
    return {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_REPOSITORY": claim_runner.REPOSITORY, "GITHUB_REF": "refs/heads/master",
            "GITHUB_SHA": "a" * 40, "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1",
            **changes}


@pytest.mark.parametrize("changes", [
    {"GITHUB_ACTIONS": "false"}, {"GITHUB_EVENT_NAME": "pull_request"},
    {"GITHUB_REPOSITORY": "other/fork"}, {"GITHUB_REF": "refs/heads/topic"},
])
def test_nonofficial_or_nondispatch_context_never_reaches_git(monkeypatch, changes):
    monkeypatch.setattr(claim_runner, "git", lambda *a: pytest.fail("unexpected Git access"))
    with pytest.raises(ValueError):
        claim_runner.runtime_context(context(**changes))


def test_context_requires_checked_out_commit_official_origin_hooks_and_clean_tree(monkeypatch, tmp_path):
    hook = tmp_path / ".githooks/pre-push"
    hook.parent.mkdir()
    hook.write_text("#!/bin/sh\nexit 0\n")
    hook.chmod(0o755)
    replies = {("rev-parse", "HEAD"): "a" * 40,
               ("remote", "get-url", "origin"): "https://github.com/Open-BFME/Open-BFME-1",
               ("config", "--get", "core.hooksPath"): ".githooks",
               ("status", "--porcelain", "--untracked-files=no"): ""}
    monkeypatch.setattr(claim_runner, "git", lambda root, *args: replies[args])
    assert claim_runner.runtime_context(context(), tmp_path)["commit"] == "a" * 40
    for key, wrong in [(('rev-parse', 'HEAD'), "b" * 40),
                       (('remote', 'get-url', 'origin'), "https://github.com/other/fork"),
                       (('config', '--get', 'core.hooksPath'), "/dev/null"),
                       (('status', '--porcelain', '--untracked-files=no'), " M tools/claims.py")]:
        old, replies[key] = replies[key], wrong
        with pytest.raises(ValueError):
            claim_runner.runtime_context(context(), tmp_path)
        replies[key] = old


def install_recording_hook(root):
    hooks = root / ".githooks"
    hooks.mkdir()
    actual = TOOLS.parent / ".githooks/pre-push"
    hook = hooks / "pre-push"
    hook.write_text("#!/bin/sh\necho run >> hook-runs\nexec " + shlex.quote(str(actual)) + ' "$@"\n')
    hook.chmod(0o755)


def tokens_of(report):
    return {int(entry["rva"], 16): entry["token"] for entry in report["held"]}


def test_real_claim_renew_release_uses_normal_hooks_and_keeps_master_untouched(hosts):
    root = hosts("a")
    install_recording_hook(root)
    _git(root, "commit", "-q", "--allow-empty", "-m", "fixture master")
    _git(root, "push", "-q", "origin", "HEAD:master")
    master = _git(hosts.origin, "rev-parse", "refs/heads/master").strip()
    result = claim_runner.operate("claim", [0x100, 0x200], OWNER, {}, root)
    assert result["complete"] and len(result["held"]) == 2
    first = tokens_of(result)
    for entry in result["held"]:
        assert entry["ref"] == f"refs/heads/claims/{entry['rva']}"
        assert _git(root, "rev-list", "--parents", "-1", entry["token"]).strip() == entry["token"]
        assert _git(root, "ls-tree", entry["token"]) == ""
    renewed = claim_runner.operate("renew", [0x100, 0x200], OWNER, first, root)
    assert renewed["complete"]
    assert [x["lease"] for x in result["held"]] == [x["lease"] for x in renewed["held"]]
    assert tokens_of(renewed) != first
    assert not claim_runner.operate("release", [0x100, 0x200], OWNER, first, root)["complete"]
    released = claim_runner.operate("release", [0x100, 0x200], OWNER, tokens_of(renewed), root)
    assert released["complete"] and released["released"] == ["0x00000100", "0x00000200"]
    assert _git(hosts.origin, "rev-parse", "refs/heads/master").strip() == master
    assert len((root / "hook-runs").read_text().splitlines()) >= 3


def test_repeated_claim_preserves_live_lease_and_requires_explicit_renew(hosts):
    root = hosts("a")
    first = claim_runner.operate("claim", [0x100], OWNER, {}, root)
    before = _git(hosts.origin, "for-each-ref", "--format=%(refname) %(objectname)")
    again = claim_runner.operate("claim", [0x100, 0x200], OWNER, {}, root)
    assert not again["complete"] and again["held"] == []
    assert "renew" in again["reason"]
    assert _git(hosts.origin, "for-each-ref", "--format=%(refname) %(objectname)") == before


@pytest.mark.parametrize("action", ["claim", "renew", "release"])
def test_another_seat_cannot_modify_a_live_claim_even_with_its_public_token(hosts, action):
    root = hosts("a")
    first = claim_runner.operate("claim", [0x100], OWNER, {}, root)
    before = _git(hosts.origin, "for-each-ref", "--format=%(refname) %(objectname)")
    other = hosts("b")
    result = claim_runner.operate(action, [0x100], "github:other:bfme1:cpp-loop-1",
                                  {} if action == "claim" else tokens_of(first), other)
    assert not result["complete"] and result["refused"] == ["0x00000100"]
    assert _git(hosts.origin, "for-each-ref", "--format=%(refname) %(objectname)") == before


@pytest.mark.parametrize("action", ["renew", "release"])
def test_runner_never_migrates_or_deletes_a_legacy_ref(hosts, action):
    root = hosts("a")
    token = claims._record(OWNER, 4, root=root)
    _git(root, "push", "-q", "origin", f"{token}:refs/claims/0x00000100")
    before = _git(hosts.origin, "for-each-ref", "--format=%(refname) %(objectname)")
    result = claim_runner.operate(action, [0x100], OWNER, {0x100: token}, root)
    assert not result["complete"]
    assert _git(hosts.origin, "for-each-ref", "--format=%(refname) %(objectname)") == before


def test_claim_write_rejected_by_hook_is_not_reported_successful(hosts):
    root = hosts("a")
    hooks = root / ".githooks"
    hooks.mkdir()
    hook = hooks / "pre-push"
    hook.write_text("#!/bin/sh\nexit 7\n")
    hook.chmod(0o755)
    with pytest.raises(claims.ClaimsUnavailable):
        claim_runner.operate("claim", [0x100], OWNER, {}, root)
    assert _git(hosts.origin, "for-each-ref", "--format=%(refname)") == ""


def test_invalid_job_context_cannot_call_claims_and_never_exports_auth(monkeypatch, tmp_path):
    monkeypatch.setattr(claim_runner, "ROOT", tmp_path)
    monkeypatch.setattr(claim_runner, "operate", lambda *a: pytest.fail("unexpected claim operation"))
    monkeypatch.setattr(claim_runner, "runtime_context", lambda *a: (_ for _ in ()).throw(ValueError("bad context")))
    for key, value in inputs().items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("GITHUB_TOKEN", "fixture-secret-never-export")
    assert claim_runner.main() == 1
    report = (tmp_path / claim_runner.OUTPUT).read_text()
    assert "fixture-secret" not in report
    assert json.loads(report) == {"schema_version": 1, "complete": False, "error": "bad context"}
