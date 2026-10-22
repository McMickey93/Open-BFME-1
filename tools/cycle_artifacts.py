#!/usr/bin/env python3
"""Integrity, freshness and immutable storage for BFME1 cycle bundles.

Adapted from Open-BFME-2 02518d74b1's cycle_artifacts.py. The BFME1 profile
requires a measured closure graph and both report files; it has no data-fold
member. Receipt provenance binds the executable, ledgers, objects and semantic
rules. The broad tool digest is provenance, with equal-rule mismatches warning.

Integrity is not authorship. Publishing is deferred: PUBLISHERS is empty and
DEFAULT_REPO is None. GitHub fetch/publish refuse before contacting the network.
Explicit --local-unpublished permits diagnostic inspection/installation only;
Bundle.authoritative is always false for these bundles, even with forged fetch
evidence. A receipt's historical `authoritative` means a consistent snapshot
measurement, never authenticated publication.

Store/<measurement id>/bundle is installed by one directory rename; current.json
is replaced atomically under a portable writer lock. Readers read the pointer
once and never revisit it. Installed directories are never replaced or removed.
BFME2 reason strings/exit codes are preserved: corrupt=1, unavailable=2, empty=3,
stale=4, incompatible-rules=5, unauthenticated=6, no-closure-report=7. Age limit
24 h; future skew 600 s; closure lookback 5; git ancestry is informational.
"""
import argparse
import ast
import calendar
import csv
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import link_cycle_context as context
from portable_lock import lock, unlock

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "bfme1-link-cycle-bundle/1"
STORE_SCHEMA = "bfme1-link-cycle-store/1"
EVIDENCE_SCHEMA = "bfme1-link-cycle-evidence/1"
MANIFEST, RECEIPT = "manifest.json", "receipt.json"
LINK_STATUS = "link_status.csv.gz"
CLOSURE_GRAPH = "closure_graph.json.gz"
CLOSURE_ROOTS = "closure_roots.json.gz"
CLOSURE_BLOCKERS = "closure_blockers.csv.gz"
RANK_JSON = "data_back_rank.json"
CYCLE_DIFF = "cycle_diff.json"
MEMBERS = (RECEIPT, LINK_STATUS, CLOSURE_GRAPH, CLOSURE_ROOTS, CLOSURE_BLOCKERS, RANK_JSON)
OPTIONAL = (CYCLE_DIFF,)
TAG_PREFIX = "bfme1-link-cycle/"
TAG = re.compile(r"^bfme1-link-cycle/([0-9a-f]{12})-(\d{8}T\d{6}Z)-([0-9a-f]{12})$")
SHA = re.compile(r"^[0-9a-f]{64}$")
DEFAULT_REPO = None
PUBLISHERS = ()
DEFAULT_STORE = ROOT / "build/cycle_bundles"
POINTER, EVIDENCE = "current.json", "evidence.json"
FRESH_HOURS, FUTURE_SKEW, CLOSURE_LOOKBACK = 24.0, 600, 5
UPSTREAM = "origin/master"
EXIT = {"corrupt": 1, "unavailable": 2, "empty": 3, "stale": 4, "incompatible-rules": 5,
        "unauthenticated": 6, "no-closure-report": 7}
EXIT_INVALID, EXIT_UNAVAILABLE, EXIT_EMPTY = 1, 2, 3
STATUS_COLUMNS = ("name", "kind", "source", "retail_rva", "size", "linked_rva", "placed", "placement_reason",
                  "self_strict", "closed_strict", "closed_strict_dumps_ok", "closed_strict_pilot_rule",
                  "pinned_strict", "byte_equal", "hardcoded", "failure_count", "failures")
LEDGERS = tuple("targets/game/reverse/" + n + ".csv" for n in ("functions", "symbols", "data_rows"))


class Problem(Exception):
    reason = "corrupt"


class BundleError(Problem):
    reason = "corrupt"


class Unavailable(Problem):
    reason = "unavailable"


class Empty(Problem):
    reason = "empty"


class Refused(Problem):
    def __init__(self, message, reason):
        super().__init__(message)
        assert reason in EXIT
        self.reason = reason


def exit_code(problem):
    return EXIT[problem.reason]


def describe(problem):
    kind = ("unavailable" if isinstance(problem, Unavailable) else "empty" if isinstance(problem, Empty)
            else "invalid" if isinstance(problem, BundleError) else "refused")
    return f"{kind} [reason={problem.reason}]: {problem}"


def dumps(value):
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def digest_of(value):
    # link_cycle receipt-core serialization (distinct from context.digest).
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def text_bytes(data):
    return data.replace(b"\r\n", b"\n")


def text_sha256(path):
    return hashlib.sha256(text_bytes(Path(path).read_bytes())).hexdigest()


def read_member(path):
    raw = Path(path).read_bytes()
    try:
        return gzip.decompress(raw) if str(path).endswith(".gz") else raw
    except (OSError, EOFError) as e:
        raise BundleError(f"{Path(path).name}: not a readable gzip stream ({e})") from None


def open_text(path):
    return io.StringIO(read_member(path).decode("utf-8"), newline="")


def read_json(path):
    try:
        doc = json.loads(read_member(path))
    except (ValueError, UnicodeError) as e:
        raise BundleError(f"{Path(path).name}: not JSON ({e})") from None
    if not isinstance(doc, dict):
        raise BundleError(f"{Path(path).name}: expected a JSON object")
    return doc


def parse_utc(text):
    return calendar.timegm(time.strptime(text.strip().rstrip("Z").replace("T", " "), "%Y-%m-%d %H:%M:%S"))


def iso_utc(seconds):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))


def receipt_end(receipt):
    # Phase 1's finalization timestamp is later and more precise than date_utc.
    ns = receipt.get("measured_end_ns")
    if not isinstance(ns, int) or isinstance(ns, bool) or ns <= 0:
        raise BundleError("receipt has no positive measured_end_ns")
    try:
        dated = parse_utc(receipt["date_utc"])
        if abs(dated - ns / 1e9) > FUTURE_SKEW:
            raise BundleError("receipt date_utc and measured_end_ns disagree")
        iso_utc(ns / 1e9)
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError, OSError):
        raise BundleError("receipt has unreadable measurement time") from None
    return ns / 1e9


