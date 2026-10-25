"""Transfer one reviewed, already qualified commit without recreating its objects.

The read-only job imports the original exporter artifact and repeats the ordinary
native pre-push against the *actual* official master. A separate write job imports
that verified bundle and may only create one derived branch in the fixed fork.
The empty expected-ref lease is an atomic compare-and-create, never an update.
Neither job executes artifact-provided code or modifies the qualifier's gates.
"""

import base64
import csv
import hashlib
import importlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile


FORK = "McMickey93/Open-BFME-1"
OFFICIAL = "Open-BFME/Open-BFME-1"
UPSTREAM = "https://github.com/" + OFFICIAL + ".git"
FORK_URL = "https://github.com/" + FORK + ".git"
WORKFLOW = ".github/workflows/bfme1-body-qualification.yml"
QUALIFIER = ".github/qualification/bfme1-body/qualify.py"
CODE_HASHES = {
    WORKFLOW: "43215d2417c13e5a1939263e92e26cd953b2e2b30454a11a9d529f7986d55d77",
    QUALIFIER: "ede59a252815d9d1d4d46745b9d7481ddd3e60d554506f9a99ec77e5a6470747",
}
LEDGER = "targets/game/reverse/functions.csv"
LEDGERS = {LEDGER, "targets/game/reverse/re_attempts.log", "targets/game/reverse/deleted_rows.csv"}
COMPILER = "inputs/toolchains/vs2003/Program Files/Microsoft Visual Studio .NET 2003/Vc7/bin/cl.exe"
COMPILER_SHA256 = "2ecf86a3edfd3deae498e08298e210e984537ce9e11759930561e43f40bd2515"
LOCAL_REF = "refs/heads/qualification/transfer"
MAX_ZIP = 128 * 1024 * 1024
MAX_EXPANDED = 512 * 1024 * 1024
MAX_MEMBER = 128 * 1024 * 1024
REQUEST_KEYS = {"schema", "enabled", "qualification_run_id", "qualification_run_attempt",
                "qualification_head_sha", "artifact_id", "artifact_sha256", "expected_base",
                "expected_commit", "expected_tree", "qualification_directory"}
WORKFLOW_KEYS = ("GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT",
                 "GITHUB_ACTOR", "GITHUB_TRIGGERING_ACTOR", "RUNNER_OS", "ImageVersion")


class Rejected(RuntimeError):
    """A failed contract check, with no credentials or download URLs in its text."""


def require(condition, message):
    if not condition:
        raise Rejected(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def object_id(kind, raw):
    return hashlib.sha1(kind.encode("ascii") + b" " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def hex_id(value, size=40):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{%d}" % size, value) is not None


def positive_int(value):
    return type(value) is int and value > 0


def json_bytes(raw):
    require(len(raw) <= 4 * 1024 * 1024, "JSON document exceeds its size bound")
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result
    def constant(_):
        raise Rejected("Non-finite JSON value")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, ValueError) as error:
        raise Rejected("Invalid UTF-8 JSON") from error


def safe_path(value):
    require(isinstance(value, str) and value and not any(c in value for c in "\\:\0\r\n<>\"|?*"),
            "Invalid path spelling")
    path = PurePosixPath(value)
    require(not path.is_absolute() and path.as_posix() == value, "Noncanonical path")
    for part in path.parts:
        require(part not in (".", "..") and part.casefold() != ".git"
                and part[-1:] not in (".", " ") and not any(ord(c) < 32 for c in part),
                "Unsafe path component")
        require(not re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part),
                "Windows device path")
    return path


def allowed_source(path):
    parsed = safe_path(path)
    if path.startswith("game/"):
        return parsed.suffix in (".c", ".cc", ".cpp", ".cxx") and not path.startswith(
            ("game/gen_asm/", "game/gen_small/", "game/masm_dumps/"))
    return (path.startswith(("targets/game/reverse/identity_evidence/",
                             "targets/game/reverse/attempt_support/"))
            and parsed.suffix in (".md", ".txt"))


def read_request(raw=None):
    raw = Path(__file__).with_name("request.json").read_bytes() if raw is None else raw
    data = json_bytes(raw)
    require(isinstance(data, dict) and set(data) == REQUEST_KEYS, "Unexpected request fields")
    require(type(data["schema"]) is int and data["schema"] == 1 and data["enabled"] is True,
            "Transfer request is disabled; review a successful qualify artifact first")
    for name in ("qualification_run_id", "qualification_run_attempt", "artifact_id"):
        require(positive_int(data[name]), "Invalid reviewed run or artifact ID")
    for name in ("qualification_head_sha", "expected_base", "expected_commit", "expected_tree"):
        require(hex_id(data[name]), "Invalid reviewed Git object ID")
    require(hex_id(data["artifact_sha256"], 64), "Invalid reviewed artifact digest")
    require(isinstance(data["qualification_directory"], str)
            and re.fullmatch(r"qualification-[0-2]", data["qualification_directory"]),
            "Invalid qualification attempt directory")
    return data, digest(raw)


