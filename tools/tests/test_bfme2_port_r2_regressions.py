"""Round 2 regression tests for Review #1.

Reviewer reproduction names are preserved; PASS now asserts the fix.
Same-account signing is an explicitly accepted owner risk.
Tests named sound assert a nearby case is correctly handled. Temporary Git
repositories and temporary keys only. No compiler, linker, Wine, census, or
real cycle(): the snapshot fixture removes cycle() before executing Python.
"""
import copy
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import shutil
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cycle_artifacts as ca
import cycle_diff as cd
import cycle_launch as launch
import cycle_stamp as stamp
import link_cycle as lc
import link_cycle_context as ctx
import publish_cycle as pc
import repair_queue as rq
from cycle_fixture import NOW, rehash, save_receipt
from test_bfme2_port_r1_regressions import (
    checkout, census_fixture, change_row, freeze, git, run_for, save_graph,
    synthetic_snapshot_checkout,
)


def failed_run(checkout, path, **kwargs):
    run, receipt = run_for(checkout, path, **kwargs)
    graph = ca.read_json(run / ca.CLOSURE_GRAPH)
    graph["nodes"]["unit:1"].update(ok=False, failures=["shift:hardcoded address"])
    change_row(run, receipt, closed_strict=0, hardcoded=1, failure_count=1,
               failures="shift:hardcoded address")
    receipt["series"]["credit_unique_bytes"] = 0
    save_graph(run, receipt, graph)
    return run, receipt


def commit_fixture(root, message):
    git(root, "add", "-f", "tools", "game")
    git(root, "-c", "core.hooksPath=.githooks", "-c", "user.name=R2 fixture",
        "-c", "user.email=r2@example.invalid", "commit", "-qm", message)
    git(root, "update-ref", "refs/remotes/origin/master", "HEAD")
    return git(root, "rev-parse", "HEAD")


@pytest.mark.parametrize("key_mode", ["existing-reader-key", "worker-env-key"])
def test_defect_worker_can_stamp_without_launcher(checkout, tmp_path, monkeypatch, key_mode):
    """Same-account signing is accepted; worker-selected reader keys are refused."""
    root, _ = checkout
    run, _ = failed_run(checkout, tmp_path / "invented-run")
    out = freeze(run, tmp_path / "invented-bundle", root, sign=False)
    assert rq.route_link_queue(out, now=NOW)["sub_reason"] == "unstamped"
    key = stamp.configured_keys()[0]
    if key_mode == "worker-env-key":
        key = stamp.keygen(tmp_path / "worker-controlled-key")
        monkeypatch.setenv("BFME_CYCLE_KEYS", str(key))
    manifest = ca.read_manifest(out)
    manifest["execution"] = {"launcher": "cycle_launch/1", "commit": manifest["commit"],
                             "snapshot": True, "semantic_sha256": manifest["rules"]["implementation_sha256"]}
    (out / ca.MANIFEST).write_text(ca.dumps(manifest))
    # Ordinary same-UID worker code. No launch.measure() and no authority mocks.
    secret = key.read_bytes()
    digest = ca.sha256_file(out / ca.MANIFEST)
    (out / stamp.STAMP).write_text(ca.dumps({
        "schema": stamp.SCHEMA, "manifest_sha256": digest,
        "key_id": hashlib.sha256(secret).hexdigest(),
        "hmac_sha256": hmac.new(secret, bytes.fromhex(digest), hashlib.sha256).hexdigest(),
    }))
    result = rq.route_link_queue(out, now=NOW)
    if key_mode == "existing-reader-key":
        # Owner accepts deliberate same-user secret access. Keep this limit visible.
        assert result["status"] == "ok" and result["authoritative"] is True
        assert "owner-accepted residual risk" in ca.__doc__
    else:
        assert result["status"] == "refused" and result["sub_reason"] == "bad-stamp"
        assert stamp.configured_keys() != [key]


def test_defect_repository_key_hardlink_accepted(checkout, tmp_path):
    root, _ = checkout
    inside = root / "tracked-secret"
    inside.write_bytes(b"repository-visible-key-material!!")
    inside.chmod(0o600)
    git(root, "add", "tracked-secret")
    git(root, "-c", "core.hooksPath=.githooks", "-c", "user.name=R2 fixture",
        "-c", "user.email=r2@example.invalid", "commit", "-qm", "fixture repository key")
    outside = tmp_path / "outside-hardlink"
    os.link(inside, outside)
    assert git(root, "show", "HEAD:tracked-secret").encode() == inside.read_bytes()
    with pytest.raises(stamp.KeyError):
        stamp.read_key(inside)
    assert outside.stat().st_ino == inside.stat().st_ino
    with pytest.raises(stamp.KeyError, match="exactly one hardlink"):
        stamp.read_key(outside)



