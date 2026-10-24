"""Qualify one immutable parser patch on Windows; never publish anything."""

import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback


PAYLOAD = Path(__file__).resolve().parent
SOURCE = Path.cwd().resolve()
EVIDENCE = SOURCE.parent / "evidence"
INPUT = json.loads((PAYLOAD / "input-manifest.json").read_text(encoding="utf-8"))
PATCH_SHA256 = "5974dfc912abb045c253d4eb7477e0b88599feb0da39086d87504dd351abde6a"
PATCH_PATHS = {"tools/list_naked_candidates.py", "tools/tests/test_list_naked_candidates.py"}
MAX_REFRESHES = 2
RESULT = {
    "status": "running", "input": INPUT, "commands": [], "attempts": [],
    "run": {key: os.environ.get(key) for key in (
        "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_REF", "GITHUB_RUN_ID",
        "GITHUB_RUN_ATTEMPT", "RUNNER_OS", "RUNNER_ARCH", "ImageOS", "ImageVersion")},
    "python": {"executable": sys.executable, "version": sys.version},
}


def save_result():
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "result.json").write_text(json.dumps(RESULT, indent=2) + "\n", encoding="utf-8")


def require(condition, explanation):
    if not condition:
        raise RuntimeError(explanation)


def run(label, argv, stdin=None, env=None):
    """Keep every command's full output, including unsuccessful attempts."""
    filename = f"{len(RESULT['commands']):03d}-{label}.log"
    record = {"label": label, "argv": argv, "exit_code": None, "log": filename,
              "attempt": RESULT.get("active_attempt")}
    RESULT["commands"].append(record)
    save_result()
    print("\n>>> " + label, flush=True)
    start, chunks = time.monotonic(), []
    with (EVIDENCE / filename).open("wb") as log:
        process = subprocess.Popen(
            argv, cwd=SOURCE, env=env,
            stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
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


def git(label, *args, stdin=None, env=None):
    return run(label, ["git", *args], stdin=stdin, env=env)


def revision(label, ref):
    value = git(label, "rev-parse", "--verify", ref).decode().strip()
    require(re.fullmatch(r"[0-9a-f]{40}", value), "Invalid Git object ID")
    return value


def tip(label):
    fields = git(label, "ls-remote", "--exit-code", "origin", "refs/heads/master").decode().split()
    require(len(fields) == 2 and fields[1] == "refs/heads/master"
            and re.fullmatch(r"[0-9a-f]{40}", fields[0]), "Invalid official master advertisement")
    return fields[0]


def fetched_master():
    git("fetch-official-master", "fetch", "--no-tags", "origin", "refs/heads/master")
    return revision("fetched-master", "FETCH_HEAD^{commit}")


def fixed_control(path, patterns):
    """Instruction, verifier, compiler, image and include rules may not advance."""
    low = path.lower()
    parts = PurePosixPath(low).parts
    name = parts[-1]
    roots = (".githooks", "tools", "inputs", "worldbuilder", "targets/worldbuilder",
             ".github", ".agents", ".codex", ".claude")
    if any(low == root or low.startswith(root + "/") for root in roots):
        return True
    if name in (".gitattributes", ".gitmodules", ".gitignore", ".editorconfig",
                "agents.md", "claude.md", "contributing.md", "instructions.md", "rules.md"):
        return True
    if name.endswith(".instructions.md") or "rules" in parts or ".rules" in parts:
        return True
    if low == "readme.md" or low.startswith("docs/") and low.endswith(".md"):
        return True
    if low in ("build.sh", "build.cmd", "build.bat", "makefile", "cmakelists.txt",
               "targets/game/reverse/publisher_mode",
               "targets/game/reverse/analysis/verifier_upgrade_plan.md"):
        return True
    return any(fnmatch.fnmatchcase(low, pattern.lower()) for pattern in patterns)


def guard_advance(base, previous, guards):
    """Compare explicit Git snapshots using helpers loaded from the clean pin."""
    target_hooks, header_dependents, protected_paths = guards
    git("descends-from-reviewed-pin", "merge-base", "--is-ancestor", INPUT["base"], base)
    git("advances-from-current-base", "merge-base", "--is-ancestor", previous, base)
    changed = set(git("upstream-changed-paths", "diff", "--name-only", "--no-renames", "-z",
                      INPUT["base"], base).decode("utf-8").split("\0")) - {""}
    patterns = (*protected_paths.PROTECTED, *protected_paths.SHRINK_ONLY)
    blocked = {path for path in changed if fixed_control(path, patterns)}
    require(not blocked, "Protected qualification inputs changed: " + ", ".join(sorted(blocked)))
    for ref in {INPUT["base"], base}:
        paths = target_hooks._paths(SOURCE, ref)
        sources = target_hooks._sources(SOURCE, ref, paths)
        donors = target_hooks._donor_paths(SOURCE, ref, paths)
        checkers = target_hooks._checker_paths(SOURCE, ref, paths)
        owned_inputs = {path.lower() for path in sources | donors}
        blocked |= {path for path in changed
                    if path.lower() in owned_inputs or path.startswith(target_hooks.OWNED)
                    or target_hooks._compiler_input(path, checkers)
                    or target_hooks._compiler_input(path.lower(), checkers)}
        # Also protect non-header include operands. The normal snapshot parser
        # follows splices/comments; any parse uncertainty aborts this refresh.
        if changed:
            edges, macro = header_dependents.scan(ref)
            # WorldBuilder itself is outside header_dependents' game scan.
            # Read its immutable sources with that same conservative parser.
            extra = [path for path in sources if path not in edges]
            for path, data in header_dependents.blobs(ref, extra).items():
                included, has_macro = header_dependents.read_whole(path, data)
                edges[path] = included
                if has_macro:
                    macro.add(path)
            included_names = {name for names in edges.values() for name in names}
            blocked |= {path for path in changed if header_dependents.name(path) in included_names}
            reached = header_dependents.dependents(changed, header_dependents.graph(edges), macro)
            require(not reached.intersection(sources),
                    "An upstream change may reach a WorldBuilder translation unit")
    require(not blocked, "WorldBuilder inputs changed: " + ", ".join(sorted(blocked)))
    publisher = git("publisher-mode", "show", base +
                    ":targets/game/reverse/publisher_mode").decode().strip()
    require(publisher == "off", "Pre-push publication mode must already be off upstream")
    return {"reviewed_pin": INPUT["base"], "previous_base": previous,
            "accepted_base": base, "changed_paths": sorted(changed)}


def expected_tree(base):
    """Derive the candidate independently from a fresh, temporary Git index."""
    for item in INPUT["files"]:
        blob = revision("patch-preimage", base + ":" + item["path"])
        require(blob == item["base_blob"], "Immutable parser patch preimage changed")
    with tempfile.TemporaryDirectory(prefix="parser-index-") as directory:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(directory) / "index")}
        git("expected-read-base", "read-tree", base, env=env)
        git("expected-check-patch", "apply", "--cached", "--check", str(PAYLOAD / "parser.patch"), env=env)
        git("expected-apply-patch", "apply", "--cached", str(PAYLOAD / "parser.patch"), env=env)
        diff = git("expected-exact-patch", "diff", "--cached", "--binary", "--full-index", base, env=env)
        require(diff == (PAYLOAD / "parser.patch").read_bytes(), "Temporary-index patch differs")
        return git("expected-tree", "write-tree", env=env).decode().strip()


