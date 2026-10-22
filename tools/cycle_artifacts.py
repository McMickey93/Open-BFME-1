#!/usr/bin/env python3
"""Integrity, freshness and immutable storage for BFME1 cycle bundles.

Adapted from Open-BFME-2 02518d74b1's cycle_artifacts.py. The BFME1 profile
requires a measured closure graph and both report files; it has no data-fold
member. Receipt provenance binds the executable, ledgers, objects and semantic
rules. The broad tool digest is provenance, with equal-rule mismatches warning.

Authority is recomputed from clean local run evidence, local origin/master
ancestry, integrity, matching rules and freshness. A manifest's own authority
claim is ignored. Authority additionally requires a host-key stamp from the
fresh-snapshot launcher, tracked Git input hashes, and bound object evidence.
Readers trust the fixed account key at ~/.config/open-bfme/cycle_key (0600).
Same-user key access is an owner-accepted residual risk: code running as that
account can deliberately read the secret and sign fabricated measurements.
The stamp does not establish a security boundary against that account.

Store/<measurement id>/bundle is installed by one directory rename; current.json
is replaced atomically under a portable writer lock. Readers derive selection
from validated installed receipts and warn about pointer rollback. Installed
payload directories are never replaced or removed; a verified stamp may be
attached atomically to an identical installed payload. Reason/exit slots:
corrupt=1, unavailable=2, empty=3, stale=4, incompatible-rules=5,
not-authoritative=6, no-closure-report=7. Age limit 24 h; future skew 600 s;
closure lookback 5. Unknown ancestry fails closed.
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
import zlib
from pathlib import Path

import cycle_stamp
import link_cycle_context as context
from portable_lock import lock, unlock

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "bfme1-link-cycle-bundle/1"
STORE_SCHEMA = "bfme1-link-cycle-store/1"
MANIFEST, RECEIPT = "manifest.json", "receipt.json"
LINK_STATUS = "link_status.csv.gz"
CLOSURE_GRAPH = "closure_graph.json.gz"
CLOSURE_ROOTS = "closure_roots.json.gz"
CLOSURE_BLOCKERS = "closure_blockers.csv.gz"
RANK_JSON = "data_back_rank.json"
CYCLE_DIFF = "cycle_diff.json"
MEMBERS = (RECEIPT, LINK_STATUS, CLOSURE_GRAPH, CLOSURE_ROOTS, CLOSURE_BLOCKERS, RANK_JSON)
PROVENANCE = "provenance.json"
OPTIONAL = (CYCLE_DIFF, PROVENANCE)
TAG_PREFIX = "bfme1-link-cycle/"
TAG = re.compile(r"^bfme1-link-cycle/([0-9a-f]{12})-(\d{8}T\d{6}Z)-([0-9a-f]{12})$")
SHA = re.compile(r"^[0-9a-f]{64}$")
DEFAULT_STORE = ROOT / "build/cycle_bundles"
POINTER = "current.json"
FRESH_HOURS, FUTURE_SKEW, CLOSURE_LOOKBACK = 24.0, 600, 5
UPSTREAM = "origin/master"
EXIT = {"corrupt": 1, "unavailable": 2, "empty": 3, "stale": 4, "incompatible-rules": 5,
        "not-authoritative": 6, "no-closure-report": 7}
EXIT_INVALID, EXIT_UNAVAILABLE, EXIT_EMPTY = 1, 2, 3
STATUS_COLUMNS = ("name", "kind", "source", "retail_rva", "size", "linked_rva", "placed", "placement_reason",
                  "self_strict", "closed_strict", "closed_strict_dumps_ok", "closed_strict_pilot_rule",
                  "pinned_strict", "byte_equal", "hardcoded", "failure_count", "failures")
LEDGERS = tuple("targets/game/reverse/" + n + ".csv" for n in ("functions", "symbols", "data_rows"))


class Problem(Exception):
    reason = "corrupt"


class BundleError(Problem):
    reason = "corrupt"
    sub_reason = "integrity"


class Unavailable(Problem):
    reason = "unavailable"


class Empty(Problem):
    reason = "empty"


class Refused(Problem):
    def __init__(self, message, reason, sub_reason=None):
        super().__init__(message)
        self.sub_reason = sub_reason
        assert reason in EXIT
        self.reason = reason


def exit_code(problem):
    return EXIT[problem.reason]


def describe(problem):
    kind = ("unavailable" if isinstance(problem, Unavailable) else "empty" if isinstance(problem, Empty)
            else "invalid" if isinstance(problem, BundleError) else "refused")
    detail = f", sub_reason={problem.sub_reason}" if getattr(problem, "sub_reason", None) else ""
    return f"{kind} [reason={problem.reason}{detail}]: {problem}"


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
    except (OSError, EOFError, zlib.error) as e:
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
    """Require complete BFME1 measurement provenance, without granting authority."""
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
            "closure_graph_sha256", "canon_rules", "measure_env", "toolchain_sha256",
            "checkout_start", "checkout_end", "run_options", "dirty", "allow_dirty", "warm_start",
            "compile_failed", "moved_during_run", "diagnostic")
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
    expected_body, blocker_rows = cr.analyze(*graph)
    strip_verified = lambda roots: [dict(e, verified=None) for e in roots]
    same("closure root gains reproduced from graph", strip_verified(doc["roots"]), expected_body["roots"])
    same("closure summary reproduced from graph", doc["summary"], expected_body["summary"])
    same("closure blockers reproduced from graph", read_member(d / CLOSURE_BLOCKERS), cr.blockers_csv(blocker_rows))
    expected_doc = json.loads(cr.document(expected_body, blocker_rows, {})[0])
    same("closure blockers metadata", doc["blockers"], expected_doc["blockers"])
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
    try:
        cd.check_report(doc)
    except cd.CycleDiffError as e:
        raise BundleError(f"cycle_diff: {e}") from None
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
    same("directory members", {p.name for p in d.iterdir()} - {cycle_stamp.STAMP}, set(members) | {MANIFEST})
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
    # Optional authority claims in an input manifest never confer trust.
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
    """Self-consistency only; never claims freshness or authority.

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
    def __init__(self, directory, manifest, receipt, root=ROOT):
        self.dir, self.manifest, self.receipt = Path(directory), manifest, receipt
        self.tag, self.commit = manifest["tag"], manifest["commit"]
        self.paths = {n: self.dir / n for n in manifest["members"]}
        self.paths[MANIFEST] = self.dir / MANIFEST
        self.root, self.now, self.notes = root, None, []

    @property
    def authoritative(self):
        # Recheck files and local policy; cached/manifest booleans are not evidence.
        try:
            return self.freshness(now=self.now)["authoritative"]
        except Problem:
            return False

    link_status = property(lambda self: self.paths[LINK_STATUS])
    closure_graph = property(lambda self: self.paths[CLOSURE_GRAPH])
    closure_roots = property(lambda self: self.paths[CLOSURE_ROOTS])
    closure_blockers = property(lambda self: self.paths[CLOSURE_BLOCKERS])
    rank_json = property(lambda self: self.paths[RANK_JSON])
    cycle_diff = property(lambda self: self.paths.get(CYCLE_DIFF))

    def freshness(self, now=None, root=None):
        root = self.root if root is None else root
        validate(self.dir, root=root)
        same("loaded receipt", read_json(self.paths[RECEIPT]), self.receipt)
        fr = freshness(self.receipt, now=now, root=root)
        # A stamp binds the complete manifest; evidence is independently checked.
        fr["stamp_failure"] = cycle_stamp.verify(self.dir)
        fr["evidence_failure"] = None if fr["stamp_failure"] else run_evidence_failure(self.dir, self.receipt, root)
        # History admission is independent of the first displayed refusal:
        # unsigned incompatible bundles must not consume the rules lookback.
        fr["execution_eligible"] = (fr["stamp_failure"] is None and fr["evidence_failure"] is None
                                    and context.run_authority_failure(self.receipt) is None
                                    and self.receipt.get("authoritative") is True and fr["ancestor"] is True)
        why = authority_refusal(self.receipt, fr)
        return dict(fr, authoritative=why is None,
                    reason=why[0] if why else None, sub_reason=why[1] if why else None)

    def data_back_rank(self):
        doc = read_json(self.rank_json)
        if doc.get("status") == "unavailable":
            raise Unavailable(doc["reason"])
        return doc


