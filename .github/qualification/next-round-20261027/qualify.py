"""Native qualification of one fixed link/header cleanup; never a body recovery.

The read-only job uses the project's ordinary builders, commit hooks and actual
upstream pre-push gate. A separate job transfers only those exact Git objects
to a fresh contributor-fork branch. Neither job can write official master.
"""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time
import traceback

CONTROL = Path(__file__).resolve().parent
DATA = json.loads((CONTROL / "payload.json").read_text(encoding="utf-8"))
SOURCE = Path.cwd().resolve()
EVIDENCE = SOURCE.parent / "qualification-evidence"
BUNDLE = SOURCE.parent / "qualified-objects"
RECEIPT = {"schema": 1, "status": "starting", "commands": [], "claims": []}
LOCAL_REF = "refs/heads/qualification/next-round"
SHA = re.compile(r"[0-9a-f]{40}")

def require(value, message):
    if not value:
        raise RuntimeError(message)

def save():
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "result.json").write_text(json.dumps(RECEIPT, indent=2) + "\n", encoding="utf-8")

def run(label, args, stdin=None, env=None, allowed=(0,), quiet=False):
    save()
    log = EVIDENCE / ("%03d-%s.log" % (len(RECEIPT["commands"]), label))
    item = {"label": label, "log": log.name, "exit_code": None}
    RECEIPT["commands"].append(item)
    print(">>> " + label, flush=True)
    start = time.monotonic()
    with log.open("wb") as stream:
        process = subprocess.Popen([str(x) for x in args], cwd=SOURCE, env=env,
                                   stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if stdin is not None:
            process.stdin.write(stdin)
            process.stdin.close()
        last = time.monotonic()
        for line in process.stdout:
            stream.write(line)
            if not quiet:
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
            elif time.monotonic() - last > 25:
                stream.flush()
                print("    %s: still running (%ds)" % (label, time.monotonic() - start), flush=True)
                last = time.monotonic()
        item["exit_code"] = process.wait()
    item["seconds"] = round(time.monotonic() - start, 2)
    save()
    output = log.read_bytes()
    if quiet or item["exit_code"] not in allowed:
        print(output.decode("utf-8", errors="replace")[-5000:], flush=True)
    require(item["exit_code"] in allowed, "%s failed: %s; log=%s" % (label, item["exit_code"], log.name))
    return output

def git(label, *args, **kw):
    return run(label, ["git", *args], **kw)

def rev(ref):
    value = git("resolve", "rev-parse", "--verify", ref, quiet=True).decode().strip()
    require(SHA.fullmatch(value), "Invalid Git object ID")
    return value

def path(value):
    p = PurePosixPath(value)
    require(value and "\\" not in value and ":" not in value and "\0" not in value
            and not p.is_absolute() and all(s not in (".", "..") for s in p.parts)
            and p.as_posix() == value, "Unsafe repository path")
    return SOURCE / value

def validate_context():
    require(sys.platform == "win32" and sys.version_info[:2] == (3, 12), "Native Windows Python 3.12 required")
    require(DATA["schema"] == 1 and DATA["purpose"] == "verified-cleanup" and DATA["expected_cpp_delta"] == 0,
            "This workflow is only for fixed, zero-coverage cleanup")
    require(DATA["fork"] in ("McMickey93/Open-BFME-1", "McMickey93/Open-BFME-2"), "Wrong fork")
    require(os.environ.get("GITHUB_REPOSITORY") == DATA["fork"]
            and os.environ.get("GITHUB_REF") == "refs/heads/" + DATA["control_branch"]
            and os.environ.get("GITHUB_EVENT_NAME") == "create", "Wrong workflow context")
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    require(event["ref_type"] == "branch" and event["ref"] == DATA["control_branch"]
            and event["repository"]["fork"] is True and event["repository"]["private"] is False, "Wrong creation event")
    require(DATA["upstream"] == "https://github.com/Open-BFME/" + DATA["fork"].split("/")[1] + ".git", "Wrong upstream")
    require(SHA.fullmatch(DATA["base"]), "Invalid source pin")
    require(git("origin", "remote", "get-url", "origin", quiet=True).decode().strip().removesuffix(".git")
            == DATA["upstream"].removesuffix(".git"), "Official origin required")
    require(rev("HEAD") == DATA["base"], "Wrong initial official checkout")
    require(not git("clean-start", "status", "--porcelain", quiet=True), "Initial checkout is dirty")
    require(rev("HEAD:AGENTS.md") == DATA["agents_blob"], "AGENTS changed: review required")
    require(os.environ.get("BFME_CLAIMS", "on") != "off", "Claims must remain enabled")
    for variable in ("BUILD_RECOMPILE_ONLY", "CL", "_CL_"):
        require(not os.environ.get(variable), "Unexpected compiler/cache override")
    bash = Path(os.environ.get("BFME_QUALIFICATION_BASH", ""))
    require(bash.is_absolute() and bash.is_file(), "Real Git Bash required")
    RECEIPT["workflow"] = {k: os.environ.get(k, "") for k in
                           ("GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_REF", "GITHUB_RUN_ID",
                            "GITHUB_RUN_ATTEMPT", "GITHUB_ACTOR", "GITHUB_TRIGGERING_ACTOR")}
    RECEIPT["input"] = DATA
    return bash

def master(fetch=False):
    raw = git("actual-master", "ls-remote", "--exit-code", "origin", "refs/heads/master", quiet=True).decode().split()
    require(len(raw) == 2 and raw[1] == "refs/heads/master" and SHA.fullmatch(raw[0]), "Cannot read official master")
    if fetch:
        git("fetch-master", "fetch", "--no-tags", "--recurse-submodules=no", "origin",
            "+refs/heads/master:refs/remotes/origin/master", quiet=True)
        require(rev("refs/remotes/origin/master") == raw[0], "Official master raced the fetch; retry with new pin")
    return raw[0]

def init_reference():
    ref = DATA["reference_path"]
    git("init-reference", "-c", "submodule.recurse=false", "submodule", "update", "--init",
        "--depth", "1", "--", ref, quiet=True)
    require(not git("reference-clean", "-C", ref, "status", "--porcelain", quiet=True), "Dirty donor inputs")
    require(git("reference-pin", "-C", ref, "rev-parse", "HEAD", quiet=True).decode().strip()
            == rev("HEAD:" + ref), "Reference differs from the committed pin")

def claims(label):
    import claims as module
    specs = module._refspecs(module.SEEN) if DATA["project"] == 2 else [
        "+" + module.NS + "*:" + module.SEEN + "*",
        "+" + module.LEGACY_NS + "*:" + module.LEGACY_MIRROR + "*"]
    git("shallow-claims", "fetch", "-q", "--prune", "--depth=1", "--no-tags",
        "--recurse-submodules=no", "origin", *specs, quiet=True)
    require(module.fetch(), "Cannot refresh real official claims")
    current = module._read_local()
    expected = DATA["claim"]
    key = module.key_of(expected["key"]) if DATA["project"] == 2 else int(expected["key"], 16)
    entry = current.get(key)
    require(entry is not None, "Claim missing")
    token, info = entry
    require(info.get("owner") == expected["owner"] and info.get("lease", token) == expected["lease"]
            and info.get("expires", 0) > time.time(), "Claim changed or expired; stop")
    require(module.holds(key, token), "Actual claim fencing token changed")
    RECEIPT["claims"].append({"at": label, "token": token, "info": info})
    save()
    return module, key, token, info

def object_definitions(label, expected):
    import build
    name = DATA["competing_symbol"]
    entries = []
    for src in DATA["consumers"]:
        obj = build.obj_path(SOURCE / src)
        require(obj.is_file(), "Missing verified consumer object")
        symbols = build.read_object_symbols(obj.read_bytes())
        defined = any(s["name"] == name and s["section"] > 0 and s["storage"] == 2 for s in symbols)
        require(defined is expected, "Unexpected competing COMDAT state: " + src)
        entries.append({"source": src, "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(), "defined": defined})
    RECEIPT[label] = entries
    save()

def scoped(bash, label):
    run(label, [bash, "build.sh", *DATA["consumers"], *DATA["providers"]], quiet=True)
    for src in DATA["consumers"]:
        run(label + "-declared", [sys.executable, "tools/find_declared_unmatched.py", src], quiet=True)

def apply_group(group):
    edited = []
    for file in group["files"]:
        p = path(file["path"])
        old = p.read_bytes() if p.exists() else b""
        if "base_blob" in file:
            actual = git("preimage", "hash-object", "--", file["path"], quiet=True).decode().strip() if p.exists() else None
            require(actual == file["base_blob"], "Reviewed preimage changed: " + file["path"])
        if file["kind"] == "replace":
            new = old
            for item in file["replacements"]:
                before, after = item["old"].encode(), item["new"].encode()
                require(new.count(before) == 1, "Replacement is not unique: " + file["path"])
                new = new.replace(before, after)
        elif file["kind"] == "append":
            require(next(line for line in file["text"].splitlines() if line.strip()) not in old.decode("utf-8"), "Documentation entry already exists")
            new = old + file["text"].encode()
        else:
            require(file["kind"] == "new" and not p.exists(), "Unexpected file creation")
            new = file["text"].encode()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(new)
        edited.append(file["path"])
    for record in group.get("attempt_records", []):
        run("record-original-attempt", [sys.executable, "tools/re_log.py", "record", *record], quiet=True)
        edited.append(DATA["attempt_log"])
    if group.get("refresh_reference"):
        ref, target = DATA["reference_path"], DATA["new_reference"]
        git("fetch-reviewed-reference", "-C", ref, "fetch", "--depth=1", "--no-tags",
            "--recurse-submodules=no", "origin", target, quiet=True)
        git("checkout-reviewed-reference", "-C", ref, "checkout", "--detach", target, quiet=True)
        require(not git("refreshed-reference-clean", "-C", ref, "status", "--porcelain", quiet=True), "Dirty reference")
        edited.append(ref)
    git("stage-explicit-paths", "add", "--", *sorted(set(edited)), quiet=True)
    return sorted(set(edited))

def allowed_paths():
    result = set()
    for group in DATA["groups"]:
        result.update(f["path"] for f in group["files"])
        if group.get("attempt_records"):
            result.add(DATA["attempt_log"])
        if group.get("refresh_reference"):
            result.add(DATA["reference_path"])
    return result

def verify_scope(base):
    changed = set(filter(None, git("qualified-paths", "diff", "--name-only", "-z", base, "HEAD", quiet=True).decode().split("\0")))
    require(changed <= allowed_paths() and set(DATA["consumers"]) <= changed, "Outgoing files differ from the exact cleanup scope")
    for name in DATA["immutable_ledgers"]:
        require(rev(base + ":" + name) == rev("HEAD:" + name), "Cleanup changed a function, pin or debt ledger")
    require(rev("HEAD:AGENTS.md") == DATA["agents_blob"], "AGENTS changed during qualification")
    require(not git("qualified-clean", "status", "--porcelain", quiet=True), "Outgoing checkout is dirty")

def progress(base):
    import progress as module
    head = rev("HEAD")
    start, size = module.retail_text()
    def cpp(ref):
        rows = module.matched_at(ref)
        return module.coverage(rows, start, size, module.naked_cpp_rows_at(rows, ref))["cpp"]
    before, after = cpp(base), cpp(head)
    require(after - before == DATA["expected_cpp_delta"] == 0, "Cleanup coverage unexpectedly changed")
    run("required-progress", [sys.executable, "tools/progress.py", "origin/master"], quiet=True)
    return {"base": base, "head": head, "cpp_exact_before": before, "cpp_exact_after": after, "cpp_exact_delta": 0}

def qualified(bash):
    os.environ["BFME_CLAIM_OWNER"] = DATA["claim"]["owner"]
    os.environ["BFME_MODEL"] = "OpenAI-Codex"
    sys.path.insert(0, str(SOURCE / "tools"))
    base = master(fetch=True)
    git("qualification-branch", "switch", "-c", LOCAL_REF.removeprefix("refs/heads/"), base, quiet=True)
    require(rev("HEAD:AGENTS.md") == DATA["agents_blob"], "Fresh official AGENTS changed")
    init_reference()
    compiler = path(DATA["compiler"])
    require(hashlib.sha256(compiler.read_bytes()).hexdigest() == DATA["compiler_sha256"], "Original compiler changed")
    run("requirements", [sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
                         "-r", "tools/requirements.txt"], quiet=True)
    run("ordinary-hook-setup", [bash, "tools/setup_hooks.sh"], quiet=True)
    require(git("normal-hooks", "config", "--get", "core.hooksPath", quiet=True).decode().strip() == ".githooks",
            "Normal project hooks required")
    git("public-author", "config", "user.name", "McMickey93", quiet=True)
    git("public-email", "config", "user.email", "347452154+McMickey93@users.noreply.github.com", quiet=True)
    git("no-interactive-editor", "config", "core.editor", "true", quiet=True)
    run("initial-ledger", [sys.executable, "tools/check_csv.py"], quiet=True)
    claims("before-work")
    scoped(bash, "baseline-whole-consumers-and-providers")
    if DATA["project"] == 1:
        object_definitions("before_comdat", True)
        run("link-preview-before", [sys.executable, "tools/link_check.py", "--hook", "--deadline", "20",
                                   "--compile-limit", "0", *DATA["consumers"]], quiet=True)
    else:
        run("crt-header-index", [sys.executable, "tools/ms_header_audit.py", "index"], quiet=True)
        run("crt-header-before", [sys.executable, "tools/ms_header_audit.py", "show", *DATA["consumers"]], quiet=True)
        # The BFME1 reference is a build input: compare full native gates at
        # the same BFME2 revision, never stamp a partial or interrupted check.
        run("full-before-reference-refresh", [bash, "build.sh"], quiet=True)
    for index, group in enumerate(DATA["groups"]):
        claims("before-group-" + str(index))
        apply_group(group)
        if group.get("refresh_reference") and DATA["project"] == 2:
            advertised = git("actual-bfme1-master", "-C", DATA["reference_path"], "ls-remote", "origin",
                             "refs/heads/master", quiet=True).decode().split()
            require(advertised[0] == DATA["new_reference"], "BFME1 advanced: review the reference refresh")
            run("full-after-reference-refresh", [bash, "build.sh"], quiet=True)
            stamp = path("build/bfme1-last-check.txt")
            stamp.write_text(json.dumps({"checked_at": time.time(), "upstream": DATA["new_reference"],
                                         "verified": True, "method": "native-full-before-and-after"}) + "\n")
        if index == len(DATA["groups"]) - 1:
            scoped(bash, "changed-whole-consumers-and-providers")
            if DATA["project"] == 1:
                object_definitions("after_comdat", False)
                run("link-preview-after", [sys.executable, "tools/link_check.py", "--hook", "--deadline", "20",
                                           "--compile-limit", "0", *DATA["consumers"]], quiet=True)
            else:
                run("crt-header-after", [sys.executable, "tools/ms_header_audit.py", "show", *DATA["consumers"]], quiet=True)
                run("crt-header-check", [sys.executable, "tools/ms_header_audit.py", "check", *DATA["consumers"]], quiet=True)
                eh = EVIDENCE / "eh-exact.json"
                run("complete-eh-graph", [sys.executable, "tools/eh_verify.py", *DATA["consumers"], "--json", eh], quiet=True)
                verdicts = json.loads(eh.read_text())
                require(verdicts and all(v[0] == "EXACT" for v in verdicts.values()), "EH graph is not fully exact")
        run("staged-ledger", [sys.executable, "tools/check_csv.py", "--staged"], quiet=True)
        git("staged-diff-check", "diff", "--cached", "--check", quiet=True)
        message = EVIDENCE / ("message-%d.txt" % index)
        message.write_text(group["message"], encoding="utf-8", newline="\n")
        git("normal-native-commit-" + str(index), "commit", "--file", message, quiet=True)
    for retry in range(4):
        verify_scope(base)
        claims("before-actual-push-gate")
        if master() == base:
            head = rev("HEAD")
            refs = ("%s %s refs/heads/master %s\n" % (LOCAL_REF, head, base)).encode()
            run("ordinary-actual-official-pre-push", [bash, ".githooks/pre-push", "origin", DATA["upstream"]],
                stdin=refs, quiet=True)
            claims("after-actual-push-gate")
            if master() == base:
                break
        require(retry < 3, "Official master kept moving: qualified objects retained for a reviewed rebase")
        new_base = master(fetch=True)
        # Ordinary rebase/post-rewrite hooks remain enabled.
        git("ordinary-rebase", "-c", "submodule.recurse=false", "rebase", new_base, quiet=True)
        base = new_base
        pinned = rev("HEAD:" + DATA["reference_path"])
        require(git("rebase-reference", "-C", DATA["reference_path"], "rev-parse", "HEAD", quiet=True).decode().strip()
                == pinned, "Rebase changed the reference: refresh and requalify explicitly")
        scoped(bash, "rebased-whole-consumers-and-providers")
    verify_scope(base)
    measured = progress(base)
    module, key, token, info = claims("before-object-export")
    # Generate release metadata through the real project tool; publication of
    # this expired marker is left to the coordinator after the actual landing.
    release_sha = module._record(DATA["claim"]["owner"], -1, "Completed cleanup; released after publication",
                                 lease=DATA["claim"]["lease"], since=info.get("since"),
                                 **({"scope": info.get("scope", ""), "locks": info.get("locks", ())}
                                    if DATA["project"] == 2 else {}))
    release_raw = git("tool-generated-release", "show", "-s", "--format=%B", release_sha, quiet=True).decode().strip()
    head = rev("HEAD")
    files = []
    for name in sorted(set(filter(None, git("export-paths", "diff", "--name-only", "-z", base, "HEAD", quiet=True).decode().split("\0")))):
        entry = git("qualified-tree-entry", "ls-tree", "HEAD", "--", name, quiet=True).decode().strip()
        mode, kind, rest = entry.split(" ", 2)
        oid, actual = rest.split("\t", 1)
        require(actual == name and mode in ("100644", "160000") and kind in ("blob", "commit"), "Unexpected output type")
        files.append({"path": name, "mode": mode, "kind": kind, "sha": oid})
    BUNDLE.mkdir(exist_ok=True)
    git("native-object-bundle", "bundle", "create", BUNDLE / "candidate.bundle", base + ".." + LOCAL_REF, quiet=True)
    manifest = {"schema": 1, "purpose": "verified-cleanup", "fork": DATA["fork"], "base": base, "commit": head,
                "tree": rev("HEAD^{tree}"), "local_ref": LOCAL_REF, "files": files,
                "normal_commit_hooks_passed": True, "normal_actual_official_pre_push_passed": True,
                "progress": measured, "workflow": RECEIPT["workflow"], "claim": DATA["claim"],
                "claim_token": token, "release_message": release_raw,
                "bundle_sha256": hashlib.sha256((BUNDLE / "candidate.bundle").read_bytes()).hexdigest(),
                "result_branch": DATA["result_branch"]}
    (BUNDLE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    RECEIPT.update(status="qualified", publication=manifest)
    save()
    print("QUALIFIED_OBJECTS " + json.dumps(manifest), flush=True)

def transfer(bash):
    os.environ["BFME_CLAIM_OWNER"] = DATA["claim"]["owner"]
    os.environ["BFME_MODEL"] = "OpenAI-Codex"
    # This job never executes any source or code supplied by the artifact.
    manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
    for key in ("schema", "purpose", "fork", "result_branch"):
        require(manifest[key] == (1 if key == "schema" else DATA[key]), "Wrong handoff identity")
    require(manifest["workflow"] == DATA["qualification_context"] and manifest == DATA["expected_manifest"],
            "Artifact differs from the pinned successful read-only qualification job")
    require(manifest["normal_commit_hooks_passed"] is True
            and manifest["normal_actual_official_pre_push_passed"] is True
            and manifest["progress"]["cpp_exact_delta"] == 0, "Native cleanup qualification missing")
    require(manifest["local_ref"] == LOCAL_REF and SHA.fullmatch(manifest["base"])
            and SHA.fullmatch(manifest["commit"]) and SHA.fullmatch(manifest["tree"]), "Invalid Git manifest")
    require({f["path"] for f in manifest["files"]} <= allowed_paths() and set(DATA["consumers"]) <= {f["path"] for f in manifest["files"]}, "Unexpected artifact paths")
    bundle = BUNDLE / "candidate.bundle"
    require(hashlib.sha256(bundle.read_bytes()).hexdigest() == manifest["bundle_sha256"], "Git bundle differs")
    git("fetch-qualified-base", "fetch", "--no-tags", "--recurse-submodules=no", "origin", manifest["base"], quiet=True)
    git("verify-native-bundle", "bundle", "verify", bundle, quiet=True)
    git("import-native-objects", "fetch", "--no-tags", "--recurse-submodules=no", bundle,
        LOCAL_REF + ":" + LOCAL_REF, quiet=True)
    require(rev(LOCAL_REF) == manifest["commit"] and rev(LOCAL_REF + "^{tree}") == manifest["tree"], "Objects changed")
    for file in manifest["files"]:
        entry = git("imported-tree-entry", "ls-tree", LOCAL_REF, "--", file["path"], quiet=True).decode().strip()
        require(entry == "%s %s %s\t%s" % (file["mode"], file["kind"], file["sha"], file["path"]), "Wrong imported file")
    actual = set(filter(None, git("imported-paths", "diff", "--name-only", "-z", manifest["base"],
                                 LOCAL_REF, quiet=True).decode().split("\0")))
    require(actual == {f["path"] for f in manifest["files"]}, "Unreviewed commit content")
    git("fast-forward-lineage", "merge-base", "--is-ancestor", manifest["base"], LOCAL_REF, quiet=True)
    # The changed-path proof excludes tools and hooks. Check out the exact
    # qualified commit: the ordinary push hook requires HEAD to be outgoing.
    # No game binary is executed. The normal official hook remains enabled.
    git("checkout-qualified-commit", "switch", LOCAL_REF.removeprefix("refs/heads/"), quiet=True)
    require(rev("HEAD") == manifest["commit"], "Wrong outgoing checkout")
    init_reference()
    run("transfer-requirements", [sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
                                  "-r", "tools/requirements.txt"], quiet=True)
    run("ordinary-transfer-hook-setup", [bash, "tools/setup_hooks.sh"], quiet=True)
    token = os.environ.pop("BFME_TRANSFER_TOKEN", "")
    require(token and "\n" not in token and "\r" not in token, "Ephemeral fork token missing")
    url = "https://github.com/" + DATA["fork"] + ".git"
    target = "refs/heads/" + DATA["result_branch"]
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_TRACE") and k != "GIT_CURL_VERBOSE"}
    count = int(env.get("GIT_CONFIG_COUNT", "0"))
    auth = "AUTHORIZATION: basic " + base64.b64encode(("x-access-token:" + token).encode()).decode()
    env.update({"GIT_CONFIG_COUNT": str(count + 1), "GIT_CONFIG_KEY_" + str(count): "http." + url + ".extraheader",
                "GIT_CONFIG_VALUE_" + str(count): auth, "GIT_TERMINAL_PROMPT": "0"})
    # Empty lease permits creation only. It never overwrites an existing ref.
    run("create-qualified-fork-branch", ["git", "push", "--porcelain",
        "--force-with-lease=" + target + ":", url, LOCAL_REF + ":" + target], env=env, quiet=True)
    raw = git("published-fork-readback", "ls-remote", "--exit-code", url, target, quiet=True).decode().split()
    require(raw == [manifest["commit"], target], "Fork transfer readback differs")
    RECEIPT.update(status="transferred", publication=manifest)
    save()
    print("TRANSFERRED_QUALIFIED_COMMIT " + json.dumps(manifest), flush=True)

try:
    bash = validate_context()
    if sys.argv[1:] == ["qualify"]:
        qualified(bash)
    elif sys.argv[1:] == ["transfer"]:
        transfer(bash)
    else:
        raise RuntimeError("Choose qualify or transfer")
except BaseException as error:
    RECEIPT.update(status="failed", error=str(error))
    save()
    traceback.print_exc()
    raise
