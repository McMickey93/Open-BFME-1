"""Shared claims as refs on origin (tools/claims.py), two hosts against a bare repo."""
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import claims  # noqa: E402


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


@pytest.fixture
def hosts(tmp_path, monkeypatch):
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", str(origin))
    clones = {}
    for name in ("a", "b"):
        clone = tmp_path / name
        _git(tmp_path, "init", "-q", str(clone))
        _git(clone, "remote", "add", "origin", str(origin))
        _git(clone, "config", "user.name", name)
        _git(clone, "config", "user.email", f"{name}@example.com")
        clones[name] = clone

    monkeypatch.delenv("BFME_RUN_ID", raising=False)

    def act(name):
        monkeypatch.setattr(claims, "ROOT", clones[name])
        monkeypatch.setenv("BFME_CLAIM_OWNER", name)
        claims.active.cache_clear()
        # never the real origin: every claim these tests push lands in the fixture
        assert Path(claims._git("remote", "get-url", "origin").stdout.strip()) == origin
        return clones[name]
    act.origin = origin
    return act


def test_a_claim_is_exclusive_across_hosts(hosts):
    hosts("a")
    assert claims.claim([0x100, 0x200]) == ([0x100, 0x200], [])
    hosts("b")
    assert set(claims.active()) == {0x100, 0x200}
    assert claims.claim([0x200, 0x300]) == ([0x300], [0x200])     # partial batch
    assert claims.active()[0x300]["owner"] == "b"


def _seen(root):
    """The claim snapshot refs a checkout holds, without fetching."""
    return set(claims._read_local(root))


def test_fetch_snapshots_are_private_to_each_worktree(hosts, tmp_path):
    # Ported from Open-BFME-2 542acb66c4: a shared refs/claims-seen/ mirror let
    # one worktree's fetch move another's refs (racing expected-old-SHA updates).
    primary = hosts("a")
    _git(primary, "commit", "-q", "--allow-empty", "-m", "worktree fixture")
    sibling = tmp_path / "sibling"
    _git(primary, "worktree", "add", "-q", "--detach", str(sibling), "HEAD")
    hosts("b")
    assert claims.claim([0x100]) == ([0x100], [])
    assert claims.fetch(primary) and _seen(primary) == {0x100}
    assert claims.fetch(sibling) and _seen(sibling) == {0x100}
    assert claims.claim([0x200]) == ([0x200], [])
    assert claims.fetch(primary) and _seen(primary) == {0x100, 0x200}
    assert _seen(sibling) == {0x100}                     # untouched by the primary's fetch
    assert claims.fetch(sibling) and _seen(sibling) == {0x100, 0x200}
    assert claims.release([0x100]) == [0x100]
    assert claims.fetch(primary) and _seen(primary) == {0x200}
    assert _seen(sibling) == {0x100, 0x200}
    assert claims.fetch(sibling) and _seen(sibling) == {0x200}


def test_worktrees_still_contend_for_the_same_remote_claim(hosts, tmp_path):
    primary = hosts("a")
    _git(primary, "commit", "-q", "--allow-empty", "-m", "worktree fixture")
    sibling = tmp_path / "sibling"
    _git(primary, "worktree", "add", "-q", "--detach", str(sibling), "HEAD")
    assert claims.claim([0x100], root=primary, who="primary") == ([0x100], [])
    assert claims.claim([0x100], root=sibling, who="sibling") == ([], [0x100])
    claims.active.cache_clear()
    assert claims.active(sibling)[0x100]["owner"] == "primary"


def test_claim_fetch_does_not_fetch_submodules(hosts, tmp_path):
    primary = hosts("a")
    dependency = tmp_path / "dependency"
    dependency.mkdir()
    _git(dependency, "init", "-q")
    _git(dependency, "-c", "user.name=fixture", "-c", "user.email=fixture@example.com",
         "commit", "-q", "--allow-empty", "-m", "dependency fixture")
    _git(primary, "-c", "protocol.file.allow=always", "submodule", "add", "-q",
         str(dependency), "dependency")
    _git(primary, "commit", "-q", "-m", "submodule fixture")
    assert claims.claim([0x100]) == ([0x100], [])
    _git(primary, "config", "submodule.recurse", "true")
    _git(primary / "dependency", "remote", "set-url", "origin", str(tmp_path / "missing.git"))
    assert claims.fetch(primary)
    assert _seen(primary) == {0x100}


def test_hook_environment_does_not_redirect_claim_git(hosts, tmp_path, monkeypatch):
    # Ported from Open-BFME-2 637d0387d7: hooks and rebase execs export GIT_DIR
    # and friends, which override cwd. A claim command run from another
    # repository's hook must still act on the checkout it was given.
    a = hosts("a")
    other = tmp_path / "other"
    _git(tmp_path, "init", "-q", str(other))
    for name, value in {"GIT_DIR": str(other / ".git"), "GIT_WORK_TREE": str(other),
                        "GIT_INDEX_FILE": str(other / ".git/index"),
                        "GIT_COMMON_DIR": str(other / ".git")}.items():
        monkeypatch.setenv(name, value)
    assert claims.claim([0x100]) == ([0x100], [])
    assert claims.fetch(a) and _seen(a) == {0x100}
    assert subprocess.run(["git", "for-each-ref", "refs/"], cwd=other, env={
        k: v for k, v in __import__("os").environ.items() if not k.startswith("GIT_")},
        capture_output=True, text=True).stdout == ""


