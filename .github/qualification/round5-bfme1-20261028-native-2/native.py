"""Fork-only native qualification; game changes always use the original hooks."""
import base64
import csv
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

CONTROL = Path(__file__).resolve().parent
M = json.loads((CONTROL / "manifest.json").read_text(encoding="utf-8"))
ROOT = Path.cwd()
OUT = ROOT.parent / "round5-evidence"
OUT.mkdir(exist_ok=True)
R = {"schema": 1, "project": M["project"], "commands": [], "status": "starting", "new_cpp_bytes": 0,
     "started": int(time.time())}
TOKEN = os.environ.pop("BFME_TRANSFER_TOKEN", "")
STATUS_TIP = None
BASH = os.environ.get("BFME_QUALIFICATION_BASH", "")
ORIGINAL = None
LEASE = None
CLAIM_KEYS = []
CLAIM_REFS = []
META_NUMBER = 0


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def git_output(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def rev(ref):
    return git_output("rev-parse", "--verify", ref)


def api(path, payload=None, method="POST"):
    require(os.environ["GITHUB_REPOSITORY"] == M["fork"], "Unexpected fork credential scope")
    request = urllib.request.Request(
        "https://api.github.com/repos/" + M["fork"] + "/git/" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Bearer " + TOKEN, "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28"}, method=method)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError("Fork metadata API %s: %s" %
                           (error.code, error.read().decode("utf-8", errors="replace")[:1500])) from error


def status(value=None):
    global STATUS_TIP
    if value:
        R.update(value)
    (OUT / "result.json").write_text(json.dumps(R, indent=2) + "\n", encoding="utf-8")
    public = {"name": "McMickey93", "email": "347452154+McMickey93@users.noreply.github.com"}
    tree = api("trees", {"tree": [{"path": "status.json", "mode": "100644", "type": "blob",
                                  "content": json.dumps(R, sort_keys=True) + "\n"}]})["sha"]
    commit = api("commits", {"tree": tree, "parents": [STATUS_TIP] if STATUS_TIP else [],
                              "message": "Native qualification evidence\n\nAgent-Authored: OpenAI Codex",
                              "author": public, "committer": public})["sha"]
    if STATUS_TIP:
        api("refs/heads/" + M["status_branch"], {"sha": commit, "force": False}, "PATCH")
    else:
        api("refs", {"ref": "refs/heads/" + M["status_branch"], "sha": commit})
    STATUS_TIP = commit


def run(label, args, *, allow_failure=False, stdin=None, env=None):
    entry = {"label": label, "exit_code": None, "log": "%02d-%s.log" % (len(R["commands"]), label)}
    R["commands"].append(entry)
    status({"step": label})
    print(">>> " + label, flush=True)
    path = OUT / entry["log"]
    with path.open("wb") as stream:
        process = subprocess.Popen([str(x) for x in args], cwd=ROOT, env=env, stdout=stream,
                                   stderr=subprocess.STDOUT,
                                   stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL)
        if stdin is not None:
            process.stdin.write(stdin)
            process.stdin.close()
        start = last = time.monotonic()
        while process.poll() is None:
            try:
                process.wait(timeout=25)
            except subprocess.TimeoutExpired:
                print("    still running: " + label, flush=True)
                if time.monotonic() - last > 90:
                    R["elapsed_seconds"] = int(time.monotonic() - start)
                    R["log_tail"] = path.read_text(encoding="utf-8", errors="replace")[-3000:]
                    status()
                    last = time.monotonic()
        entry["exit_code"] = process.returncode
    output = path.read_text(encoding="utf-8", errors="replace")
    print(output[-4500:], flush=True)
    status()
    if not allow_failure:
        require(process.returncode == 0, label + " failed (see " + path.name + ")")
    return process.returncode, output


def auth_env():
    env = dict(os.environ)
    count = int(env.get("GIT_CONFIG_COUNT", "0"))
    env.update({"GIT_CONFIG_COUNT": str(count + 1),
                "GIT_CONFIG_KEY_" + str(count): "http.https://github.com/" + M["fork"] + ".git.extraheader",
                "GIT_CONFIG_VALUE_" + str(count): "AUTHORIZATION: basic " +
                    base64.b64encode(("x-access-token:" + TOKEN).encode()).decode()})
    return env


def export_marker(marker, label):
    global META_NUMBER
    META_NUMBER += 1
    # Real project marker, real unmodified pre-push hook. The fork ref is a
    # transport copy; only the project's official refs coordinate work.
    # BFME2's current unchanged hook recognizes the legacy claim-marker
    # transport namespace. This fork-only export is not an official claim.
    prefix = "refs/claims/lease/" if M["project"] == 2 else "refs/heads/claims/lease/"
    branch = prefix + M["tag"] + "-" + label + "-" + str(META_NUMBER)
    run("normal-marker-push-" + label, ["git", "-c", "core.hooksPath=.githooks", "push", "--porcelain",
        "https://github.com/" + M["fork"] + ".git", marker + ":" + branch], env=auth_env())
    return branch


def mint_claim():
    global LEASE, CLAIM_KEYS, CLAIM_REFS
    import claims
    rows_path = M["ledger"]
    with (ROOT / rows_path).open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("source") == M["source"]
                and row.get("status") == "matched"]
    require(rows, "The selected source no longer owns matched rows")
    keys = {int(row["target_rva"], 16) for row in rows}
    if M["project"] == 1:
        import link_check
        keys.add(link_check.claim_key(M["removed_symbol"]))
    else:
        keys.add(claims.file_key(M["source"]))
        _, classes, _ = claims.scope_index(ROOT)
        require(not classes.get(claims.file_key(M["source"])),
                "This bounded direct-ref protocol requires a freestanding-function TU")
    CLAIM_KEYS = sorted(keys, key=lambda value: (isinstance(value, str), str(value)))
    CLAIM_REFS = [claims.ref_of(key) for key in CLAIM_KEYS]
    kwargs = {"root": ROOT}
    if M["project"] == 2:
        kwargs.update(scope=M["source"], locks=CLAIM_KEYS)
    marker = claims._record(M["owner"], 4, M["task"], **kwargs)
    record = json.loads(git_output("show", "-s", "--format=%B", marker))
    LEASE = record["lease"]
    export_marker(marker, "acquire")
    R["claim_request"] = {"marker": marker, "refs": CLAIM_REFS, "record": record}
    status({"status": "awaiting-official-claims"})
    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        visible = read_target_claims()
        if visible is not None:
            found = [visible.get(key) for key in CLAIM_KEYS]
            if all(item and item[1].get("owner") == M["owner"] and item[1].get("lease") == LEASE
                   and item[1].get("expires", 0) > time.time() for item in found):
                assert_claim()
                status({"status": "claims-confirmed"})
                return
            for item in found:
                require(not item or item[1].get("expires", 0) <= time.time()
                        or item[1].get("owner") == M["owner"], "A foreign worker holds this scope")
        time.sleep(8)
    raise RuntimeError("No confirmed official reservation; source remains untouched")


