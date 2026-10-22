#!/usr/bin/env python3
"""Build and install an immutable local BFME1 cycle bundle.

Ported lifecycle/serialization from BFME2 02518d74b1 with BFME1 adapters.
`bundle RUN --out DIR --producer LABEL` freezes the receipt,
status, measured graph, closure report and explicit unavailable data-back member.
A missing report is computed from the receipt-bound graph without measuring or
linking. --closure DIR uses a precomputed report, validated against this run.
Optional --previous DIR or --first adds the scoped interval-union cycle diff.
The producer label is required: there is no donor host or identity default.

Bytes are deterministic: gzip has mtime=0/no name, JSON is sorted, and the default
manifest timestamp is the receipt's finalization time (not assembly wall time).
The temporary directory is validated before one rename; no existing destination,
even empty, is replaced. `--install STORE` uses cycle_artifacts' immutable store.
Authority is recomputed by consumers from the run evidence and local policy.
No ledger, source, receipt, graph, or input run file is modified.
"""
import argparse
import csv
import hashlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

import cycle_artifacts as ca
import data_back_rank

ROOT = ca.ROOT


class RunError(ca.BundleError):
    pass


def validate_run(run_dir, *, root=ROOT):
    run = Path(run_dir)
    try:
        rpath = run / ca.RECEIPT
        raw = rpath.read_bytes()
        receipt = ca.read_json(rpath)
        ca.check_receipt(receipt, root)
        if receipt.get("moved_during_run") or receipt.get("remeasured_utc"):
            raise RunError("receipt records changed inputs or a diagnostic remeasure")
        rejected = run / "receipt.rejected.json"
        if rejected.exists() and rejected.stat().st_mtime_ns > rpath.stat().st_mtime_ns:
            raise RunError("a newer rejected run may have replaced the measurement outputs")
        status = run / "link_status.csv"
        if not status.is_file():
            status = run / ca.LINK_STATUS
        content = ca.read_member(status)
        ca.same("run status", hashlib.sha256(content).hexdigest(), receipt["series"]["link_status_sha256"])
        with ca.open_text(status) as f:
            ca.same("run status header", tuple(next(csv.reader(f), ())), ca.STATUS_COLUMNS)
        graph = run / ca.CLOSURE_GRAPH
        if not receipt.get("closure_graph_sha256"):
            raise ca.Refused("measurement has no receipt-bound closure graph", "no-closure-report")
        ca.same("run graph", ca.sha256_file(graph), receipt["closure_graph_sha256"])
        return {"run_dir": run, "receipt": receipt, "receipt_bytes": raw, "status": status, "graph": graph,
                "commit": receipt["commit"], "core": receipt["core_sha256"]}
    except ca.Problem:
        raise
    except OSError as e:
        raise ca.Unavailable(f"{run}: {e}") from None
    except (KeyError, ValueError, TypeError, AttributeError, IndexError, UnicodeError, OverflowError) as e:
        raise RunError(f"malformed cycle run: {e}") from None


def gzip_bytes(raw, dest):
    import gzip
    # GzipFile fixes OS header bytes across Python/zlib versions too.
    with Path(dest).open("wb") as f:
        with gzip.GzipFile(filename="", mode="wb", fileobj=f, compresslevel=9, mtime=0) as gz:
            gz.write(raw)


def gzip_into(src, dest):
    gzip_bytes(Path(src).read_bytes(), dest)


def closure_members(facts, tmp, closure=None):
    import closure_report as cr
    src = Path(closure) if closure else facts["run_dir"]
    roots, blockers = src / cr.ROOTS, src / cr.BLOCKERS
    if roots.is_file() and blockers.is_file():
        raw, table = roots.read_bytes(), blockers.read_bytes()
    elif closure:
        raise ca.Refused("supplied closure directory lacks the report pair", "no-closure-report")
    elif roots.exists() or blockers.exists():
        raise RunError("incomplete closure report pair in run directory")
    else:
        try:
            raw, table, _ = cr.from_graph(facts["run_dir"])
        except (cr.ReportError, KeyError, ValueError, TypeError, IndexError) as e:
            raise RunError(f"closure report: {e}") from None
    gzip_bytes(raw, tmp / ca.CLOSURE_ROOTS)
    gzip_bytes(table, tmp / ca.CLOSURE_BLOCKERS)
    return {"included": True, "schema": cr.SCHEMA, "algorithm": cr.ALGORITHM, "graph": cr.BOUND}