def measured_of(receipt):
    end = receipt_end(receipt)
    total = (receipt.get("seconds") or {}).get("total")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise BundleError("receipt seconds.total must be a nonnegative integer")
    return {"start_utc": iso_utc(end - total), "end_utc": iso_utc(end),
            "end_ns": receipt["measured_end_ns"], "seconds": total,
            "basis": "receipt finalization measured_end_ns; start estimated from seconds.total"}


def headline_of(receipt):
    series = receipt.get("series") or {}
    return {"credit_unique_bytes": series.get("credit_unique_bytes"),
            **{f"real_{k}_unique_bytes": ((series.get("real") or {}).get(k) or {}).get("unique_bytes")
               for k in ("placed_closed_strict", "placed_self_strict", "placed")}}


def rules_of(receipt):
    return receipt.get("rule_identity")


def tag_for(raw):
    try:
        receipt = json.loads(raw)
        commit = receipt["commit"]
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError("not a full commit")
    except (ValueError, TypeError, KeyError):
        raise BundleError("receipt has no full commit") from None
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(receipt_end(receipt)))
    return f"{TAG_PREFIX}{commit[:12]}-{stamp}-{hashlib.sha256(raw).hexdigest()[:12]}"


def tag_time(tag):
    m = TAG.fullmatch(tag or "")
    if m:
        try:
            return calendar.timegm(time.strptime(m.group(2), "%Y%m%dT%H%M%SZ"))
        except ValueError:
            pass
    return None


def bundle_id(tag):
    if tag_time(tag) is None:
        raise BundleError(f"invalid BFME1 measurement tag {tag!r}")
    return tag[len(TAG_PREFIX):]


def local_dependencies(root=ROOT):
    deps = context.tool_dependencies(root)
    # Unlike a running snapshot driver, a consumer asks about ROOT's adapter.
    deps["link_cycle_context.py"] = text_sha256(Path(root) / "tools/link_cycle_context.py")
    return deps


def local_tool_digest(root=ROOT):
    try:
        return context.digest(local_dependencies(root))
    except OSError:
        return None


def local_rules(root=ROOT):
    """Read ROOT's semantic constants without importing a different checkout's code.

    Only literal assignments, earlier constants and list(constant) are evaluated.
    Unknown/dynamic configuration refuses compatibility; nothing is executed.
    """
    try:
        tree = ast.parse((Path(root) / "tools/link_cycle_context.py").read_text())
        constants = {}

        def literal(node):
            if isinstance(node, ast.Name):
                return constants[node.id]
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "list" \
                    and len(node.args) == 1 and not node.keywords:
                return list(literal(node.args[0]))
            if isinstance(node, ast.Dict):
                return {literal(k): literal(v) for k, v in zip(node.keys, node.values)}
            if isinstance(node, (ast.List, ast.Tuple)):
                values = [literal(v) for v in node.elts]
                return tuple(values) if isinstance(node, ast.Tuple) else values
            return ast.literal_eval(node)

        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                try:
                    constants[node.targets[0].id] = literal(node.value)
                except (KeyError, ValueError, TypeError):
                    pass
        deps = local_dependencies(root)
        files = constants["MEASUREMENT_FILES"]
        if not files or any(n not in deps for n in files):
            return None
        profile = constants["PROFILE"]
        return {"id": constants["RULES"], "profile": profile, "profile_sha256": context.digest(profile),
                "measurement_files": list(files),
                "implementation_sha256": context.digest({n: deps[n] for n in files})}
    except (OSError, SyntaxError, KeyError, ValueError, TypeError):
        return None


def link_cycle_module(root=ROOT):
    # The BFME1 schema is verified with this port's receipt serialization, never
    # code loaded from an untrusted bundle or a measurement directory.
    import link_cycle
    return link_cycle


def core_check(receipt, root=ROOT):
    lc = link_cycle_module(root)
    if receipt.get("core_sha256") != lc.digest_of(lc.receipt_core(receipt)):
        raise BundleError("receipt core_sha256 does not digest its contents")
    core = lc.receipt_canon_core(receipt)
    if core is None or receipt.get("core_canon_sha256") != lc.digest_of(core):
        raise BundleError("receipt core_canon_sha256 does not digest its contents")
    return "recomputed with BFME1 receipt serialization"


def check_receipt(receipt, root=ROOT):
    """Require complete BFME1 measurement provenance, without granting publication trust."""
    if receipt.get("tool") != "link_cycle":
        raise BundleError("receipt is not from link_cycle")
    if not re.fullmatch(r"[0-9a-f]{40}", str(receipt.get("commit", ""))):
        raise BundleError("receipt has no full commit")
    measured_of(receipt)
    deps, ident = receipt.get("tool_dependencies"), rules_of(receipt)
    if not isinstance(deps, dict) or not deps:
        raise BundleError("receipt lacks measurement dependency hashes")
    if not isinstance(ident, dict) or ident.get("id") != receipt.get("rules") \
            or not isinstance(ident.get("profile"), dict) \
            or ident.get("profile_sha256") != context.digest(ident["profile"]):
        raise BundleError("receipt semantic rule identity is inconsistent")
    # The declared closure belongs to this measurement. Do not silently re-hash
    # an old receipt with today's enlarged/shrunk set and call it corrupt.
    files = ident.get("measurement_files")
    if files is None and ident.get("implementation_sha256") == context.digest(deps):
        core_check(receipt, root)
        raise Refused("pre-split Phase 1 rule identity; a new BFME1 measurement is required",
                      "incompatible-rules")
    if not isinstance(files, list) or not files or len(set(files)) != len(files) \
            or any(not isinstance(n, str) or n not in deps or not SHA.fullmatch(str(deps[n])) for n in files):
        raise BundleError("receipt has no valid declared semantic dependency closure")
    semantic = context.digest({n: deps[n] for n in files})
    if ident.get("implementation_sha256") != semantic:
        raise BundleError("receipt semantic dependency digest is inconsistent")
    if receipt.get("tool_digest") != context.digest(deps):
        raise BundleError("receipt tool_digest is inconsistent")
    target = receipt.get("target") or {}
    if not SHA.fullmatch(str(target.get("sha256", ""))) or target.get("sha256") != receipt.get("retail_sha256") \
            or target.get("machine") != 0x14c or target.get("image_base") != 0x400000:
        raise BundleError("receipt has no consistent BFME1 i386 executable identity")
    if any(not SHA.fullmatch(str((receipt.get("inputs") or {}).get(n, ""))) for n in LEDGERS):
        raise BundleError("receipt lacks functions/symbols/data ledger hashes")
    for key in ("objects_digest", "objects_canon_digest", "provenance_sha256", "provenance_canon_sha256"):
        if not SHA.fullmatch(str(receipt.get(key, ""))):
            raise BundleError(f"receipt lacks {key}")
    core_check(receipt, root)