def load_bundle(directory, *, root=ROOT):
    manifest = validate(directory, root=root)
    return Bundle(directory, manifest, read_json(Path(directory) / RECEIPT), root)


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
        return None, None, f"ancestry unknown: no local {ref} here (git fetch origin)"
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
                          + " (git fetch origin for a current count)")


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
    if fr["future"]:
        return "corrupt", "measurement is more than 600 s in the future"
    if fr["stale"] and not allow_stale:
        return "stale", f"measurement exceeds the {fr['max_age_hours']:g} h freshness window"
    return None


def authority_refusal(receipt, fr):
    """(reason, sub-reason, explanation), independent of any bundle claim/flag."""
    run_failure = context.run_authority_failure(receipt)
    if run_failure:
        return "not-authoritative", run_failure, "receipt does not prove a clean local run: " + run_failure
    if receipt.get("authoritative") is not True:
        return "not-authoritative", "receipt-not-authoritative", "link_cycle did not produce an authoritative receipt"
    why = refusal(fr)
    if why:
        return why[0], {"corrupt": "future", "stale": "stale", "incompatible-rules": "rules-mismatch"}[why[0]], why[1]
    if fr["ancestor"] is not True:
        sub = "non-ancestor" if fr["ancestor"] is False else "ancestry-unknown"
        return "not-authoritative", sub, fr["ancestry"]
    if fr.get("stamp_failure", "unstamped"):
        sub = fr.get("stamp_failure", "unstamped")
        return "not-authoritative", sub, "no valid stamp under a configured host key: " + sub
    if fr.get("evidence_failure"):
        return "not-authoritative", fr["evidence_failure"], "snapshot evidence failed: " + fr["evidence_failure"]
    return None