def make_bundle(run_dir, out, producer, *, root=ROOT, now=None, closure=None, previous=None,
                first=False):
    if not isinstance(producer, str) or not producer.strip():
        raise RunError("a BFME1 producer label is required")
    if first and previous is not None:
        raise RunError("--first and --previous are mutually exclusive")
    facts = validate_run(run_dir, root=root)
    out = Path(out)
    if out.exists():
        raise RunError("bundle destination exists: immutable bundles are never replaced")
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f".{out.name}.partial-", dir=out.parent))
    try:
        (tmp / ca.RECEIPT).write_bytes(facts["receipt_bytes"])
        gzip_bytes(ca.read_member(facts["status"]), tmp / ca.LINK_STATUS)
        shutil.copyfile(facts["graph"], tmp / ca.CLOSURE_GRAPH)
        if (facts["run_dir"] / ca.PROVENANCE).is_file():
            ca.same("run provenance", ca.sha256_file(facts["run_dir"] / ca.PROVENANCE),
                    facts["receipt"]["provenance_sha256"])
            shutil.copyfile(facts["run_dir"] / ca.PROVENANCE, tmp / ca.PROVENANCE)
        report = closure_members(facts, tmp, closure)
        receipt = facts["receipt"]
        (tmp / ca.RANK_JSON).write_text(ca.dumps(data_back_rank.unavailable(receipt)), encoding="utf-8", newline="\n")
        diff = {"included": False, "why": "no predecessor comparison requested"}
        if first or previous is not None:
            import cycle_diff as cd
            try:
                doc = cd.compare(previous, facts["run_dir"])
            except cd.CycleDiffError as e:
                raise RunError(str(e)) from None
            if previous is not None:
                was = ca.read_json(Path(previous) / ca.RECEIPT)
                if receipt["measured_end_ns"] < was["measured_end_ns"]:
                    raise RunError("predecessor was measured after this run")
                if (Path(previous) / ca.RECEIPT).read_bytes() == facts["receipt_bytes"]:
                    raise RunError("predecessor is this measurement itself")
            (tmp / ca.CYCLE_DIFF).write_text(cd.dumps(doc), encoding="utf-8", newline="\n")
            diff = {"included": True, "schema": cd.SCHEMA, "predecessor": doc["identity"]["old"]}
        members = {p.name: ca.member_meta(p) for p in sorted(tmp.iterdir())}
        manifest = {"schema": ca.SCHEMA, "tag": ca.tag_for(facts["receipt_bytes"]),
                    "commit": receipt["commit"], "producer": producer.strip(),
                    "created_utc": ca.iso_utc(ca.receipt_end(receipt) if now is None else now),
                    "measured": ca.measured_of(receipt), "headline": ca.headline_of(receipt),
                    "instance": {"receipt_sha256": members[ca.RECEIPT]["sha256"],
                                 "measured_end_ns": receipt["measured_end_ns"]},
                    "binding": ca.binding_of(receipt), "rules": ca.rules_of(receipt),
                    "tool_digest": receipt["tool_digest"], "members": members,
                    "components": {"closure_report": report, "cycle_diff": diff}}
        (tmp / ca.MANIFEST).write_text(ca.dumps(manifest), encoding="utf-8", newline="\n")
        ca.validate(tmp, root=root)
        ca.publish_directory(tmp, out)
        return manifest
    except OSError as e:
        raise ca.Unavailable(f"cannot assemble local bundle: {e}") from None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("run_dir")
    b = sub.add_parser("bundle")
    b.add_argument("run_dir")
    b.add_argument("--out", required=True)
    b.add_argument("--producer", required=True)
    b.add_argument("--closure")
    prior = b.add_mutually_exclusive_group()
    prior.add_argument("--previous")
    prior.add_argument("--first", action="store_true")
    b.add_argument("--install", metavar="STORE")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "validate":
            facts = validate_run(args.run_dir)
            print(f"consistent local measurement {facts['commit']}; authority is recomputed when served")
        elif args.cmd == "bundle":
            m = make_bundle(args.run_dir, args.out, args.producer, closure=args.closure, previous=args.previous,
                            first=args.first)
            if args.install:
                ca.install_local(args.out, args.install)
            print(f"bundle {m['tag']}: local bundle; authority is recomputed when served; data-back rank unavailable")
        return 0
    except OSError as e:
        problem = ca.Unavailable(str(e))
        print(f"publish_cycle: {ca.describe(problem)}", file=sys.stderr)
        return ca.exit_code(problem)
    except ca.Problem as e:
        print(f"publish_cycle: {ca.describe(e)}", file=sys.stderr)
        return ca.exit_code(e)


if __name__ == "__main__":
    sys.exit(main())