def staged_exact(tree):
    diff = git("staged-patch", "diff", "--cached", "--binary", "--full-index")
    require(diff == (PAYLOAD / "parser.patch").read_bytes(), "Staged diff is not the immutable patch")
    require(git("staged-tree", "write-tree").decode().strip() == tree, "Staged candidate tree differs")


def inspect_candidate(base, tree, directory):
    commit = revision("candidate-commit", "HEAD")
    parents = git("candidate-parents", "rev-list", "--parents", "-n", "1", "HEAD").decode().split()
    require(parents == [commit, base], "Candidate must have exactly the accepted base as parent")
    require(revision("candidate-tree", "HEAD^{tree}") == tree, "Candidate tree differs")
    diff = git("candidate-patch", "diff", "--binary", "--full-index", base, commit)
    require(diff == (PAYLOAD / "parser.patch").read_bytes(), "Committed diff is not the immutable patch")
    require(not git("candidate-status", "status", "--porcelain", "--untracked-files=no"),
            "Tracked source changed during qualification")
    raw = git("commit-object", "cat-file", "commit", commit)
    message = raw.split(b"\n\n", 1)[1]
    require(message == (PAYLOAD / "commit-message.txt").read_bytes(), "Candidate message changed")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "commit-object.txt").write_bytes(raw)
    (directory / "commit-message.txt").write_bytes(message)
    (directory / "parser.patch").write_bytes(diff)
    for item in INPUT["files"]:
        require(revision("candidate-blob", commit + ":" + item["path"]) == item["candidate_blob"],
                "Candidate blob changed")
        raw = (SOURCE / item["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item["sha256"], "Candidate file bytes changed")
        destination = directory / "candidate-files" / item["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    return {"commit": commit, "parent": base, "tree": tree, "files": INPUT["files"],
            "evidence": directory.relative_to(EVIDENCE).as_posix()}


def main():
    require(sys.platform == "win32" and sys.version_info[:2] == (3, 12),
            "Use native Windows Python 3.12, not MSYS Python or Wine.")
    git_bash = Path(os.environ.get("BFME_QUALIFICATION_BASH", ""))
    require(git_bash.is_absolute() and git_bash.is_file(), "The calling Git Bash must supply its absolute executable")
    RESULT["git_bash"] = str(git_bash)
    require(INPUT["repository"] == "McMickey93/Open-BFME-1" and INPUT["branch"] == "master"
            and INPUT["upstream"] == "https://github.com/Open-BFME/Open-BFME-1.git", "Wrong qualification target")
    require(os.environ.get("GITHUB_REPOSITORY") == INPUT["repository"], "Wrong fork")
    require(os.environ.get("GITHUB_REF") == "refs/heads/" + INPUT["branch"], "Wrong branch")
    require(len(INPUT["files"]) == 2 and {item["path"] for item in INPUT["files"]} == PATCH_PATHS,
            "This qualification is only for the immutable two-file parser patch")
    require(INPUT["patch_sha256"] == PATCH_SHA256, "Wrong parser patch")
    for name, digest in (("parser.patch", PATCH_SHA256), ("commit-message.txt", INPUT["message_sha256"])):
        require(hashlib.sha256((PAYLOAD / name).read_bytes()).hexdigest() == digest, "Changed input: " + name)
        shutil.copyfile(PAYLOAD / name, EVIDENCE / name)
    shutil.copyfile(PAYLOAD / "input-manifest.json", EVIDENCE / "input-manifest.json")
    require(revision("initial-head", "HEAD") == INPUT["base"], "Wrong official pin")
    require(revision("initial-tree", "HEAD^{tree}") == INPUT["base_tree"], "Wrong pinned tree")
    require(not git("initial-status", "status", "--porcelain"), "Pinned source checkout is not clean")
    remote = git("origin-url", "remote", "get-url", "origin").decode().strip()
    require(remote.removesuffix(".git") == INPUT["upstream"].removesuffix(".git"), "Wrong public origin")
    require(hashlib.sha256((SOURCE / INPUT["compiler_path"]).read_bytes()).hexdigest()
            == INPUT["compiler_sha256"], "Reviewed MSVC 7.1 compiler changed")
    require(expected_tree(INPUT["base"]) == INPUT["candidate_tree"], "Pinned expected candidate tree changed")
    # Import only the already verified pinned tools. All tools must remain
    # byte-identical before a fetched descendant is ever checked out.
    sys.path.insert(0, str(SOURCE / "tools"))
    import target_hooks
    import header_dependents
    import protected_paths
    guards = target_hooks, header_dependents, protected_paths
    base = fetched_master()
    proof = guard_advance(base, INPUT["base"], guards)
    tree = expected_tree(base)
    git("candidate-branch", "switch", "-c", "qualification/parser-candidate", base)
    run("install-requirements", [sys.executable, "-m", "pip", "install", "--no-cache-dir",
                                 "--disable-pip-version-check", "-r", "tools/requirements.txt"])
    run("python-packages", [sys.executable, "-m", "pip", "freeze"])
    run("initial-ledger-check", [sys.executable, "tools/check_csv.py"])
    run("setup-hooks", [str(git_bash), "tools/setup_hooks.sh"])
    require(git("hooks-path", "config", "--get", "core.hooksPath").decode().strip() == ".githooks", "Ordinary hooks required")
    git("author-name", "config", "user.name", "ChatGPT")
    git("author-email", "config", "user.email", "chatgpt@localhost")
    git("apply-patch", "apply", "--index", str(PAYLOAD / "parser.patch"))
    refreshes = 0
    while True:
        RESULT["active_attempt"] = refreshes
        attempt = {"number": refreshes, "base": base, "base_tree": revision("accepted-base-tree", base + "^{tree}"),
                   "expected_tree": tree, "guard": proof, "status": "staged"}
        RESULT["attempts"].append(attempt)
        directory = EVIDENCE / f"attempt-{refreshes}"
        staged_exact(tree)
        if refreshes == 0:
            run("focused-tests", [sys.executable, "-m", "pytest", "-q", "tools/tests/test_list_naked_candidates.py"])
        # HEAD is the accepted base here, so both immutable parser files are
        # staged and the unchanged pre-commit selects the full WorldBuilder gate.
        git("normal-commit", "commit", "--file", str(PAYLOAD / "commit-message.txt"))
        candidate = inspect_candidate(base, tree, directory / "candidate")
        attempt.update(candidate=candidate, normal_commit_passed=True, status="commit_passed")
        save_result()
        advertised = tip("pre-push-advertised-master")
        if advertised == base:
            refs = f"refs/heads/qualification/parser-candidate {candidate['commit']} refs/heads/master {advertised}\n"
            (directory / "pre-push-stdin.txt").write_text(refs, encoding="utf-8", newline="\n")
            run("normal-pre-push", [str(git_bash), ".githooks/pre-push", "origin", INPUT["upstream"]], stdin=refs.encode())
            attempt["normal_pre_push_passed"] = True
            advertised = tip("post-gate-advertised-master")
            if advertised == base:
                inspect_candidate(base, tree, directory / "candidate")
                attempt["status"] = "passed"
                RESULT.update(status="passed", candidate=candidate, refreshes=refreshes)
                return
        attempt.update(status="master_advanced", observed_master=advertised)
        save_result()
        require(refreshes < MAX_REFRESHES, "Official master kept moving; two refresh cycles exhausted")
        next_base = fetched_master()
        proof = guard_advance(next_base, base, guards)
        next_tree = expected_tree(next_base)
        require(next_base != base, "Official master did not advance consistently; refusing to retry")
        # Rebase only this one unpublished candidate. Preserve its result, then
        # restage that exact delta against the new parent for a fresh ordinary
        # commit. A plain amend would leave no staged delta for pre-commit.
        git("normal-rebase", "rebase", next_base)
        rebased = inspect_candidate(next_base, next_tree, directory / "rebase-output-unverified")
        attempt["rebased_output_before_fresh_hooks"] = rebased
        save_result()
        git("restage-unpublished-candidate", "reset", "--soft", next_base)
        base, tree = next_base, next_tree
        refreshes += 1


def execute():
    save_result()
    try:
        main()
    except (Exception, SystemExit) as error:
        RESULT["status"] = "failed"
        RESULT["error"] = str(error)
        (EVIDENCE / "failure.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise RuntimeError("Qualification failed: " + str(error)) from error
    finally:
        for pattern in ("verify-*/*.compile.log", "verify-*/*.json"):
            for source in (SOURCE / "build/worldbuilder").glob(pattern):
                destination = EVIDENCE / "worldbuilder" / source.relative_to(SOURCE / "build/worldbuilder")
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
        save_result()


if __name__ == "__main__":
    execute()