def test_reader_key_location_ignores_worker_home_and_environment(checkout, tmp_path, monkeypatch):
    import subprocess
    env = dict(os.environ, HOME=str(tmp_path), BFME_CYCLE_KEYS=str(tmp_path / "worker-key"))
    result = subprocess.run([sys.executable, "-I", "-B", "-c",
        "import sys; sys.path.insert(0, sys.argv[1]); import cycle_stamp as s; "
        "print(s.configured_keys()[0])", str(Path(stamp.__file__).parent)],
        env=env, check=True, capture_output=True, text=True)
    assert result.stdout.strip() == str(stamp.DEFAULT_KEY)


def test_key_checks_opened_descriptor_after_parent_swap(checkout, tmp_path, monkeypatch):
    root, _ = checkout
    outside = tmp_path / "key-directory"
    outside.mkdir()
    stamp.keygen(outside / "key")
    inside = root / "key-directory"
    inside.mkdir()
    (inside / "key").write_bytes(b"x" * 32)
    (inside / "key").chmod(0o600)
    alias = tmp_path / "key-alias"
    alias.symlink_to(outside, target_is_directory=True)
    original = os.open
    def swap(path, *args, **kwargs):
        alias.unlink()
        alias.symlink_to(inside, target_is_directory=True)
        return original(path, *args, **kwargs)
    monkeypatch.setattr(stamp.os, "open", swap)
    with pytest.raises(stamp.KeyError, match="outside every"):
        stamp.read_key(alias / "key")

@pytest.mark.parametrize("cache_location", ["provider", "shim-helper", "full-snapshot"])
def test_defect_snapshot_executes_unhashed_bytecode(checkout, tmp_path, cache_location):
    root, _ = synthetic_snapshot_checkout(checkout)
    driver = root / "tools/link_cycle.py"
    source = driver.read_text()
    needle = '    receipt["synthetic_execution"] = '
    at = source.index(needle)
    source = source[:at] + (
        '    receipt["cached_object_verdict"] = context.current_object(ROOT / "game/absent.cpp", ROOT / "build/absent.obj")\n'
    ) + source[at:]
    driver.write_text(source)
    commit_fixture(root, "inert source-only object probe")
    adapter = root / "tools/link_cycle_context.py"
    before = ca.local_rules(root)
    assert ctx.current_object(root / "game/absent.cpp", root / "build/absent.obj") is False
    modified = adapter.read_text().replace(
        "def current_object(source, obj, **kwargs):\n",
        "def current_object(source, obj, **kwargs):\n    return True  # alternate cached verifier\n")
    alternate = tmp_path / "alternate_context.py"
    alternate.write_text(modified)
    target = {"provider": adapter, "shim-helper": root / "tools/gen_case_shims.py",
              "full-snapshot": root / "game/probe.py"}[cache_location]
    cache = Path(importlib.util.cache_from_source(str(target)))
    cache.parent.mkdir(exist_ok=True)
    py_compile.compile(str(alternate), cfile=str(cache), dfile=str(adapter), doraise=True,
                       invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
    commit = commit_fixture(root, "fixture alternate measurement bytecode")
    assert ca.local_rules(root) == before
    assert not git(root, "status", "--porcelain")
    out = tmp_path / "launched"
    import subprocess
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        launch.measure(out, "R2 inert bytecode probe", root=root, key=stamp.configured_keys()[0])
    assert not out.exists()



@pytest.mark.parametrize("sourceless", [False, True])
def test_source_loader_refuses_late_bytecode(tmp_path, sourceless):
    import subprocess
    import cycle_source
    tools = tmp_path / "tools"
    tools.mkdir()
    shutil.copyfile(cycle_source.__file__, tools / "cycle_source.py")
    (tools / "probe.py").write_text("current = False\n")
    alternate = tmp_path / "alternate.py"
    alternate.write_text("current = True\n")
    # Introduce bytecode only AFTER bootstrap's initial cache inventory.
    program = """import importlib.util, py_compile
source = tools / 'probe.py'
cache = tools / 'probe.pyc' if sys.argv[1] == 'True' else Path(importlib.util.cache_from_source(str(source)))
cache.parent.mkdir(exist_ok=True)
py_compile.compile(str(tools.parent / 'alternate.py'), cfile=str(cache), doraise=True,
                   invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
if sys.argv[1] == 'True':
    source.unlink()
    try:
        import probe
    except ImportError:
        pass
    else:
        raise AssertionError('sourceless bytecode executed')
else:
    import probe
    assert probe.current is False, 'cached bytecode executed'
"""
    subprocess.run(cycle_source.command(tools, program, sourceless), check=True,
                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))

