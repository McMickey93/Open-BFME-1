"""One-shot native Windows qualification; never pushes or publishes anything."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback


PAYLOAD = Path(__file__).resolve().parent
SOURCE = Path.cwd().resolve()
EVIDENCE = SOURCE.parent / "evidence"
EVIDENCE.mkdir(exist_ok=True)
INPUT = json.loads((PAYLOAD / "input-manifest.json").read_text(encoding="utf-8"))
RESULT = {
    "status": "running",
    "input": INPUT,
    "run": {key: os.environ.get(key) for key in (
        "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_REF", "GITHUB_RUN_ID",
        "GITHUB_RUN_ATTEMPT", "RUNNER_OS", "RUNNER_ARCH", "ImageOS", "ImageVersion")},
    "python": {"executable": sys.executable, "version": sys.version},
    "commands": [],
}


def save_result():
    (EVIDENCE / "result.json").write_text(
        json.dumps(RESULT, indent=2) + "\n", encoding="utf-8")


def require(condition, explanation):
    if not condition:
        raise RuntimeError(explanation)


def run(label, argv, stdin=None):
    """Stream complete output to both the Actions log and a local artifact file."""
    record = {"label": label, "argv": argv, "exit_code": None}
    RESULT["commands"].append(record)
    save_result()
    print("\n>>> " + label, flush=True)
    start = time.monotonic()
    chunks = []
    with (EVIDENCE / (label + ".log")).open("wb") as log:
        process = subprocess.Popen(
            argv, cwd=SOURCE, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if stdin is not None:
            process.stdin.write(stdin)
            process.stdin.close()
        for line in process.stdout:
            log.write(line)
            log.flush()
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
            chunks.append(line)
        record["exit_code"] = process.wait()
    record["seconds"] = round(time.monotonic() - start, 3)
    save_result()
    require(record["exit_code"] == 0, f"{label} failed: exit {record['exit_code']}")
    return b"".join(chunks)


def git(label, *args, stdin=None):
    return run(label, ["git", *args], stdin=stdin)


def tip(label):
    advertised = git(label, "ls-remote", "--exit-code", "origin", "refs/heads/master")
    fields = advertised.decode().split()
    require(fields == [INPUT["base"], "refs/heads/master"],
            "Official master moved; refresh the pinned base and qualify again.")
    return fields[0]


def main():
    require(sys.platform == "win32" and sys.version_info[:2] == (3, 12),
            "Use native Windows Python 3.12, not MSYS Python or Wine.")
    git_bash = Path(os.environ.get("BFME_QUALIFICATION_BASH", ""))
    require(git_bash.is_absolute() and git_bash.is_file(),
            "The calling Git Bash must supply its absolute Windows executable path.")
    RESULT["git_bash"] = str(git_bash)
    require(os.environ.get("GITHUB_REPOSITORY") == INPUT["repository"], "Wrong fork")
    require(os.environ.get("GITHUB_REF") == "refs/heads/" + INPUT["branch"], "Wrong branch")
    for name, digest in (("parser.patch", INPUT["patch_sha256"]),
                         ("commit-message.txt", INPUT["message_sha256"])):
        raw = (PAYLOAD / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, f"Changed input: {name}")
        shutil.copyfile(PAYLOAD / name, EVIDENCE / name)
    shutil.copyfile(PAYLOAD / "input-manifest.json", EVIDENCE / "input-manifest.json")
    require(git("initial-head", "rev-parse", "HEAD").decode().strip() == INPUT["base"],
            "Wrong official base")
    require(git("initial-tree", "rev-parse", "HEAD^{tree}").decode().strip() == INPUT["base_tree"],
            "Wrong official base tree")
    require(not git("initial-status", "status", "--porcelain"), "Source checkout is not clean")
    remote = git("origin-url", "remote", "get-url", "origin").decode().strip()
    require(remote.removesuffix(".git") == INPUT["upstream"].removesuffix(".git"),
            "Origin must be the official public repository")
    tip("initial-advertised-master")
    publisher = git("publisher-mode", "show", INPUT["base"] +
                    ":targets/game/reverse/publisher_mode").decode().strip()
    require(publisher == "off", "Pre-push publication mode must already be off upstream")
    require(hashlib.sha256((SOURCE / INPUT["compiler_path"]).read_bytes()).hexdigest()
            == INPUT["compiler_sha256"], "MSVC7.1 compiler differs from the reviewed input")
    run("install-requirements", [sys.executable, "-m", "pip", "install", "--no-cache-dir",
                                 "--disable-pip-version-check", "-r", "tools/requirements.txt"])
    run("python-packages", [sys.executable, "-m", "pip", "freeze"])
    run("initial-ledger-check", [sys.executable, "tools/check_csv.py"])
    git("candidate-branch", "switch", "-c", "qualification/parser-candidate")
    run("setup-hooks", [str(git_bash), "tools/setup_hooks.sh"])
    require(git("hooks-path", "config", "--get", "core.hooksPath").decode().strip()
            == ".githooks", "Ordinary repository hooks are required")
    git("author-name", "config", "user.name", "ChatGPT")
    git("author-email", "config", "user.email", "chatgpt@localhost")
    for item in INPUT["files"]:
        blob = git("base-blob-" + Path(item["path"]).stem, "rev-parse", "HEAD:" + item["path"])
        require(blob.decode().strip() == item["base_blob"], "Patch preimage changed")
    patch = str(PAYLOAD / "parser.patch")
    git("check-patch", "apply", "--check", "--index", patch)
    git("apply-patch", "apply", "--index", patch)
    staged = git("staged-patch", "diff", "--cached", "--binary", "--full-index")
    require(staged == (PAYLOAD / "parser.patch").read_bytes(), "Staged diff is not the exact patch")
    require(git("staged-tree", "write-tree").decode().strip() == INPUT["candidate_tree"],
            "Candidate tree differs from the prepared two-file change")
    run("focused-tests", [sys.executable, "-m", "pytest", "-q",
                          "tools/tests/test_list_naked_candidates.py"])
    # This is an ordinary commit: pre-commit, commit-msg and post-commit run unchanged.
    # In particular, target_hooks invokes the complete accepted WorldBuilder gate.
    git("normal-commit", "commit", "--file", str(PAYLOAD / "commit-message.txt"))
    commit = git("candidate-commit", "rev-parse", "HEAD").decode().strip()
    parent = git("candidate-parent", "rev-parse", "HEAD^").decode().strip()
    tree = git("candidate-tree", "rev-parse", "HEAD^{tree}").decode().strip()
    require(parent == INPUT["base"] and tree == INPUT["candidate_tree"], "Unexpected commit tree/parent")
    RESULT["candidate"] = {"commit": commit, "parent": parent, "tree": tree, "files": INPUT["files"]}
    raw_commit = git("commit-object", "cat-file", "commit", commit)
    (EVIDENCE / "commit-object.txt").write_bytes(raw_commit)
    (EVIDENCE / "commit-message.txt").write_bytes(raw_commit.split(b"\n\n", 1)[1])
    committed = git("committed-patch", "diff", "--binary", "--full-index", parent, commit)
    require(committed == (PAYLOAD / "parser.patch").read_bytes(), "Commit changed the exact patch")
    for item in INPUT["files"]:
        raw = (SOURCE / item["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item["sha256"], "Candidate file bytes changed")
        destination = EVIDENCE / "candidate-files" / item["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    base = tip("pre-push-advertised-master")
    refs = f"refs/heads/qualification/parser-candidate {commit} refs/heads/master {base}\n"
    (EVIDENCE / "pre-push-stdin.txt").write_text(refs, encoding="utf-8", newline="\n")
    # Invoke the genuine hook against the just-advertised official master; never git push.
    run("normal-pre-push", [str(git_bash), ".githooks/pre-push", "origin", INPUT["upstream"]],
        stdin=refs.encode())
    tip("final-advertised-master")
    require(not git("final-status", "status", "--porcelain", "--untracked-files=no"),
            "Tracked source changed during qualification")
    RESULT["status"] = "passed"


save_result()
try:
    main()
except Exception as error:
    RESULT["status"] = "failed"
    RESULT["error"] = str(error)
    (EVIDENCE / "failure.txt").write_text(traceback.format_exc(), encoding="utf-8")
    raise
finally:
    # Logs and textual verification receipts only; no binaries, object files,
    # compiler distributions, checkout metadata, credentials or caches.
    for pattern in ("verify-*/*.compile.log", "verify-*/*.json"):
        for source in (SOURCE / "build/worldbuilder").glob(pattern):
            destination = EVIDENCE / "worldbuilder" / source.relative_to(SOURCE / "build/worldbuilder")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    save_result()