def test_only_the_owner_releases(hosts):
    hosts("a")
    claims.claim([0x100])
    hosts("b")
    assert claims.release([0x100]) == []
    assert 0x100 in claims.active()
    hosts("a")
    assert claims.release([0x100]) == [0x100]
    assert claims.active() == {}


def test_an_expired_claim_can_be_taken_over(hosts):
    hosts("a")
    claims.claim([0x100], ttl_hours=-1)                            # already expired
    hosts("b")
    assert claims.active() == {}
    assert claims.claim([0x100]) == ([0x100], [])
    assert claims.active()[0x100]["owner"] == "b"


def test_renewing_your_own_claim_succeeds(hosts):
    hosts("a")
    claims.claim([0x100])
    assert claims.claim([0x100]) == ([0x100], [])


def test_an_unreachable_origin_fails_closed(hosts, monkeypatch):
    # Readers still serve (a picker only proposes), but claim() may no longer
    # answer ([], []) -- "nothing claimed" and "nothing to claim" looked alike.
    hosts("a")
    monkeypatch.setattr(claims, "REMOTE", "no-such-remote")
    assert claims.active() == {}
    with pytest.raises(claims.ClaimsUnavailable):
        claims.claim([0x100])
    assert claims.main(["claim", "0x100"]) == 2


def test_active_reads_the_origin_of_the_given_root_not_this_checkout(hosts, tmp_path):
    # tools/tests/test_fleet_lifecycle_regressions.py failed on every host with
    # live claims on the real origin: busy_rvas(fixture_root) merged claims.active(),
    # which always fetched from THIS checkout. A root is now fetched through
    # its own origin, so a fixture repository without a remote sees none.
    hosts("a")
    assert claims.claim([0x300]) == ([0x300], [])
    hosts("b")
    assert set(claims.active(claims.ROOT)) == {0x300}
    lonely = tmp_path / "lonely"
    _git(tmp_path, "init", "-q", str(lonely))
    assert claims.active(lonely) == {}
    import eligibility
    (lonely / "build").mkdir()
    assert "0x00000300" not in eligibility.busy_rvas(lonely)


def test_a_claim_result_carries_tokens_and_still_unpacks(hosts):
    hosts("a")
    result = claims.claim([0x100, 0x200])
    got, refused = result
    assert (got, refused) == ([0x100, 0x200], [])
    assert result.worker == "a" and result.unconfirmed == []
    token = result.tokens[0x100]
    assert claims.holds(0x100, token)
    assert result.tokens[0x200] == token          # one claim commit per call


def test_a_push_origin_refuses_without_a_holder_is_unconfirmed(hosts, monkeypatch):
    hosts("a")
    real = claims._git

    def flaky(*args, **kw):
        if args[:1] == ("push",):
            return claims.subprocess.CompletedProcess(args, 1, "", "connection reset")
        return real(*args, **kw)
    monkeypatch.setattr(claims, "_git", flaky)
    with pytest.raises(claims.ClaimsUnavailable):
        claims.claim([0x100])


def test_a_race_lost_after_fetch_is_refused_not_unconfirmed(hosts, monkeypatch):
    hosts("a")
    real_fetch = claims.fetch
    calls = []

    def fetch_then_race(root=None):
        ok = real_fetch(root)
        if not calls:                  # b claims between a's fetch and a's push
            calls.append(1)
            monkeypatch.setenv("BFME_CLAIM_OWNER", "b")
            claims.claim([0x100], root=hosts.b_root)
            monkeypatch.setenv("BFME_CLAIM_OWNER", "a")
        return ok
    hosts.b_root = hosts("b")
    hosts("a")
    monkeypatch.setattr(claims, "fetch", fetch_then_race)
    result = claims.claim([0x100])
    assert result == ([], [0x100]) and result.unconfirmed == []


def test_the_default_owner_is_per_checkout_not_per_host(hosts, monkeypatch, tmp_path):
    a = hosts("a")
    b = hosts("b")
    monkeypatch.delenv("BFME_CLAIM_OWNER")
    assert claims.owner(a) != claims.owner(b)
    assert claims.owner(a) == claims.owner(a)
    monkeypatch.setenv("BFME_RUN_ID", "20260929T000000Z-abc")
    assert claims.owner(a) == "fleet:20260929T000000Z-abc"


def test_heartbeat_renews_and_fencing_detects_a_takeover(hosts):
    hosts("a")
    result = claims.claim([0x100, 0x200], ttl_hours=-1)            # both already expired
    renewed, lost = claims.renew({0x100: result.tokens[0x100]})
    assert lost == [] and claims.holds(0x100, renewed[0x100])
    assert not claims.holds(0x100, result.tokens[0x100])           # old token is dead
    hosts("b")
    taken = claims.claim([0x200])                                  # expired: b takes it over
    assert taken.claimed == [0x200]
    hosts("a")
    renewed, lost = claims.renew({0x200: result.tokens[0x200]})
    assert renewed == {} and lost == [0x200]
    # a stale release (even forced) never deletes the successor's claim
    assert claims.release([0x200], force=True, tokens={0x200: result.tokens[0x200]}) == []
    assert claims.active()[0x200]["owner"] == "b"


def _commit_ledger(clone, rows, message, files=None):
    ledger = clone / claims.LEDGER
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("name,export_rva,target_rva,target_size,source,status,notes\n"
                      + "".join(r + "\n" for r in rows), encoding="utf-8")
    for path, text in (files or {}).items():
        (clone / path).parent.mkdir(parents=True, exist_ok=True)
        (clone / path).write_text(text, encoding="utf-8")
        _git(clone, "add", path)
    _git(clone, "add", claims.LEDGER)
    _git(clone, "commit", "-q", "-m", message)
    return _git(clone, "rev-parse", "HEAD").strip()


