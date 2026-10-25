"""Native, single-target attempt banking; never a recovery or command runner.

Only the unmodified official re_log.py writes the bank, history, and verdict.
The read-only job measures, commits, and runs the complete ordinary push gate.
The separate write job can transfer only that exact zero-progress commit to a
fresh derived banked branch in the contributor fork. It runs no artifact code.
"""

import hashlib
import importlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time


HELPER = Path(__file__).resolve().parent.parent / "bfme1-transfer" / "transfer.py"
HELPER_SHA256 = "2d8f7d1bbbb810276594c7ac46d361c915bfe818f251012e3eae6e5e67b29a26"
if hashlib.sha256(HELPER.read_bytes()).hexdigest() != HELPER_SHA256:
    raise RuntimeError("Reviewed object-transfer helper changed")
_spec = importlib.util.spec_from_file_location("reviewed_bfme_transfer_helpers", HELPER)
t = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t)
require, Rejected = t.require, t.Rejected

WORKFLOW = ".github/workflows/bfme1-attempt-bank.yml"
RVA = "0x008C6AD0"
SYMBOL = "?BooleanCoerce008C6AD0@@YAPAVAptValue@@PAXH@Z"
OWNER = "github:mcmickey93:bfme1:cpp-loop-2"
MODEL = "gpt-6-astra-pro"
LOCAL_REF = "refs/heads/attempt-bank/008c6ad0"
LOG = "targets/game/reverse/re_attempts.log"
BANK = "targets/game/reverse/attempts/0x008c6ad0.cpp"
HISTORY = "targets/game/reverse/attempt_history/0x008c6ad0/"
SUPPORT = "targets/game/reverse/attempt_support/008c6ad0-tail-order-20261025/"
BEST = SUPPORT + "best-whole-tu.cpp.txt"
HANDOFF = SUPPORT + "readme.md"
BEST_BLOB = "6f590f236f882e4fa62d50b22b5214ed2c5a4b8c"
BEST_SHA256 = "872ab57f5654deadc23c474e1307b6a73709030d396b5cfd923b3c827539f927"
GAME_SOURCE = "game/Libraries/Source/Apt/AptActionInterpreter.cpp"
GAME_BLOB = "60df2491d6c680d667ad689a1e79e7203aca56e3"
CLAIM_RVAS = {RVA, "0x008CF1B0"}
REQUEST_KEYS = {"schema", "enabled", "expected_base", "expected_tree",
                "previous_bank_blob", "support_files", "claims", "base_rows"}
EVIDENCE = (
    "Complete retail extent 0x008C6AD0..0x008C6BB8, ret followed by alignment; "
    "t=60min model=gpt-6-astra-pro blocker=codegen-order/branch-tail-order "
    "handoff=" + HANDOFF + " native-run=40186548577 best-variant=07 "
    "ours=229/233 nonreloc-diffs=120 first-diff=+0x3C relocs=11 drift-sites=8 "
    "instruction-shape=0.893. Canonical callee/data bindings and array-load roles verified; "
    "four factory blocks retained but shared numeric stays at +0xB7 instead of +0x8A. "
    "Original 520B sibling remains exact modulo relocations. 06 equals04 and08 equals07; "
    "+0 C++ exact bytes. Submitted score is shape only; accept tool remeasurement "
    "and preserve the better canonical bank."
)