def binding_of(receipt):
    """All provenance repeated in the manifest must equal the original receipt."""
    keys = ("core_sha256", "core_canon_sha256", "rule_identity", "tool_digest", "target", "retail_sha256",
            "inputs", "objects_digest", "objects_canon_digest", "provenance_sha256", "provenance_canon_sha256",
            "objects", "objects_missing", "tree_manifest", "submodules", "snapshot", "authoritative",
            "closure_graph_sha256", "canon_rules", "measure_env", "toolchain_sha256")
    return {k: receipt.get(k) for k in keys}


def read_manifest(directory):
    doc = read_json(Path(directory) / MANIFEST)
    if doc.get("schema") != SCHEMA:
        raise BundleError(f"manifest schema is not {SCHEMA}")
    return doc


def member_meta(path):
    path = Path(path)
    meta = {"sha256": sha256_file(path), "size": path.stat().st_size}
    if path.suffix == ".gz":
        raw = read_member(path)
        meta.update(content_sha256=hashlib.sha256(raw).hexdigest(), content_size=len(raw))
    return meta


def same(label, said, want):
    if said != want:
        raise BundleError(f"{label} disagrees with the receipt or member")


def check_closure(d, manifest, receipt):
    import closure_report as cr
    members = manifest["members"]
    same("closure graph hash", members[CLOSURE_GRAPH]["sha256"], receipt.get("closure_graph_sha256"))
    same("series graph hash", receipt.get("closure_graph_sha256"), receipt["series"].get("closure_graph_sha256"))
    doc = read_json(d / CLOSURE_ROOTS)
    if doc.get("schema") != cr.SCHEMA or doc.get("algorithm") != cr.ALGORITHM:
        raise BundleError("closure report schema/algorithm is not BFME1's")
    for k, want in (("commit", receipt["commit"]), ("receipt_core_sha256", receipt["core_sha256"]),
                    ("receipt_sha256", members[RECEIPT]["sha256"]),
                    ("link_status_sha256", receipt["series"]["link_status_sha256"]),
                    ("rules", receipt["rules"]), ("rule_identity", receipt["rule_identity"]),
                    ("link_cycle_tool_digest", receipt["tool_digest"])):
        same(f"closure report {k}", doc.get(k), want)
    same("closure blockers hash", (doc.get("blockers") or {}).get("sha256"),
         members[CLOSURE_BLOCKERS]["content_sha256"])
    same("closure graph binding", doc.get("graph"),
         {"bound": True, "label": cr.BOUND, "sha256": receipt["closure_graph_sha256"]})
    same("closure credit", (doc.get("summary") or {}).get("credit_unique_bytes"),
         receipt["series"].get("credit_unique_bytes"))
    # Reproduce rows/credit from the measured graph; never consult current ledgers.
    graph_doc = read_json(d / CLOSURE_GRAPH)
    same("graph rules", graph_doc.get("rules"), receipt["rules"])
    # Older rule IDs remain internally verifiable; freshness decides compatibility.
    graph_doc = dict(graph_doc, rules=context.RULES)
    try:
        graph = cr.graph_from_doc(graph_doc)
        closed = cr.reference_closure(graph[0], graph[1])
        count = cr.check_rows(graph[2], closed, cr.status_rows(d / LINK_STATUS))
        credit = cr.credit_of(graph[0], graph[1], graph[2])
    except (cr.ReportError, KeyError, TypeError, ValueError, IndexError) as e:
        raise BundleError(f"closure graph/status do not reproduce: {e}") from None
    if not count:
        raise Empty("cycle has no measured rows")
    same("reproduced credit", credit, receipt["series"].get("credit_unique_bytes"))
    expected = {"included": True, "schema": cr.SCHEMA, "algorithm": cr.ALGORITHM, "graph": cr.BOUND}
    same("closure component", (manifest.get("components") or {}).get("closure_report"), expected)


def check_cycle_diff(d, manifest, receipt):
    component = (manifest.get("components") or {}).get("cycle_diff")
    if CYCLE_DIFF not in manifest["members"]:
        same("cycle_diff component", component, {"included": False, "why": "no predecessor comparison requested"})
        return
    import cycle_diff as cd
    doc = read_json(d / CYCLE_DIFF)
    if doc.get("schema") != cd.SCHEMA:
        raise BundleError("cycle_diff has an unknown schema")
    same("cycle_diff NEW", (doc.get("identity") or {}).get("new"), cd.identity(receipt))
    same("cycle_diff component", component,
         {"included": True, "schema": cd.SCHEMA, "predecessor": (doc.get("identity") or {}).get("old")})
    cd.check_report(doc)
    _, spans = cd.load_run(d)
    same("cycle_diff NEW credit union", doc["credit"]["new"], spans)