def test_a_landing_releases_only_once_origin_master_holds_the_row(hosts):
    a = hosts("a")
    base = _commit_ledger(a, ["?d_00000100@@YAXXZ,,0x00000100,16,game/gen_asm/x.asm,matched,gen-dump"], "base")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    sha = _commit_ledger(a, [row], "land", {"game/x.cpp": "void f() {}\n"})
    claims.queue_landed(0x100, row)
    # verified and committed locally, not pushed: the claim must hold
    assert claims.release_landed() == ([], [0x100])
    assert 0x100 in claims.active()
    with pytest.raises(ValueError):
        claims.landed_rvas(sha)
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed() == ([0x100], [])
    assert claims.active() == {} and claims.pending() == []
    assert base != sha


def test_release_landed_sha_releases_the_leases_the_commit_names(hosts):
    a = hosts("a")
    _commit_ledger(a, [], "base")
    got = claims.claim([0x300, 0x400])
    sha = _commit_ledger(a, ["?g@@YAXXZ,,0x00000300,8,game/y.cpp,matched,",
                             "?h@@YAXXZ,,0x00000400,8,game/y.cpp,matched,"],
                         f"land\n\nClaim-Lease: 0x00000300={got.leases[0x300]}\n")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.landed_rvas(sha) == [0x300, 0x400]
    assert claims.lease_trailers(sha) == {0x300: got.leases[0x300]}
    assert claims.main(["release", "--landed", sha]) == 0
    assert set(claims.active()) == {0x400}          # no trailer, no evidence: untouched