def git_blob(root, commit, path):
    if not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts or "\\" in path:
        return None
    got = subprocess.run(["git", "-C", str(root), "show", f"{commit}:{path}"], capture_output=True)
    return got.stdout if got.returncode == 0 else None


def tracked_input_failure(receipt, root):
    """Prove declared tracked inputs and executed tools against the measured tree."""
    commit = receipt["commit"]
    got = _git(root, "ls-tree", "-r", "--name-only", commit)
    if got is None or got.returncode:
        return "git-evidence-unavailable"
    tracked = set(got.stdout.splitlines())
    inputs = receipt.get("inputs") or {}
    if any(n not in tracked for n in LEDGERS):
        return "input-mismatch"
    for name, digest in inputs.items():
        if name in tracked:
            raw = git_blob(root, commit, name)
            if raw is None or hashlib.sha256(text_bytes(raw)).hexdigest() != digest:
                return "input-mismatch"
    for name, digest in receipt["tool_dependencies"].items():
        path = "tools/" + name
        raw = git_blob(root, commit, path) if path in tracked else None
        if raw is None or hashlib.sha256(text_bytes(raw)).hexdigest() != digest:
            return "tool-mismatch"
    return None


def run_evidence_failure(directory, receipt, root):
    """Require launcher execution binding and reproduce the object inventory."""
    d = Path(directory)
    execution = read_manifest(d).get("execution")
    want = {"launcher": "cycle_launch/1", "commit": receipt["commit"], "snapshot": True,
            "semantic_sha256": receipt["rule_identity"]["implementation_sha256"]}
    if execution != want or receipt.get("snapshot") is not True:
        return "snapshot-required"
    why = tracked_input_failure(receipt, root)
    if why:
        return why
    if PROVENANCE not in read_manifest(d)["members"]:
        return "missing-object-evidence"
    try:
        same("object evidence hash", sha256_file(d / PROVENANCE), receipt["provenance_sha256"])
        prov = read_json(d / PROVENANCE)
        if not prov or len(prov) != receipt.get("objects"):
            return "missing-object-evidence"
        h = hashlib.sha256()
        for name in sorted(prov):
            rec = prov[name]
            if not SHA.fullmatch(str(rec.get("object"))) or not SHA.fullmatch(str(rec.get("object_canon"))):
                return "missing-object-evidence"
            h.update(name.encode() + b"\0" + rec["object"].encode())
            if rec.get("source"):
                raw = git_blob(root, receipt["commit"], rec["source"])
                if raw is None or hashlib.sha256(raw).hexdigest() != rec.get("source_sha256") \
                        or rec.get("proof") not in ("inventory", "deps") or not SHA.fullmatch(str(rec.get("deps_sha256"))):
                    return "object-source-mismatch"
        same("objects inventory", h.hexdigest(), receipt["objects_digest"])
        canon = link_cycle_module(root).canonical_digests(prov)
        for key, value in canon.items():
            same(key, value, receipt.get(key))
    except (Problem, KeyError, ValueError, TypeError, AttributeError, OSError):
        return "bad-object-evidence"
    return None


def format_freshness(bundle, fr):
    lines = [f"bundle {bundle.tag}: commit {bundle.commit}, measured {fr['measured_end_utc']}",
             f"{'STALE' if fr['stale'] else 'age'}: {fr['age_hours']:.2f} h", fr["ancestry"]]
    if fr["rules_match"] is not True:
        lines.append("RULES MISMATCH OR UNKNOWN: incompatible-rules")
    elif fr["tool_digest_matches"] is False:
        lines.append("WARNING: tool digest differs under equal BFME1 semantic rules")
    lines.append("AUTHORITATIVE: clean local run (host-stamped snapshot)" if fr["authoritative"] else
                 f"NOT AUTHORITATIVE: {fr['reason']} / {fr['sub_reason']}")
    return lines


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


