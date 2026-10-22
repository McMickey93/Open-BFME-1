#!/usr/bin/env python3
"""BFME1 bundle companion: compare receipt-verified unique credit intervals.

The interval-union comparison is adapted from BFME2 02518d74b1. Names do not
score: renames gain zero. This scoped port omits BFME2 fold diagnostics and
candidate-cause attribution; it reports ruler changes using the single BFME1
semantic dependency declaration in link_cycle_context, plus target/environment.
The CLI labels raw/unsigned comparisons diagnostic and checks both bundles'
authority independently of receipt/status consistency.
"""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

SCHEMA = "bfme1-cycle-diff/1"


class CycleDiffError(ValueError):
    pass


def union(spans):
    out = []
    for a, b in sorted(spans):
        if type(a) is not int or type(b) is not int or a < 0 or b <= a:
            raise CycleDiffError("invalid credit interval")
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def difference(left, right):
    out, j = [], 0
    for a, b in left:
        while j < len(right) and right[j][1] <= a:
            j += 1
        k, cursor = j, a
        while k < len(right) and right[k][0] < b:
            lo, hi = right[k]
            if lo > cursor:
                out.append([cursor, min(lo, b)])
            cursor = max(cursor, hi)
            if cursor >= b:
                break
            k += 1
        if cursor < b:
            out.append([cursor, b])
    return out


def size(spans):
    return sum(b - a for a, b in spans)


def identity(receipt):
    return {"commit": receipt["commit"], "core_sha256": receipt["core_sha256"],
            "rule_identity": receipt["rule_identity"], "tool_digest": receipt["tool_digest"],
            "target": receipt["target"], "measure_env": receipt.get("measure_env"),
            "toolchain_sha256": receipt.get("toolchain_sha256")}


def load_run(directory):
    import cycle_artifacts as ca
    d = Path(directory)
    try:
        receipt = ca.read_json(d / ca.RECEIPT)
        ca.check_receipt(receipt)
        path = d / "link_status.csv"
        if not path.is_file():
            path = d / ca.LINK_STATUS
        raw = ca.read_member(path)
        if hashlib.sha256(raw).hexdigest() != receipt["series"]["link_status_sha256"]:
            raise CycleDiffError("status is not the receipt's")
        spans = verified_credit(receipt, raw)
        return receipt, spans
    except (ca.Problem, OSError, KeyError, TypeError, ValueError) as e:
        raise CycleDiffError(f"{d}: {e}") from None


def verified_credit(receipt, raw):
    """Reproduce a credit union from the receipt's exact status artifact."""
    import io
    import cycle_artifacts as ca
    ca.check_receipt(receipt)
    if hashlib.sha256(raw).hexdigest() != receipt["series"]["link_status_sha256"]:
        raise CycleDiffError("status is not the receipt's")
    rows = csv.DictReader(io.StringIO(raw.decode("utf-8")))
    spans = []
    for row in rows:
        if row["kind"] == "real" and row["placed"] == "1" and row["closed_strict"] == "1":
            if ca.context.source_kind(row) != "real":
                raise CycleDiffError("generated/assembly source cannot score")
            a = int(row["retail_rva"], 16)
            spans.append([a, a + int(row["size"])])
    spans = union(spans)
    if size(spans) != receipt["series"]["credit_unique_bytes"]:
        raise CycleDiffError("credit union disagrees with receipt")
    return spans


def evidence(directory, receipt):
    import cycle_artifacts as ca
    d = Path(directory)
    path = d / "link_status.csv"
    if not path.is_file():
        path = d / ca.LINK_STATUS
    return {"receipt": receipt, "link_status": ca.read_member(path).decode("utf-8")}