def _validate(d, root):
    manifest = read_manifest(d)
    members = manifest.get("members")
    if not isinstance(members, dict):
        raise BundleError("manifest has no members table")
    missing = set(MEMBERS) - set(members)
    if missing:
        raise BundleError("missing required member(s): " + ", ".join(sorted(missing)))
    if set(members) - set(MEMBERS + OPTIONAL):
        raise BundleError("manifest lists an unknown member")
    same("directory members", {p.name for p in d.iterdir()}, set(members) | {MANIFEST})
    for name, meta in members.items():
        path = d / name
        if path.is_symlink() or not path.is_file():
            raise BundleError(f"{name}: not a regular bundle member")
        same(f"member {name} size/hash/content", meta, member_meta(path))
    if (d / MANIFEST).is_symlink():
        raise BundleError("manifest is a symlink")
    receipt = read_json(d / RECEIPT)
    check_receipt(receipt, root)
    same("commit", manifest.get("commit"), receipt["commit"])
    same("tag", manifest.get("tag"), tag_for((d / RECEIPT).read_bytes()))
    same("binding", manifest.get("binding"), binding_of(receipt))
    same("rules", manifest.get("rules"), rules_of(receipt))
    same("tool_digest", manifest.get("tool_digest"), receipt["tool_digest"])
    same("measured", manifest.get("measured"), measured_of(receipt))
    same("headline", manifest.get("headline"), headline_of(receipt))
    same("instance", manifest.get("instance"),
         {"receipt_sha256": members[RECEIPT]["sha256"], "measured_end_ns": receipt["measured_end_ns"]})
    if manifest.get("publication") not in ("local-unpublished", "release"):
        raise BundleError("manifest lacks publication mode")
    # These are publication claims, never copied from receipt.authoritative.
    same("manifest authority", manifest.get("authoritative"), False)
    same("manifest authentication", manifest.get("authenticated"), False)
    if not isinstance(manifest.get("producer"), str) or not manifest["producer"].strip():
        raise BundleError("manifest has no producer label")
    if parse_utc(manifest["created_utc"]) + FUTURE_SKEW < receipt_end(receipt):
        raise BundleError("bundle created before measurement")
    same("status content", members[LINK_STATUS]["content_sha256"], receipt["series"].get("link_status_sha256"))
    with open_text(d / LINK_STATUS) as f:
        same("status header", tuple(next(csv.reader(f), ())), STATUS_COLUMNS)
    check_closure(d, manifest, receipt)
    from data_back_rank import check_member
    check_member(read_json(d / RANK_JSON), receipt)
    check_cycle_diff(d, manifest, receipt)
    return manifest


def validate(directory, *, root=ROOT, recompute_core=True):
    """Self-consistency only; never claims authentication, freshness or authority.

    Every consumer must use serve(). Unavailable diagnostic rank members are
    validly encoded, but Bundle.data_back_rank() refuses to serve their contents.
    """
    d = Path(directory)
    if not d.is_dir():
        raise Unavailable(f"no bundle at {d}")
    try:
        return _validate(d, root)
    except Problem:
        raise
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, UnicodeError, OverflowError) as e:
        raise BundleError(f"malformed BFME1 bundle: {e}") from None


class Bundle:
    def __init__(self, directory, manifest, receipt):
        self.dir, self.manifest, self.receipt = Path(directory), manifest, receipt
        self.tag, self.commit = manifest["tag"], manifest["commit"]
        self.paths = {n: self.dir / n for n in manifest["members"]}
        self.paths[MANIFEST] = self.dir / MANIFEST
        self.evidence, self.notes = None, []

    @property
    def authenticated(self):
        if self.manifest["publication"] == "local-unpublished":
            return False
        try:
            authenticate_local(self)
            return True
        except Refused:
            return False

    authoritative = property(lambda self: self.authenticated)
    link_status = property(lambda self: self.paths[LINK_STATUS])
    closure_graph = property(lambda self: self.paths[CLOSURE_GRAPH])
    closure_roots = property(lambda self: self.paths[CLOSURE_ROOTS])
    closure_blockers = property(lambda self: self.paths[CLOSURE_BLOCKERS])
    rank_json = property(lambda self: self.paths[RANK_JSON])
    cycle_diff = property(lambda self: self.paths.get(CYCLE_DIFF))

    def freshness(self, now=None, root=ROOT, **kwargs):
        fr = freshness(self.receipt, now=now, root=root, **kwargs)
        return dict(fr, authenticated=self.authenticated, authoritative=self.authoritative)

    def data_back_rank(self):
        doc = read_json(self.rank_json)
        if doc.get("status") == "unavailable":
            raise Unavailable(doc["reason"])
        return doc


def load_bundle(directory, *, root=ROOT):
    manifest = validate(directory, root=root)
    return Bundle(directory, manifest, read_json(Path(directory) / RECEIPT))


class GhError(Unavailable):
    def __init__(self, args, code, err):
        super().__init__(f"gh {' '.join(args)}: " + (f"exit {code}: " if code is not None else "") + (err or "")[:500])
        self.args_, self.code, self.err = list(args), code, err or ""


class Gh:
    """The gh CLI. run(args) -> stdout text; json(args) -> parsed stdout. Tests pass a fake
    with the same two methods."""

    def __init__(self, exe=None):
        self.exe = exe or os.environ.get("GH") or "gh"

    def run(self, args):
        try:
            got = subprocess.run([self.exe, *args], capture_output=True, text=True, encoding="utf-8",
                                 errors="replace")
        except OSError as e:
            raise GhError(args, None, str(e)) from None
        if got.returncode:
            raise GhError(args, got.returncode, got.stderr.strip())
        return got.stdout

    def json(self, args):
        text = self.run(args)
        try:
            return json.loads(text) if text.strip() else None
        except ValueError as e:
            raise GhError(args, 0, f"invalid API JSON: {e}") from None


def publisher_ok(author):
    return any(isinstance(author, dict) and author.get("login") == p["login"] and author.get("id") == p["id"]
               for p in PUBLISHERS)


def publishers_text():
    return ", ".join(f"{p['login']} (id {p['id']})" for p in PUBLISHERS)


def release_trust(release, allow_mutable=False):
    """Why RELEASE is not a trusted publication, or None: its author is a designated
    publisher and GitHub reports it immutable."""
    if not PUBLISHERS:
        return "publisher trust not configured"
    author = release.get("author") or {}
    if not publisher_ok(author):
        return (f"author {author.get('login')!r} (id {author.get('id')!r}) is not a designated publisher "
                f"({publishers_text()})")
    if release.get("immutable") is not True and not allow_mutable:
        return ("the release is not immutable (GitHub reports immutable="
                f"{release.get('immutable')!r}): its assets and tag can be replaced. The maintainer enables "
                "immutable releases in the repository settings; --allow-mutable only exercises fetch")
    return None


def tag_commit(gh, repo, tag):
    """The commit TAG resolves to on REPO, annotated tags peeled; Refused when there is none."""
    try:
        ref = gh.json(["api", f"repos/{repo}/git/ref/tags/{tag}"]) or {}
        obj = ref.get("object") or {}
        for _ in range(4):
            if obj.get("type") != "tag":
                break
            obj = (gh.json(["api", f"repos/{repo}/git/tags/{obj.get('sha')}"]) or {}).get("object") or {}
    except GhError as e:
        raise Refused(f"the tag {tag} cannot be resolved on {repo} ({e.err.strip()[:200]})", "unauthenticated") from None
    if obj.get("type") != "commit" or not obj.get("sha"):
        raise Refused(f"the tag {tag} does not resolve to a commit ({obj.get('type')!r})", "unauthenticated")
    return obj["sha"]