def read_request(raw=None):
    raw = Path(__file__).with_name("request.json").read_bytes() if raw is None else raw
    data = t.json_bytes(raw)
    require(isinstance(data, dict) and set(data) == REQUEST_KEYS, "Unexpected bank request fields")
    require(type(data["schema"]) is int and data["schema"] == 1 and data["enabled"] is True,
            "Bank request is disabled pending review")
    for key in ("expected_base", "expected_tree", "previous_bank_blob"):
        require(t.hex_id(data[key]), "Invalid reviewed source or existing-bank pin")
    files = data["support_files"]
    require(isinstance(files, list) and len(files) == 2
            and all(isinstance(f, dict) for f in files)
            and {f.get("path") for f in files} == {BEST, HANDOFF}, "Only the two fixed committed inputs are allowed")
    for entry in files:
        require(set(entry) == {"path", "blob", "sha256", "size"}
                and t.hex_id(entry["blob"]) and t.hex_id(entry["sha256"], 64)
                and type(entry["size"]) is int and 0 < entry["size"] <= 65536,
                "Invalid fixed support input")
        if entry["path"] == BEST:
            require(entry["blob"] == BEST_BLOB and entry["sha256"] == BEST_SHA256
                    and entry["size"] == 8354, "Input is not the reviewed best07 whole file")
    claims = data["claims"]
    require(isinstance(claims, list) and len(claims) == 2
            and all(isinstance(c, dict) for c in claims)
            and {c.get("rva") for c in claims} == CLAIM_RVAS, "Bank claim scope changed")
    for claim in claims:
        require(set(claim) == {"rva", "lease", "owner"} and claim["owner"] == OWNER
                and isinstance(claim.get("lease"), str)
                and re.fullmatch(r"[0-9a-f]{32}|[0-9a-f]{40}", claim.get("lease", "")), "Invalid actual claim pin")
    rows = data["base_rows"]
    require(isinstance(rows, list) and len(rows) == 2
            and all(isinstance(r, dict) and all(isinstance(v, str) for v in r.values()) for r in rows)
            and {r.get("target_rva") for r in rows} == CLAIM_RVAS, "Reviewed body rows missing")
    return data, t.digest(raw)


def context(environ):
    result = t.workflow_context(environ)
    require(result["GITHUB_ACTOR"].casefold() == "mcmickey93" and result["RUNNER_OS"] == "Windows",
            "Only the pinned claim owner and native runner may dispatch")
    return result


def check_run(api, ctx):
    run = api.json("/actions/runs/%s/attempts/%s" % (ctx["GITHUB_RUN_ID"], ctx["GITHUB_RUN_ATTEMPT"]))
    require(run.get("id") == int(ctx["GITHUB_RUN_ID"])
            and run.get("run_attempt") == int(ctx["GITHUB_RUN_ATTEMPT"])
            and run.get("head_sha") == ctx["GITHUB_SHA"] and run.get("path") == WORKFLOW
            and run.get("event") == "workflow_dispatch" and run.get("head_branch") == "master",
            "Bank run provenance changed")
    for key in ("repository", "head_repository"):
        require(run.get(key, {}).get("full_name") == t.FORK, "Run is outside the fixed fork")
    require(run["repository"].get("fork") is True and run["repository"].get("private") is False,
            "Bank workflow requires the public contributor fork")
    for key in ("actor", "triggering_actor"):
        require(run.get(key, {}).get("login", "").casefold() == ctx["GITHUB_ACTOR"].casefold(), "Run actor changed")


class Runner:
    """Logging for the fixed operations below; not exposed as a CLI command."""
    def __init__(self, source):
        self.source = Path(source).resolve()
        self.evidence = self.source.parent / "bank-evidence"
        self.evidence.mkdir(exist_ok=True)
        self.receipt = {"status": "starting", "commands": [], "claims": [], "fork_ref_created": False}
        self.secrets = ()

    def save(self):
        (self.evidence / "receipt.json").write_text(json.dumps(self.receipt, indent=2) + "\n", encoding="utf-8")

    def run(self, label, argv, stdin=None, env=None, log=False):
        result = subprocess.run(argv, cwd=self.source, input=stdin, env=env, capture_output=True)
        entry = {"label": label, "argv": [str(a) for a in argv], "exit_code": result.returncode,
                 "stdout_size": len(result.stdout), "stdout_sha256": t.digest(result.stdout)}
        self.receipt["commands"].append(entry)
        if log:
            output = result.stdout + result.stderr
            for secret in self.secrets:
                output = output.replace(secret.encode(), b"[redacted]")
            name = "%03d-%s.log" % (len(self.receipt["commands"]), label)
            (self.evidence / name).write_bytes(output)
            entry["log"] = name
        self.save()
        print(">>> %s: exit %d, %d stdout bytes" % (label, result.returncode, len(result.stdout)), flush=True)
        require(result.returncode == 0, label + " failed; inspect the retained log")
        return result.stdout

    def git(self, label, *args, **kwargs):
        return self.run(label, ["git", *args], **kwargs)

    def rev(self, ref):
        value = self.git("object-id", "rev-parse", "--verify", ref).decode().strip()
        require(t.hex_id(value), "Invalid resolved Git object")
        return value

    def entry(self, ref, path):
        raw = self.git("ordinary-tree-entry", "ls-tree", "-z", ref, "--", path)
        if not raw:
            return None
        meta, actual = raw.rstrip(b"\0").split(b"\t", 1)
        mode, kind, oid = meta.decode().split()
        require(actual.decode() == path and mode == "100644" and kind == "blob", "Nonordinary file entry")
        return oid

    def assert_master(self, expected, fetch=False):
        raw = self.git("actual-official-master", "ls-remote", "--exit-code", "origin", "refs/heads/master")
        require(raw.decode().split() == [expected, "refs/heads/master"], "Official master moved; review a fresh bank base")
        if fetch:
            self.git("fetch-official-master", "fetch", "--no-tags", "--recurse-submodules=no", "origin",
                     "refs/heads/master:refs/remotes/origin/master", log=True)
            require(self.rev("origin/master") == expected, "Official master moved during fetch")


