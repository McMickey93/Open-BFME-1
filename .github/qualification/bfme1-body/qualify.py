"""One immutable C++ experiment on native Windows; no remote write capability.

Explore calls the project's probe and relocation-aware mismatch tools, leaving
the ledger untouched. Qualify admits one primary body through add_match, then
normal commit/pre-push hooks. A successful probe alone is never qualification.
"""

import argparse
import csv
import hashlib
import io
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


REPOSITORY = "McMickey93/Open-BFME-1"
UPSTREAM = "https://github.com/Open-BFME/Open-BFME-1.git"
LEDGER = "targets/game/reverse/functions.csv"
COMPILER = "inputs/toolchains/vs2003/Program Files/Microsoft Visual Studio .NET 2003/Vc7/bin/cl.exe"
COMPILER_SHA256 = "2ecf86a3edfd3deae498e08298e210e984537ce9e11759930561e43f40bd2515"
PAYLOAD = Path(__file__).resolve().parent
MAX_REFRESHES = 2
SOURCE = Path.cwd().resolve()
EVIDENCE = SOURCE.parent / "evidence"
RESULT = {"status": "starting", "commands": [], "claims": [], "attempts": []}


def require(condition, explanation):
    if not condition:
        raise RuntimeError(explanation)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(value):
    require(isinstance(value, str) and value and "\\" not in value
            and "\0" not in value and ":" not in value, "Invalid repository path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and path.as_posix() == value
            and all(part not in (".", "..") for part in path.parts), "Noncanonical path")
    return path


def allowed_patch_path(value):
    path = safe_path(value)
    if value.startswith("game/"):
        return path.suffix.lower() in (".c", ".cc", ".cpp", ".cxx") and not value.startswith(
            ("game/gen_asm/", "game/gen_small/", "game/masm_dumps/"))
    return (value.startswith(("targets/game/reverse/identity_evidence/",
                              "targets/game/reverse/attempt_support/"))
            and path.suffix.lower() in (".md", ".txt"))


