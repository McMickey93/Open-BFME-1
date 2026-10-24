"""Prepare an immutable native experiment payload from an explicit JSON request.

Usage: python prepare.py --source-repo PATH --request request.json
The request supplies base, mode, body, admissions (optional), claims, model,
notes, patch_path and commit_message_path. It contains real acquired claim
leases; preparation creates no claim and changes neither the source checkout
nor its index. Root reviews the resulting payload before publication.
"""

import argparse
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile

import qualify


def prepare(repo, request, destination):
    def git(*args, env=None):
        return subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True).stdout

    base = request["base"]
    patch = Path(request["patch_path"]).read_bytes()
    message = Path(request["commit_message_path"]).read_bytes()
    source_status = git("status", "--porcelain=v1", "-z")
    current_index = git("write-tree")
    with tempfile.TemporaryDirectory(prefix="bfme-body-payload-") as directory:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(directory) / "index")}
        git("read-tree", base, env=env)
        result = subprocess.run(["git", "apply", "--cached", "--check", "-"], cwd=repo,
                                env=env, input=patch, capture_output=True)
        qualify.require(result.returncode == 0, "Patch does not apply to the explicit base: " + result.stderr.decode("utf-8", "replace"))
        subprocess.run(["git", "apply", "--cached", "-"], cwd=repo, env=env, input=patch,
                       capture_output=True, check=True)
        paths = git("diff", "--cached", "--name-only", "-z", base, env=env).decode().split("\0")
        files = []
        for path in filter(None, paths):
            qualify.require(qualify.allowed_patch_path(path), "Patch changes a forbidden path: " + path)
            original = git("ls-tree", "-z", base, "--", path)
            base_blob = original.split(b"\t", 1)[0].decode().split()[2] if original else None
            staged = git("ls-files", "--stage", "-z", "--", path, env=env)
            if not staged:
                qualify.require(base_blob is not None, "Deletion has no preimage")
                files.append({"path": path, "mode": "100644", "base_blob": base_blob,
                              "candidate_blob": None, "sha256": None, "deleted": True})
                continue
            mode, blob, stage = staged.split(b"\t", 1)[0].decode().split()
            qualify.require(mode == "100644" and stage == "0", "Nonordinary or conflicted patch entry")
            content = git("show", ":" + path, env=env)
            files.append({"path": path, "mode": mode, "base_blob": base_blob,
                          "candidate_blob": blob, "sha256": qualify.digest(content)})
        patch_tree = git("write-tree", env=env).decode().strip()
    qualify.require(source_status == git("status", "--porcelain=v1", "-z")
                    and current_index == git("write-tree"), "Preparation changed the source worktree or index")
    ledger = git("show", base + ":" + qualify.LEDGER)
    rows = qualify.claimed_rows(ledger, {"claims": request["claims"], "files": files})
    data = {key: request[key] for key in ("base", "mode", "body", "claims", "model", "notes")}
    if "admissions" in request:
        data["admissions"] = request["admissions"]
    data.update(schema_version=1, repository=qualify.REPOSITORY, upstream=qualify.UPSTREAM,
                base_tree=git("rev-parse", base + "^{tree}").decode().strip(), patch_tree=patch_tree,
                patch_sha256=qualify.digest(patch), message_sha256=qualify.digest(message),
                files=files, base_rows=rows)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "candidate.patch").write_bytes(patch)
    (destination / "commit-message.txt").write_bytes(message)
    (destination / "input-manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    qualify.read_manifest(destination)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", required=True, type=Path)
    parser.add_argument("--request", required=True, type=Path)
    args = parser.parse_args()
    data = prepare(args.source_repo.resolve(), json.loads(args.request.read_text(encoding="utf-8")),
                   Path(__file__).resolve().parent)
    print(json.dumps({"base": data["base"], "mode": data["mode"], "body": data["body"],
                      "patch_sha256": data["patch_sha256"], "files": data["files"]}, indent=2))


if __name__ == "__main__":
    main()