def initial_checkout(runner, request):
    require(runner.rev("HEAD") == request["expected_base"]
            and runner.rev("HEAD^{tree}") == request["expected_tree"], "Wrong immutable source checkout")
    require(not runner.git("initial-status", "status", "--porcelain"), "Initial source tree is dirty")
    require(runner.git("official-origin", "remote", "get-url", "origin").decode().strip().removesuffix(".git")
            == t.UPSTREAM.removesuffix(".git"), "Origin must remain the real official repository")
    runner.assert_master(request["expected_base"], fetch=True)
    require(runner.entry("HEAD", BANK) == request["previous_bank_blob"], "The retained bank preimage changed")
    require(runner.entry("HEAD", GAME_SOURCE) == GAME_BLOB, "Original same-TU source context changed")
    for entry in request["support_files"]:
        require(runner.entry("HEAD", entry["path"]) == entry["blob"], "Committed support input changed")
        t.validate_blob((runner.source / entry["path"]).read_bytes(), entry)
    require(runner.git("publisher-mode", "show", "HEAD:targets/game/reverse/publisher_mode").strip() == b"off",
            "Publisher mode must already be off")
    # Select only the two claimed rows, without loading functions.csv whole.
    process = subprocess.Popen(["git", "show", "HEAD:" + t.LEDGER], cwd=runner.source, stdout=subprocess.PIPE)
    try:
        with io.TextIOWrapper(process.stdout, encoding="utf-8", newline="") as lines:
            rows = t.selected_claim_rows(lines, {"claims": request["claims"], "files": [{"path": GAME_SOURCE}]})
        require(process.wait() == 0 and rows == request["base_rows"], "Claimed ledger rows changed")
    finally:
        if process.poll() is None:
            process.terminate()
        process.wait()


def prepare_native(runner):
    for name in ("CL", "_CL_", "BUILD_RECOMPILE_ONLY", "MSYS_NO_PATHCONV", "MSYS2_ARG_CONV_EXCL"):
        require(not os.environ.get(name), "Native measurement environment override: " + name)
    require(sys.platform == "win32" and sys.version_info[:2] == (3, 12), "Native Windows Python 3.12 required")
    require(t.digest((runner.source / t.COMPILER).read_bytes()) == t.COMPILER_SHA256, "Original MSVC 7.1 compiler changed")
    require(not os.environ.get("BFME_TARGET") and not os.environ.get("BFME_TARGET_SHA256")
            and os.environ.get("BFME_CLAIMS", "on") != "off", "Target redirection or disabled claims are forbidden")
    bash = Path(os.environ.get("BFME_BANK_BASH", ""))
    require(bash.is_absolute() and bash.is_file(), "Native Git Bash path missing")
    runner.run("normal-requirements", [sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
                                      "--no-cache-dir", "-r", "tools/requirements.txt"], log=True)
    runner.run("ordinary-hook-setup", [str(bash), "tools/setup_hooks.sh"], log=True)
    require(runner.git("ordinary-hooks-path", "config", "--get", "core.hooksPath").strip() == b".githooks",
            "Ordinary hooks must remain enabled")
    os.environ["BFME_CLAIM_OWNER"], os.environ["BFME_MODEL"] = OWNER, MODEL
    sys.path.insert(0, str(runner.source / "tools"))
    return str(bash)