def read_manifest(payload=PAYLOAD):
    data = json.loads((payload / "input-manifest.json").read_text(encoding="utf-8"))
    require(data.get("schema_version") == 1 and data.get("repository") == REPOSITORY
            and data.get("upstream") == UPSTREAM, "Wrong experiment contract")
    require(data.get("mode") in ("explore", "qualify"), "Unknown experiment mode")
    for field in ("base", "base_tree", "patch_tree"):
        require(re.fullmatch(r"[0-9a-f]{40}", data.get(field, "")), "Invalid " + field)
    for name, field in (("candidate.patch", "patch_sha256"), ("commit-message.txt", "message_sha256")):
        require(digest((payload / name).read_bytes()) == data.get(field), "Changed payload: " + name)
    body = data["body"]
    require(re.fullmatch(r"0x[0-9A-F]{8}", body.get("rva", "")), "Invalid body RVA")
    require(isinstance(body.get("size"), int) and 0 < body["size"] <= 32768, "Invalid body size")
    require(isinstance(body.get("symbol"), str) and body["symbol"] and body["symbol"][0] in "?_@"
            and not any(c in body["symbol"] for c in "\r\n\0"), "Invalid body symbol")
    require(allowed_patch_path(body["source"]) and body["source"].startswith("game/"), "Invalid body source")
    require(body.get("replace") in ("rva", "existing", "new"), "Unsupported primary admission mode")
    require(re.fullmatch(r"[A-Za-z0-9_.-]+", data.get("model", "")), "Missing model attribution")
    require(isinstance(data.get("notes"), str) and data["notes"].strip()
            and not any(c in data["notes"] for c in "\r\n\0,"), "Invalid admission evidence")
    claims = data.get("claims", [])
    require(1 <= len(claims) <= 20 and len({c["rva"] for c in claims}) == len(claims), "Invalid claim list")
    require(body["rva"] in {c["rva"] for c in claims}, "Primary body has no claim")
    for claim in claims:
        require(re.fullmatch(r"0x[0-9A-F]{8}", claim.get("rva", "")), "Invalid claim RVA")
        require(re.fullmatch(r"(?:[0-9a-f]{32}|[0-9a-f]{40})", claim.get("lease", "")), "Invalid claim lease")
        require(isinstance(claim.get("owner"), str) and claim["owner"]
                and len(claim["owner"]) <= 200 and not any(c in claim["owner"] for c in "\r\n\0"), "Invalid claim owner")
    require(len({c["owner"] for c in claims}) == 1, "This job needs one explicit claim owner")
    admissions = data.get("admissions", [body])
    require(1 <= len(admissions) <= 4 and len({a["rva"] for a in admissions}) == len(admissions), "Invalid admission sequence")
    require(admissions[-1] == body, "The primary recovery must be the final admission")
    for admission in admissions:
        require(admission["rva"] in {c["rva"] for c in claims}, "Admission is not covered by a real claim")
        require(isinstance(admission["size"], int) and 0 < admission["size"] <= 32768, "Invalid admission extent")
        require(admission["source"] == body["source"], "Dependency repair must stay in this translation unit")
        require(isinstance(admission["symbol"], str) and admission["symbol"] and admission["symbol"][0] in "?_@"
                and not any(c in admission["symbol"] for c in "\r\n\0"), "Invalid admitted symbol")
        if admission != body:
            require(admission.get("replace") == "identity", "Only an explicit identity repair may precede the primary recovery")
            require(isinstance(admission.get("old_symbol"), str) and admission["old_symbol"] and admission["old_symbol"][0] in "?_@"
                    and not any(c in admission["old_symbol"] for c in "\r\n\0"), "Missing old identity")
            proof = admission.get("identity_evidence", "")
            require(allowed_patch_path(proof) and proof.startswith("targets/game/reverse/identity_evidence/")
                    and proof.endswith(".md"), "Invalid identity evidence path")
    files = data.get("files", [])
    require(1 <= len(files) <= 8 and len({f["path"] for f in files}) == len(files), "Invalid patch file set")
    require(body["source"] in {f["path"] for f in files}, "Primary source is not in the patch")
    for entry in files:
        require(allowed_patch_path(entry["path"]), "Patch edits a control, header or generated path")
        require(entry["mode"] == "100644", "Only ordinary source files are supported")
        require(entry.get("base_blob") is None or re.fullmatch(r"[0-9a-f]{40}", entry["base_blob"]), "Invalid preimage")
        if entry.get("deleted"):
            require(entry["base_blob"] is not None and entry.get("candidate_blob") is None
                    and entry.get("sha256") is None and entry["path"] != body["source"], "Invalid deletion")
        else:
            require(re.fullmatch(r"[0-9a-f]{40}", entry.get("candidate_blob", "")), "Invalid candidate blob")
            require(re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256", "")), "Invalid candidate digest")
    for admission in admissions[:-1]:
        require(admission["identity_evidence"] in {f["path"] for f in files if not f.get("deleted")}, "Identity evidence is not in the reviewed patch")
    message = (payload / "commit-message.txt").read_text(encoding="utf-8")
    for claim in claims:
        require(f"Claim-Lease: {claim['rva']}={claim['lease']}" in message.splitlines(), "Missing honest claim trailer")
    return data


def save_result():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "result.json").write_text(json.dumps(RESULT, indent=2) + "\n", encoding="utf-8")