def test_an_old_published_row_does_not_release_an_unpublished_source_change(hosts):
    # review 2026-09-29: the same row key was already on origin (an earlier
    # lift); the new source existed only locally, and release_landed released.
    a = hosts("a")
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,gen-dump"
    _commit_ledger(a, [row], "existing lift", {"game/x.cpp": "__asm { emit }\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    (a / "game/x.cpp").write_text("void f() { real(); }\n", encoding="utf-8")
    (a / "game/x.h").write_text("struct X;\n", encoding="utf-8")          # a new dependency
    claims.queue_landed(0x100, row.replace("gen-dump", "model=m"))
    entry = claims.pending()[0]
    assert set(entry["deps"]) == {"game/x.cpp", "game/x.h"}
    assert claims.release_landed() == ([], [0x100])
    _commit_ledger(a, [row.replace("gen-dump", "model=m")], "real body",
                   {"game/x.cpp": "void f() { real(); }\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed() == ([], [0x100])        # the header is still local
    _commit_ledger(a, [row.replace("gen-dump", "model=m")], "header",
                   {"game/x.h": "struct X;\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed() == ([0x100], [])


def test_a_missing_source_never_releases(hosts):
    a = hosts("a")
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "row only")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    claims.queue_landed(0x100, row)
    assert claims.release_landed() == ([], [0x100])


def test_concurrent_queue_appends_all_survive(tmp_path):
    import threading
    jobs = [threading.Thread(target=claims.queue_landed,
                             args=(r, f"f,,0x{r:08X},1,game/x.cpp,matched,"),
                             kwargs={"who": "t", "root": tmp_path, "deps": {"game/x.cpp": "b"}})
            for r in range(0x100, 0x100 + 24)]
    for job in jobs:
        job.start()
    for job in jobs:
        job.join(timeout=30)
    assert sorted(int(e["rva"], 16) for e in claims.pending(tmp_path)) == list(range(0x100, 0x118))


def test_a_directory_inside_a_checkout_never_inherits_its_origin(hosts, monkeypatch):
    # review 2026-09-29: pytest's basetemp under a real checkout let a
    # "no origin" fixture discover the enclosing repo and push real claims.
    a = hosts("a")
    inner = a / "build" / "fixture"
    inner.mkdir(parents=True)
    assert not claims.configured(inner)
    with pytest.raises(claims.ClaimsUnavailable):
        claims.claim([0x500], root=inner)
    assert _git(hosts.origin, "for-each-ref", "refs/claims/") == ""


def test_release_landed_sha_cannot_override_a_pending_landing(hosts):
    # review 2026-09-29 (reproduction test_release_bypass.py): settlement kept
    # the claim, but `release --landed <old published sha>` released it while
    # the replacement source was still local.
    a = hosts("a")
    _commit_ledger(a, [], "base")
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    sha = _commit_ledger(a, [row], "old published body", {"game/x.cpp": "void f() {}\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    (a / "game/x.cpp").write_text("void f() { different(); }\n", encoding="utf-8")
    claims.queue_landed(0x100, row)
    assert claims.release_landed() == ([], [0x100])
    assert claims.release_landed(sha) == ([], [0x100])
    assert 0x100 in claims.active()
    assert claims.main(["release", "--landed", sha]) == 0 and 0x100 in claims.active()


def test_an_earlier_settled_landing_does_not_release_a_newer_pending_one(hosts):
    a = hosts("a")
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "published", {"game/x.cpp": "void f() {}\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    claims.queue_landed(0x100, row)                          # matches origin: settled
    (a / "game/x.cpp").write_text("void f() { again(); }\n", encoding="utf-8")
    claims.queue_landed(0x100, row)                          # a second, local-only pass
    assert claims.release_landed() == ([], [0x100])
    assert 0x100 in claims.active()


def test_a_committed_but_unpushed_repair_is_not_released(hosts):
    # 2026-09-29 audit fixture: the row was on origin, the repaired source was
    # committed locally but never pushed, and release_landed released.
    a = hosts("a")
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=old"
    _commit_ledger(a, [row], "old landing", {"game/x.cpp": "old source\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    _git(a, "fetch", "-q", "origin")
    claims.claim([0x100])
    _commit_ledger(a, [row], "unpublished repair", {"game/x.cpp": "repaired source\n"})
    claims.queue_landed(0x100, row.replace("model=old", "model=new"))
    assert claims.release_landed() == ([], [0x100])
    assert 0x100 in claims.active()


def test_peer_changes_on_a_newer_origin_master_are_not_landing_deps(hosts):
    # re_attempts.log 0x008615F0: origin/master had moved on (peers changed
    # other game/ files) when the landing was verified; the two-dot diff made
    # those files deps whose old local blobs never matched, so the landed
    # body's claim could not settle.
    b = hosts("b")
    _commit_ledger(b, [], "base", {"game/peer.cpp": "old\n"})
    _git(b, "push", "-q", "origin", "HEAD:refs/heads/master")
    a = hosts("a")
    _git(a, "pull", "-q", "origin", "master")
    hosts("b")
    _commit_ledger(b, [], "peer change", {"game/peer.cpp": "new\n"})
    _git(b, "push", "-q", "origin", "HEAD:refs/heads/master")
    a = hosts("a")
    _git(a, "fetch", "-q", "origin")
    _git(a, "update-ref", "refs/remotes/origin/master", "FETCH_HEAD")
    claims.claim([0x100])
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "land", {"game/x.cpp": "void f() {}\n",
                                       "game/x.h": "struct X;\n"})
    claims.queue_landed(0x100, row)
    # this checkout's own committed dependency is still required
    assert set(claims.pending()[0]["deps"]) == {"game/x.cpp", "game/x.h"}
    _git(a, "pull", "-q", "--rebase", "origin", "master")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed() == ([0x100], [])


def test_a_lease_survives_renewal_and_dies_with_a_takeover(hosts):
    a = hosts("a")
    got = claims.claim([0x100], ttl_hours=-1)                       # expired at once
    lease = got.leases[0x100]
    assert claims.lease_holder(0x100, lease) is None                # expired: not held
    renewed, _ = claims.renew(got.tokens)
    assert claims.lease_holder(0x100, lease) == renewed[0x100]      # same lease, new token
    assert claims.lease_holder(0x100, got.tokens[0x100]) is None    # the old token alone is dead
    hosts("b")
    claims.release([0x100], force=True)
    claims.claim([0x100])
    hosts("a")
    assert claims.lease_holder(0x100, lease) is None


def test_a_landing_queued_during_settlement_keeps_its_claim(hosts, monkeypatch):
    # review 2026-09-30: the queue was snapshotted before the fetch, so a
    # repair queued meanwhile was never evaluated and its claim was released.
    a = hosts("a")
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "published", {"game/x.cpp": "void f() {}\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    claims.queue_landed(0x100, row)                    # settled on origin
    real_fetch = claims._fetch_master

    def queue_while_on_network(root=None):
        (a / "game/x.cpp").write_text("void f() { local_repair(); }\n", encoding="utf-8")
        claims.queue_landed(0x100, row)
        return real_fetch(root)
    monkeypatch.setattr(claims, "_fetch_master", queue_while_on_network)
    released, waiting = claims.release_landed()
    assert released == [] and 0x100 in waiting
    assert len(claims.pending()) == 1 and 0x100 in claims.active()


def test_settlement_releases_only_the_claim_generation_it_evaluated(hosts, monkeypatch):
    a = hosts("a")
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "published", {"game/x.cpp": "void f() {}\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    claims.queue_landed(0x100, row)
    real_release = claims.release

    def reclaimed_first(rvas, **kwargs):
        # the claim is re-taken (a new generation) between evaluation and release
        claims.claim([0x100], who="a")
        return real_release(rvas, **kwargs)
    monkeypatch.setattr(claims, "release", reclaimed_first)
    assert claims.release_landed()[0] == []
    assert 0x100 in claims.active()


def _published_and_queued(a):
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "published", {"game/x.cpp": "void f() {}\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    old = claims.claim([0x100])
    claims.queue_landed(0x100, row)
    assert claims.pending()[0]["lease"] == old.leases[0x100]
    return old


def test_a_fresh_claim_during_settlement_survives_the_old_landing(hosts, monkeypatch):
    # review 2026-09-30 (test_review_probes.py): the body was re-claimed by the
    # same owner while settlement fetched; the old landing deleted the NEW claim.
    a = hosts("a")
    old = _published_and_queued(a)
    real_fetch = claims._fetch_master
    fresh = []

    def replace_before_evaluation(root=None):
        fresh.append(claims.claim([0x100], who="a"))
        return real_fetch(root)
    monkeypatch.setattr(claims, "_fetch_master", replace_before_evaluation)
    released, _ = claims.release_landed()
    assert fresh[0].leases[0x100] != old.leases[0x100]
    assert released == [] and 0x100 in claims.active()
    assert claims.holds(0x100, fresh[0].tokens[0x100])


def test_a_renewal_keeps_the_lease_so_the_landing_still_releases(hosts):
    a = hosts("a")
    old = _published_and_queued(a)
    renewed, lost = claims.renew(old.tokens)
    assert lost == [] and renewed[0x100] != old.tokens[0x100]
    assert claims.release_landed() == ([0x100], [])
    assert claims.active() == {}


def test_release_landed_sha_never_releases_on_timing(hosts, monkeypatch):
    # review 2026-09-30 (test_ca142ff_review.py): a claim taken 0.9 s AFTER the
    # commit passed the whole-second `since <= commit time` test and was freed.
    a = hosts("a")
    _commit_ledger(a, [], "base")
    sha = _commit_ledger(a, ["?g@@YAXXZ,,0x00000300,8,game/y.cpp,matched,"], "land")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    committed = int(_git(a, "log", "-1", "--format=%ct", sha))
    monkeypatch.setattr(claims.time, "time", lambda: committed + 0.9)
    fresh = claims.claim([0x300])
    released, _ = claims.release_landed(sha)
    assert released == [] and claims.holds(0x300, fresh.tokens[0x300])


def test_a_trailer_naming_an_old_lease_does_not_release_a_fresh_claim(hosts):
    a = hosts("a")
    _commit_ledger(a, [], "base")
    old = claims.claim([0x300])
    sha = _commit_ledger(a, ["?g@@YAXXZ,,0x00000300,8,game/y.cpp,matched,"],
                         f"land\n\nClaim-Lease: 0x00000300={old.leases[0x300]}\n")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    fresh = claims.claim([0x300])                    # same owner, new lease
    assert fresh.leases[0x300] != old.leases[0x300]
    assert claims.release_landed(sha)[0] == []
    assert claims.holds(0x300, fresh.tokens[0x300])


@pytest.mark.parametrize("failure", [None, "fetch", "head", "head_error_with_output", "empty", "timeout"])
def test_fetch_master_preserves_commands_and_reports_failed_step(
        tmp_path, monkeypatch, capsys, failure):
    # Exercise the real _fetch_master and _git with a mocked subprocess only:
    # no fixture or production Git/network operation is launched.
    import os

    monkeypatch.setattr(claims, "REMOTE", "fixture-origin")
    inherited_env = dict(os.environ)
    calls = []

    def run(command, **kwargs):
        step = "fetch" if len(calls) == 0 else "head"
        calls.append(command)
        assert kwargs == {
            "cwd": tmp_path, "capture_output": True, "text": True,
            "input": None, "timeout": 300 if step == "fetch" else 60,
            "env": dict(inherited_env, GIT_CEILING_DIRECTORIES=str(tmp_path.parent)),
        }
        if step == "fetch":
            assert command == ["git", "fetch", "-q", "--no-tags", "--recurse-submodules=no", "--refmap=", "fixture-origin",
                               f"+refs/heads/master:{claims.MASTER_SEEN}"]
            if failure == "timeout":
                raise subprocess.TimeoutExpired(command, 300)
            if failure == "fetch":
                return subprocess.CompletedProcess(command, 128, "", "fatal: fixture fetch failed\n")
            return subprocess.CompletedProcess(command, 0, "", "")
        assert command == ["git", "rev-parse", claims.MASTER_SEEN]
        if failure == "head":
            return subprocess.CompletedProcess(command, 128, "", "fatal: fixture FETCH_HEAD failed\n")
        if failure == "head_error_with_output":
            return subprocess.CompletedProcess(command, 128, "abc123\n", "fatal: fixture FETCH_HEAD failed\n")
        if failure == "empty":
            return subprocess.CompletedProcess(command, 0, " \n", "")
        return subprocess.CompletedProcess(command, 0, "abc123\n", "")

    monkeypatch.setattr(claims.subprocess, "run", run)
    result = claims._fetch_master(tmp_path)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert len(calls) == (1 if failure in ("fetch", "timeout") else 2)
    if failure is None:
        assert result == "abc123"
        assert captured.err == ""
    else:
        assert result is None
        expected = {
            "fetch": "claims: git fetch fixture-origin master failed (exit 128): fatal: fixture fetch failed\n",
            "head": "claims: git rev-parse refs/worktree/claims-master failed (exit 128, empty stdout): fatal: fixture FETCH_HEAD failed\n",
            "head_error_with_output": "claims: git rev-parse refs/worktree/claims-master failed (exit 128): fatal: fixture FETCH_HEAD failed\n",
            "empty": "claims: git rev-parse refs/worktree/claims-master failed (exit 0, empty stdout): (no stderr)\n",
            "timeout": "claims: git fetch fixture-origin master failed (exit 124): timed out after 300s\n",
        }
        assert captured.err == expected[failure]


def test_printed_trailers_round_trip_and_release(hosts, capsys):
    a = hosts("a")
    _commit_ledger(a, [], "base")
    assert claims.main(["claim", "0x500", "0x600"]) == 0
    printed = [l for l in capsys.readouterr().out.splitlines() if l.startswith("Claim-Lease:")]
    assert len(printed) == 2
    assert claims.main(["lease", "0x500"]) == 0
    recovered = capsys.readouterr().out.splitlines()
    assert recovered == [printed[0]]
    assert claims.main(["lease"]) == 0
    assert capsys.readouterr().out.splitlines() == printed
    hosts("b")
    assert claims.main(["lease", "0x500"]) == 1          # not b's claim
    a = hosts("a")
    sha = _commit_ledger(a, ["?g@@YAXXZ,,0x00000500,8,game/y.cpp,matched,",
                             "?h@@YAXXZ,,0x00000600,8,game/y.cpp,matched,"],
                         "land\n\n" + "\n".join(printed) + "\n")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert set(claims.lease_trailers(sha)) == {0x500, 0x600}
    assert claims.main(["release", "--landed", sha]) == 0
    assert claims.active() == {}


# Ported from Open-BFME-2 9733e43795: `claims.py claim` settles this checkout's
# queued landings after claiming, holding what it was asked to claim.

def test_claim_command_settles_landings_origin_already_holds(hosts, capsys):
    a = hosts("a")
    _published_and_queued(a)                       # 0x100 landed on origin, still claimed
    assert claims.main(["claim", "0x700"]) == 0
    assert "released 1 landed claim(s) origin/master now holds: 0x00000100" in capsys.readouterr().out
    assert set(claims.active()) == {0x700}
    assert claims.pending() == []


def test_claim_command_holds_the_bodies_it_claims_again(hosts):
    a = hosts("a")
    _published_and_queued(a)
    assert claims.main(["claim", "0x100"]) == 0    # claiming a landed body again keeps it
    assert 0x100 in claims.active()
    assert [e["rva"] for e in claims.pending()] == ["0x00000100"]   # its landing is kept
    # BFME1 re-claims under a fresh lease, which the old landing never releases
    assert claims.release_landed()[0] == [] and 0x100 in claims.active()


def test_hold_also_covers_a_sha_trailer(hosts):
    a = hosts("a")
    _commit_ledger(a, [], "base")
    got = claims.claim([0x300])
    sha = _commit_ledger(a, ["?g@@YAXXZ,,0x00000300,8,game/y.cpp,matched,"],
                         f"land\n\nClaim-Lease: 0x00000300={got.leases[0x300]}\n")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed(sha, hold=iter([0x300])) == ([], [])
    assert 0x300 in claims.active()


def test_claim_command_exit_code_survives_a_settlement_failure(hosts, monkeypatch, capsys):
    a = hosts("a")
    _published_and_queued(a)

    def broken(**_):
        raise claims.ClaimsUnavailable("claims: cannot fetch origin/master")
    monkeypatch.setattr(claims, "release_landed", broken)
    assert claims.main(["claim", "0x700"]) == 0
    assert "settling queued landings failed" in capsys.readouterr().err
    assert {0x100, 0x700} <= set(claims.active())


def test_fetch_never_touches_the_old_shared_mirror(hosts):
    # review 2026-10-15 round 2: checkouts on pre-53a0bc2eb4 claims.py read
    # refs/claims-seen/ as their live mirror; pruning it broke their leases.
    a = hosts("a")
    _git(a, "commit", "-q", "--allow-empty", "-m", "fixture")
    head = _git(a, "rev-parse", "HEAD").strip()
    _git(a, "update-ref", "refs/claims-seen/00000100", head)
    assert claims.claim([0x300]) == ([0x300], [])
    assert claims.fetch(a)
    assert _git(a, "for-each-ref", "--format=%(refname)", "refs/claims-seen/").split() == [
        "refs/claims-seen/00000100"]
    assert set(claims._read_local(a)) == {0x300}


def test_a_landing_settles_after_a_later_edit_of_its_file(hosts):
    # 2026-10-15 fleet: workers land the next body of the same file, so the
    # tip's blob never matched an earlier landing's and it waited out its claim.
    a = hosts("a")
    _commit_ledger(a, [], "base")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "land f", {"game/x.cpp": "void f() {}\n"})
    claims.queue_landed(0x100, row)
    _commit_ledger(a, [row], "land g", {"game/x.cpp": "void f() {}\nvoid g() {}\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed() == ([0x100], [])
    assert claims.active() == {} and claims.pending() == []


def test_a_never_published_blob_still_waits(hosts):
    a = hosts("a")
    _commit_ledger(a, [], "base")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    (a / "game").mkdir(exist_ok=True)
    (a / "game/x.cpp").write_text("void f() { /* local only */ }\n", encoding="utf-8")
    claims.queue_landed(0x100, row)
    _commit_ledger(a, [row], "land f", {"game/x.cpp": "void f() {}\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed() == ([], [0x100])
    assert 0x100 in claims.active()


def test_a_landed_entry_without_a_lease_settles_instead_of_waiting(hosts):
    a = hosts("a")
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "published", {"game/x.cpp": "void f() {}\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.queue_landed(0x100, row)                 # never claimed: no lease
    assert claims.pending()[0].get("lease") in (None, "")
    assert claims.release_landed() == ([], [])
    assert claims.pending() == []


def test_unpushed_restore_of_an_earlier_published_blob_is_not_a_landing(hosts):
    # review 2026-10-15 round 1 (build/review_op4_r1): restoring x.cpp to a
    # version origin/master published BEFORE the landing's base, unpushed,
    # must keep its claim.
    a = hosts("a")
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "f landed earlier", {"game/x.cpp": "void f() {}\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    _commit_ledger(a, [row], "someone breaks f", {"game/x.cpp": "void f() { int broken; }\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    _commit_ledger(a, [row], "repair f (local only)", {"game/x.cpp": "void f() {}\n"})
    claims.queue_landed(0x100, row)
    assert claims.release_landed() == ([], [0x100])


def _set_pending(a, **fields):
    import json
    path = a / claims.PENDING
    entries = [dict(json.loads(line), **fields) for line in path.read_text().splitlines() if line.strip()]
    path.write_text("".join(json.dumps(e) + "\n" for e in entries))


def _land_then_edit_again(a, files_land, files_next):
    _commit_ledger(a, [], "base")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "land f", files_land)
    claims.queue_landed(0x100, row)
    _commit_ledger(a, [row], "land g", files_next)
    return row


def test_every_dependency_blob_must_be_published_in_one_commit(hosts):
    # review round 1 should-fix: x.cpp's and y.h's verified blobs each reached
    # origin/master, but never in the same tree, so that build never landed.
    a = hosts("a")
    _commit_ledger(a, [], "base")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    row = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"
    _commit_ledger(a, [row], "x first", {"game/x.cpp": "void f() {}\n", "game/y.h": "#define Y 0\n"})
    blob_x = _git(a, "rev-parse", "HEAD:game/x.cpp").strip()
    _commit_ledger(a, [row], "y later", {"game/x.cpp": "void f() { }\n", "game/y.h": "#define Y 1\n"})
    blob_y = _git(a, "rev-parse", "HEAD:game/y.h").strip()
    _set_pending_base = _git(a, "rev-parse", "HEAD~2").strip()
    claims.queue_landed(0x100, row, deps={"game/x.cpp": blob_x, "game/y.h": blob_y})
    _set_pending(a, base=_set_pending_base)
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed() == ([], [0x100])
    # the same blobs together in one later commit are a landing
    _commit_ledger(a, [row], "together", {"game/x.cpp": "void f() {}\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed() == ([0x100], [])


def test_a_commit_older_than_the_queue_time_is_not_the_landing(hosts):
    import time
    a = hosts("a")
    _land_then_edit_again(a, {"game/x.cpp": "void f() {}\n"}, {"game/x.cpp": "void f() {}\nvoid g() {}\n"})
    _set_pending(a, queued=int(time.time()) + 3 * claims.QUEUE_SKEW)
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed() == ([], [0x100])


def test_an_entry_without_a_base_needs_the_tip_blob(hosts):
    a = hosts("a")
    _land_then_edit_again(a, {"game/x.cpp": "void f() {}\n"}, {"game/x.cpp": "void f() {}\nvoid g() {}\n"})
    _set_pending(a, base=None)                      # queued before this change
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    assert claims.release_landed() == ([], [0x100])


def test_settling_never_moves_the_worktrees_origin_master(hosts):
    # review 2026-10-15 round 1: settlement inside `claims.py claim` fetched
    # origin master and moved refs/remotes/origin/master mid-task.
    a = hosts("a")
    _published_and_queued(a)
    before = _git(a, "rev-parse", "refs/remotes/origin/master").strip()
    hosts("b")
    _commit_ledger(hosts.origin.parent / "b", [], "peer moves master")
    _git(hosts.origin.parent / "b", "push", "-q", "-f", "origin", "HEAD:refs/heads/master")
    hosts("a")
    claims.release_landed()
    assert _git(a, "rev-parse", "refs/remotes/origin/master").strip() == before
    assert _git(a, "rev-parse", claims.MASTER_SEEN).strip() != before


# Review 2026-10-15 round 2 (build/review_op4_r2/cl/tools/tests/test_review_r2.py).
ROW_R2 = "?f@@YAXXZ,,0x00000100,16,game/x.cpp,matched,model=m"


def test_stale_base_unpushed_restore_within_window(hosts):
    """a fetched long ago (base = 'base'); peers then publish X and break it
    to Y within the 600 s window. a restores X locally, never pushes."""
    a = hosts("a")
    _commit_ledger(a, [], "base")
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    b = hosts("b")
    _git(b, "fetch", "-q", "origin")
    _git(b, "reset", "-q", "--hard", "origin/master")
    _commit_ledger(b, [ROW_R2], "b lands f", {"game/x.cpp": "void f() {}\n"})
    _commit_ledger(b, [ROW_R2], "c breaks f", {"game/x.cpp": "void f() { int broken; }\n"})
    _git(b, "push", "-q", "origin", "HEAD:refs/heads/master")
    a = hosts("a")                                       # no fetch: stale origin/master
    claims.claim([0x100])
    _commit_ledger(a, [ROW_R2], "repair f (local only)", {"game/x.cpp": "void f() {}\n"})
    claims.queue_landed(0x100, ROW_R2)
    # the base is origin's tip fetched at queue time, not the stale tracking ref
    assert claims.pending()[0]["base"] == _git(a, "rev-parse", claims.MASTER_SEEN).strip()
    assert claims.pending()[0]["base"] != _git(a, "rev-parse", "origin/master").strip()
    assert claims.release_landed() == ([], [0x100])


def test_peer_republish_of_same_blob_releases_unpushed(hosts):
    """Not necessarily wrong: a peer after base publishes exactly a's blob."""
    a = hosts("a")
    _commit_ledger(a, [ROW_R2], "f", {"game/x.cpp": "void f() { int broken; }\n"})
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")
    claims.claim([0x100])
    _commit_ledger(a, [ROW_R2], "repair (local)", {"game/x.cpp": "void f() {}\n"})
    claims.queue_landed(0x100, ROW_R2)
    b = hosts("b")
    _git(b, "fetch", "-q", "origin"); _git(b, "reset", "-q", "--hard", "origin/master")
    _commit_ledger(b, [ROW_R2], "peer same fix", {"game/x.cpp": "void f() {}\n"})
    _commit_ledger(b, [ROW_R2], "peer next", {"game/x.cpp": "void f() {}\nvoid g(){}\n"})
    _git(b, "push", "-q", "origin", "HEAD:refs/heads/master")
    hosts("a")
    claims.release_landed()         # either answer is defensible; it must not raise


def test_pull_merge_puts_base_on_second_parent_and_replay_mixes_lineages(hosts):
    """origin/master gets a `git pull` (no rebase) merge: first parent = a
    peer's local commit L forked before a's base B; B is the second parent.
    Replaying L's diff over B's tree invents a state ({x fixed, y=1}) no
    origin commit ever had."""
    a = hosts("a")
    _commit_ledger(a, [ROW_R2], "root", {"game/y.h": "#define Y 0\n", "game/x.cpp": "void f() { int broken; }\n"})
    root = _git(a, "rev-parse", "HEAD").strip()
    _commit_ledger(a, [ROW_R2], "B: y=1", {"game/y.h": "#define Y 1\n"})
    B = _git(a, "rev-parse", "HEAD").strip()
    _git(a, "push", "-q", "origin", "HEAD:refs/heads/master")     # a's origin/master = B
    claims.claim([0x100])
    (a / "game/x.cpp").write_text("void f() {}\n")
    blob_x = _git(a, "hash-object", "game/x.cpp").strip()
    blob_y = _git(a, "rev-parse", "HEAD:game/y.h").strip()
    claims.queue_landed(0x100, ROW_R2, deps={"game/x.cpp": blob_x, "game/y.h": blob_y})  # unpushed
    _git(a, "checkout", "-q", "--", "game/x.cpp")
    # peer: forked at root, fixes x (y still 0), pulls with merge, resolves y back to 0
    b = hosts("b")
    _git(b, "fetch", "-q", "origin")
    _git(b, "checkout", "-q", "-b", "w", root)
    _commit_ledger(b, [ROW_R2], "L: x fixed", {"game/x.cpp": "void f() {}\n"})
    _git(b, "merge", "-q", "--no-edit", "-s", "ours", "origin/master")   # M: x fixed, y=0
    _commit_ledger(b, [ROW_R2], "break x", {"game/x.cpp": "void f() { int b2; }\n"})
    _git(b, "push", "-q", "origin", "HEAD:refs/heads/master")
    for rev in ("HEAD~1", "HEAD~2"):
        print(rev, _git(b, "ls-tree", "-r", rev, "--", "game").strip())
    hosts("a")
    assert claims.release_landed() == ([], [0x100])


def _proxy(origin):
    """Make the fixture origin behave like Claude Code's cloud git proxy:
    only branch pushes, and no branch deletions."""
    hook = Path(origin) / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\nwhile read old new ref; do\n"
                    "  case \"$ref\" in refs/heads/*) ;; *) echo \"403 $ref\" >&2; exit 1 ;; esac\n"
                    "done\n", newline="\n")
    hook.chmod(0o755)
    _git(origin, "config", "receive.denyDeletes", "true")


def _legacy_claim(rva, ttl_hours=4):
    """A claim as checkouts before the branch namespace wrote it."""
    sha = claims._record(claims.owner(), ttl_hours)
    claims._git("push", "-q", "origin", f"{sha}:{claims.ref_of(rva, claims.LEGACY_NS)}")
    claims.active.cache_clear()
    return sha


def test_claims_are_branches_a_cloud_proxy_accepts(hosts):
    _proxy(hosts.origin)
    hosts("a")
    assert claims.claim([0x100]) == ([0x100], [])
    assert _git(hosts.origin, "for-each-ref", "--format=%(refname)").split() == [
        "refs/heads/claims/0x00000100"]
    hosts("b")
    assert claims.claim([0x100]) == ([], [0x100])
    hosts("a")
    token = claims._branch_sha(0x100)
    renewed, lost = claims.renew({0x100: token})
    assert lost == [] and claims.holds(0x100, renewed[0x100])


def test_a_release_the_proxy_cannot_delete_leaves_an_expired_marker(hosts):
    _proxy(hosts.origin)
    hosts("a")
    claims.claim([0x100])
    assert claims.release([0x100]) == [0x100]
    assert claims.active() == {}
    assert "refs/heads/claims/0x00000100" in _git(hosts.origin, "for-each-ref")
    hosts("b")
    assert claims.claim([0x100]) == ([0x100], [])                 # free again
    assert claims.prune(hours=0) == []                             # live, and no deletions anyway


def test_live_legacy_claims_are_still_honoured(hosts):
    hosts("a")
    token = _legacy_claim(0x100)
    hosts("b")
    assert set(claims.active()) == {0x100}
    assert claims.claim([0x100]) == ([], [0x100])
    assert claims.holds(0x100, token)
    hosts("a")
    renewed, lost = claims.renew({0x100: token})                   # moves to its branch
    assert lost == [] and claims.holds(0x100, renewed[0x100])
    assert _git(hosts.origin, "for-each-ref", "--format=%(refname)").split() == [
        "refs/heads/claims/0x00000100"]                            # the legacy ref is gone
    assert claims.release([0x100]) == [0x100]
    assert claims.active() == {}


def test_a_live_claim_branch_wins_over_a_live_legacy_ref(hosts):
    hosts("a")
    _legacy_claim(0x100)
    hosts("b")
    sha = claims._record("b", 4)
    claims._git("push", "-q", "origin", f"{sha}:{claims.ref_of(0x100)}")   # a race an old checkout lost
    claims.active.cache_clear()
    assert claims.active()[0x100]["owner"] == "b"


def test_prune_deletes_long_expired_claims_in_both_namespaces(hosts):
    hosts("a")
    claims.claim([0x100], ttl_hours=-48)
    claims.claim([0x200])
    _legacy_claim(0x300, ttl_hours=-48)
    _legacy_claim(0x400, ttl_hours=-1)
    assert claims.prune(hours=24) == [0x100, 0x300]
    assert _git(hosts.origin, "for-each-ref", "--format=%(refname)").split() == [
        "refs/claims/0x00000400", "refs/heads/claims/0x00000200"]