def attest(gh, repo, tag):
    """`gh release verify TAG`: 'verified', or 'not run: ...' when this gh has no such
    command; Refused when the verification itself fails."""
    try:
        gh.run(["release", "verify", tag, "--repo", repo])
    except GhError as e:
        if e.code is None or "unknown command" in e.err or "unknown flag" in e.err:
            return "not run: this gh has no `release verify` (gh 2.81 or newer)"
        raise Refused(f"`gh release verify {tag}` failed ({e.err.strip()[:300]})", "unauthenticated") from None
    return "verified"


def _authenticate_local(bundle, root=ROOT):
    """The evidence fetch stored beside BUNDLE (its directory's sibling evidence.json),
    re-checked against the files; Refused(unauthenticated) when there is none, it is not this
    bundle's, or it records a release that was not immutable."""
    if not PUBLISHERS or bundle.manifest["publication"] == "local-unpublished":
        raise Refused("publisher trust not configured; local-unpublished bundles are never authoritative",
                      "unauthenticated")
    path = bundle.dir.parent / EVIDENCE
    try:
        ev = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise Refused(f"bundle {bundle.tag} at {bundle.dir} has no fetch evidence ({path.name}): it is a local "
                      "directory, not an authenticated publication (python3 tools/cycle_artifacts.py fetch; a "
                      "producer inspecting its own unpublished bundle passes --local-unpublished)",
                      "unauthenticated") from None
    if not isinstance(ev, dict):
        raise Refused("malformed publication evidence", "unauthenticated")
    if ev.get("schema") != EVIDENCE_SCHEMA or ev.get("tag") != bundle.tag or not ev.get("repo"):
        raise Refused(f"{path} is not the evidence of {bundle.tag}", "unauthenticated")
    if ev.get("manifest_sha256") != sha256_file(bundle.dir / MANIFEST):
        raise Refused(f"{bundle.dir / MANIFEST} is not the manifest that was authenticated", "unauthenticated")
    if not isinstance(ev.get("assets"), dict) or any(not isinstance(v, dict) for v in ev["assets"].values()):
        raise Refused("malformed asset evidence", "unauthenticated")
    for name in list(bundle.manifest["members"]) + [MANIFEST]:
        want = ((ev.get("assets") or {}).get(name) or {}).get("sha256")
        if not want or want != sha256_file(bundle.dir / name) or \
                (ev["assets"][name].get("size") != (bundle.dir / name).stat().st_size):
            raise Refused(f"{name} is not the asset that was authenticated", "unauthenticated")
    if not publisher_ok(ev.get("author")):
        raise Refused(f"bundle {bundle.tag} was published by {(ev.get('author') or {}).get('login')!r}, who is not a "
                      f"designated publisher ({publishers_text()})", "unauthenticated")
    if ev.get("tag_commit") != bundle.commit or ev.get("target_commitish") != bundle.commit:
        raise Refused(f"the tag of {bundle.tag} resolved to {str(ev.get('tag_commit'))[:12]}, not the measured commit",
                      "unauthenticated")
    r = bundle.receipt
    if r.get("authoritative") is not True or r.get("snapshot") is not True or r.get("dirty") \
            or r.get("compile_failed") or r.get("moved_during_run") or (r.get("warm_start") or {}).get("stale"):
        raise Refused("release does not carry a consistent clean snapshot measurement", "unauthenticated")
    if ev.get("immutable") is not True:
        raise Refused(f"bundle {bundle.tag} was fetched with --allow-mutable from a release that is NOT immutable: "
                      "it is not authenticated and is not served", "unauthenticated")
    return ev


def authenticate_local(bundle, root=ROOT):
    """Authenticate installed publication evidence; malformed evidence never confers trust."""
    try:
        return _authenticate_local(bundle, root)
    except Refused:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as e:
        raise Refused(f"unreadable/malformed publication evidence: {e}", "unauthenticated") from None


def list_releases(gh, repo):
    """Every release of REPO (drafts too when the token may see them), REST order."""
    pages = gh.json(["api", "--paginate", "--slurp", f"repos/{repo}/releases?per_page=100"]) or []
    out = []
    for page in pages:
        out.extend(page if isinstance(page, list) else [page])
    return out


def release_problem(release):
    """Why RELEASE is not a complete link-cycle prerelease, or None."""
    if tag_time(release.get("tag_name")) is None:
        return "not a link-cycle measurement tag"
    if release.get("draft"):
        return "draft (not published)"
    if not release.get("prerelease"):
        return "not a prerelease"
    state = {a.get("name"): a.get("state") for a in release.get("assets") or ()}
    missing = [m for m in (MANIFEST,) + MEMBERS if state.get(m) != "uploaded"]
    missing += [m for m in OPTIONAL if m in state and state[m] != "uploaded"]
    if missing:
        return "incomplete: no uploaded " + ", ".join(missing)
    extra = sorted(set(state) - set((MANIFEST,) + MEMBERS + OPTIONAL))
    if extra:
        return "holds assets that are not bundle members: " + ", ".join(extra)
    return None


def candidates(releases, tag=None, allow_mutable=False):
    """([trusted complete link-cycle prereleases, newest MEASUREMENT first], [(tag, why skipped)])."""
    link = [r for r in releases if str(r.get("tag_name", "")).startswith(TAG_PREFIX)]
    if tag is not None:
        link = [r for r in link if r.get("tag_name") == tag]
    good, skipped = [], []
    for r in link:
        why = release_problem(r)
        if why is None:
            why = release_trust(r, allow_mutable)
            why = why and "UNTRUSTED: " + why
        if why:
            skipped.append((r.get("tag_name"), why))
        else:
            good.append(r)
    good.sort(key=lambda r: (tag_time(r["tag_name"]), r["tag_name"]), reverse=True)
    return good, skipped


def has_closure(release):
    names = {a.get("name") for a in release.get("assets") or ()}
    return CLOSURE_ROOTS in names and CLOSURE_BLOCKERS in names


def _git(root, *args):
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    except OSError:
        return None


