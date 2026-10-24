#!/usr/bin/env python3
"""Bounded manual Actions entry point for the ordinary shared-claim tool.

The job operates on one to five RVA claim refs, never code or master. Owners
are derived from the dispatching GitHub actor and a validated seat. Renewal
and release require the exact currently observed tokens from an earlier run.
The existing claims implementation still owns marker creation, expiry, hooks,
compare-and-swap, and refusal of another worker's claim.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import claims

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "Open-BFME/Open-BFME-1"
OUTPUT = Path("build/claim_runner/result.json")
ACTIONS = {"claim", "renew", "release"}
RVA = re.compile(r"0x[0-9A-Fa-f]{8}\Z")
TOKEN = re.compile(r"[0-9a-f]{40}\Z")
SEAT = re.compile(r"[a-z0-9][a-z0-9-]{0,31}\Z")
ACTOR = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}\Z")


def label(rva):
    return f"0x{rva:08X}"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate token key")
        result[key] = value
    return result


def request(env):
    action = env.get("CLAIM_ACTION", "")
    actor = env.get("GITHUB_ACTOR", "")
    seat = env.get("CLAIM_SEAT", "")
    if action not in ACTIONS:
        raise ValueError("action must be claim, renew, or release")
    if not ACTOR.fullmatch(actor) or actor != env.get("GITHUB_TRIGGERING_ACTOR"):
        raise ValueError("the triggering actor must equal the original GitHub actor")
    if not SEAT.fullmatch(seat):
        raise ValueError("seat must be 1-32 lowercase letters, digits, or hyphens")
    words = re.split(r"[\s,]+", env.get("CLAIM_RVAS", "").strip())
    if not 1 <= len(words) <= 5 or any(not RVA.fullmatch(word) for word in words):
        raise ValueError("supply one to five 0x-prefixed eight-digit RVAs")
    rvas = [int(word, 16) for word in words]
    if 0 in rvas or len(set(rvas)) != len(rvas):
        raise ValueError("RVAs must be nonzero and unique")
    raw = env.get("CLAIM_TOKENS", "").strip()
    tokens = {}
    if action == "claim":
        if raw:
            raise ValueError("claim does not accept tokens; use renew for an existing claim")
    else:
        try:
            values = json.loads(raw, object_pairs_hook=unique_object)
        except (ValueError, TypeError):
            raise ValueError("renew and release require a JSON object of exact claim tokens") from None
        if not isinstance(values, dict) or set(values) != {label(rva) for rva in rvas}:
            raise ValueError("token keys must be exactly the requested canonical RVAs")
        if any(not isinstance(token, str) or not TOKEN.fullmatch(token) for token in values.values()):
            raise ValueError("every token must be a 40-digit lowercase Git commit SHA")
        tokens = {int(key, 16): token for key, token in values.items()}
    return action, sorted(rvas), f"github:{actor.lower()}:bfme1:{seat}", tokens


def git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                            env=claims._git_env(root), timeout=30)
    if result.returncode:
        raise ValueError("cannot establish the checked-out workflow context")
    return result.stdout.strip()


def runtime_context(env, root=ROOT):
    """Only the trusted official default-branch workflow may use job credentials."""
    if (env.get("GITHUB_ACTIONS") != "true"
            or env.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
            or env.get("GITHUB_REPOSITORY") != REPOSITORY
            or env.get("GITHUB_REF") != "refs/heads/master"):
        raise ValueError("run only by manual dispatch on the official repository's master branch")
    sha = env.get("GITHUB_SHA", "")
    if not TOKEN.fullmatch(sha) or git(root, "rev-parse", "HEAD") != sha:
        raise ValueError("checkout must equal the dispatched commit")
    if git(root, "remote", "get-url", "origin") not in (
            f"https://github.com/{REPOSITORY}", f"https://github.com/{REPOSITORY}.git"):
        raise ValueError("origin must be the official HTTPS repository")
    if claims.NS != "refs/heads/claims/" or claims.REMOTE != "origin":
        raise ValueError("unexpected claims namespace or remote")
    if git(root, "config", "--get", "core.hooksPath") != ".githooks":
        raise ValueError("the repository's normal hooks must be configured")
    if not os.access(root / ".githooks/pre-push", os.X_OK):
        raise ValueError("the normal pre-push hook must be executable")
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("tracked workflow inputs must be unchanged")
    for name in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT"):
        if not re.fullmatch(r"[1-9][0-9]*", env.get(name, "")):
            raise ValueError("missing workflow run provenance")
    return {"repository": REPOSITORY, "commit": sha,
            "run_id": env["GITHUB_RUN_ID"], "run_attempt": env["GITHUB_RUN_ATTEMPT"]}


def snapshot(root):
    if not claims.fetch(root):
        raise claims.ClaimsUnavailable("cannot read the claim refs; no further operation attempted")
    return claims._read_local(root)


def held_records(current, tokens, owner, root):
    result = []
    for rva, token in sorted(tokens.items()):
        entry = current.get(rva)
        if (not entry or entry[0] != token or claims._branch_sha(rva, root) != token
                or entry[1].get("owner") != owner
                or entry[1].get("expires", 0) <= time.time()):
            continue
        info = entry[1]
        result.append({"rva": label(rva), "ref": claims.ref_of(rva), "token": token,
                       "lease": info.get("lease") or token, "expires": info["expires"]})
    return result


def operate(action, rvas, owner, tokens, root=ROOT):
    """Call the existing claim APIs with fixed bounds and exact-token fencing."""
    current = snapshot(root)
    report = {"action": action, "owner": owner, "requested": list(map(label, rvas)),
              "held": [], "released": [], "refused": [], "complete": False}
    if action == "claim":
        # claim() starts a new lease even for its current owner. A rerun must
        # not invalidate a landing's existing Claim-Lease trailer; use renew.
        if any(rva in current and current[rva][1].get("owner") == owner
               and current[rva][1].get("expires", 0) > time.time() for rva in rvas):
            report["reason"] = "an existing live claim of this seat requires renew and its token"
            report["refused"] = list(map(label, rvas))
            return report
        result = claims.claim(rvas, who=owner, ttl_hours=4, root=root)
        after = snapshot(root)
        report["held"] = held_records(after, result.tokens, owner, root)
        confirmed = {int(entry["rva"], 16) for entry in report["held"]}
        report["refused"] = [label(rva) for rva in rvas if rva not in confirmed]
        report["complete"] = confirmed == set(rvas)
        return report
    # Reject a stale token even if an old commit belongs to the current lease.
    # This runner requires the explicit generation the operator inspected.
    if any(rva not in current or current[rva][0] != tokens[rva]
           or claims._branch_sha(rva, root) != tokens[rva]
           or current[rva][1].get("owner") != owner for rva in rvas):
        report["reason"] = "the exact token and seat owner must still match every requested claim"
        report["refused"] = list(map(label, rvas))
        return report
    if action == "renew":
        renewed, lost = claims.renew(tokens, who=owner, ttl_hours=4, root=root)
        after = snapshot(root)
        report["held"] = held_records(after, renewed, owner, root)
        confirmed = {int(entry["rva"], 16) for entry in report["held"]}
        report["refused"] = [label(rva) for rva in rvas if rva not in confirmed]
        report["complete"] = confirmed == set(rvas) and not lost
    elif action == "release":
        released = claims.release(rvas, who=owner, root=root, tokens=tokens)
        after = snapshot(root)
        confirmed = {rva for rva in released if rva not in after or after[rva][0] != tokens[rva]}
        report["released"] = [label(rva) for rva in sorted(confirmed)]
        report["refused"] = [label(rva) for rva in rvas if rva not in confirmed]
        report["complete"] = confirmed == set(rvas)
    else:
        raise ValueError("unsupported action")
    return report


def main():
    report = {"schema_version": 1, "complete": False}
    try:
        action, rvas, owner, tokens = request(os.environ)
        report.update(runtime_context(os.environ))
        report.update(operate(action, rvas, owner, tokens))
    except (ValueError, claims.ClaimsUnavailable, subprocess.TimeoutExpired) as error:
        # None of these messages includes captured Git stderr or credentials.
        report["error"] = str(error) if not isinstance(error, subprocess.TimeoutExpired) else "Git context check timed out"
    path = ROOT / OUTPUT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