def run(label, argv, *, stdin=None, env=None, required=True):
    filename = f"{len(RESULT['commands']):03d}-{label}.log"
    record = {"label": label, "argv": [str(a) for a in argv], "exit_code": None,
              "log": filename, "attempt": RESULT.get("active_attempt")}
    RESULT["commands"].append(record)
    save_result()
    print("\n>>> " + label, flush=True)
    started, chunks = time.monotonic(), []
    with (EVIDENCE / filename).open("wb") as log:
        process = subprocess.Popen(argv, cwd=SOURCE, env=env,
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
    record["seconds"] = round(time.monotonic() - started, 3)
    save_result()
    if required:
        require(record["exit_code"] == 0, f"{label} failed: exit {record['exit_code']}")
    return record["exit_code"], b"".join(chunks)


def git(label, *args, **kwargs):
    return capture_git(label, *args, log_stdout=True, **kwargs)


def capture_git(label, *args, env=None, log_stdout=False):
    """Read binary/large Git objects without dumping a ledger into job logs."""
    completed = subprocess.run(["git", *args], cwd=SOURCE, env=env, capture_output=True)
    record = {"label": label, "argv": ["git", *args], "exit_code": completed.returncode,
              "stdout_size": len(completed.stdout), "stdout_sha256": digest(completed.stdout),
              "stderr": completed.stderr.decode("utf-8", "replace")}
    if log_stdout:
        filename = f"{len(RESULT['commands']):03d}-{label}.stdout.log"
        (EVIDENCE / filename).write_bytes(completed.stdout)
        record["stdout_log"] = filename
    RESULT["commands"].append(record)
    save_result()
    print(f">>> {label}: exit {completed.returncode}, {len(completed.stdout)} stdout bytes", flush=True)
    if completed.stderr:
        print(record["stderr"], end="", flush=True)
    require(completed.returncode == 0, label + " failed: " + record["stderr"])
    return completed.stdout


def rev(label, ref):
    value = git(label, "rev-parse", "--verify", ref).decode().strip()
    require(re.fullmatch(r"[0-9a-f]{40}", value), "Invalid Git object ID")
    return value


def master_tip(label):
    fields = git(label, "ls-remote", "--exit-code", "origin", "refs/heads/master").decode().split()
    require(len(fields) == 2 and fields[1] == "refs/heads/master"
            and re.fullmatch(r"[0-9a-f]{40}", fields[0]), "Malformed official master advertisement")
    return fields[0]


def fetched_master():
    git("fetch-official-master", "fetch", "--no-tags", "origin",
        "refs/heads/master:refs/remotes/origin/master")
    return rev("fetched-master", "refs/remotes/origin/master")


def claimed_rows(raw, data):
    """Bind every existing matched body in an edited/deleted TU to a claim."""
    wanted = {int(c["rva"], 16) for c in data["claims"]}
    sources = {entry["path"] for entry in data["files"] if entry["path"].startswith("game/")}
    selected, missing = [], set()
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8"))):
        rva = int(row["target_rva"], 16)
        if rva in wanted:
            selected.append(row)
        if row.get("status") == "matched" and row.get("source") in sources and rva not in wanted:
            missing.add(rva)
    require(not missing, "Edited TU has unclaimed matched bodies: " + ", ".join(f"0x{rva:08X}" for rva in sorted(missing)))
    return selected


def guard_advance(data, new_base):
    git("descends-from-reviewed-pin", "merge-base", "--is-ancestor", data["base"], new_base)
    changed = set(git("upstream-paths", "diff", "--name-only", "--no-renames", "-z",
                      data["base"], new_base).decode().split("\0")) - {""}
    protected = []
    for path in changed:
        p, low = PurePosixPath(path), path.lower()
        if (low.startswith(("tools/", ".githooks/", "inputs/", ".github/", "worldbuilder/",
                            "targets/worldbuilder/", "docs/", ".agents/", ".codex/", ".claude/"))
                or p.name.lower() in ("agents.md", "claude.md", "readme.md", "contributing.md",
                                      ".gitattributes", ".gitmodules", ".gitignore", "build.sh", "build.cmd")
                or p.suffix.lower() in (".h", ".hpp", ".hh", ".hxx", ".inl", ".inc")
                or low in ("targets/game/reverse/publisher_mode",
                           "targets/game/reverse/analysis/verifier_upgrade_plan.md")
                or low.startswith("targets/game/reverse/retail_inventory/")
                or (low.startswith("targets/game/reverse/") and any(word in p.name.lower()
                    for word in ("baseline", "whitelist", "flag_region", "flag_override")))):
            protected.append(path)
    require(not protected, "Reviewed controls or shared inputs advanced: " + ", ".join(sorted(protected)))
    for entry in data["files"]:
        raw = git("patch-preimage", "ls-tree", "-z", new_base, "--", entry["path"])
        actual = raw.split(b"\t", 1)[0].decode().split()[2] if raw else None
        require(actual == entry["base_blob"], "Candidate source preimage advanced: " + entry["path"])
    raw = capture_git("claim-row-preconditions", "show", new_base + ":" + LEDGER)
    rows = claimed_rows(raw, data)
    require(rows == data["base_rows"], "A claimed body changed upstream; review its current evidence")
    require(git("publisher-mode", "show", new_base + ":targets/game/reverse/publisher_mode").decode().strip()
            == "off", "Publisher mode must already be off; this job never changes it")
    return {"base": new_base, "reviewed_pin": data["base"], "changed_paths": sorted(changed)}


def expected_tree(data, base):
    with tempfile.TemporaryDirectory(prefix="body-index-") as directory:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(directory) / "index")}
        git("expected-read-base", "read-tree", base, env=env)
        git("expected-check-patch", "apply", "--cached", "--check", str(PAYLOAD / "candidate.patch"), env=env)
        git("expected-apply-patch", "apply", "--cached", str(PAYLOAD / "candidate.patch"), env=env)
        paths = set(git("expected-patch-paths", "diff", "--cached", "--name-only", "-z", base, env=env).decode().split("\0")) - {""}
        require(paths == {f["path"] for f in data["files"]}, "Patch scope differs from its manifest")
        for entry in data["files"]:
            if entry.get("deleted"):
                require(not capture_git("expected-deletion", "ls-files", "--stage", "--", entry["path"], env=env), "Patch deletion differs")
                continue
            raw = capture_git("expected-blob", "show", ":" + entry["path"], env=env)
            require(digest(raw) == entry["sha256"], "Patch candidate content changed")
            staged = capture_git("expected-file-mode", "ls-files", "--stage", "--", entry["path"], env=env)
            require(staged.split(None, 1)[0] == b"100644", "Patch introduced a nonordinary file")
            actual = git("expected-blob-id", "rev-parse", ":" + entry["path"], env=env).decode().strip()
            require(actual == entry["candidate_blob"], "Patch candidate Git blob changed")
        return git("expected-tree", "write-tree", env=env).decode().strip()