def assert_claim():
    visible = read_target_claims()
    require(visible is not None, "Cannot refresh official reservations")
    for key in CLAIM_KEYS:
        item = visible.get(key)
        require(item and item[1].get("owner") == M["owner"] and item[1].get("lease") == LEASE
                and item[1].get("expires", 0) > time.time(), "Reservation lost before source work")


def read_target_claims(allow_successor=False):
    # The existing approved Windows transfer checks exact authoritative refs.
    # Do not mirror unrelated historical ref names into Windows' filesystem.
    # Both current and legacy namespaces are checked before any source edit.
    wanted = {}
    for key, ref in zip(CLAIM_KEYS, CLAIM_REFS):
        wanted[ref] = key
        wanted[ref.replace("refs/heads/claims/", "refs/claims/")] = key
    probe = subprocess.run(["git", "ls-remote", "--refs", "origin", *wanted], cwd=ROOT,
                           capture_output=True, text=True, timeout=60)
    if probe.returncode:
        R["claim_transport_error"] = probe.stderr[-1500:]
        status()
        return None
    advertised = {}
    for line in probe.stdout.splitlines():
        sha, ref = line.split()
        if ref in wanted:
            advertised[ref] = sha
    if advertised:
        fetched = subprocess.run(["git", "fetch", "-q", "--no-tags", "--depth=1", "--recurse-submodules=no",
                                  "origin", *advertised], cwd=ROOT, capture_output=True, text=True, timeout=90)
        if fetched.returncode:
            R["claim_transport_error"] = fetched.stderr[-1500:]
            status()
            return None
    visible = {}
    for ref, sha in advertised.items():
        record = json.loads(git_output("show", "-s", "--format=%B", sha))
        if record.get("expires", 0) > time.time() and not allow_successor:
            require(record.get("owner") == M["owner"] and record.get("lease") == LEASE,
                    "Foreign or successor reservation at " + ref)
        key = wanted[ref]
        if ref.startswith("refs/heads/claims/") or key not in visible:
            visible[key] = (sha, record)
    R["target_claim_readback"] = {ref: sha for ref, sha in advertised.items()}
    return visible