@pytest.mark.parametrize("initial_stamp", ["missing", "bad", "wrong-key"])
def test_defect_unsigned_install_reserves_signed_measurement(checkout, tmp_path, initial_stamp):
    root, _ = checkout
    run, _ = failed_run(checkout, tmp_path / "run")
    good = freeze(run, tmp_path / "signed", root)
    unsigned = tmp_path / "unsigned"
    shutil.copytree(good, unsigned)
    if initial_stamp == "missing":
        (unsigned / stamp.STAMP).unlink()
    elif initial_stamp == "bad":
        (unsigned / stamp.STAMP).write_text("{}")
    else:
        from cycle_fixture import host_stamp
        host_stamp(unsigned, stamp.keygen(tmp_path / "untrusted-key"))
    assert rq.route_link_queue(good, now=NOW)["status"] == "ok"
    store = tmp_path / "store"
    ca.install_local(unsigned, store, root=root, now=NOW)
    installed = ca.resolve(store, root=root, now=NOW)[0]
    payload = {p.name: (p.read_bytes(), p.stat().st_ino) for p in installed.iterdir() if p.name != stamp.STAMP}
    manifest, pointer = ca.install_local(good, store, root=root, now=NOW)
    installed = store / ca.bundle_id(manifest["tag"]) / "bundle"
    assert stamp.verify(installed) is None
    assert {p.name: (p.read_bytes(), p.stat().st_ino) for p in installed.iterdir() if p.name != stamp.STAMP} == payload
    result = rq.route_link_queue(store, now=NOW)
    assert result["status"] == "ok" and result["authoritative"] is True
    assert pointer["latest_measurement"] == installed.parent.name
    # Later unsigned or invalid stamps cannot downgrade the installed signature.
    before = (installed / stamp.STAMP).read_bytes()
    ca.install_local(unsigned, store, root=root, now=NOW)
    assert (installed / stamp.STAMP).read_bytes() == before
    assert ca.serve(store, root=root, now=NOW)[1]["authoritative"]

@pytest.mark.parametrize("signature", ["unsigned", "invalid", "wrong-key"])
def test_defect_unsigned_incompatible_bundles_evict_closure(checkout, tmp_path, signature):
    root, _ = checkout
    good_run, _ = failed_run(checkout, tmp_path / "good-run")
    good = freeze(good_run, tmp_path / "good", root)
    store = tmp_path / "store"
    ca.install_local(good, store, root=root, now=NOW)
    assert rq.route_link_queue(store, closure=True, now=NOW)["status"] == "ok"
    for index in range(ca.CLOSURE_LOOKBACK + 1):
        run, receipt = failed_run(checkout, tmp_path / f"bad-run-{index}", now=NOW + index + 1)
        receipt["tool_dependencies"]["build.py"] = "f" * 64
        receipt["tool_digest"] = ctx.digest(receipt["tool_dependencies"])
        receipt["rule_identity"] = ctx.rule_identity(receipt["tool_dependencies"])
        save_receipt(run, receipt)
        out = freeze(run, tmp_path / f"bad-{index}", root, sign=False)
        if signature == "invalid":
            (out / stamp.STAMP).write_text("{}")
        elif signature == "wrong-key":
            from cycle_fixture import host_stamp
            host_stamp(out, stamp.keygen(tmp_path / f"untrusted-key-{index}"))
        ca.install_local(out, store, root=root, now=NOW + 10)
    assert rq.route_link_queue(store, now=NOW + 10)["status"] == "ok"
    result = rq.route_link_queue(store, closure=True, now=NOW + 10)
    assert result["status"] == "ok" and result["authoritative"] is True
    assert result["items"][0]["function"] == "f"
    installed = ca.installed(store, root=root, now=NOW + 10)
    assert sum(e["execution_eligible"] for e in installed) == 1
    assert ca.serve(store, root=root, now=NOW + 10, need_closure=True)[0].tag == ca.read_manifest(good)["tag"]