def current_claims(runner, request, label):
    claims = importlib.import_module("claims")
    require(claims.fetch(), "Cannot read real official claim refs")
    current, proof, now = claims._read_local(), [], time.time()
    for expected in request["claims"]:
        rva = int(expected["rva"], 16)
        require(rva in current, "Required official claim is missing")
        token, record = current[rva]
        require(record.get("owner") == expected["owner"] and record.get("lease", token) == expected["lease"]
                and record.get("expires", 0) > now and claims.holds(rva, token), "Actual claim changed or expired")
        proof.append({"rva": expected["rva"], "token": token, "record": record})
    runner.receipt["claims"].append({"at": label, "checked_at": now, "proof": proof})
    runner.save()


def allowed_result(path):
    t.safe_path(path)
    return path in (BANK, LOG) or re.fullmatch(re.escape(HISTORY) + r"[0-9a-f]{64}\.json", path) is not None


def validate_append(before, after):
    require(after.startswith(before), "Attempt log was rewritten or truncated")
    delta = after[len(before):]
    require(delta.endswith(b"\n") and delta.count(b"\n") == 1 and b"\r" not in delta,
            "Banking must append exactly one LF verdict row")
    fields = delta[:-1].decode("utf-8").split("\t")
    require(len(fields) == 5 and fields[:4] == [SYMBOL, RVA, "233", "partial"], "Appended verdict target or status changed")
    for token in ("model=" + MODEL, "handoff=" + HANDOFF, "native-run=40186548577", "best-variant=07", "submitted=0.893"):
        require(token in fields[4].split(), "Required bank evidence token missing")
    measured = evidence_token(fields[4], "measured")
    require(re.fullmatch(r"(?:0(?:\.\d+)?|1(?:\.0+)?)", measured), "Unmodified tool did not record a measured score")
    require(evidence_token(fields[4], "stash") == BANK, "Bank verdict points elsewhere")
    return fields[4], float(measured)


def evidence_token(evidence, key):
    values = [token[len(key) + 1:] for token in evidence.split() if token.startswith(key + "=")]
    require(len(values) == 1, "Missing or repeated " + key + " evidence token")
    return values[0]


def zero_progress(base, commit):
    progress = importlib.import_module("progress")
    start, size = progress.retail_text()
    def value(ref):
        matched = progress.matched_at(ref)
        return progress.coverage(matched, start, size, progress.naked_cpp_rows_at(matched, ref))["cpp"]
    before, after = value(base), value(commit)
    require(after == before, "Attempt banking changed exact C++ coverage")
    return {"base": base, "head": commit, "cpp_exact_before": before,
            "cpp_exact_after": after, "cpp_exact_delta": 0}


def validate_publication(publication, request, ctx):
    require(publication.get("kind") == "native-attempt-bank" and publication.get("repository") == t.OFFICIAL
            and publication.get("published") is False and publication.get("normal_commit_passed") is True
            and publication.get("full_normal_pre_push_passed") is True
            and publication.get("native_re_log_passed") is True
            and publication.get("base") == request["expected_base"], "Not a completed native bank result")
    for key in ("commit", "tree"):
        require(t.hex_id(publication.get(key)), "Invalid banked Git object")
    files = publication.get("files")
    require(isinstance(files, list) and 1 <= len(files) <= 4, "Bank result exceeds the one-target file bound")
    seen = set()
    for entry in files:
        require(isinstance(entry, dict) and set(entry) == {"path", "mode", "blob", "sha256", "size"}
                and allowed_result(entry["path"]) and entry["path"] not in seen
                and entry["mode"] == "100644" and t.hex_id(entry["blob"])
                and t.hex_id(entry["sha256"], 64) and type(entry["size"]) is int
                and 0 < entry["size"] <= t.MAX_MEMBER, "Bank result contains a forbidden file or mode")
        seen.add(entry["path"])
    require(LOG in seen, "No appended attempt verdict")
    message = publication.get("message")
    require(isinstance(message, str) and "\0" not in message and len(message.encode()) < 16384, "Invalid bank commit message")
    trailers = [line for line in message.splitlines() if line.startswith("Claim-Lease:")]
    require(sorted(trailers) == sorted("Claim-Lease: %s=%s" % (c["rva"], c["lease"]) for c in request["claims"]),
            "Bank commit claim trailers changed")
    actual = publication.get("progress", {})
    require(actual.get("base") == publication["base"] and actual.get("head") == publication["commit"]
            and all(type(actual.get(k)) is int for k in ("cpp_exact_before", "cpp_exact_after", "cpp_exact_delta"))
            and actual["cpp_exact_before"] >= 0 and actual["cpp_exact_before"] == actual["cpp_exact_after"]
            and actual["cpp_exact_delta"] == 0, "Bank publication requires exactly zero C++ delta")
    require(all(publication.get("workflow", {}).get(k) == ctx[k]
                for k in t.WORKFLOW_KEYS if k != "ImageVersion")
            and publication.get("claims") == request["claims"], "Bank context changed")