def setup_references():
    other = M["reference_path"]
    run("initialize-pinned-reference", ["git", "-c", "submodule.recurse=false", "submodule", "update",
                                      "--init", "--depth=1", "--", other])
    requirements = "tools/requirements.txt" if M["project"] == 1 else other + "/tools/requirements.txt"
    run("python-requirements", [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "-r", requirements])
    run("normal-hook-setup", [BASH, "tools/setup_hooks.sh"])
    run("entry-ledger-integrity", [sys.executable, "tools/check_csv.py"])
    run("read-official-master", ["git", "fetch", "--no-tags", "--recurse-submodules=no", "origin",
                                 "master:refs/remotes/origin/master"])
    # Fetch official reference HEAD, retain the published verified pointer. A
    # newer unverified tree never silently becomes a compiler input.
    run("observe-reference-upstream", ["git", "-C", other, "fetch", "--depth=1", "--no-tags",
                                       "--recurse-submodules=no", "origin", "master"])
    pinned = rev("HEAD:" + other)
    observed = git_output("rev-parse", "FETCH_HEAD", cwd=ROOT / other)
    require(git_output("rev-parse", "HEAD", cwd=ROOT / other) == pinned, "Reference checkout differs from its pin")
    R["reference"] = {"pinned": pinned, "observed_upstream": observed, "pointer_changed": False,
                      "newer_head_qualified": observed == pinned}
    if M["project"] == 2:
        from datetime import datetime, timezone
        proof = ROOT / M["reference_proof"]
        receipt = json.loads((proof / "input-receipt.json").read_text(encoding="utf-8"))
        require(receipt["selected_official_reference"] == pinned and receipt["changed_headers"] == []
                and receipt["gate_results"]["old"]["exit_code"] == 0
                and receipt["gate_results"]["new"]["exit_code"] == 0
                and receipt["donor_scan"]["exit_code"] == 0, "Published canonical-reference proof is not green")
        for name in ("old-full-gate.log", "new-full-gate.log"):
            require("FULL GATE: OK" in (proof / name).read_text(encoding="utf-8"), "Incomplete canonical gate receipt")
        stamp = datetime.fromisoformat(M["reference_stamp"].replace("Z", "+00:00"))
        require(0 <= (datetime.now(timezone.utc) - stamp).total_seconds() < 72 * 3600, "Canonical proof expired")
        (ROOT / "build").mkdir(exist_ok=True)
        (ROOT / "build/bfme1-last-check.txt").write_text(M["reference_stamp"] + " " + pinned + "\n", encoding="utf-8")
        R["reference"]["reused_published_verification"] = M["reference_proof"]
    else:
        R["reference"]["freshness_update_blocked"] = observed != pinned
        R["reference"]["note"] = "Inspection uses current main BFME2 donor packets in the reviewed manifest; no donor-pointer update or success stamp is claimed."
    status()