def workflow_context(environ):
    require(environ.get("GITHUB_REPOSITORY") == FORK
            and environ.get("GITHUB_REF") == "refs/heads/master"
            and environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch", "Wrong transfer context")
    actor = environ.get("GITHUB_ACTOR", "")
    require(re.fullmatch(r"[A-Za-z0-9-]{1,39}", actor or "")
            and environ.get("GITHUB_TRIGGERING_ACTOR", "").casefold() == actor.casefold(),
            "Dispatching and triggering accounts differ")
    require(hex_id(environ.get("GITHUB_SHA")), "Invalid immutable workflow head")
    for name in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT"):
        require(re.fullmatch(r"[1-9][0-9]*", environ.get(name, "")), "Invalid workflow run")
    return {key: environ.get(key) for key in WORKFLOW_KEYS}


def target_ref(request):
    # No caller-provided destination, ref, force or lease argument exists.
    return "refs/heads/qualified/bfme1-%d-%d-%s" % (
        request["qualification_run_id"], request["qualification_run_attempt"], request["expected_commit"])


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def download_url(url):
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").lower()
    require(parsed.scheme == "https" and not parsed.username and not parsed.password
            and parsed.port in (None, 443) and not parsed.fragment
            and (host.endswith(".blob.core.windows.net") or host.endswith(".githubusercontent.com")),
            "Artifact redirect is not an approved HTTPS storage host")
    return url


class DownloadRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Construct a fresh request, rather than copying API Authorization.
        return urllib.request.Request(download_url(newurl), headers={"User-Agent": "BFME-qualified-transfer"})


class GitHub:
    def __init__(self, token):
        require(isinstance(token, str) and token and "\n" not in token and "\r" not in token,
                "Ephemeral repository token missing")
        self.token = token
        self.api_opener = urllib.request.build_opener(NoRedirect())
        self.download_opener = urllib.request.build_opener(DownloadRedirect())

    def request(self, suffix):
        require(suffix.startswith("/") and not suffix.startswith("//"), "Invalid API endpoint")
        return urllib.request.Request("https://api.github.com/repos/" + FORK + suffix, headers={
            "Authorization": "Bearer " + self.token, "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "BFME-qualified-transfer"})

    def json(self, suffix):
        try:
            with self.api_opener.open(self.request(suffix), timeout=60) as response:
                raw = response.read(4 * 1024 * 1024 + 1)
            return json_bytes(raw)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise Rejected("GitHub metadata request failed") from error

    def content(self, path, sha):
        safe_path(path)
        require(hex_id(sha), "Invalid content revision")
        value = self.json("/contents/" + path + "?ref=" + sha)
        require(value.get("encoding") == "base64" and value.get("type") == "file", "Missing pinned file")
        try:
            raw = base64.b64decode("".join(value["content"].split()), validate=True)
        except (ValueError, KeyError) as error:
            raise Rejected("Invalid pinned file encoding") from error
        require(len(raw) <= 1024 * 1024 and object_id("blob", raw) == value.get("sha"),
                "Pinned file object mismatch")
        return raw

    def artifact(self, artifact_id, expected_digest, path):
        require(positive_int(artifact_id) and hex_id(expected_digest, 64), "Invalid artifact pin")
        request = self.request("/actions/artifacts/%d/zip" % artifact_id)
        try:
            # Never permit urllib to forward Authorization through a redirect.
            try:
                response = self.api_opener.open(request, timeout=60)
            except urllib.error.HTTPError as error:
                require(error.code in (301, 302, 303, 307, 308), "Artifact API download failed")
                url = download_url(error.headers.get("Location", ""))
                response = self.download_opener.open(
                    urllib.request.Request(url, headers={"User-Agent": "BFME-qualified-transfer"}), timeout=60)
            total, hasher = 0, hashlib.sha256()
            with response, path.open("wb") as target:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    total += len(block)
                    require(total <= MAX_ZIP, "Compressed artifact exceeds its size bound")
                    hasher.update(block)
                    target.write(block)
            require(hasher.hexdigest() == expected_digest, "Downloaded artifact digest differs")
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            # Exception strings can contain signed URLs; do not log them.
            raise Rejected("Artifact download failed") from error


def check_run(run, request, actor):
    require(run.get("id") == request["qualification_run_id"]
            and run.get("run_attempt") == request["qualification_run_attempt"]
            and run.get("head_sha") == request["qualification_head_sha"]
            and run.get("path") == WORKFLOW and run.get("event") == "workflow_dispatch"
            and run.get("head_branch") == "master" and run.get("status") == "completed"
            and run.get("conclusion") == "success", "Source run is not the reviewed successful qualification")
    for field in ("repository", "head_repository"):
        require(run.get(field, {}).get("full_name") == FORK, "Source run is outside the fixed fork")
    require(run["repository"].get("fork") is True and run["repository"].get("private") is False,
            "Source repository must remain the public contributor fork")
    for field in ("actor", "triggering_actor"):
        require(run.get(field, {}).get("login", "").casefold() == actor.casefold(), "Source run actor differs")


def check_artifact(meta, artifact_id, sha256, run_id, head, name):
    require(meta.get("id") == artifact_id and meta.get("name") == name
            and meta.get("expired") is False and meta.get("digest") == "sha256:" + sha256
            and meta.get("workflow_run", {}).get("id") == run_id
            and meta.get("workflow_run", {}).get("head_sha") == head, "Artifact provenance or digest differs")
    require(type(meta.get("size_in_bytes")) is int and 0 < meta["size_in_bytes"] <= MAX_ZIP,
            "Artifact size is outside the download bound")


def source_provenance(api, request, actor):
    run = api.json("/actions/runs/%d/attempts/%d" % (
        request["qualification_run_id"], request["qualification_run_attempt"]))
    check_run(run, request, actor)
    meta = api.json("/actions/artifacts/%d" % request["artifact_id"])
    check_artifact(meta, request["artifact_id"], request["artifact_sha256"],
                   request["qualification_run_id"], request["qualification_head_sha"],
                   "bfme1-body-%d-%d" % (request["qualification_run_id"], request["qualification_run_attempt"]))
    for path, expected in CODE_HASHES.items():
        require(digest(api.content(path, request["qualification_head_sha"])) == expected,
                "Qualification implementation differs from the reviewed implementation")


class Archive:
    def __init__(self, path):
        self.zip = zipfile.ZipFile(path)
        entries = self.zip.infolist()
        require(len(entries) <= 10000, "Artifact has too many entries")
        self.entries, folded, total = {}, set(), 0
        for info in entries:
            name = info.filename[:-1] if info.is_dir() else info.filename
            safe_path(name)
            require(name.casefold() not in folded, "Duplicate or case-colliding artifact path")
            folded.add(name.casefold())
            mode = info.external_attr >> 16
            kind = stat.S_IFMT(mode)
            require(kind in ((0, stat.S_IFDIR) if info.is_dir() else (0, stat.S_IFREG))
                    and not info.flag_bits & 1, "Artifact contains a link, special or encrypted entry")
            require(info.file_size <= MAX_MEMBER, "Artifact entry is too large")
            total += info.file_size
            require(total <= MAX_EXPANDED, "Artifact expansion exceeds its size bound")
            if not info.is_dir():
                self.entries[name] = info

    def read(self, name, limit=MAX_MEMBER):
        safe_path(name)
        require(name in self.entries and self.entries[name].file_size <= limit, "Missing or oversized artifact member")
        raw = self.zip.read(self.entries[name])
        require(len(raw) == self.entries[name].file_size, "Artifact entry size differs")
        return raw

    def json(self, name):
        return json_bytes(self.read(name, 4 * 1024 * 1024))

    def close(self):
        self.zip.close()


def validate_manifests(request, data, publication, actor):
    require(data.get("schema_version") == 1 and data.get("repository") == FORK
            and data.get("upstream") == UPSTREAM and data.get("mode") == "qualify", "Artifact is not qualify-mode")
    for name in ("base", "base_tree", "patch_tree"):
        require(hex_id(data.get(name)), "Invalid qualification source pin")
    require(publication.get("repository") == OFFICIAL and publication.get("published") is False
            and publication.get("normal_commit_passed") is True
            and publication.get("normal_pre_push_passed") is True, "Qualification gates did not pass")
    for field in ("base", "commit", "tree"):
        require(publication.get(field) == request["expected_" + field], "Qualified object differs from request")
    wf = publication.get("workflow", {})
    for field, expected in (("GITHUB_REPOSITORY", FORK), ("GITHUB_SHA", request["qualification_head_sha"]),
                            ("GITHUB_RUN_ID", str(request["qualification_run_id"])),
                            ("GITHUB_RUN_ATTEMPT", str(request["qualification_run_attempt"])), ("RUNNER_OS", "Windows")):
        require(wf.get(field) == expected, "Qualification workflow evidence differs")
    for name in ("GITHUB_ACTOR", "GITHUB_TRIGGERING_ACTOR"):
        require(wf.get(name, "").casefold() == actor.casefold(), "Qualification evidence actor differs")
    claims = data.get("claims", [])
    require(isinstance(claims, list) and 1 <= len(claims) <= 20 and claims == publication.get("claims"), "Claim manifests differ")
    wanted, owners = set(), set()
    for claim in claims:
        require(set(claim) == {"rva", "lease", "owner"}
                and re.fullmatch(r"0x[0-9A-F]{8}", claim.get("rva", ""))
                and claim["rva"] not in wanted
                and re.fullmatch(r"(?:[0-9a-f]{32}|[0-9a-f]{40})", claim.get("lease", "")), "Invalid claim")
        owner = re.fullmatch(r"github:([^:]+):bfme1:([a-z0-9][a-z0-9-]{0,60})", claim.get("owner", ""))
        require(owner and owner.group(1).casefold() == actor.casefold(), "Claim owner differs from current actor")
        wanted.add(claim["rva"])
        owners.add(claim["owner"])
    require(len(owners) == 1 and re.fullmatch(r"[A-Za-z0-9_.-]+", data.get("model", "")), "Invalid owner or model")
    body = data.get("body", {})
    require(body.get("rva") in wanted and allowed_source(body.get("source", ""))
            and body["source"].startswith("game/"), "Primary body is outside the claim/source scope")
    admissions = data.get("admissions", [body])
    require(isinstance(admissions, list) and 1 <= len(admissions) <= 4 and admissions[-1] == body
            and len({a["rva"] for a in admissions}) == len(admissions), "Invalid admission sequence")
    for admission in admissions:
        require(admission.get("rva") in wanted and admission.get("source") == body["source"]
                and type(admission.get("size")) is int and 0 < admission["size"] <= 32768,
                "Admission differs from the claimed translation unit")
    source_entries = data.get("files", [])
    require(isinstance(source_entries, list) and 1 <= len(source_entries) <= 8, "Invalid source file count")
    source_paths = set()
    for entry in source_entries:
        path = entry.get("path", "")
        require(allowed_source(path) and path.casefold() not in {p.casefold() for p in source_paths}
                and entry.get("mode") == "100644", "Invalid source path or mode")
        require(entry.get("base_blob") is None or hex_id(entry["base_blob"]), "Invalid source preimage")
        if entry.get("deleted") is True:
            require(entry["base_blob"] is not None and entry.get("candidate_blob") is None
                    and entry.get("sha256") is None and path != body["source"], "Invalid source deletion")
        else:
            require(hex_id(entry.get("candidate_blob")) and hex_id(entry.get("sha256"), 64), "Invalid source object pin")
        source_paths.add(path)
    require(body["source"] in source_paths, "Primary source missing from patch")
    bank_paths = {"targets/game/reverse/attempts/0x%08x.cpp" % int(a["rva"], 16) for a in admissions}
    files = publication.get("files", [])
    require(isinstance(files, list) and 1 <= len(files) <= 15, "Invalid qualified file count")
    seen = set()
    for entry in files:
        path = entry.get("path", "")
        safe_path(path)
        require(path in source_paths | LEDGERS | bank_paths and path.casefold() not in seen, "Qualified path exceeds allowlist")
        seen.add(path.casefold())
        if entry.get("deleted") is True:
            require(set(entry) == {"path", "deleted"} and path not in LEDGERS, "Invalid qualified deletion")
        else:
            require(path not in bank_paths and entry.get("mode") == "100644" and hex_id(entry.get("blob"))
                    and hex_id(entry.get("sha256"), 64) and type(entry.get("size")) is int
                    and 0 <= entry["size"] <= MAX_MEMBER, "Invalid qualified blob")
            require(entry.get("content_file") == request["qualification_directory"] + "/candidate-files/" + path,
                    "Candidate content path is not the exact exporter path")
    require(source_paths <= {f["path"] for f in files}, "Qualified commit omitted a reviewed source edit")
    result_sources = {f["path"]: f for f in files if f["path"] in source_paths}
    for source in source_entries:
        result = result_sources[source["path"]]
        require(bool(source.get("deleted")) == bool(result.get("deleted")), "Source deletion changed")
        if not source.get("deleted"):
            require(source["candidate_blob"] == result["blob"] and source["sha256"] == result["sha256"],
                    "Qualified source changed from the immutable reviewed patch")
    message = publication.get("message")
    require(isinstance(message, str) and "\0" not in message and len(message.encode()) <= 65536, "Invalid commit message")
    trailers = [line for line in message.splitlines() if line.startswith("Claim-Lease:")]
    require(sorted(trailers) == sorted("Claim-Lease: %s=%s" % (c["rva"], c["lease"]) for c in claims),
            "Commit claim trailers differ")
    progress = publication.get("progress", {})
    require(progress.get("base") == publication["base"] and progress.get("head") == publication["commit"]
            and all(type(progress.get(key)) is int for key in ("cpp_exact_before", "cpp_exact_after", "cpp_exact_delta"))
            and progress["cpp_exact_before"] >= 0
            and progress["cpp_exact_after"] - progress["cpp_exact_before"] == progress["cpp_exact_delta"] > 0,
            "Qualified artifact has no positive C++ exact delta")


def raw_commit(raw, publication):
    require(len(raw) <= 128 * 1024 and object_id("commit", raw) == publication["commit"], "Raw commit hash differs")
    require(b"\n\n" in raw, "Commit lacks a message boundary")
    headers, message = raw.split(b"\n\n", 1)
    lines = headers.split(b"\n")
    require(len(lines) == 4 and lines[0] == b"tree " + publication["tree"].encode()
            and lines[1] == b"parent " + publication["base"].encode()
            and lines[2].startswith(b"author ") and lines[3].startswith(b"committer ")
            and message == publication["message"].encode("utf-8"), "Commit parent, tree, headers or message differ")


class Runner:
    def __init__(self, source):
        self.source = Path(source).resolve()
        self.evidence = self.source.parent / "transfer-evidence"
        self.evidence.mkdir(exist_ok=True)
        self.receipt = {"status": "starting", "commands": [], "claims": [], "fork_ref_created": False}
        self.secrets = ()

    def save(self):
        (self.evidence / "receipt.json").write_text(json.dumps(self.receipt, indent=2) + "\n", encoding="utf-8")

    def run(self, label, argv, stdin=None, env=None, log=False, allowed=(0,)):
        result = subprocess.run(argv, cwd=self.source, input=stdin, env=env, capture_output=True)
        entry = {"label": label, "argv": [str(a) for a in argv], "exit_code": result.returncode,
                 "stdout_size": len(result.stdout), "stdout_sha256": digest(result.stdout)}
        self.receipt["commands"].append(entry)
        if log:
            filename = "%03d-%s.log" % (len(self.receipt["commands"]), label)
            output = result.stdout + result.stderr
            for secret in self.secrets:
                output = output.replace(secret.encode(), b"[redacted]")
            (self.evidence / filename).write_bytes(output)
            entry["log"] = filename
        self.save()
        print(">>> %s: exit %d, %d stdout bytes" % (label, result.returncode, len(result.stdout)), flush=True)
        require(result.returncode in allowed, label + " failed; inspect the retained command log")
        return result.stdout

    def git(self, label, *args, **kwargs):
        return self.run(label, ["git", *args], **kwargs)

    def rev(self, ref):
        value = self.git("object-id", "rev-parse", "--verify", ref).decode().strip()
        require(hex_id(value), "Invalid resolved object ID")
        return value

    def entry(self, ref, path):
        raw = self.git("tree-entry", "ls-tree", "-z", ref, "--", path)
        if not raw:
            return None
        metadata, actual_path = raw.rstrip(b"\0").split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        require(actual_path.decode() == path and kind == "blob" and mode == "100644", "Nonordinary tree entry")
        return oid

    def assert_master(self, expected, fetch=False):
        fields = self.git("actual-official-master", "ls-remote", "--exit-code", "origin", "refs/heads/master").decode().split()
        require(fields == [expected, "refs/heads/master"], "Official master changed; review a new qualification")
        if fetch:
            self.git("fetch-official-master", "fetch", "--no-tags", "--recurse-submodules=no", "origin",
                     "refs/heads/master:refs/remotes/origin/master", log=True)
            require(self.rev("refs/remotes/origin/master") == expected, "Official master changed during fetch")

    def claimed_rows(self, ref, data):
        # AGENTS requires narrow ledger selection: consume git show as lines,
        # never capture or decode the whole functions.csv just to select rows.
        argv = ["git", "show", ref + ":" + LEDGER]
        filename = "%03d-base-claim-rows.stderr.log" % (len(self.receipt["commands"]) + 1)
        record = {"label": "stream-base-claim-rows", "argv": argv, "exit_code": None, "stderr_log": filename}
        self.receipt["commands"].append(record)
        self.save()
        with (self.evidence / filename).open("wb") as stderr:
            process = subprocess.Popen(argv, cwd=self.source, stdout=subprocess.PIPE, stderr=stderr)
            try:
                with io.TextIOWrapper(process.stdout, encoding="utf-8", newline="") as lines:
                    rows = selected_claim_rows(lines, data)
            except BaseException:
                process.terminate()
                record["exit_code"] = process.wait()
                self.save()
                raise
            record["exit_code"] = process.wait()
        self.save()
        require(record["exit_code"] == 0, "Could not stream official base ledger rows")
        record.update(selected_row_count=len(rows), selected_rows_sha256=digest(json.dumps(rows, sort_keys=True).encode()))
        self.save()
        return rows


def protected_advance(path):
    parsed, low = PurePosixPath(path), path.lower()
    return (low.startswith(("tools/", ".githooks/", "inputs/", ".github/", "worldbuilder/",
                             "targets/worldbuilder/", "docs/", ".agents/", ".codex/", ".claude/"))
            or parsed.name.lower() in ("agents.md", "claude.md", "readme.md", "contributing.md", ".gitattributes",
                                        ".gitmodules", ".gitignore", "build.sh", "build.cmd")
            or parsed.suffix.lower() in (".h", ".hpp", ".hh", ".hxx", ".inl", ".inc")
            or low in ("targets/game/reverse/publisher_mode", "targets/game/reverse/analysis/verifier_upgrade_plan.md")
            or low.startswith("targets/game/reverse/retail_inventory/")
            or (low.startswith("targets/game/reverse/") and any(word in parsed.name.lower()
                for word in ("baseline", "whitelist", "flag_region", "flag_override"))))


def selected_claim_rows(lines, data):
    wanted = {int(claim["rva"], 16) for claim in data["claims"]}
    sources = {entry["path"] for entry in data["files"] if entry["path"].startswith("game/")}
    rows = []
    for row in csv.DictReader(lines):
        rva = int(row["target_rva"], 16)
        if rva in wanted:
            rows.append(row)
        require(not (row.get("status") == "matched" and row.get("source") in sources and rva not in wanted),
                "Edited translation unit has an unclaimed matched body")
    return rows


def validate_base(runner, data, publication):
    base = publication["base"]
    runner.git("reviewed-base-ancestry", "merge-base", "--is-ancestor", data["base"], base)
    require(runner.rev(data["base"] + "^{tree}") == data["base_tree"], "Original source tree pin differs")
    changed = runner.git("advanced-paths", "diff", "--no-renames", "--name-only", "-z", data["base"], base).decode().split("\0")
    require(not any(protected_advance(path) for path in changed if path), "Controls or shared inputs advanced")
    for entry in data["files"]:
        require(runner.entry(base, entry["path"]) == entry["base_blob"], "Reviewed source preimage advanced")
    rows = runner.claimed_rows(base, data)
    require(rows == data.get("base_rows"), "Claimed ledger rows advanced")
    require(runner.git("publisher-mode", "show", base + ":targets/game/reverse/publisher_mode").strip() == b"off",
            "Publisher mode must already be off")


def validate_blob(raw, entry):
    require(len(raw) == entry["size"] and digest(raw) == entry["sha256"]
            and object_id("blob", raw) == entry["blob"], "Qualified file content or Git object differs")


def import_exact(runner, publication, commit, read_content):
    raw_commit(commit, publication)
    with tempfile.TemporaryDirectory(prefix="bfme-import-") as directory:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(directory) / "index")}
        runner.git("import-base-tree", "read-tree", publication["base"], env=env)
        for entry in publication["files"]:
            path = entry["path"]
            if entry.get("deleted"):
                require(runner.entry(publication["base"], path) is not None, "Deletion has no base file")
                runner.git("import-deletion", "update-index", "--force-remove", "--", path, env=env)
            else:
                raw = read_content(entry)
                validate_blob(raw, entry)
                oid = runner.git("import-blob", "hash-object", "-w", "--stdin", stdin=raw).decode().strip()
                require(oid == entry["blob"], "Git imported a different blob")
                runner.git("import-index-entry", "update-index", "--add", "--cacheinfo", "100644", oid, path, env=env)
        require(runner.git("import-tree", "write-tree", env=env).decode().strip() == publication["tree"],
                "Reconstructed tree differs from the qualified tree")
    require(runner.git("import-raw-commit", "hash-object", "-t", "commit", "-w", "--stdin", stdin=commit).decode().strip()
            == publication["commit"], "Git imported a different raw commit")
    validate_objects(runner, publication)


def validate_objects(runner, publication):
    commit = publication["commit"]
    raw_commit(runner.git("verify-raw-commit", "cat-file", "commit", commit), publication)
    require(runner.rev(commit + "^{tree}") == publication["tree"], "Imported commit tree differs")
    changed = set(filter(None, runner.git("qualified-paths", "diff", "--no-renames", "--name-only", "-z",
                                         publication["base"], commit).decode().split("\0")))
    require(changed == {entry["path"] for entry in publication["files"]}, "Imported commit changes an unlisted path")
    for entry in publication["files"]:
        require(runner.entry(commit, entry["path"]) == (None if entry.get("deleted") else entry["blob"]),
                "Imported entry mode or object differs")
        if not entry.get("deleted"):
            validate_blob(runner.git("qualified-content", "cat-file", "blob", entry["blob"]), entry)


def initial_checkout(runner, request):
    require(runner.rev("HEAD") == request["expected_base"], "Checkout is not the actual qualified base")
    require(not runner.git("initial-status", "status", "--porcelain"), "Initial source checkout is not clean")
    require(runner.git("official-origin", "remote", "get-url", "origin").decode().strip().removesuffix(".git")
            == UPSTREAM.removesuffix(".git"), "Origin must remain the real official repository")
    runner.assert_master(request["expected_base"], fetch=True)


def prepare_hooks(runner, data):
    require(sys.platform == "win32" and sys.version_info[:2] == (3, 12), "Native Windows Python 3.12 required")
    require(digest((runner.source / COMPILER).read_bytes()) == COMPILER_SHA256, "Original MSVC 7.1 compiler differs")
    bash = Path(os.environ.get("BFME_TRANSFER_BASH", ""))
    require(bash.is_absolute() and bash.is_file(), "Native Git Bash path missing")
    runner.run("install-normal-requirements", [sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
                                               "--no-cache-dir", "-r", "tools/requirements.txt"], log=True)
    runner.run("ordinary-hook-setup", [str(bash), "tools/setup_hooks.sh"], log=True)
    require(runner.git("ordinary-hooks-path", "config", "--get", "core.hooksPath").decode().strip() == ".githooks",
            "Ordinary hooks must remain enabled")
    require(os.environ.get("BFME_CLAIMS", "on") != "off", "Claims must not be disabled")
    os.environ["BFME_CLAIM_OWNER"] = data["claims"][0]["owner"]
    os.environ["BFME_MODEL"] = data["model"]
    sys.path.insert(0, str(runner.source / "tools"))
    return str(bash)


def current_claims(runner, data, label, module=None, now=None):
    claims = importlib.import_module("claims") if module is None else module
    now = time.time() if now is None else now
    require(claims.fetch(), "Could not fetch real upstream claims")
    live, proof = claims._read_local(), []
    for expected in data["claims"]:
        rva = int(expected["rva"], 16)
        require(rva in live, "A required actual claim is missing")
        token, info = live[rva]
        require(info.get("owner") == expected["owner"] and info.get("lease", token) == expected["lease"]
                and info.get("expires", 0) > now, "An actual claim changed or expired")
        require(claims.holds(rva, token), "Actual upstream claim moved during readback")
        proof.append({"rva": expected["rva"], "token": token, "record": info})
    runner.receipt["claims"].append({"at": label, "checked_at": now, "proof": proof})
    runner.save()


def cpp_progress(publication):
    progress = importlib.import_module("progress")
    start, size = progress.retail_text()
    def value(ref):
        matched = progress.matched_at(ref)
        return progress.coverage(matched, start, size, progress.naked_cpp_rows_at(matched, ref))["cpp"]
    before, after = value(publication["base"]), value(publication["commit"])
    actual = {"base": publication["base"], "head": publication["commit"], "cpp_exact_before": before,
              "cpp_exact_after": after, "cpp_exact_delta": after - before}
    require(actual == publication["progress"] and actual["cpp_exact_delta"] > 0,
            "Actual C++ exact progress differs or is not positive")
    return actual


def candidate_checkout(runner, publication):
    runner.git("exact-candidate-checkout", "switch", "-c", LOCAL_REF.removeprefix("refs/heads/"), publication["commit"], log=True)
    require(runner.rev("HEAD") == publication["commit"], "Candidate checkout changed the exact commit")
    for entry in publication["files"]:
        if not entry.get("deleted"):
            validate_blob((runner.source / entry["path"]).read_bytes(), entry)
    require(not runner.git("candidate-status", "status", "--porcelain"), "Candidate checkout is not clean")


def verify_job(runner, api, request, request_hash, context):
    initial_checkout(runner, request)
    source_provenance(api, request, context["GITHUB_ACTOR"])
    path = runner.source.parent / "qualification-artifact.zip"
    api.artifact(request["artifact_id"], request["artifact_sha256"], path)
    archive = Archive(path)
    try:
        # Bind these small artifact inputs to the reviewed source head too.
        for name in ("input-manifest.json", "candidate.patch", "commit-message.txt"):
            require(archive.read(name, 1024 * 1024) == api.content(
                ".github/qualification/bfme1-body/" + name, request["qualification_head_sha"]),
                "Artifact input differs from the immutable qualification head")
        data, publication, result = archive.json("input-manifest.json"), archive.json("publication-manifest.json"), archive.json("result.json")
        validate_manifests(request, data, publication, context["GITHUB_ACTOR"])
        require(result.get("status") == "qualified" and result.get("published") is False
                and result.get("candidate") == publication and result.get("input") == data,
                "Qualification result does not attest these exact manifests")
        require(digest(archive.read("candidate.patch")) == data.get("patch_sha256")
                and digest(archive.read("commit-message.txt")) == data.get("message_sha256")
                and archive.read("commit-message.txt") == publication["message"].encode(), "Reviewed payload hashes differ")
        validate_base(runner, data, publication)
        commit = archive.read(request["qualification_directory"] + "/commit-object.txt", 128 * 1024)
        import_exact(runner, publication, commit, lambda entry: archive.read(entry["content_file"]))
    finally:
        archive.close()
    candidate_checkout(runner, publication)
    bash = prepare_hooks(runner, data)
    current_claims(runner, data, "before-full-native-gate")
    runner.assert_master(publication["base"], fetch=True)
    refs = "%s %s refs/heads/master %s\n" % (LOCAL_REF, publication["commit"], publication["base"])
    (runner.evidence / "full-pre-push-stdin.txt").write_text(refs, encoding="utf-8", newline="\n")
    runner.run("full-ordinary-native-pre-push", [bash, ".githooks/pre-push", "origin", UPSTREAM], stdin=refs.encode(), log=True)
    current_claims(runner, data, "after-full-native-gate")
    runner.assert_master(publication["base"])
    progress = cpp_progress(publication)
    runner.run("ordinary-session-progress", [sys.executable, "tools/progress.py", "origin/master"], log=True)
    require(not runner.git("post-gate-status", "status", "--porcelain"), "Native gate left a modified tracked tree")
    output = runner.source.parent / "verified-transfer"
    output.mkdir()
    bundle = output / "candidate.bundle"
    runner.git("export-exact-bundle", "bundle", "create", str(bundle), publication["base"] + ".." + LOCAL_REF, log=True)
    receipt = {"schema": 1, "request_sha256": request_hash, "request": request, "workflow": context,
               "source_artifact_sha256": request["artifact_sha256"], "input": data, "publication": publication,
               "bundle_sha256": digest(bundle.read_bytes()), "bundle_size": bundle.stat().st_size,
               "full_normal_native_pre_push_passed": True, "progress": progress,
               "actual_claims": runner.receipt["claims"], "target_ref": target_ref(request)}
    (output / "transfer-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    runner.receipt.update(status="verified", progress=progress, commit=publication["commit"], tree=publication["tree"],
                          full_normal_native_pre_push_passed=True, target_ref=target_ref(request))


def validate_bundle_header(raw, publication):
    require(raw.startswith(b"# v2 git bundle\n") and b"\n\n" in raw, "Unsupported Git bundle format")
    header = raw.split(b"\n\n", 1)[0].split(b"\n")
    require(len(header) == 3 and header[1].startswith(b"-" + publication["base"].encode() + b" ")
            and header[2] == publication["commit"].encode() + b" " + LOCAL_REF.encode(),
            "Bundle does not have exactly the qualified base prerequisite and one exact head")


def push_command(request):
    ref = target_ref(request)
    return ["git", "push", "--porcelain", "--force-with-lease=" + ref + ":", FORK_URL,
            request["expected_commit"] + ":" + ref]


def push_environment(token, environ):
    # The token lives only in this process and the one authenticated Git child.
    # Its URL scope cannot authorize claims fetches or writes to official origin.
    env = {key: value for key, value in environ.items()
           if not key.startswith("GIT_TRACE") and key not in ("GIT_CURL_VERBOSE", "BFME_TRANSFER_TOKEN")}
    count = int(env.get("GIT_CONFIG_COUNT", "0"))
    require(0 <= count <= 20, "Unexpected Git environment configuration count")
    value = "AUTHORIZATION: basic " + base64.b64encode(("x-access-token:" + token).encode()).decode()
    env.update({"GIT_CONFIG_COUNT": str(count + 1), "GIT_CONFIG_KEY_" + str(count): "http." + FORK_URL + ".extraheader",
                "GIT_CONFIG_VALUE_" + str(count): value, "GIT_TERMINAL_PROMPT": "0"})
    return env, value


def existing_ref(runner, request):
    ref = target_ref(request)
    lines = runner.git("fixed-fork-branch-readback", "ls-remote", FORK_URL, ref).decode().splitlines()
    if not lines:
        return False
    require(lines == [request["expected_commit"] + "\t" + ref], "Target branch exists at a different commit")
    return True


def transfer_job(runner, api, request, request_hash, context):
    initial_checkout(runner, request)
    source_provenance(api, request, context["GITHUB_ACTOR"])
    artifact_id = os.environ.get("BFME_VERIFIED_ARTIFACT_ID", "")
    sha256 = os.environ.get("BFME_VERIFIED_ARTIFACT_DIGEST", "")
    require(re.fullmatch(r"[1-9][0-9]*", artifact_id) and hex_id(sha256, 64), "Verified handoff artifact pin missing")
    artifact_id = int(artifact_id)
    meta = api.json("/actions/artifacts/%d" % artifact_id)
    check_artifact(meta, artifact_id, sha256, int(context["GITHUB_RUN_ID"]), context["GITHUB_SHA"],
                   "bfme1-transfer-%s-%s" % (context["GITHUB_RUN_ID"], context["GITHUB_RUN_ATTEMPT"]))
    path = runner.source.parent / "verified-artifact.zip"
    api.artifact(artifact_id, sha256, path)
    archive = Archive(path)
    try:
        require(set(archive.entries) == {"candidate.bundle", "transfer-receipt.json"}, "Unexpected verified handoff files")
        receipt = archive.json("transfer-receipt.json")
        require(receipt.get("schema") == 1 and receipt.get("request") == request and receipt.get("request_sha256") == request_hash
                and all(receipt.get("workflow", {}).get(key) == context[key] for key in WORKFLOW_KEYS if key != "ImageVersion")
                and receipt.get("source_artifact_sha256") == request["artifact_sha256"]
                and receipt.get("full_normal_native_pre_push_passed") is True
                and receipt.get("target_ref") == target_ref(request), "Handoff is not from this exact read-only verification job")
        data, publication = receipt["input"], receipt["publication"]
        validate_manifests(request, data, publication, context["GITHUB_ACTOR"])
        require(receipt.get("progress") == publication["progress"], "Handoff C++ progress differs")
        validate_base(runner, data, publication)
        bundle = archive.read("candidate.bundle")
        require(len(bundle) == receipt.get("bundle_size") and digest(bundle) == receipt.get("bundle_sha256"), "Verified Git bundle differs")
        validate_bundle_header(bundle, publication)
        bundle_path = runner.source.parent / "candidate.bundle"
        bundle_path.write_bytes(bundle)
    finally:
        archive.close()
    runner.git("verify-exact-bundle", "bundle", "verify", str(bundle_path), log=True)
    runner.git("import-exact-bundle", "fetch", "--no-tags", "--no-write-fetch-head", "--recurse-submodules=no",
               str(bundle_path), LOCAL_REF, log=True)
    validate_objects(runner, publication)
    candidate_checkout(runner, publication)
    prepare_hooks(runner, data)
    current_claims(runner, data, "immediately-before-fork-transfer")
    runner.assert_master(publication["base"], fetch=True)
    require(cpp_progress(publication) == receipt["progress"], "Transfer objects have different C++ progress")
    if existing_ref(runner, request):
        runner.receipt.update(status="already-present-exact", commit=publication["commit"], target_ref=target_ref(request))
        return
    env, header = push_environment(api.token, os.environ)
    # Never print the token or its reversible encoding, including mask commands.
    runner.secrets = (api.token, header, header.removeprefix("AUTHORIZATION: basic "))
    runner.run("atomic-create-fixed-fork-branch", push_command(request), env=env, log=True)
    runner.receipt["fork_ref_created"] = True
    runner.save()
    require(existing_ref(runner, request), "Created fork branch is not readable at the exact commit")
    current_claims(runner, data, "after-fork-transfer")
    runner.assert_master(publication["base"])
    runner.receipt.update(status="transferred", commit=publication["commit"], tree=publication["tree"],
                          base=publication["base"], target_ref=target_ref(request), progress=receipt["progress"],
                          full_native_gate="separate read-only verification job against real official master",
                          actual_push_gate="unmodified ordinary hook; new branch receives static checks",
                          publication_scope="fork candidate branch only; official repository unchanged")


def main():
    require(len(sys.argv) == 2 and sys.argv[1] in ("pin", "verify", "transfer"), "Use a fixed pin, verify or transfer command")
    request, request_hash = read_request()
    context = workflow_context(os.environ)
    if sys.argv[1] == "pin":
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write("base=" + request["expected_base"] + "\n")
        return
    # Children (pip, tools, hooks) must not inherit the raw repository token.
    token = os.environ.pop("BFME_TRANSFER_TOKEN", "")
    runner = Runner(Path.cwd())
    runner.receipt.update(request_sha256=request_hash, workflow=context, command=sys.argv[1])
    try:
        api = GitHub(token)
        job = verify_job if sys.argv[1] == "verify" else transfer_job
        job(runner, api, request, request_hash, context)
    except Exception as error:
        runner.receipt.update(status="rejected", reason=str(error) if isinstance(error, Rejected) else type(error).__name__)
        # No traceback: urllib exceptions can expose credential-bearing URLs.
        print("Transfer rejected: " + runner.receipt["reason"], file=sys.stderr)
        return 1
    finally:
        runner.save()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Rejected as error:
        print("Transfer rejected: " + str(error), file=sys.stderr)
        sys.exit(1)