def ancestry(commit, root=ROOT, ref=UPSTREAM):
    """(is_ancestor True/False/None, commits behind or None, note). ROOT must itself be the
    top of a git checkout: a directory that merely sits inside one is not asked about it."""
    top = _git(root, "rev-parse", "--show-toplevel")
    try:
        is_top = top is not None and top.returncode == 0 and Path(top.stdout.strip()).resolve() == Path(root).resolve()
    except OSError:
        is_top = False
    if not is_top:
        return None, None, f"ancestry unknown: {root} is not a git checkout"
    have = _git(root, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    if have is None or have.returncode:
        return None, None, f"ancestry unknown: no local {ref} here"
    known = _git(root, "cat-file", "-e", commit + "^{commit}")
    if known is None or known.returncode:
        return None, None, f"ancestry unknown: {commit[:12]} is not in this clone (git fetch origin)"
    got = _git(root, "merge-base", "--is-ancestor", commit, ref)
    if got is None or got.returncode not in (0, 1):
        return None, None, "ancestry unknown: git merge-base failed" + (f" ({got.stderr.strip()[:200]})" if got else "")
    if got.returncode == 1:
        return False, None, (f"the measured commit is NOT an ancestor of local {ref} (another line, or a "
                             f"{ref} older than the run: git fetch origin)")
    count = _git(root, "rev-list", "--count", f"{commit}..{ref}")
    behind = int(count.stdout.strip()) if count is not None and count.returncode == 0 and count.stdout.strip().isdigit() else None
    return True, behind, (f"the measured commit is an ancestor of local {ref}, "
                          + (f"{behind} commit(s) behind it" if behind is not None else "distance unknown")
                          + " (information only; git fetch origin for a current count)")


def freshness(receipt, now=None, root=ROOT, ref=UPSTREAM, max_age_hours=FRESH_HOURS):
    now = time.time() if now is None else now
    end = receipt_end(receipt)
    anc, behind, note = ancestry(receipt["commit"], root, ref)
    mine, theirs = local_rules(root), rules_of(receipt)
    local = local_tool_digest(root)
    age = (now - end) / 3600
    return {"rules": receipt.get("rules"), "bundle_rules": theirs, "local_rules": mine,
            "rules_match": None if mine is None else mine == theirs,
            "measured_end_utc": iso_utc(end), "age_hours": round(age, 2), "future": now + FUTURE_SKEW < end,
            "max_age_hours": max_age_hours, "stale": age > max_age_hours, "ref": ref,
            "ancestor": anc, "behind": behind, "ancestry": note,
            "tool_digest": receipt.get("tool_digest"), "local_tool_digest": local,
            "tool_digest_matches": None if local is None else local == receipt.get("tool_digest")}


def refusal(fr, allow_stale=False):
    if fr["rules_match"] is not True:
        return "incompatible-rules", "BFME1 semantic rules differ or local rules are unreadable; no override"
    if fr["stale"] and not allow_stale:
        return "stale", f"measurement exceeds the {fr['max_age_hours']:g} h freshness window"
    return None


def format_freshness(bundle, fr):
    lines = [f"bundle {bundle.tag}: commit {bundle.commit}, measured {fr['measured_end_utc']}",
             f"{'STALE' if fr['stale'] else 'age'}: {fr['age_hours']:.2f} h", fr["ancestry"]]
    if fr["rules_match"] is not True:
        lines.append("RULES MISMATCH OR UNKNOWN: incompatible-rules")
    elif fr["tool_digest_matches"] is False:
        lines.append("WARNING: tool digest differs under equal BFME1 semantic rules")
    if not bundle.authenticated:
        lines.append("UNAUTHENTICATED: local diagnostic; never authoritative")
    return lines


def require_publisher_trust(repo):
    if not PUBLISHERS or not repo:
        raise Refused("publisher trust not configured (empty BFME1 allowlist or no release repository)",
                      "unauthenticated")


def _writer(store):
    store = Path(store)
    store.mkdir(parents=True, exist_ok=True)
    handle = (store / ".lock").open("a+b")
    try:
        lock(handle, exclusive=True)
    except BaseException:
        handle.close()
        raise
    return handle


def installed(store, root=ROOT):
    out = []
    for d in Path(store).iterdir():
        if d.name.startswith(".") or not d.is_dir():
            continue
        if not (d / "bundle").is_dir():
            raise BundleError(f"unexpected directory in bundle store: {d.name}")
        b = load_bundle(d / "bundle", root=root)
        same("installed directory identity", d.name, bundle_id(b.tag))
        out.append({"id": d.name, "tag": b.tag, "commit": b.commit,
                    "measured_end_ns": b.receipt["measured_end_ns"],
                    "measured_end_utc": measured_of(b.receipt)["end_utc"],
                    "rules_tuple": rules_of(b.receipt), "closure_report": True,
                    "authenticated": b.authenticated, "authoritative": b.authoritative,
                    "publication": b.manifest["publication"]})
    return sorted(out, key=lambda e: (e["measured_end_ns"], e["id"]), reverse=True)


def write_pointer(store, now=None, root=ROOT):
    """Caller holds the writer lock; pointer claims never confer authentication."""
    store = Path(store)
    entries = installed(store, root)
    trusted = [e for e in entries if e["authenticated"]]
    doc = {"schema": STORE_SCHEMA, "written_utc": iso_utc(time.time() if now is None else now),
           "latest_measurement": trusted[0]["id"] if trusted else None,
           "latest_closure_ready": next((e["id"] for e in trusted if e["closure_report"]), None),
           "latest_local_unpublished": next((e["id"] for e in entries if e["publication"] == "local-unpublished"), None),
           "bundles": entries}
    fd, tmp = tempfile.mkstemp(prefix=".current-", dir=store)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(doc))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, store / POINTER)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return doc


def read_pointer(store):
    path = Path(store) / POINTER
    if not path.is_file():
        if Path(store).is_dir() and not any(p.is_dir() and not p.name.startswith(".") for p in Path(store).iterdir()):
            raise Empty("bundle store has no measurements")
        raise Unavailable(f"no bundle store pointer at {path}")
    try:
        doc = read_json(path)  # Exactly one read: refresh cannot redirect this reader.
        if doc.get("schema") != STORE_SCHEMA or not isinstance(doc.get("bundles"), list):
            raise BundleError("invalid bundle store pointer")
        ids = []
        for e in doc["bundles"]:
            if e.get("id") != bundle_id(e.get("tag")):
                raise BundleError("unsafe/mismatched bundle id in pointer")
            ids.append(e["id"])
        if len(set(ids)) != len(ids):
            raise BundleError("duplicate bundle id in pointer")
        for k in ("latest_measurement", "latest_closure_ready", "latest_local_unpublished"):
            if doc.get(k) is not None and doc[k] not in ids:
                raise BundleError(f"pointer {k} is not installed")
        return doc
    except Problem:
        raise
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        raise BundleError(f"invalid pointer: {e}") from None