def build_source(label):
    if M["project"] == 1:
        return run(label, ["cmd", "/d", "/c", "build.cmd", *M["verify_sources"]], allow_failure=True)
    return run(label, [BASH, "build.sh", *M["verify_sources"]], allow_failure=True)


def preview(label):
    if M["project"] == 1:
        args = [sys.executable, "tools/link_check.py", M["source"], "--compile-limit", "0"]
    else:
        args = [sys.executable, "tools/link_check.py", M["source"]]
    code, output = run(label, args, allow_failure=True)
    R.setdefault("previews", []).append({"label": label, "exit_code": code, "output": output[-12000:]})
    status()
    return code


def coff_proof(before, after):
    import link_census as census
    name = M["removed_symbol"]
    old, new = before.read_bytes(), after.read_bytes()
    if M.get("mode") == "retarget":
        import struct
        def summary(data, rename):
            u16 = lambda p: struct.unpack_from("<H", data, p)[0]
            u32 = lambda p: struct.unpack_from("<I", data, p)[0]
            require(u16(0) == 0x14c, "Expected x86 COFF")
            symbols = {s["index"]: s for s in census._coff_symbols(data)}
            defined = sorted(s["name"] for s in symbols.values() if s["storage"] == 2 and s["section"] != 0)
            undefined = sorted(rename.get(s["name"], s["name"]) for s in symbols.values()
                               if s["storage"] == 2 and s["section"] == 0 and s["value"] == 0)
            sections = []
            for n in range(u16(2)):
                h = 20 + u16(16) + n * 40
                section_name = data[h:h + 8].split(b"\0", 1)[0].decode("ascii")
                if section_name.startswith(".debug"):
                    continue
                size, raw, rel_at, rel_count = u32(h + 16), u32(h + 20), u32(h + 24), u16(h + 32)
                relocs = []
                for j in range(rel_count):
                    p = rel_at + 10 * j
                    sym = symbols[u32(p + 4)]
                    target = ("local", sym["section"], sym["value"]) if sym["storage"] != 2 and sym["section"] > 0 else (
                        "external", rename.get(sym["name"], sym["name"]))
                    relocs.append((u32(p), u16(p + 8), target))
                sections.append((n + 1, section_name, u32(h + 36), size,
                                 data[raw:raw + size].hex() if raw else None, relocs))
            return sections, defined, undefined
        replacement = M["replacement_symbol"]
        require(summary(old, {name: replacement}) == summary(new, {}),
                "Runtime COFF sections, definitions or bindings differ beyond the reviewed retarget")
        proof = {"old_undefined": name, "new_undefined": replacement, "runtime_sections_identical_after_retarget": True,
                 "external_definitions_identical": True, "only_reviewed_undefined_retarget": True,
                 "retail_ilt_and_body_witness": M["route_proof"]}
        (OUT / "object-proof.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
        return proof
    a = {symbol["name"]: (digest, size) for symbol, _, _, digest, size in census._comdat_sections(old)}
    b = {symbol["name"]: (digest, size) for symbol, _, _, digest, size in census._comdat_sections(new)}
    require(name in a, "The selected external copy is absent before the trial")
    require(name not in b and {key: value for key, value in a.items() if key != name} == b,
            "Retained external COMDAT bytes/relocations changed, or the unwanted copy remains")
    def symbols(data):
        syms = census._coff_symbols(data)
        return ({s["name"] for s in syms if s["storage"] == 2 and s["section"] != 0},
                {s["name"] for s in syms if s["storage"] == 2 and s["section"] == 0 and s["value"] == 0})
    ad, au = symbols(old)
    bd, bu = symbols(new)
    require(ad - {name} == bd, "External definitions changed beyond the selected unused copy")
    roots, edges = census.object_references(before)
    require(name not in roots and all(name not in targets for source, targets in edges.items() if source != name),
            "The removed copy has an incoming runtime reference")
    allowed_removed = set(edges.get(name, ()))
    require(not (bu - au) and au - bu <= allowed_removed, "Unexpected undefined-symbol changes")
    require(census._weak_externals(old) == census._weak_externals(new), "Weak bindings changed")
    proof = {"removed_unused_external": name, "retained_external_comdats": len(b),
             "retained_external_comdat_fingerprints_identical": True, "no_incoming_runtime_reference": True,
             "external_definitions_removed": sorted(ad - bd), "undefined_removed": sorted(au - bu),
             "undefined_added": sorted(bu - au), "weak_bindings_unchanged": True}
    (OUT / "object-proof.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    return proof


def acquire_link_index():
    if M["project"] == 2:
        run("fetch-published-census", [sys.executable, "tools/link_check.py", "--fetch-index"], allow_failure=True)
    else:
        import zipfile
        request = urllib.request.Request(M["index_archive"], headers={"Authorization": "Bearer " + TOKEN,
                                         "Accept": "application/vnd.github+json"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
            require(hashlib.sha256(raw).hexdigest() == M["index_sha256"], "Official census artifact digest differs")
            import io
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                member = next(value for value in archive.namelist() if value == "link_index.pkl")
                target = ROOT / "build/link_census/link_index.pkl"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(member))
            R["census_download"] = "official artifact digest verified"
        except Exception as error:
            R["census_download"] = "unavailable: " + str(error)[:1000]
        status()


def trials():
    global ORIGINAL
    import build
    path = ROOT / M["source"]
    ORIGINAL = path.read_bytes()
    require(hashlib.sha1(b"blob " + str(len(ORIGINAL)).encode() + b"\0" + ORIGINAL).hexdigest() == M["source_before"],
            "Reviewed original source changed")
    run("frozen-source-check", [sys.executable, "tools/find_declared_unmatched.py", M["source"]])
    code, _ = build_source("original-byte-and-relocation-gates")
    require(code == 0, "Unmodified selected source does not pass its original-compiler gate")
    object_path = build.obj_path(Path(M["source"]))
    before = OUT / "before.obj"
    before.write_bytes(object_path.read_bytes())
    acquire_link_index()
    if M["project"] == 2:
        run("original-strict-current-preparation", [sys.executable, "tools/link_check.py", "--prepare-current",
                                                   *M["verify_sources"]])
    preview("before-link-preview")
    R["trials"] = []
    for variant in M["variants"]:
        assert_claim()
        planned = (CONTROL / variant["file"]).read_bytes()
        require(hashlib.sha1(b"blob " + str(len(planned)).encode() + b"\0" + planned).hexdigest() == variant["blob"],
                "Candidate payload changed")
        path.write_bytes(planned)
        code, output = build_source("trial-" + variant["name"])
        verdict = {"variant": variant["name"], "gate_exit": code}
        if code == 0:
            after = OUT / (variant["name"] + ".obj")
            after.write_bytes(object_path.read_bytes())
            try:
                verdict["coff_proof"] = coff_proof(before, after)
                R["trials"].append(verdict)
                R["selected_variant"] = variant
                R["object_proof"] = verdict["coff_proof"]
                if M["project"] == 2:
                    run("modified-strict-current-preparation", [sys.executable, "tools/link_check.py", "--prepare-current",
                                                               *M["verify_sources"]])
                preview("after-link-preview")
                run("modified-frozen-source-check", [sys.executable, "tools/find_declared_unmatched.py", M["source"]])
                return True
            except Exception as error:
                verdict["structural_refusal"] = str(error)
        R["trials"].append(verdict)
        path.write_bytes(ORIGINAL)
        status()
    return False


def bank(success, error=None):
    if not success and ORIGINAL is not None:
        (ROOT / M["source"]).write_bytes(ORIGINAL)
    details = M["evidence_intro"] + "\n\n"
    details += "Native run: https://github.com/" + M["fork"] + "/actions/runs/" + os.environ["GITHUB_RUN_ID"] + "\n\n"
    details += "Original compiler and unchanged ordinary project gates; no new C++ bytes, census measurement or game test.\n\n"
    details += "Outcome: " + ("reviewed binding/emitter repair verified; affected source rows remain exact" if success else "blocked; game source restored") + ".\n"
    if error:
        details += "Blocker: " + str(error) + "\n"
    details += "\nQualification observations:\n\n```json\n" + json.dumps(
        {key: R.get(key) for key in ("reference", "trials", "object_proof", "previews", "census_download")}, indent=2) + "\n```\n"
    evidence = ROOT / M["evidence"]
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(details, encoding="utf-8", newline="\n")
    for variant in M["variants"]:
        (evidence.parent / (M["tag"] + "-" + variant["name"] + ".patch")).write_text("".join(difflib.unified_diff(
            (ORIGINAL or (ROOT / M["source"]).read_bytes()).decode("utf-8").splitlines(keepends=True),
            (CONTROL / variant["file"]).read_text(encoding="utf-8").splitlines(keepends=True),
            fromfile="a/" + M["source"], tofile="b/" + M["source"])), encoding="utf-8", newline="\n")
    files = [M["evidence"], M["attempt_log"]]
    files.extend(str((evidence.parent / (M["tag"] + "-" + variant["name"] + ".patch")).relative_to(ROOT)).replace("\\", "/")
                 for variant in M["variants"])
    if success:
        files.append(M["source"])
        if M["project"] == 2:
            obstacle = "docs/linking_obstacles.md"
            with (ROOT / obstacle).open("a", encoding="utf-8", newline="\n") as stream:
                stream.write("\n### Radio-button unused floorf copy (2026-10-28)\n\n" +
                    "Status: bounded emitter repair; census confirmation pending. The RadioButton TU stops publishing " +
                    "its unused math-header `_floorf`. All three existing rows remain exact; retained external COMDAT " +
                    "fingerprints and weak bindings are unchanged. Before/after ordinary-preview scope and remaining " +
                    "limitations are in [the native handoff](../" + M["evidence"] + "). No measured linking gain is claimed.\n")
            files.append(obstacle)
            targets = "docs/linking_targets.md"
            with (ROOT / targets).open("a", encoding="utf-8", newline="\n") as stream:
                stream.write("\nAdditional current target (2026-10-28): W3DRadioButton.cpp received the bounded " +
                    "unused math-header floorf emitter repair. The existing three rows remain exact, with " +
                    "retained external COMDAT fingerprints and weak bindings preserved. Current preview scope, " +
                    "limitations and remaining census prerequisites: [native handoff](../" + M["evidence"] + ").\n")
            files.append(targets)
    run("record-project-attempt", [sys.executable, "tools/re_log.py", "record", M["function"], M["rva"], str(M["size"]),
        "solved" if success else "blocked", "t=%smin model=OpenAI-Codex " % max(1, int((time.time() - R["started"] + 59) // 60)) + M["task"] + "; " +
        ("original and modified byte gates and structural checks pass" if success else "native prerequisite or candidate gate refused; source restored") +
        "; no new C++ bytes or measured linking gain. Evidence: " + M["evidence"]])
    assert_claim()
    run("stage-exact-source-and-handoff", ["git", "add", "--", *files])
    message = ("[BFME 2 donor] " if M["project"] == 1 else "") + (M["commit_title"] if success else "Record " + M["task"] + " blocker")
    message += "\n\nOriginal-compiler qualification and structural observations: " + M["evidence"] + ".\n"
    message += "No new C++ bytes, census result or game test is claimed.\n\n"
    for key in CLAIM_KEYS:
        if isinstance(key, int):
            message += "Claim-Lease: 0x%08X=%s\n" % (key, LEASE)
    message += "Agent-Authored: OpenAI Codex\n"
    message_path = OUT / "commit-message.txt"
    message_path.write_text(message, encoding="utf-8")
    run("normal-native-commit", ["git", "commit", "-F", str(message_path)])
    R["normal_precommit_passed"] = True
    R["native_commit"] = rev("HEAD")
    patch = subprocess.check_output(["git", "format-patch", "-1", "--stdout", "HEAD"], cwd=ROOT)
    (OUT / "native-commit.patch").write_bytes(patch)
    run("preserve-qualified-commit-bundle", ["git", "bundle", "create", str(OUT / "native-commit.bundle"),
                                            "origin/master..HEAD"])
    R["source_repair"] = success
    for attempt in range(4):
        run("normal-rebase-" + str(attempt), ["git", "pull", "--rebase", "origin", "master"])
        require(rev("HEAD:AGENTS.md") == M["agents_blob"], "AGENTS changed; manual review needed")
        assert_claim()
        base, tip = rev("origin/master"), rev("HEAD")
        wire = ("refs/heads/" + M["native_branch"] + " " + tip + " refs/heads/master " + base + "\n").encode()
        code, _ = run("actual-official-prepush-" + str(attempt), [BASH, ".githooks/pre-push", "origin",
                       "https://github.com/" + M["official"] + ".git"], stdin=wire, allow_failure=True)
        if code:
            if git_output("ls-remote", "--exit-code", "origin", "refs/heads/master").split()[0] != base:
                continue
            raise RuntimeError("The unchanged official pre-push hook refused the outgoing batch")
        R.update({"status": "awaiting-transport-base", "base": base, "commit": tip,
                  "tree": rev("HEAD^{tree}"), "normal_official_prepush_passed": True})
        status()
        target = "refs/heads/" + M["result_branch"]
        deadline = time.monotonic() + 900
        while time.monotonic() < deadline:
            observed = subprocess.run(["git", "ls-remote", "--exit-code", "https://github.com/" + M["fork"] + ".git", target],
                                      cwd=ROOT, text=True, capture_output=True)
            if observed.returncode == 0 and observed.stdout.split()[0] == base:
                break
            time.sleep(8)
        else:
            raise RuntimeError("Exact native-push transport base was not provided")
        if git_output("ls-remote", "--exit-code", "origin", "refs/heads/master").split()[0] != base:
            continue
        assert_claim()
        run("normal-native-fork-push", ["git", "-c", "core.hooksPath=.githooks", "push", "--porcelain",
            "--force-with-lease=" + target + ":" + base, "https://github.com/" + M["fork"] + ".git", "HEAD:" + target], env=auth_env())
        R.update({"normal_fork_push_passed": True, "status": "awaiting-official-publication", "commit": rev("HEAD")})
        status()
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            observed = git_output("ls-remote", "--exit-code", "origin", "refs/heads/master").split()[0]
            if observed == R["commit"]:
                R["publication"] = "official-master"
                return
            decision = subprocess.run(["git", "ls-remote", "--exit-code", "https://github.com/" + M["fork"] + ".git",
                                       "refs/heads/" + M["decision_branch"]], cwd=ROOT, capture_output=True)
            if decision.returncode == 0:
                R["publication"] = "banked-in-fork-project-integration-required"
                return
            time.sleep(8)
        R["publication"] = "banked-in-fork-publication-unconfirmed"
        return
    raise RuntimeError("Upstream kept moving; no unverified publication was attempted")


def release_packet():
    import claims
    kwargs = {"root": ROOT, "lease": LEASE}
    if M["project"] == 2:
        kwargs.update(scope=M["source"], locks=CLAIM_KEYS)
    marker = claims._record(M["owner"], 0, "released", **kwargs)
    export_marker(marker, "release")
    observed = {}
    for ref in CLAIM_REFS:
        value = subprocess.run(["git", "ls-remote", "--exit-code", "origin", ref], cwd=ROOT, capture_output=True, text=True)
        if value.returncode == 0:
            observed[ref] = value.stdout.split()[0]
    R["release_request"] = {"marker": marker, "refs": CLAIM_REFS, "observed": observed,
                             "owner": M["owner"], "lease": LEASE}
    status({"status": "awaiting-official-release"})
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        visible = read_target_claims(allow_successor=True)
        if visible is not None:
            if all(not visible.get(key) or visible[key][1].get("owner") != M["owner"]
                   or visible[key][1].get("lease") != LEASE or visible[key][1].get("expires", 0) <= time.time()
                   for key in CLAIM_KEYS):
                R["own_claims_released"] = True
                status()
                return
        time.sleep(8)
    raise RuntimeError("Awaiting fenced project release; release packet remains available")


def retire_predecessor():
    """Stop the superseded fork job, then release only its fenced own claims."""
    global LEASE, CLAIM_KEYS, CLAIM_REFS
    previous = M.get("predecessor")
    if not previous:
        return
    def action_request(suffix, method="GET"):
        request = urllib.request.Request("https://api.github.com/repos/" + M["fork"] +
            "/actions/runs/" + str(previous["run_id"]) + suffix,
            data=b"{}" if method == "POST" else None,
            headers={"Authorization": "Bearer " + TOKEN, "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json"}, method=method)
        with urllib.request.urlopen(request, timeout=40) as response:
            return json.load(response) if response.status != 202 else {}
    previous_run = action_request("")
    require(previous_run["head_sha"] == previous["control_sha"], "Wrong predecessor workflow")
    if previous_run["status"] != "completed":
        try:
            action_request("/cancel", "POST")
        except urllib.error.HTTPError as error:
            require(error.code == 409, "Could not cancel the superseded own job")
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline and action_request("")["status"] != "completed":
            time.sleep(5)
        require(action_request("")["status"] == "completed", "Old worker is still running; no handover")
    R["predecessor_stopped"] = previous["run_id"]
    import claims
    LEASE = previous["lease"]
    CLAIM_REFS = previous["refs"]
    CLAIM_KEYS = [claims.key_of(ref.split("claims/", 1)[1]) if M["project"] == 2 else
                  int(ref.rsplit("/", 1)[1], 16) for ref in CLAIM_REFS]
    release_packet()
    LEASE, CLAIM_KEYS, CLAIM_REFS = None, [], []
    R.pop("release_request", None)
    R["predecessor_claims_released"] = True
    status()


def main():
    require(TOKEN and "\n" not in TOKEN and "\r" not in TOKEN, "Fork workflow credential absent")
    require(sys.platform == "win32" and sys.version_info[:2] == (3, 12), "Native Windows Python 3.12 required")
    require(os.environ["GITHUB_REPOSITORY"] == M["fork"] and os.environ["GITHUB_REF"] == "refs/heads/" + M["control_branch"]
            and os.environ["GITHUB_EVENT_NAME"] == "create", "Unexpected workflow context")
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    require(event["repository"]["fork"] and not event["repository"]["private"]
            and event["ref_type"] == "branch" and event["ref"] == M["control_branch"], "Unexpected create event")
    require(rev("HEAD") == M["base"] and rev("HEAD:AGENTS.md") == M["agents_blob"], "Pinned source/AGENTS changed")
    require(Path(BASH).is_file() and not os.environ.get("CL") and not os.environ.get("_CL_")
            and not os.environ.get("BUILD_RECOMPILE_ONLY"), "Unexpected compiler environment")
    run("public-author", ["git", "config", "user.name", "McMickey93"])
    run("public-author-email", ["git", "config", "user.email", "347452154+McMickey93@users.noreply.github.com"])
    run("native-work-branch", ["git", "switch", "-c", M["native_branch"]])
    setup_references()
    sys.path.insert(0, str(ROOT / "tools"))
    retire_predecessor()
    mint_claim()
    failure = None
    try:
        success = trials()
        if not success:
            failure = "Every reviewed candidate failed byte or retained-COFF verification"
    except Exception as error:
        success, failure = False, str(error)
        R["trial_blocker"] = failure
        status()
    bank(success, failure)


try:
    main()
except BaseException as error:
    R["error"] = str(error)
    R["outcome"] = "blocked"
    status({"status": "failed"})
finally:
    try:
        if ORIGINAL is not None and not R.get("normal_precommit_passed"):
            (ROOT / M["source"]).write_bytes(ORIGINAL)
        code, _ = run("required-final-progress", [sys.executable, "tools/progress.py", "origin/master"], allow_failure=True)
        R["final_progress_passed"] = code == 0
        if LEASE:
            release_packet()
        status({"status": "finished", "outcome": R.get("outcome", "banked"), "new_cpp_bytes": 0})
    except BaseException as error:
        R["cleanup_error"] = str(error)
        status({"status": "cleanup-blocked"})
        raise
if R.get("error"):
    raise SystemExit(1)
