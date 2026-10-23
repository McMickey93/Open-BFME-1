#!/usr/bin/env python3
"""Measure an approved immutable snapshot and stamp its bundle with a host key.

keygen [--key PATH] creates a mode-0600 key outside every repository.
measure --out DIR --producer LABEL [--rev origin/master] builds in a fresh
snapshot subprocess; it never measures the caller's imported verifier modules.
Readers trust only the fixed account key path; --key selects a signing key.
"""
import argparse
import hashlib
import hmac
import io
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

import cycle_artifacts as ca
import cycle_stamp as stamp
import cycle_source
import publish_cycle as pc


def frozen_tools(root, commit, destination):
    """Bootstrap only committed tools, without importing any caller providers."""
    archive = subprocess.run(["git", "-C", str(root), "archive", "--format=tar", commit, "tools"],
                             check=True, capture_output=True, env=cycle_source.clean_environment({})).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(destination, filter="data")
    cycle_source.reject_bytecode(destination)
    cycle_source.reject_shadows(Path(destination) / "tools")
    rules = ca.local_rules(destination)
    if rules is None:
        raise ca.BundleError("approved commit has no readable BFME1 snapshot implementation")
    return rules


def snapshot_command(seed, root, commit, snapshots):
    # Import providers only from the frozen bootstrap. Then point the existing
    # --snapshot exporter at the source Git database. Its measurement subprocess
    # executes snapshot/tools/link_cycle.py through the same source-only loader.
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import link_cycle as lc; "
            "lc.ROOT = lc.Path(sys.argv[2]); "
            "raise SystemExit(lc.main(['--snapshot', sys.argv[3], '--snapshot-dir', sys.argv[4], '--build']))")
    return cycle_source.command(seed / "tools", code, seed / "tools", root, commit, snapshots)


def measure(out, producer, *, root=ca.ROOT, rev=ca.UPSTREAM, key=stamp.DEFAULT_KEY, snapshot_dir=None):
    root, out = Path(root).resolve(), Path(out).absolute()
    secret = stamp.read_key(key)  # Read only in the launcher; never passed to the child.
    commit = ca._git(root, "rev-parse", "--verify", rev + "^{commit}")
    if commit is None or commit.returncode:
        raise ca.Unavailable("cannot resolve requested origin/master commit")
    commit = commit.stdout.strip()
    if ca.ancestry(commit, root)[0] is not True:
        raise ca.Refused("measurement must be an ancestor of local origin/master", "not-authoritative", "non-ancestor")
    if out.exists():
        raise ca.BundleError("bundle destination exists: immutable bundles are never replaced")
    # Unique empty directories also prevent reuse of old code, bytecode or objects.
    with tempfile.TemporaryDirectory(prefix="lc-", dir=snapshot_dir) as workspace:
        workspace = Path(workspace)
        seed, snapshots = workspace / "seed", workspace / "s"
        seed.mkdir()
        rules = frozen_tools(root, commit, seed)
        preflight = cycle_source.clean_runtime_identity(seed / "tools")
        ca.same("clean preflight interpreter installation", preflight, rules["runtime"])
        executed = {n: cycle_source.module_record(seed / "tools", seed / "tools" / n,
                                                (seed / "tools" / n).read_bytes())[1]
                    for n in rules["measurement_files"]}
        audit = workspace / "module-audit"
        audit.mkdir()
        expected = rules["implementation_sha256"]  # tools hashed before any execution
        env = cycle_source.clean_environment({})
        env.update(LINK_CYCLE_ROOT=str(seed), BFME_CYCLE_EXPECTED_SEMANTIC=expected,
                   BFME_OBJSTORE="off", **{cycle_source.AUDIT_ENV: str(audit)})
        subprocess.run(snapshot_command(seed, root, commit, snapshots), cwd=root, env=env, check=True)
        snapshot = snapshots / commit[:10]
        # Hash the actual export again, and bind the preflight to the receipt.
        cycle_source.reject_bytecode(snapshot)
        ca.same("snapshot tools after execution", ca.local_rules(snapshot), rules)
        run = snapshot / "build/link_cycle"
        receipt = ca.read_json(run / ca.RECEIPT)
        ca.same("snapshot measured commit", receipt["commit"], commit)
        ca.same("executed semantic dependency digest", receipt["rule_identity"], rules)
        actual = cycle_source.audit_modules(audit, roots=(seed / "tools", snapshot / "tools"))
        runtime = cycle_source.audit_modules(audit, roots=(seed / "tools", snapshot / "tools"), runtime=True)
        ca.same("executed module set", actual, executed)
        ca.same("receipt executed module set", receipt.get("executed_modules"), actual)
        ca.same("receipt runtime module set", receipt.get("runtime_modules"), runtime)
        ca.same("unchanged interpreter installation", cycle_source.runtime_identity(), rules["runtime"])
        failure = ca.context.run_authority_failure(receipt)
        if failure or receipt.get("authoritative") is not True:
            raise ca.Refused("snapshot was diagnostic: " + str(failure), "not-authoritative", failure or "diagnostic")
        # Publish on the destination filesystem, even if snapshots use /tmp.
        out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=f".{out.name}.launch-", dir=out.parent) as publishing:
            stage = Path(publishing) / "bundle"
            manifest = pc.make_bundle(run, stage, producer, root=root)
            manifest["execution"] = {"launcher": "cycle_launch/1", "commit": commit, "snapshot": True,
                                     "semantic_sha256": expected}
            (stage / ca.MANIFEST).write_text(ca.dumps(manifest), encoding="utf-8")
            ca.validate(stage, root=root)
            failure = ca.run_evidence_failure(stage, receipt, root)
            if failure:
                raise ca.Refused("snapshot evidence failed: " + failure, "not-authoritative", failure)
            if ca.ancestry(commit, root)[0] is not True:
                raise ca.Refused("origin/master changed during measurement", "not-authoritative", "non-ancestor")
            digest = ca.sha256_file(stage / ca.MANIFEST)
            record = {"schema": stamp.SCHEMA, "manifest_sha256": digest,
                      "key_id": hashlib.sha256(secret).hexdigest(),
                      "hmac_sha256": hmac.new(secret, bytes.fromhex(digest), hashlib.sha256).hexdigest()}
            (stage / stamp.STAMP).write_text(ca.dumps(record), encoding="utf-8")
            ca.publish_directory(stage, out)
            return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    k = sub.add_parser("keygen")
    k.add_argument("--key", default=str(stamp.DEFAULT_KEY))
    m = sub.add_parser("measure")
    m.add_argument("--key", default=str(stamp.DEFAULT_KEY))
    m.add_argument("--rev", default=ca.UPSTREAM)
    m.add_argument("--out", required=True)
    m.add_argument("--producer", required=True)
    m.add_argument("--snapshot-dir")
    args = ap.parse_args(argv)
    try:
        if args.command == "keygen":
            print(stamp.keygen(args.key))
        else:
            result = measure(args.out, args.producer, rev=args.rev, key=args.key, snapshot_dir=args.snapshot_dir)
            print("host-stamped snapshot bundle " + result["tag"])
        return 0
    except (ca.Problem, OSError, ValueError, subprocess.CalledProcessError) as error:
        print("cycle_launch: " + str(error), file=sys.stderr)
        return ca.exit_code(error) if isinstance(error, ca.Problem) else 1


if __name__ == "__main__":
    sys.exit(main())