def check_report(doc):
    """Reproduce both identified receipt/status unions before counting progress."""
    if doc.get("schema") != SCHEMA:
        raise CycleDiffError("unknown diff schema")
    ident = doc["identity"]
    comparison = ident["old"] is not None
    if doc["comparison"] != comparison:
        raise CycleDiffError("diff comparison/old identity disagree")
    new, old = doc["credit"]["new"], doc["credit"]["old"]
    if union(new) != new or old is not None and union(old) != old:
        raise CycleDiffError("noncanonical credit intervals")
    if comparison != (old is not None):
        raise CycleDiffError("diff old credit/identity disagree")
    changes = [k for k in ("rule_identity", "target", "measure_env", "toolchain_sha256")
               if comparison and ident["old"].get(k) != ident["new"].get(k)]
    warning = bool(comparison and ident["old"]["tool_digest"] != ident["new"]["tool_digest"] and
                   ident["old"]["rule_identity"] == ident["new"]["rule_identity"])
    if doc["measurement_changed"] != changes or doc["tool_digest_warning"] != warning:
        raise CycleDiffError("diff ruler provenance disagrees")
    if not comparison:
        if doc["totals"] is not None or doc["gained"] is not None or doc["lost"] is not None:
            raise CycleDiffError("first-run report invents a gain")
        return
    if doc.get("consistent", doc.get("comparison_verified")) is not True:
        if any(doc.get(k) is not None for k in ("totals", "gained", "lost")):
            raise CycleDiffError("unverified comparison cannot count progress")
        return
    for side in ("old", "new"):
        try:
            proof = doc["evidence"][side]
            if identity(proof["receipt"]) != ident[side]:
                raise CycleDiffError(f"{side} evidence identifies another receipt")
            if verified_credit(proof["receipt"], proof["link_status"].encode("utf-8")) != doc["credit"][side]:
                raise CycleDiffError(f"{side} credit union disagrees with evidence")
        except (KeyError, TypeError, ValueError) as e:
            raise CycleDiffError(f"unverified {side} comparison evidence: {e}") from None
    gained, lost = difference(new, old), difference(old, new)
    if doc["gained"] != gained or doc["lost"] != lost or doc["totals"] != {
            "old": size(old), "new": size(new), "gained": size(gained), "lost": size(lost),
            "delta": size(new) - size(old)}:
        raise CycleDiffError("diff totals/intervals disagree")
    if size(gained) - size(lost) != size(new) - size(old):
        raise CycleDiffError("diff does not reconcile")


def compare(old, new):
    after, new_spans = load_run(new)
    before, old_spans = load_run(old) if old is not None else (None, None)
    changes = []
    if before is not None:
        changes = [k for k in ("rule_identity", "target", "measure_env", "toolchain_sha256")
                   if before.get(k) != after.get(k)]
    gained = difference(new_spans, old_spans) if before is not None else None
    lost = difference(old_spans, new_spans) if before is not None else None
    doc = {"schema": SCHEMA, "comparison": before is not None,
           "comparison_verified": before is not None,
           "evidence": {"new": evidence(new, after), "old": evidence(old, before) if before else None},
           "identity": {"new": identity(after), "old": identity(before) if before is not None else None},
           "credit": {"new": new_spans, "old": old_spans}, "gained": gained, "lost": lost,
           "totals": None if before is None else {
               "old": size(old_spans), "new": size(new_spans), "gained": size(gained), "lost": size(lost),
               "delta": size(new_spans) - size(old_spans)},
           "measurement_changed": changes,
           "tool_digest_warning": bool(before and before["tool_digest"] != after["tool_digest"] and
                                       before["rule_identity"] == after["rule_identity"]),
           "limits": "unique-byte comparison only; no attribution of causes or data ownership"}
    check_report(doc)
    return doc


def dumps(doc):
    return json.dumps(doc, sort_keys=True, indent=1) + "\n"


def cli_input_authority(directory, expected):
    """Verify a CLI input host stamp independently of the internal interval validator."""
    import cycle_artifacts as ca
    directory = Path(directory)
    if not (directory / ca.MANIFEST).exists():
        return {"authoritative": False, "reason": "not-authoritative", "sub_reason": "raw-run"}
    try:
        bundle, fr, _ = ca.serve(directory, root=ca.ROOT)
    except ca.Refused as error:
        return {"authoritative": False, "reason": error.reason, "sub_reason": error.sub_reason}
    except ca.Problem as error:
        raise CycleDiffError(ca.describe(error)) from None
    if identity(bundle.receipt) != expected:
        raise CycleDiffError("host-stamped input identifies another receipt")
    return {"authoritative": fr["authoritative"], "reason": None, "sub_reason": None}


def cli_compare(old, new):
    doc = compare(old, new)
    inputs = {"new": cli_input_authority(new, doc["identity"]["new"]),
              "old": cli_input_authority(old, doc["identity"]["old"]) if old is not None else None}
    authoritative = all(side is None or side["authoritative"] for side in inputs.values()) and not doc["measurement_changed"]
    # Keep comparison_verified as an internal, legacy consistency field only.
    doc.pop("comparison_verified")
    doc.update(consistent=True, authoritative=authoritative, diagnostic=not authoritative,
               label="AUTHORITATIVE: measured unique bytes" if authoritative else "DIAGNOSTIC: consistent unique bytes; no authoritative progress claim",
               input_authority=inputs)
    check_report(doc)
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("new")
    ap.add_argument("--previous")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    try:
        raw = dumps(cli_compare(args.previous, args.new))
        if args.json:
            Path(args.json).write_text(raw, encoding="utf-8")
        else:
            print(raw, end="")
        return 0
    except (CycleDiffError, OSError) as e:
        print(f"cycle_diff: invalid [reason=corrupt]: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