def validate_result_contents(runner, base, commit, request):
    """All bank/history parsing uses the pinned repository's own source parser."""
    re_log = importlib.import_module("re_log")
    old = runner.git("retained-bank-before", "show", base + ":" + BANK)
    incoming = (runner.source / BEST).read_bytes()
    old_body, incoming_body = re_log._source_body(old), re_log._source_body(incoming)
    bodies = {t.digest(old_body), t.digest(incoming_body)}
    preferred = re_log.stash_for(int(RVA, 16))
    require(preferred is not None and preferred[0].resolve() == (runner.source / BANK).resolve(), "Canonical bank missing")
    require(t.digest(re_log._source_body(preferred[0].read_bytes())) in bodies, "Tool-selected bank is neither measured input")
    before = runner.git("attempt-log-before", "show", base + ":" + LOG)
    after = (runner.source / LOG).read_bytes()
    evidence, measured = validate_append(before, after)
    preferred_body = re_log._source_body(preferred[0].read_bytes())
    require(preferred[1] >= measured and (preferred_body != incoming_body or preferred[1] == measured),
            "Preferred bank contradicts the incoming measured score")
    preferred_score = evidence_token(evidence, "score")
    require(re.fullmatch(r"(?:0(?:\.\d+)?|1(?:\.0+)?)", preferred_score)
            and float(preferred_score) == preferred[1], "Verdict disagrees with the tool-selected bank score")
    alternative = evidence_token(evidence, "alternative")
    require(allowed_result(alternative) and alternative.startswith(HISTORY),
            "Measured incoming history record missing")
    paths = set(filter(None, runner.git("banked-paths", "diff", "--name-only", "--no-renames", "-z", base, commit).decode().split("\0")))
    for path in paths | {alternative}:
        require(allowed_result(path), "Attempt result changes a forbidden path")
        if path.startswith(HISTORY):
            if path in paths:
                require(runner.entry(base, path) is None, "Existing attempt history was changed")
            raw = (runner.source / path).read_bytes()
            item = t.json_bytes(raw)
            require(isinstance(item, dict) and set(item) == {"schema", "sha256", "symbol", "score_kind", "score", "source"}
                    and type(item["schema"]) is int and item["schema"] == 1 and isinstance(item["source"], str)
                    and item["score_kind"] in ("author-estimate", "measured")
                    and type(item["score"]) in (int, float) and math.isfinite(item["score"])
                    and 0 <= item["score"] <= 1, "Invalid tool history record")
            source = item["source"].encode("utf-8")
            require(t.digest(source) == item["sha256"] == Path(path).stem
                    and source.splitlines() and item["symbol"] == source.splitlines()[0].decode()[3:]
                    and t.digest(re_log._source_body(source)) in bodies, "History source differs from both measured inputs")
            if path == alternative:
                require(item["score_kind"] == "measured" and item["score"] == measured
                        and item["symbol"] == SYMBOL and re_log._source_body(source) == incoming_body,
                        "Incoming measurement record differs")
            else:
                require(source == old, "Retained history did not preserve the exact original bank")
    return {"previous_bank_blob": request["previous_bank_blob"], "incoming_blob": BEST_BLOB,
            "incoming_measured_score": measured, "preferred_score": preferred[1], "alternative": alternative,
            "retained_bank_required_before_unmodified_re_log": True}


def bank_command():
    return [sys.executable, "tools/re_log.py", "record", SYMBOL, RVA, "233", "partial", EVIDENCE,
            "--stash", BEST, "--score", "0.893"]


def changed_paths(runner, base):
    paths = set(filter(None, runner.git("working-bank-paths", "diff", "--no-renames", "--name-only", "-z", base).decode().split("\0")))
    paths.update(filter(None, runner.git("untracked-bank-paths", "ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")))
    require(1 <= len(paths) <= 4 and LOG in paths and all(allowed_result(p) for p in paths),
            "Native bank changed paths outside its strict result scope")
    require(all((runner.source / p).is_file() and not (runner.source / p).is_symlink() for p in paths),
            "Native bank deleted a file or introduced a link")
    return sorted(paths)


