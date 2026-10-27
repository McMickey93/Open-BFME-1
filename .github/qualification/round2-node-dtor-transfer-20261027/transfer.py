"""Import one reviewed native commit and run normal hooks; write only this public fork."""
import base64, hashlib, json, os, subprocess, sys, time, urllib.request
from pathlib import Path

CONTROL = Path(__file__).resolve().parent
DATA = json.loads((CONTROL / "manifest.json").read_text(encoding="utf-8"))
ROOT = Path.cwd()
OUT = ROOT.parent / "source-transfer-evidence"
OUT.mkdir(exist_ok=True)
RESULT = {"schema": 1, "status": "starting", "commands": []}

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def save():
    (OUT / "result.json").write_text(json.dumps(RESULT, indent=2) + "\n", encoding="utf-8")

def run(label, args, stdin=None, env=None):
    print(">>> " + label, flush=True)
    log = OUT / ("%02d-%s.log" % (len(RESULT["commands"]), label))
    entry = {"label": label, "exit_code": None, "log": log.name}
    RESULT["commands"].append(entry)
    save()
    with log.open("wb") as stream:
        proc = subprocess.Popen([str(x) for x in args], cwd=ROOT, env=env,
                                stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                stdout=stream, stderr=subprocess.STDOUT)
        if stdin is not None:
            proc.stdin.write(stdin)
            proc.stdin.close()
        while proc.poll() is None:
            try:
                proc.wait(timeout=25)
            except subprocess.TimeoutExpired:
                print("    " + label + ": still running", flush=True)
        entry["exit_code"] = proc.returncode
    save()
    output = log.read_bytes()
    print(output.decode("utf-8", errors="replace")[-3000:], flush=True)
    require(proc.returncode == 0, label + " failed")
    return output

def git(label, *args, **kwargs):
    return run(label, ["git", *args], **kwargs)

def rev(ref):
    return subprocess.check_output(["git", "rev-parse", "--verify", ref], cwd=ROOT, text=True).strip()

def claim():
    require(len(DATA["claims"]) == 2, "Both body leases required")
    for scope in DATA["claims"]:
        git("fetch-own-claim", "fetch", "-q", "--depth=1", "--no-tags", "--recurse-submodules=no",
            "origin", scope["ref"])
        info = json.loads(subprocess.check_output(["git", "show", "-s", "--format=%B", "FETCH_HEAD"], cwd=ROOT, text=True))
        require(info.get("owner") == scope["owner"] and info.get("lease") == scope["lease"]
                and info.get("expires", 0) > time.time(), "Claim changed or expired")