def closure_choice(doc, root=ROOT, local_unpublished=False):
    mine = local_rules(root)
    ready = [e for e in doc["bundles"] if e.get("closure_report") and
             (e.get("authenticated") or local_unpublished and e.get("publication") == "local-unpublished")]
    for e in ready[:CLOSURE_LOOKBACK + 1]:
        if mine is not None and e.get("rules_tuple") == mine:
            return e["id"], True
    return (ready[0]["id"] if ready else None), False


def resolve(path, need_closure=False, root=ROOT, local_unpublished=False):
    path = Path(path)
    if (path / MANIFEST).is_file():
        return path, []
    doc = read_pointer(path)
    if not doc["bundles"]:
        raise Empty("bundle store has no measurements")
    if need_closure:
        ident, _ = closure_choice(doc, root, local_unpublished)
        if ident is None:
            reason = "unauthenticated" if any(e.get("closure_report") for e in doc["bundles"]) else "no-closure-report"
            raise Refused("store has no authenticated closure report", reason)
    else:
        ident = doc.get("latest_measurement")
        if local_unpublished:
            ident = doc["bundles"][0]["id"]
        if ident is None:
            raise Refused("store has no authenticated measurement", "unauthenticated")
    notes = []
    if ident != doc["bundles"][0]["id"]:
        notes.append(f"NOT THE NEWEST: serving compatible closure measurement {ident}")
    return path / ident / "bundle", notes


def install_local(directory, store, *, local_unpublished=False, root=ROOT, now=None):
    """Copy and validate before one rename under the writer lock. Never overwrite an id."""
    if not local_unpublished:
        raise Refused("local install requires --local-unpublished", "unauthenticated")
    source = load_bundle(directory, root=root)
    if source.manifest["publication"] != "local-unpublished":
        raise Refused("local install accepts only explicitly local-unpublished bundles", "unauthenticated")
    store = Path(store)
    handle = _writer(store)
    tmp = None
    try:
        final = store / bundle_id(source.tag)
        tmp = Path(tempfile.mkdtemp(prefix=".partial-", dir=store))
        shutil.copytree(source.dir, tmp / "bundle", symlinks=True)
        copied = load_bundle(tmp / "bundle", root=root)
        same("copied manifest", copied.manifest, source.manifest)
        # An explicit marker is informational, never fetch authentication evidence.
        (tmp / EVIDENCE).write_text(dumps({"schema": EVIDENCE_SCHEMA, "local_unpublished": True,
                                         "authenticated": False, "tag": source.tag}), encoding="utf-8")
        if final.exists():
            same("immutable installed manifest", validate(final / "bundle", root=root), copied.manifest)
        else:
            os.rename(tmp, final)
            tmp = None
        pointer = write_pointer(store, now, root)
        return copied.manifest, pointer
    except OSError as e:
        raise Unavailable(f"local install failed: {e}") from None
    finally:
        if tmp is not None:
            shutil.rmtree(tmp, ignore_errors=True)
        unlock(handle)
        handle.close()


def serve(path, *, allow_stale=False, local_unpublished=False, need_closure=False, need_rank=False,
          now=None, root=ROOT):
    directory, notes = resolve(path, need_closure, root, local_unpublished)
    if need_closure and (directory / MANIFEST).is_file():
        m = read_manifest(directory)
        # A declared profile member subsequently deleted remains corruption.
        if not {CLOSURE_ROOTS, CLOSURE_BLOCKERS} <= set(m.get("members") or {}):
            raise Refused("bundle carries no closure report", "no-closure-report")
    b = load_bundle(directory, root=root)
    b.notes = notes
    if not local_unpublished:
        b.evidence = authenticate_local(b, root)
    else:
        b.notes.append("UNAUTHENTICATED LOCAL BUNDLE (--local-unpublished): never authoritative")
    fr = b.freshness(now=now, root=root)
    if fr["future"]:
        raise BundleError("measurement is more than 600 s in the future")
    why = refusal(fr, allow_stale)
    if why:
        raise Refused(why[1], why[0])
    if need_rank:
        b.data_back_rank()
    return b, fr, format_freshness(b, fr) + b.notes