def publication_for(runner, request, ctx, paths):
    commit = runner.rev("HEAD")
    require(runner.rev(commit + "^") == request["expected_base"], "Bank commit has a different parent")
    files = []
    for path in paths:
        blob = runner.entry(commit, path)
        raw = runner.git("banked-blob", "cat-file", "blob", blob)
        require(raw == (runner.source / path).read_bytes(), "Committed bank bytes differ from the tool's result")
        files.append({"path": path, "mode": "100644", "blob": blob, "sha256": t.digest(raw), "size": len(raw)})
    raw = runner.git("raw-bank-commit", "cat-file", "commit", commit)
    publication = {"kind": "native-attempt-bank", "repository": t.OFFICIAL, "published": False,
                   "base": request["expected_base"], "commit": commit, "tree": runner.rev(commit + "^{tree}"),
                   "message": raw.split(b"\n\n", 1)[1].decode(), "files": files,
                   "claims": request["claims"], "workflow": ctx, "native_re_log_passed": True,
                   "normal_commit_passed": True, "full_normal_pre_push_passed": True,
                   "progress": zero_progress(request["expected_base"], commit)}
    validate_publication(publication, request, ctx)
    t.raw_commit(raw, publication)
    t.validate_objects(runner, publication)
    return publication, raw


def target_ref(ctx, commit):
    require(t.hex_id(commit) and all(re.fullmatch(r"[1-9][0-9]*", ctx.get(k, ""))
                                    for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT")), "Invalid fixed branch inputs")
    return "refs/heads/banked/bfme1-008c6ad0-%s-%s-%s" % (ctx["GITHUB_RUN_ID"], ctx["GITHUB_RUN_ATTEMPT"], commit)


def bank_job(runner, api, request, request_hash, ctx):
    initial_checkout(runner, request)
    check_run(api, ctx)
    bash = prepare_native(runner)
    runner.run("initial-ledger-check", [sys.executable, "tools/check_csv.py"], log=True)
    current_claims(runner, request, "before-native-re-log")
    runner.git("bank-local-branch", "switch", "-c", LOCAL_REF.removeprefix("refs/heads/"), request["expected_base"], log=True)
    # The retained file is required and pinned above. Unmodified _bank always
    # measures incoming AND retained source before writing either history/log.
    runner.run("unmodified-native-re-log", bank_command(), log=True)
    paths = changed_paths(runner, request["expected_base"])
    before = runner.git("before-log-prefix", "show", request["expected_base"] + ":" + LOG)
    validate_append(before, (runner.source / LOG).read_bytes())
    runner.git("stage-only-bank-results", "add", "--", *paths)
    runner.git("ordinary-staged-whitespace", "diff", "--cached", "--check")
    runner.git("ordinary-author-name", "config", "user.name", "ChatGPT")
    runner.git("ordinary-author-email", "config", "user.email", "chatgpt@localhost")
    message = ("[BFME 2 donor] Bank measured Apt coercion attempts\n\n"
               "Preserve the complete 233-byte Boolean conversion attempt and its\n"
               "documented native trials after reassessment. The exact source remains\n"
               "unmatched. Unmodified re_log.py measures both the incoming and retained\n"
               "banks and chooses the preferred body without a manual score override.\n\n"
               "The bank/history and one appended partial verdict are the only changes.\n"
               "Game source, matching ledgers, pins, headers and controls are unchanged;\n"
               "exact C++ progress is zero. See " + HANDOFF + ".\n\n"
               + "".join("Claim-Lease: %s=%s\n" % (c["rva"], c["lease"]) for c in request["claims"]))
    message_path = runner.evidence / "bank-commit-message.txt"
    message_path.write_text(message, encoding="utf-8", newline="\n")
    current_claims(runner, request, "before-ordinary-bank-commit")
    runner.git("ordinary-bank-commit", "commit", "--file", str(message_path), log=True)
    commit = runner.rev("HEAD")
    require(not runner.git("committed-status", "status", "--porcelain"), "Ordinary commit left uncommitted results")
    result = validate_result_contents(runner, request["expected_base"], commit, request)
    runner.assert_master(request["expected_base"], fetch=True)
    refs = "%s %s refs/heads/master %s\n" % (LOCAL_REF, commit, request["expected_base"])
    (runner.evidence / "full-pre-push-stdin.txt").write_text(refs, encoding="utf-8", newline="\n")
    runner.run("full-ordinary-native-pre-push", [bash, ".githooks/pre-push", "origin", t.UPSTREAM], stdin=refs.encode(), log=True)
    current_claims(runner, request, "after-full-native-gate")
    runner.assert_master(request["expected_base"])
    runner.run("ordinary-session-progress", [sys.executable, "tools/progress.py", "origin/master"], log=True)
    require(not runner.git("post-gate-status", "status", "--porcelain"), "Native gate left a changed tree")
    publication, raw_commit = publication_for(runner, request, ctx, paths)
    output = runner.source.parent / "banked-attempt"
    output.mkdir()
    bundle = output / "candidate.bundle"
    runner.git("export-exact-bank-bundle", "bundle", "create", "--version=2", str(bundle),
               request["expected_base"] + ".." + LOCAL_REF, log=True)
    (output / "commit-object.txt").write_bytes(raw_commit)
    receipt = {"schema": 1, "request": request, "request_sha256": request_hash, "workflow": ctx,
               "publication": publication, "bank_result": result, "actual_claims": runner.receipt["claims"],
               "bundle_sha256": t.digest(bundle.read_bytes()), "bundle_size": bundle.stat().st_size,
               "target_ref": target_ref(ctx, commit)}
    (output / "bank-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    runner.receipt.update(status="banked-and-verified", publication=publication, bank_result=result,
                          target_ref=target_ref(ctx, commit))


def validate_bundle(raw, publication):
    require(raw.startswith(b"# v2 git bundle\n") and b"\n\n" in raw, "Unexpected bank bundle format")
    lines = raw.split(b"\n\n", 1)[0].split(b"\n")
    require(len(lines) == 3 and lines[1].startswith(b"-" + publication["base"].encode() + b" ")
            and lines[2] == publication["commit"].encode() + b" " + LOCAL_REF.encode(),
            "Bundle does not have exactly the reviewed base and one bank head")


def push_command(ctx, commit):
    ref = target_ref(ctx, commit)
    return ["git", "push", "--porcelain", "--force-with-lease=" + ref + ":", t.FORK_URL, commit + ":" + ref]


def existing_ref(runner, ctx, commit):
    ref = target_ref(ctx, commit)
    lines = runner.git("fixed-banked-branch-readback", "ls-remote", t.FORK_URL, ref).decode().splitlines()
    if not lines:
        return False
    require(lines == [commit + "\t" + ref], "The fixed banked branch already has different content")
    return True


def transfer_job(runner, api, request, request_hash, ctx):
    initial_checkout(runner, request)
    check_run(api, ctx)
    artifact_id = os.environ.get("BFME_BANK_ARTIFACT_ID", "")
    sha256 = os.environ.get("BFME_BANK_ARTIFACT_DIGEST", "")
    require(re.fullmatch(r"[1-9][0-9]*", artifact_id) and t.hex_id(sha256, 64), "Read-only bank artifact pin missing")
    artifact_id = int(artifact_id)
    meta = api.json("/actions/artifacts/%d" % artifact_id)
    t.check_artifact(meta, artifact_id, sha256, int(ctx["GITHUB_RUN_ID"]), ctx["GITHUB_SHA"],
                     "bfme1-banked-%s-%s" % (ctx["GITHUB_RUN_ID"], ctx["GITHUB_RUN_ATTEMPT"]))
    archive_path = runner.source.parent / "native-bank-artifact.zip"
    api.artifact(artifact_id, sha256, archive_path)
    archive = t.Archive(archive_path)
    try:
        require(set(archive.entries) == {"candidate.bundle", "commit-object.txt", "bank-receipt.json"}, "Unexpected bank handoff files")
        receipt = archive.json("bank-receipt.json")
        require(receipt.get("schema") == 1 and receipt.get("request") == request
                and receipt.get("request_sha256") == request_hash
                and all(receipt.get("workflow", {}).get(k) == ctx[k] for k in t.WORKFLOW_KEYS if k != "ImageVersion"),
                "Bank handoff is not from this exact read-only job")
        publication = receipt["publication"]
        validate_publication(publication, request, ctx)
        require(receipt.get("target_ref") == target_ref(ctx, publication["commit"]), "Bank destination changed")
        commit_raw = archive.read("commit-object.txt", 128 * 1024)
        t.raw_commit(commit_raw, publication)
        bundle = archive.read("candidate.bundle")
        require(len(bundle) == receipt.get("bundle_size") and t.digest(bundle) == receipt.get("bundle_sha256"), "Bank bundle changed")
        validate_bundle(bundle, publication)
        bundle_path = runner.source.parent / "bank-candidate.bundle"
        bundle_path.write_bytes(bundle)
    finally:
        archive.close()
    runner.git("verify-exact-bank-bundle", "bundle", "verify", str(bundle_path), log=True)
    runner.git("import-exact-bank-bundle", "fetch", "--no-tags", "--no-write-fetch-head", "--recurse-submodules=no",
               str(bundle_path), LOCAL_REF, log=True)
    t.validate_objects(runner, publication)
    require(runner.git("imported-raw-bank-commit", "cat-file", "commit", publication["commit"]) == commit_raw,
            "Imported raw commit changed")
    runner.git("exact-bank-checkout", "switch", "-c", LOCAL_REF.removeprefix("refs/heads/"), publication["commit"], log=True)
    require(not runner.git("bank-checkout-status", "status", "--porcelain"), "Imported bank tree is dirty")
    # Only ordinary official tooling executes here: allowed object differences
    # cannot include hooks, scripts, game source, headers, pins, or controls.
    prepare_native(runner)
    result = validate_result_contents(runner, publication["base"], publication["commit"], request)
    require(result == receipt.get("bank_result"), "Imported bank selection or measured evidence differs")
    require(zero_progress(publication["base"], publication["commit"]) == publication["progress"], "Imported progress differs")
    current_claims(runner, request, "immediately-before-fork-bank-transfer")
    runner.assert_master(publication["base"], fetch=True)
    if existing_ref(runner, ctx, publication["commit"]):
        runner.receipt.update(status="already-present-exact", commit=publication["commit"], target_ref=receipt["target_ref"])
        return
    env, header = t.push_environment(api.token, os.environ)
    runner.secrets = (api.token, header, header.removeprefix("AUTHORIZATION: basic "))
    runner.run("atomic-create-fixed-banked-branch", push_command(ctx, publication["commit"]), env=env, log=True)
    runner.receipt["fork_ref_created"] = True
    runner.save()
    require(existing_ref(runner, ctx, publication["commit"]), "Exact new banked branch is not readable")
    current_claims(runner, request, "after-fork-bank-transfer")
    runner.assert_master(publication["base"])
    runner.receipt.update(status="transferred", commit=publication["commit"], tree=publication["tree"],
                          target_ref=receipt["target_ref"], bank_result=result, progress=publication["progress"],
                          full_native_gate="separate read-only job against actual official master",
                          actual_push_gate="unmodified ordinary pre-push; new branch receives normal static checks",
                          publication_scope="fresh fixed fork banked branch only")


def main():
    require(len(sys.argv) == 2 and sys.argv[1] in ("pin", "bank", "transfer"), "Use only pin, bank, or transfer")
    request, request_hash = read_request()
    ctx = context(os.environ)
    if sys.argv[1] == "pin":
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write("base=" + request["expected_base"] + "\n")
        return 0
    # The ephemeral API token never enters pip, compiler, tools, or hook envs.
    token = os.environ.pop("BFME_BANK_TOKEN", "")
    runner = Runner(Path.cwd())
    runner.secrets = (token,) if token else ()
    runner.receipt.update(command=sys.argv[1], workflow=ctx, request_sha256=request_hash)
    try:
        api = t.GitHub(token)
        (bank_job if sys.argv[1] == "bank" else transfer_job)(runner, api, request, request_hash, ctx)
    except Exception as error:
        runner.receipt.update(status="rejected", reason=str(error) if isinstance(error, Rejected) else type(error).__name__)
        print("Bank workflow rejected: " + runner.receipt["reason"], file=sys.stderr)
        return 1
    finally:
        runner.save()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Rejected as error:
        print("Bank workflow rejected: " + str(error), file=sys.stderr)
        sys.exit(1)
