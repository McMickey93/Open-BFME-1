#!/usr/bin/env python3
"""Export ledger-derived recovered-source progress in objdiff's report v2 format.

  python3 tools/bytematch_report.py --output-dir build/bytematch

ByteMatch's matched_code is authored C++ plus vendored source, using progress.py's
non-padding interval union. Generated code, prebuilt libraries and dumps remain
visible in provenance.json but receive no recovered-source credit. This reads
the committed ledger; it does not compile, verify bytes or prove a complete link.
Function, unit, data, linked and fuzzy-match measures are not reported. ByteMatch
defaults omitted measures to zero; those zeros do not establish measurements.

CI uploads report.json and provenance.json as <game-version>_report. A repository
admin must sign in at https://bytematch.dev, open Manage, add Open-BFME/Open-BFME-1,
select bfme1-1.03 and optionally restrict ingestion to bytematch.yml. This workflow
needs no upload secret; ByteMatch needs authenticated artifact access through its
instance token or GitHub App. Add a badge only after registration and a successful
default-branch push run have produced a visible report.

Format and registration: https://bytematch.dev/docs/getting-started
Schema: https://github.com/Veradictus/ByteMatch/blob/master/src/report/proto/report.proto
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import progress
import progress_v2
from target_guard import require_game_cli

METRIC = "recovered-source-v1"


def measure(ref):
    """Return the summary and its counters from one committed repository state."""
    if tuple(progress.DECOMPILED_LANES) != ("authored", "vendored"):
        raise ValueError("recovered-source-v1 requires authored and vendored lanes")
    matched, notes = progress.matched_at(ref), progress.notes_at(ref)
    start, size = progress.retail_text()
    naked = progress.naked_cpp_rows_at(matched, ref)
    lanes = progress.real_split(matched, notes, start, size, naked)
    padding, total = progress.real_code_denominator(start, size)
    recovered = progress.decompiled(lanes)
    counts = [padding, total, recovered, *lanes.values()]
    if any(type(value) is not int or value < 0 for value in counts):
        raise ValueError("progress byte counts must be nonnegative integers")
    if padding + total != size or not 0 <= recovered <= sum(lanes.values()) <= total:
        raise ValueError("progress lanes or padding exceed the retail .text extent")
    report = {
        "version": 2,
        "measures": {
            "total_code": total,
            "matched_code": recovered,
            "matched_code_percent": progress.percent(recovered, total),
        },
        "units": [],
        "categories": [],
    }
    provenance = {
        "schema_version": 1,
        "metric": METRIC,
        "commit": ref,
        "measurement": "committed ledger; no fresh compilation, byte verification or link",
        "denominator": "retail .text excluding 0xCC padding, as in progress.py",
        "total_code_bytes": total,
        "padding_bytes": padding,
        "recovered_source_bytes": recovered,
        "credited_lanes": list(progress.DECOMPILED_LANES),
        "source_lanes": lanes,
        "excluded_lanes": [lane for lane in lanes if lane not in progress.DECOMPILED_LANES],
        "unclaimed_code_bytes": total - sum(lanes.values()),
        "counters": {
            "matched_ledger_rows": len(matched),
            "registered_hatches": progress_v2.hatch_totals(ref),
            "gate_debt": progress_v2.gate_debt(ref),
        },
        "unreported": ["functions", "units", "data", "linked", "fuzzy_match"],
        "omitted_measures_note": "ByteMatch defaults omitted measures to zero; they are not measured",
    }
    return report, provenance


def checkout_commit(expected=None):
    """The image/tools on disk and the ledger/source read from Git must agree."""
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=progress.ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    if expected is not None and commit != expected:
        raise ValueError(f"checkout is {commit}, expected {expected}")
    result = subprocess.run(["git", "diff", "--quiet", "HEAD", "--"], cwd=progress.ROOT)
    if result.returncode == 1:
        raise ValueError("use a clean committed checkout; tracked inputs differ from HEAD")
    result.check_returncode()
    return commit


def json_text(value):
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def main(argv=None):
    require_game_cli("bytematch_report.py")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", type=Path, default=progress.ROOT / "build/bytematch")
    parser.add_argument("--expected-commit", help="require this exact HEAD (CI uses its event SHA)")
    args = parser.parse_args(argv)
    try:
        commit = checkout_commit(args.expected_commit)
        report, provenance = measure(commit)
        checkout_commit(commit)  # Refuse a checkout changed while it was being measured.
        report_text = json_text(report)
        provenance["report_sha256"] = hashlib.sha256(report_text.encode("utf-8")).hexdigest()
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "report.json").write_text(report_text, encoding="utf-8", newline="\n")
        (args.output_dir / "provenance.json").write_text(json_text(provenance), encoding="utf-8", newline="\n")
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"bytematch_report: {exc}\n")
    values = report["measures"]
    print(f"recovered source: {values['matched_code']:,}/{values['total_code']:,} non-padding bytes "
          f"({values['matched_code_percent']:.2f}%); ledger-derived at {commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