def verify_claims(data, label):
    import claims
    require(claims.fetch(), "Cannot read real upstream claims")
    current = claims._read_local()
    proof = []
    for expected in data["claims"]:
        rva = int(expected["rva"], 16)
        entry = current.get(rva)
        require(entry is not None, "No actual upstream claim for " + expected["rva"])
        token, info = entry
        require(info.get("owner") == expected["owner"] and info.get("lease", token) == expected["lease"]
                and info.get("expires", 0) > time.time(), "Claim changed or expired: " + expected["rva"])
        require(claims.holds(rva, token), "Actual upstream claim ref changed during readback")
        proof.append({"rva": expected["rva"], "token": token, "record": info})
    RESULT["claims"].append({"at": label, "checked_at": time.time(), "proof": proof})
    save_result()


def verify_actor(data, actor, triggering_actor):
    require(actor and triggering_actor.casefold() == actor.casefold(),
            "The same account must dispatch and trigger this run")
    expected_owner = re.fullmatch(r"github:([^:]+):bfme1:([a-z0-9][a-z0-9-]{0,60})", data["claims"][0]["owner"])
    require(expected_owner and expected_owner.group(1).casefold() == actor.casefold(),
            "The manifest claim owner is not the dispatching GitHub account")


def collect_build_evidence(label):
    destination = EVIDENCE / "compiler" / label
    # Only a scoped job ran here. Keep its objects, receipts and compiler logs,
    # plus probe's separate experiments; never copy the retail input image.
    patterns = ("match/*.obj", "match/*.json", "match/*.log", "experiments/**/*.obj",
                "experiments/**/*.json", "experiments/**/*.log", "experiments.sqlite",
                "claims/landed_pending.jsonl")
    for pattern in patterns:
        for source in (SOURCE / "build").glob(pattern):
            if source.is_file():
                target = destination / source.relative_to(SOURCE / "build")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)


def allowed_result_paths(data):
    return {f["path"] for f in data["files"]} | {
        LEDGER, "targets/game/reverse/re_attempts.log", "targets/game/reverse/deleted_rows.csv"} | {
        f"targets/game/reverse/attempts/0x{int(body['rva'], 16):08x}.cpp"
        for body in data.get("admissions", [data["body"]])}