def main():
    token = os.environ.pop("BFME_TRANSFER_TOKEN", "")
    require(token and "\n" not in token and "\r" not in token, "Fork credential absent")
    require(sys.platform == "win32" and sys.version_info[:2] == (3, 12), "Native Windows Python 3.12 required")
    require(os.environ["GITHUB_REPOSITORY"] == DATA["fork"]
            and os.environ["GITHUB_REF"] == "refs/heads/" + DATA["control_branch"]
            and os.environ["GITHUB_EVENT_NAME"] == "create", "Wrong workflow context")
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    require(event["repository"]["fork"] is True and event["repository"]["private"] is False
            and event["ref_type"] == "branch" and event["ref"] == DATA["control_branch"], "Wrong fork event")
    require(rev("HEAD") == DATA["base"] and rev("HEAD:AGENTS.md") == DATA["agents_blob"], "Wrong initial base or AGENTS")
    require(DATA["normal_precommit_passed"] is True and DATA["normal_official_prepush_passed"] is True,
            "Local native checks absent")
    require(not os.environ.get("BUILD_RECOMPILE_ONLY") and not os.environ.get("CL") and not os.environ.get("_CL_"),
            "Unexpected compiler override")
    bundle = CONTROL / "native.bundle"
    require(hashlib.sha256(bundle.read_bytes()).hexdigest() == DATA["sha256"], "Bundle hash differs")
    git("verify-native-bundle", "bundle", "verify", bundle)
    git("import-native-commit", "fetch", "--no-tags", "--recurse-submodules=no", bundle,
        DATA["branch"] + ":" + DATA["branch"])
    require(rev(DATA["branch"]) == DATA["commit"] and rev(DATA["branch"] + "^{tree}") == DATA["tree"], "Git identity changed")
    git("checkout-native-source", "switch", DATA["branch"].removeprefix("refs/heads/"))
    original_source = rev("HEAD:" + DATA["source"])
    git("public-author", "config", "user.name", "McMickey93")
    git("public-email", "config", "user.email", "347452154+McMickey93@users.noreply.github.com")
    installed = False
    expected = DATA["transport_expected"]

    def fork_api(path, payload):
        req = urllib.request.Request("https://api.github.com/repos/" + DATA["fork"] + "/git/" + path,
              data=json.dumps(payload).encode("utf-8"),
              headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                       "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"},
              method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError("Fork metadata API " + str(error.code) + ": " +
                               error.read().decode("utf-8", errors="replace")[:2000]) from error
    for attempt in range(8):
        print("PUBLICATION_ATTEMPT " + str(attempt + 1), flush=True)
        git("normal-rebase", "pull", "--rebase", "origin", "master")
        require(rev("HEAD:AGENTS.md") == DATA["agents_blob"], "AGENTS changed: review required")
        require(rev("HEAD:" + DATA["source"]) == original_source, "Reviewed consumer changed")
        for path, digest in DATA["reviewed_blobs"].items():
            require(rev("HEAD:" + path) == digest, "Reviewed provider or consumer changed: " + path)
        base, tip = rev("origin/master"), rev("HEAD")
        changed = set(subprocess.check_output(["git", "diff", "--name-only", "-z", base, tip], cwd=ROOT).decode().strip("\0").split("\0"))
        require(changed == set(DATA["files"]), "Unexpected outgoing paths")
        require(subprocess.check_output(["git", "rev-list", "--count", base + ".." + tip], cwd=ROOT, text=True).strip() == "1", "Not one source commit")
        git("reference-inputs", "-c", "submodule.recurse=false", "submodule", "update", "--init", "--depth=1", "--", "inputs/reference/open-bfme-2")
        bash = os.environ["BFME_QUALIFICATION_BASH"]
        require(Path(bash).is_file(), "Real Git Bash missing")
        if not installed:
            run("verification-requirements", [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "-r",
                                            "tools/requirements.txt"])
            run("normal-hook-setup", [bash, "tools/setup_hooks.sh"])
            installed = True
        claim()
        wire = (DATA["branch"] + " " + tip + " refs/heads/master " + base + "\n").encode()
        run("actual-official-pre-push", [bash, ".githooks/pre-push", "origin",
                                       "https://github.com/Open-BFME/Open-BFME-1.git"], stdin=wire)
        run("provider-and-consumer-byte-verification", ["cmd", "/d", "/c", "build.cmd", *DATA["verify_sources"]])
        claim()
        git("refresh-before-transfer", "fetch", "-q", "--no-tags", "--recurse-submodules=no", "origin", "master")
        if rev("origin/master") != base:
            print("UPSTREAM_MOVED: rebase and run the normal gate again", flush=True)
            continue
        run("required-progress", [sys.executable, "tools/progress.py", "origin/master"])
        git("preseed-fast-forward-lineage", "merge-base", "--is-ancestor", DATA["base"], tip)
        RESULT.update(status="qualified", base=base, commit=tip, tree=rev("HEAD^{tree}"),
                      normal_official_prepush_passed=True, new_cpp_bytes=0)
        save()
        print("QUALIFIED_SOURCE " + json.dumps(RESULT), flush=True)
        url = "https://github.com/McMickey93/Open-BFME-1.git"
        target = "refs/heads/" + DATA["result_branch"]
        env = dict(os.environ)
        count = int(env.get("GIT_CONFIG_COUNT", "0"))
        auth = "AUTHORIZATION: basic " + base64.b64encode(("x-access-token:" + token).encode()).decode()
        env.update({"GIT_CONFIG_COUNT": str(count + 1), "GIT_CONFIG_KEY_" + str(count): "http." + url + ".extraheader",
                    "GIT_CONFIG_VALUE_" + str(count): auth, "GIT_TERMINAL_PROMPT": "0"})
        # Publish only checkpoint.json on a new, parentless fork metadata branch.
        # The app bridge seeds the transport branch at this exact official base.
        # Thus the unmodified fork push hook verifies our one-commit delta.
        checkpoint = dict(RESULT, status="awaiting-fork-base", run_id=os.environ["GITHUB_RUN_ID"],
                          source_blob=original_source, files=sorted(changed), attempt=attempt + 1)
        public_identity = {"name": "McMickey93", "email": "347452154+McMickey93@users.noreply.github.com"}
        checkpoint_text = json.dumps(checkpoint, sort_keys=True)
        metadata_tree = fork_api("trees", {"tree": [{"path": "checkpoint.json", "mode": "100644",
                                    "type": "blob", "content": checkpoint_text + "\n"}]})["sha"]
        metadata = fork_api("commits", {"message": checkpoint_text,
                    "tree": metadata_tree, "parents": [], "author": public_identity, "committer": public_identity})
        checkpoint_ref = "refs/heads/" + DATA["checkpoint_prefix"] + "-" + str(attempt + 1)
        fork_api("refs", {"ref": checkpoint_ref, "sha": metadata["sha"]})
        print("FORK_BASE_CHECKPOINT " + checkpoint_ref + " " + base, flush=True)
        deadline = time.monotonic() + 600
        while True:
            observed = subprocess.check_output(["git", "ls-remote", "--exit-code", url, target],
                                               cwd=ROOT, text=True).split()
            require(len(observed) == 2 and observed[1] == target, "Transport ref absent")
            if observed[0] == base:
                expected = base
                break
            require(time.monotonic() < deadline, "Awaiting exact fork base timed out")
            time.sleep(5)
        claim()
        git("refresh-after-fork-base", "fetch", "-q", "--no-tags", "--recurse-submodules=no", "origin", "master")
        if rev("origin/master") != base:
            print("UPSTREAM_MOVED: qualify the new official parent before transferring", flush=True)
            continue
        git("normal-hook-fork-push", "-c", "core.hooksPath=.githooks", "push", "--porcelain",
            "--force-with-lease=" + target + ":" + expected, url, "HEAD:" + target, env=env)
        expected = tip
        readback = git("fork-readback", "ls-remote", "--exit-code", url, target).decode().split()
        require(readback == [tip, target], "Fork readback differs")
        git("refresh-after-transfer", "fetch", "-q", "--no-tags", "--recurse-submodules=no", "origin", "master")
        if rev("origin/master") != base:
            print("UPSTREAM_MOVED: native objects banked; rebase and qualify the new parent", flush=True)
            continue
        RESULT.update(status="transferred", base=base, commit=tip, tree=rev("HEAD^{tree}"),
                      source_blob=original_source, normal_official_prepush_passed=True,
                      normal_fork_push_passed=True, files=sorted(changed), new_cpp_bytes=0)
        save()
        print("SOURCE_TRANSFER_COMPLETE " + json.dumps(RESULT), flush=True)
        return
    raise RuntimeError("Upstream did not settle within eight verified attempts; native objects remain banked")

try:
    main()
except BaseException:
    RESULT["status"] = "failed"
    save()
    raise