def installed(store, root=ROOT, now=None):
    out = []
    for d in Path(store).iterdir():
        if d.name.startswith(".") or not d.is_dir():
            continue
        if not (d / "bundle").is_dir():
            raise BundleError(f"unexpected directory in bundle store: {d.name}")
        b = load_bundle(d / "bundle", root=root)
        same("installed directory identity", d.name, bundle_id(b.tag))
        fr = b.freshness(now=now)
        out.append({"id": d.name, "tag": b.tag, "commit": b.commit,
                    "measured_end_ns": b.receipt["measured_end_ns"],
                    "measured_end_utc": measured_of(b.receipt)["end_utc"],
                    "rules_tuple": rules_of(b.receipt), "closure_report": True,
                    "authoritative": fr["authoritative"], "execution_eligible": fr["execution_eligible"],
                    "reason": fr["reason"],
                    "sub_reason": fr["sub_reason"]})
    return sorted(out, key=lambda e: (e["measured_end_ns"], e["id"]), reverse=True)


def write_pointer(store, now=None, root=ROOT):
    """Caller holds the writer lock; pointer claims never confer authority."""
    store = Path(store)
    entries = installed(store, root, now)
    trusted = [e for e in entries if e["authoritative"]]
    doc = {"schema": STORE_SCHEMA, "written_utc": iso_utc(time.time() if now is None else now),
           "latest_measurement": trusted[0]["id"] if trusted else None,
           "latest_closure_ready": next((e["id"] for e in trusted if e["closure_report"]), None),
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
        for k in ("latest_measurement", "latest_closure_ready"):
            if doc.get(k) is not None and doc[k] not in ids:
                raise BundleError(f"pointer {k} is not installed")
        return doc
    except Problem:
        raise
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        raise BundleError(f"invalid pointer: {e}") from None


def closure_choice(doc, root=ROOT):
    mine = local_rules(root)
    ready = [e for e in doc["bundles"] if e.get("closure_report")]
    for e in ready[:CLOSURE_LOOKBACK + 1]:
        if e.get("authoritative") is True and mine is not None and e.get("rules_tuple") == mine:
            return e["id"], True
    return (ready[0]["id"] if ready else None), False


def resolve(path, need_closure=False, root=ROOT, now=None):
    path = Path(path)
    if (path / MANIFEST).is_file():
        notes = []
        store = path.parent.parent
        if path.name == "bundle" and (store / POINTER).is_file():
            entries = installed(store, root, now)
            eligible = [e for e in entries if e["authoritative"]]
            if eligible and path.parent.name != eligible[0]["id"]:
                notes.append("NOT THE NEWEST: explicit historical selection " + path.parent.name)
        return path, notes
    pointer = read_pointer(path)
    entries = installed(path, root, now)
    if not entries:
        raise Empty("bundle store has no measurements")
    eligible = [e for e in entries if e["authoritative"]]
    if need_closure:
        # Diagnostic installs never consume the compatible history window.
        candidates = [e for e in entries if e["execution_eligible"]]
        ident, _ = closure_choice({"bundles": candidates or entries}, root)
        if ident is None:
            raise Refused("store has no closure report", "no-closure-report")
    else:
        ident = (eligible or entries)[0]["id"]
    notes = []
    expected = eligible[0]["id"] if eligible else None
    if pointer.get("latest_measurement") != expected or [e["id"] for e in pointer["bundles"]] != [e["id"] for e in entries]:
        notes.append("WARNING: current pointer rollback or outdated inventory detected; using validated installed receipts")
    if ident != entries[0]["id"]:
        notes.append(f"NOT THE NEWEST: serving eligible measurement {ident}")
    return path / ident / "bundle", notes


def publish_directory(source, destination):
    """Atomically reserve a new destination; never replace a concurrent creator.

    Linux provides a single no-replace rename. The portable fallback reserves
    with mkdir and installs manifest last, so incomplete bundles are never read
    as published. Failure removes only the reservation this call created.
    """
    source, destination = Path(source), Path(destination)
    if sys.platform.startswith("linux"):
        import ctypes
        import errno
        libc = ctypes.CDLL(None, use_errno=True)
        rename = getattr(libc, "renameat2", None)
        if rename is not None:
            if rename(-100, os.fsencode(source), -100, os.fsencode(destination), 1) == 0:
                return
            error = ctypes.get_errno()
            if error not in (errno.ENOSYS, errno.EINVAL, errno.EOPNOTSUPP):
                raise OSError(error, os.strerror(error), str(destination))
    destination.mkdir()  # exclusive reservation, even when the competitor is empty
    try:
        for child in sorted(source.iterdir(), key=lambda p: (p.name == MANIFEST, p.name)):
            os.rename(child, destination / child.name)
        source.rmdir()
    except BaseException:
        shutil.rmtree(destination)
        raise


def attach_verified_stamp(source, destination):
    """Under the store writer lock, upgrade authentication only, never payload.

    The caller has validated both payloads and proved manifest equality. The
    manifest binds every member, so the incoming verified stamp covers exactly
    the installed immutable bytes. Invalid/unsigned copies cannot downgrade it.
    """
    if cycle_stamp.verify(source) is not None or cycle_stamp.verify(destination) is None:
        return
    fd, temporary = tempfile.mkstemp(prefix=".stamp-", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write((source / cycle_stamp.STAMP).read_bytes())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination / cycle_stamp.STAMP)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def install_local(directory, store, *, root=ROOT, now=None):
    """Install immutable payload; allow verified stamp upgrades under the writer lock."""
    source = load_bundle(directory, root=root)
    store = Path(store)
    handle = _writer(store)
    tmp = None
    try:
        final = store / bundle_id(source.tag)
        tmp = Path(tempfile.mkdtemp(prefix=".partial-", dir=store))
        shutil.copytree(source.dir, tmp / "bundle", symlinks=True)
        copied = load_bundle(tmp / "bundle", root=root)
        same("copied manifest", copied.manifest, source.manifest)
        if final.exists():
            same("immutable installed manifest", validate(final / "bundle", root=root), copied.manifest)
            attach_verified_stamp(copied.dir, final / "bundle")
        else:
            publish_directory(tmp, final)
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


def serve(path, *, allow_stale=False, need_closure=False, need_rank=False, now=None, root=ROOT):
    directory, notes = resolve(path, need_closure, root, now)
    if need_closure and (directory / MANIFEST).is_file():
        m = read_manifest(directory)
        if not {CLOSURE_ROOTS, CLOSURE_BLOCKERS} <= set(m.get("members") or {}):
            raise Refused("bundle carries no closure report", "no-closure-report")
    b = load_bundle(directory, root=root)
    b.notes, b.now = notes, now
    fr = b.freshness(now=now, root=root)
    why = authority_refusal(b.receipt, fr)
    if why and not (allow_stale and why[0] == "stale"):
        raise Refused(why[2], why[0], why[1])
    # A human stale override can inspect, but cannot grant authority or bypass ancestry.
    if allow_stale and fr["ancestor"] is not True:
        sub = "non-ancestor" if fr["ancestor"] is False else "ancestry-unknown"
        raise Refused(fr["ancestry"], "not-authoritative", sub)
    if need_rank:
        b.data_back_rank()
    return b, fr, format_freshness(b, fr) + b.notes


def report(bundle, now=None, out=None, err=None, root=None):
    fr = bundle.freshness(now=now, root=root)
    for line in format_freshness(bundle, fr) + bundle.notes:
        print(line, file=out or sys.stdout)
    return fr


def status(store, now=None, root=ROOT, out=None):
    doc = read_pointer(store)
    doc["bundles"] = installed(store, root, now)
    trusted = [e for e in doc["bundles"] if e["authoritative"]]
    doc["latest_measurement"] = trusted[0]["id"] if trusted else None
    doc["latest_closure_ready"] = next((e["id"] for e in trusted if e["closure_report"]), None)
    print(dumps(doc), end="", file=out or sys.stdout)
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("store", nargs="?", default=str(DEFAULT_STORE))
    i = sub.add_parser("install")
    i.add_argument("dir")
    i.add_argument("--store", default=str(DEFAULT_STORE))
    inspect = sub.add_parser("inspect", help="inspect a bundle as a labelled diagnostic")
    inspect.add_argument("dir")
    v = sub.add_parser("validate")
    v.add_argument("dir")
    v.add_argument("--allow-stale", action="store_true")
    v.add_argument("--closure", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "status":
            status(args.store)
        elif args.cmd == "install":
            m, _ = install_local(args.dir, args.store)
            print(f"installed {m['tag']}; authority is recomputed when served")
        elif args.cmd == "inspect":
            directory, notes = resolve(args.dir)
            b = load_bundle(directory)
            b.notes = notes
            report(b)
        else:
            _, _, lines = serve(args.dir, allow_stale=args.allow_stale, need_closure=args.closure)
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