def probe_targets(data):
    """Probe the complete claimed TU, using each repaired identity's symbol."""
    targets = {int(row["target_rva"], 16): {
        "rva": f"0x{int(row['target_rva'], 16):08X}", "size": int(row["target_size"]),
        "symbol": row["name"], "source": row["source"]}
        for row in data["base_rows"]
        if row.get("status") == "matched" and row["source"] == data["body"]["source"]}
    for body in data.get("admissions", [data["body"]]):
        targets[int(body["rva"], 16)] = body
    return [targets[rva] for rva in sorted(targets)]


def stage_result(data, base):
    changes = set(git("result-paths", "diff", "--name-only", "-z", base).decode().split("\0")) - {""}
    untracked = set(git("untracked-paths", "ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")) - {""}
    require(not untracked, "Unexpected untracked files: " + ", ".join(sorted(untracked)))
    require(changes and changes <= allowed_result_paths(data), "Admission changed an undeclared path")
    git("stage-explicit-paths", "add", "--", *sorted(changes))
    git("staged-whitespace-check", "diff", "--cached", "--check")
    require(not git("unstaged-result", "diff", "--name-only"), "Unstaged result remains")
    return changes


def cpp_progress(data, base):
    import progress
    head = rev("progress-head", "HEAD")
    text_start, text_size = progress.retail_text()
    def value(ref):
        rows = progress.matched_at(ref)
        return progress.coverage(rows, text_start, text_size, progress.naked_cpp_rows_at(rows, ref))["cpp"]
    # progress caches ledger reads by ref. HEAD changes after a refresh;
    # immutable commit IDs keep the measurement bound to the actual candidate.
    before, after = value(base), value(head)
    result = {"base": base, "head": head, "cpp_exact_before": before,
              "cpp_exact_after": after, "cpp_exact_delta": after - before}
    require(result["cpp_exact_delta"] > 0, "C++ exact is +0 bytes; this is not a completed recovery")
    return result


def export_commit(data, base, directory):
    directory.mkdir(parents=True, exist_ok=True)
    commit = rev("candidate-commit", "HEAD")
    parents = git("candidate-parents", "rev-list", "--parents", "-n", "1", "HEAD").decode().split()
    require(parents == [commit, base], "Candidate is not one normal commit on its accepted base")
    require(not git("candidate-status", "status", "--porcelain"), "Candidate checkout is not clean")
    raw_commit = capture_git("candidate-raw-commit", "cat-file", "commit", commit)
    message = raw_commit.split(b"\n\n", 1)[1]
    require(message == (PAYLOAD / "commit-message.txt").read_bytes(), "Candidate commit message differs")
    (directory / "commit-object.txt").write_bytes(raw_commit)
    (directory / "candidate.patch").write_bytes(capture_git("candidate-patch", "diff", "--binary", "--full-index", base, commit))
    files = []
    changes = git("committed-paths", "diff", "--name-only", "-z", base, commit).decode().split("\0")
    for path in filter(None, changes):
        require(path in allowed_result_paths(data), "Committed path exceeds scope: " + path)
        record = git("candidate-tree-entry", "ls-tree", "-z", commit, "--", path)
        if not record:
            files.append({"path": path, "deleted": True})
            continue
        mode, kind, blob = record.split(b"\t", 1)[0].decode().split()
        require(kind == "blob" and mode == "100644", "Non-file output is not publishable")
        content = (SOURCE / path).read_bytes()
        require(git("candidate-hash", "hash-object", "--", path).decode().strip() == blob, "Checkout differs from committed blob")
        target = directory / "candidate-files" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        files.append({"path": path, "mode": mode, "blob": blob, "sha256": digest(content),
                      "size": len(content), "content_file": target.relative_to(EVIDENCE).as_posix()})
    return {"repository": "Open-BFME/Open-BFME-1", "base": base, "commit": commit,
            "tree": rev("candidate-tree", "HEAD^{tree}"), "message": message.decode("utf-8"),
            "files": files, "claims": data["claims"], "progress": cpp_progress(data, base),
            "published": False, "normal_commit_passed": True}