def install(gh, repo, release, store, *, root=ROOT, allow_mutable=False, now=None):
    """Download RELEASE into a temporary directory inside STORE, authenticate and validate
    it, write its evidence, and rename the complete directory to STORE/<id>. An id already
    installed from the same release is kept as it is (bundles are immutable). On any
    failure the store is unchanged. Returns the manifest."""
    require_publisher_trust(repo)
    store = Path(store)
    tag = release["tag_name"]
    final = store / bundle_id(tag)
    why = release_trust(release, allow_mutable)
    if why:
        raise Refused(f"{tag}: {why}", "unauthenticated")
    if final.is_dir():
        try:
            ev = json.loads((final / EVIDENCE).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            ev = {}
        if isinstance(ev, dict) and ev.get("release_id") == release.get("id") and (ev.get("immutable") is True or allow_mutable):
            return validate(final / "bundle", root=root)
        raise BundleError(f"{final} is already installed from another release than "
                          f"{release.get('id')}: a published bundle is never replaced; inspect both")
    store.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=".partial-", dir=store))
    try:
        down = tmp / "bundle"
        down.mkdir()
        gh.run(["release", "download", tag, "--repo", repo, "--dir", str(down)])
        assets = {a["name"]: a for a in release.get("assets") or ()}
        if len(assets) != len(release.get("assets") or ()):
            raise BundleError("release lists duplicate asset names")
        got = {p.name for p in down.iterdir()}
        if got != set(assets):
            raise BundleError(f"{tag}: downloaded {sorted(got)}, the release lists {sorted(assets)}")
        hashes = {}
        for name, a in sorted(assets.items()):
            digest = str(a.get("digest") or "")
            hashes[name] = sha256_file(down / name)
            if a.get("size") != (down / name).stat().st_size:
                raise BundleError(f"release asset size mismatch for {name}")
            if not digest.startswith("sha256:"):
                raise Refused(f"{tag}: the release API reports no SHA-256 digest for {name}: its bytes are not "
                              "bound by the platform", "unauthenticated")
            if digest[7:] != hashes[name]:
                raise BundleError(f"{tag}: {name} downloads as {hashes[name][:16]}, the release API says "
                                  f"{digest[7:23]}")
        manifest = validate(down, root=root)
        if manifest["tag"] != tag:
            raise BundleError(f"release {tag} carries the manifest of {manifest['tag']}")
        if manifest["publication"] == "local-unpublished":
            raise Refused("local-unpublished bundles are never authenticated", "unauthenticated")
        commit = tag_commit(gh, repo, tag)
        if commit != manifest["commit"]:
            raise Refused(f"the tag {tag} resolves to {commit[:12]}, not the measured commit "
                          f"{manifest['commit'][:12]}", "unauthenticated")
        if release.get("target_commitish") != manifest["commit"]:
            raise Refused(f"release {tag} targets {str(release.get('target_commitish'))[:40]!r}, not the measured "
                          f"commit {manifest['commit']}", "unauthenticated")
        immutable = release.get("immutable") is True
        evidence = {"schema": EVIDENCE_SCHEMA, "repo": repo, "release_id": release.get("id"), "tag": tag,
                    "author": {k: (release.get("author") or {}).get(k) for k in ("login", "id")},
                    "immutable": immutable, "tag_commit": commit, "target_commitish": release.get("target_commitish"),
                    "published_at": release.get("published_at"),
                    "assets": {n: {"sha256": h, "size": (down / n).stat().st_size} for n, h in hashes.items()},
                    "manifest_sha256": hashes[MANIFEST],
                    "attestation": attest(gh, repo, tag) if immutable else "not run: the release is not immutable",
                    "fetched_utc": iso_utc(time.time() if now is None else now),
                    "note": None if immutable else "FETCHED WITH --allow-mutable: NOT AUTHENTICATED, not served"}
        (tmp / EVIDENCE).write_text(json.dumps(evidence, indent=1, sort_keys=True) + "\n", encoding="utf-8",
                                    newline="\n")
        os.chmod(tmp, 0o755)                     # mkdtemp's 0700 would follow the rename
        os.rename(tmp, final)                    # one rename of a complete directory; nothing is replaced
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return manifest


def fetch(repo, store, *, tag=None, gh=None, root=ROOT, now=None, warn=None):
    require_publisher_trust(repo)  # Refuse before credentials/network or filesystem writes.
    gh = gh or Gh()
    warn = warn or (lambda line: print(line, file=sys.stderr))
    good, skipped = candidates(list_releases(gh, repo), tag)
    if not good:
        if any("UNTRUSTED" in why for _, why in skipped):
            raise Refused("no trusted BFME1 publisher release", "unauthenticated")
        if tag:
            raise Unavailable(f"no complete release {tag}")
        raise Empty("no complete BFME1 cycle release")
    handle = _writer(store)
    try:
        manifest = None
        failures = []
        for release in good[:CLOSURE_LOOKBACK + 1]:
            try:
                got = install(gh, repo, release, store, root=root, now=now)
            except Problem as e:
                if tag:
                    raise
                failures.append(e)
                warn(describe(e))
                continue
            if manifest is None:
                manifest = got
            if got["rules"] == local_rules(root) or tag:
                break
        if manifest is None:
            raise failures[0]
        return manifest, [describe(e) for e in failures], write_pointer(store, now, root)
    finally:
        unlock(handle)
        handle.close()


def report(bundle, now=None, out=None, err=None, root=ROOT):
    fr = bundle.freshness(now=now, root=root)
    for line in format_freshness(bundle, fr) + bundle.notes:
        print(line, file=out or sys.stdout)
    return fr


def status(store, now=None, root=ROOT, out=None):
    doc = read_pointer(store)
    # Recheck the files/authentication; pointer booleans are never trust evidence.
    for entry in doc["bundles"]:
        b = load_bundle(Path(store) / entry["id"] / "bundle", root=root)
        entry["authenticated"], entry["authoritative"] = b.authenticated, b.authoritative
    trusted = [e for e in doc["bundles"] if e["authenticated"]]
    doc["latest_measurement"] = trusted[0]["id"] if trusted else None
    doc["latest_closure_ready"] = next((e["id"] for e in trusted if e["closure_report"]), None)
    print(dumps(doc), end="", file=out or sys.stdout)
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    which = f.add_mutually_exclusive_group(required=True)
    which.add_argument("--latest", action="store_true")
    which.add_argument("--tag")
    f.add_argument("--repo", default=DEFAULT_REPO)
    f.add_argument("--store", default=str(DEFAULT_STORE))
    s = sub.add_parser("status")
    s.add_argument("store", nargs="?", default=str(DEFAULT_STORE))
    i = sub.add_parser("install")
    i.add_argument("dir")
    i.add_argument("--store", default=str(DEFAULT_STORE))
    i.add_argument("--local-unpublished", action="store_true")
    v = sub.add_parser("validate")
    v.add_argument("dir")
    v.add_argument("--local-unpublished", action="store_true")
    v.add_argument("--allow-stale", action="store_true")
    v.add_argument("--closure", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "fetch":
            fetch(args.repo, args.store, tag=args.tag)
        elif args.cmd == "status":
            status(args.store)
        elif args.cmd == "install":
            m, _ = install_local(args.dir, args.store, local_unpublished=args.local_unpublished)
            print(f"installed {m['tag']}: UNAUTHENTICATED, never authoritative")
        else:
            b, _, lines = serve(args.dir, allow_stale=args.allow_stale,
                                local_unpublished=args.local_unpublished, need_closure=args.closure)
            for line in lines:
                print(line)
        return 0
    except OSError as e:
        problem = Unavailable(str(e))
        print(f"cycle_artifacts: {describe(problem)}", file=sys.stderr)
        return exit_code(problem)
    except Problem as e:
        print(f"cycle_artifacts: {describe(e)}", file=sys.stderr)
        return exit_code(e)


if __name__ == "__main__":
    sys.exit(main())