def main(data):
    require(sys.platform == "win32" and sys.version_info[:2] == (3, 12), "Native Windows Python 3.12 is required")
    require(os.environ.get("GITHUB_REPOSITORY") == REPOSITORY
            and os.environ.get("GITHUB_REF") == "refs/heads/master", "Wrong workflow repository or branch")
    verify_actor(data, os.environ.get("GITHUB_ACTOR", ""), os.environ.get("GITHUB_TRIGGERING_ACTOR", ""))
    git_bash = Path(os.environ.get("BFME_QUALIFICATION_BASH", ""))
    require(git_bash.is_absolute() and git_bash.is_file(), "Calling Git Bash path is missing")
    require(rev("source-pin", "HEAD") == data["base"]
            and rev("source-tree", "HEAD^{tree}") == data["base_tree"], "Wrong official source pin")
    require(not git("initial-status", "status", "--porcelain"), "Source pin is not clean")
    require(git("origin-url", "remote", "get-url", "origin").decode().strip().removesuffix(".git")
            == UPSTREAM.removesuffix(".git"), "Wrong real upstream origin")
    require(digest((SOURCE / COMPILER).read_bytes()) == COMPILER_SHA256, "Original MSVC 7.1 compiler changed")
    require(expected_tree(data, data["base"]) == data["patch_tree"], "Reviewed patch tree differs")
    for filename in ("input-manifest.json", "candidate.patch", "commit-message.txt"):
        shutil.copyfile(PAYLOAD / filename, EVIDENCE / filename)
    base = fetched_master()
    guard = guard_advance(data, base)
    git("body-branch", "switch", "-c", "qualification/native-body", base)
    run("install-requirements", [sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
                                 "--no-cache-dir", "-r", "tools/requirements.txt"])
    run("python-packages", [sys.executable, "-m", "pip", "freeze"])
    run("initial-ledger-check", [sys.executable, "tools/check_csv.py"])
    run("setup-hooks", [str(git_bash), "tools/setup_hooks.sh"])
    require(git("hooks-path", "config", "--get", "core.hooksPath").decode().strip() == ".githooks", "Ordinary hooks required")
    git("author-name", "config", "user.name", "ChatGPT")
    git("author-email", "config", "user.email", "chatgpt@localhost")
    os.environ["BFME_CLAIM_OWNER"] = data["claims"][0]["owner"]
    os.environ["BFME_MODEL"] = data["model"]
    require(os.environ.get("BFME_CLAIMS", "on") != "off", "Claims must not be disabled")
    sys.path.insert(0, str(SOURCE / "tools"))
    verify_claims(data, "before-body-edit")
    body = data["body"]
    run("callee-evidence", [sys.executable, "tools/callees.py", body["rva"], str(body["size"])])
    tree = expected_tree(data, base)
    git("apply-candidate", "apply", "--index", str(PAYLOAD / "candidate.patch"))
    require(git("applied-patch-tree", "write-tree").decode().strip() == tree, "Applied patch tree differs")
    require(rev("applied-tree", ":0:" + body["source"]) == next(f["candidate_blob"] for f in data["files"]
                                                                 if f["path"] == body["source"]), "Applied source differs")
    RESULT["attempts"].append({"base": base, "guard": guard, "patch_tree": tree})
    RESULT["probes"] = []
    for target in probe_targets(data):
        code, output = run("probe-" + target["rva"], [sys.executable, "tools/probe.py", target["source"], target["symbol"],
                              target["rva"], "--size", str(target["size"]), "--all", "--shape"], required=False)
        RESULT["probes"].append({"rva": target["rva"], "exit_code": code,
                                "diagnostic_exact_modulo_relocations": b"result   EXACT" in output,
                                "is_qualification": False})
        if code == 0:
            run("explain-mismatch-" + target["rva"], [sys.executable, "tools/explain_mismatch.py", target["symbol"],
                    "--rva", target["rva"], "--size", str(target["size"]), "--source", target["source"]], required=False)
    collect_build_evidence("probe")
    if data["mode"] == "explore":
        run("session-progress", [sys.executable, "tools/progress.py", "origin/master"])
        good = all(probe["exit_code"] == 0 for probe in RESULT["probes"])
        RESULT["status"] = "explored" if good else "compile_failed"
        RESULT["published"] = False
        require(good, "Exploratory compilation failed; inspect retained diagnostics")
        return
    require(all(probe["exit_code"] == 0 for probe in RESULT["probes"]), "Cannot admit a body that did not compile")
    verify_claims(data, "before-admission")
    for target in data.get("admissions", [body]):
        command = [sys.executable, "tools/add_match.py", target["symbol"], target["rva"], str(target["size"]),
                   target["source"], "--notes", data["notes"], "--model", data["model"]]
        if target["replace"] in ("rva", "identity"):
            command += ["--replace-rva", target["rva"]]
        elif target["replace"] == "existing":
            command += ["--replace-existing"]
        if target["replace"] == "identity":
            command += ["--correct-identity", target["old_symbol"], "--identity-evidence", target["identity_evidence"]]
        run("verified-add-match-" + target["rva"], command)
    run("ordinary-scoped-build", [str(git_bash), "build.sh", body["source"]])
    stage_result(data, base)
    run("ledger-check", [sys.executable, "tools/check_csv.py"])
    for refresh in range(MAX_REFRESHES + 1):
        RESULT["active_attempt"] = refresh
        verify_claims(data, "before-normal-commit")
        git("normal-commit", "commit", "--file", str(PAYLOAD / "commit-message.txt"))
        directory = EVIDENCE / f"qualification-{refresh}"
        candidate = export_commit(data, base, directory)
        advertised = master_tip("pre-gate-master")
        if advertised == base:
            refs = f"refs/heads/qualification/native-body {candidate['commit']} refs/heads/master {base}\n"
            (directory / "pre-push-stdin.txt").write_text(refs, encoding="utf-8", newline="\n")
            run("normal-pre-push", [str(git_bash), ".githooks/pre-push", "origin", UPSTREAM], stdin=refs.encode())
            verify_claims(data, "after-normal-pre-push")
            advertised = master_tip("post-gate-master")
            if advertised == base:
                run("session-progress", [sys.executable, "tools/progress.py", "origin/master"])
                final = export_commit(data, base, directory)
                final["normal_pre_push_passed"] = True
                final["workflow"] = RESULT["workflow"]
                (EVIDENCE / "publication-manifest.json").write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
                RESULT.update(status="qualified", candidate=final, published=False)
                return
        require(refresh < MAX_REFRESHES, "Official master advanced repeatedly; preserve this result and review a fresh pin")
        next_base = fetched_master()
        guard = guard_advance(data, next_base)
        require(next_base != base, "Inconsistent upstream advertisement")
        git("ordinary-rebase", "rebase", next_base)
        for entry in candidate["files"]:
            if entry["path"].startswith(("game/", "targets/game/reverse/identity_evidence/",
                                          "targets/game/reverse/attempt_support/")):
                raw = git("rebased-body-entry", "ls-tree", "-z", "HEAD", "--", entry["path"])
                actual = raw.split(b"\t", 1)[0].decode().split()[2] if raw else None
                require(actual == (None if entry.get("deleted") else entry["blob"]), "Rebase changed reviewed body/evidence bytes")
        # Restage this one unpublished commit so normal pre-commit sees the
        # full body/ledger delta again, instead of amending an empty index.
        git("restage-unpublished-body", "reset", "--soft", next_base)
        base = next_base
        stage_result(data, base)
        RESULT["attempts"].append({"base": base, "guard": guard})


def execute():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout-pin", action="store_true")
    args = parser.parse_args()
    data = read_manifest()
    if args.checkout_pin:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
            handle.write("sha=" + data["base"] + "\n")
        return
    RESULT.update(input=data, workflow={key: os.environ.get(key) for key in (
        "GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_ACTOR",
        "GITHUB_TRIGGERING_ACTOR", "RUNNER_OS", "ImageVersion")})
    save_result()
    try:
        main(data)
    except (Exception, SystemExit) as error:
        RESULT.update(status="failed", error=str(error), published=False)
        (EVIDENCE / "failure.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
    finally:
        collect_build_evidence("final")
        # Preserve tool-written evidence even when a later hook rejects it.
        for path in sorted(allowed_result_paths(data)):
            source = SOURCE / path
            if source.is_file():
                target = EVIDENCE / "final-worktree" / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        save_result()


if __name__ == "__main__":
    execute()
