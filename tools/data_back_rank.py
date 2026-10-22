#!/usr/bin/env python3
"""BFME1 bundle data-back evidence availability, never data ownership admission.

BFME2's ranker consumes its derived data_ledger and boot-image resolver. Neither
is an honest BFME1 ownership provider. BFME1 instead owns data through matched,
byte-verified data_rows and typed DIR32/reloc_ledger evidence. Phase 1 archives
bind input hashes and collision addresses, but do not freeze the typed reference
sites, their scope, or the per-row data verification results. Looking up today's
mutable generated evidence would mix measurements. Until a measured evidence
view is provided, emit an explicit unavailable member, never an empty ranking
that looks successful. No compilation, ledger writes or guessed name/size.
"""
import argparse
import sys
from pathlib import Path

SCHEMA = "bfme1-data-back-rank/1"
PROVIDER = "bfme1-verified-data-rows+typed-relocation-evidence"
REASON = ("BFME1 measured evidence view unavailable: cycle archives bind ledger hashes but do not freeze "
          "verified data_rows results and typed DIR32/relocation sites with scope; derived names and extents "
          "cannot establish ownership")


def unavailable(receipt):
    return {"schema": SCHEMA, "status": "unavailable", "reason": REASON, "provider": PROVIDER,
            "commit": receipt["commit"], "receipt_core_sha256": receipt["core_sha256"],
            "inputs": receipt["inputs"], "authority": "diagnostic; never ownership evidence"}


def check_member(doc, receipt):
    import cycle_artifacts as ca
    # Only the explicit unavailable provider is currently implemented. Reject a
    # hand-authored 'available' result until BFME1 supplies independently checked
    # verified rows and typed references from this exact measurement.
    ca.same("data-back evidence member", doc, unavailable(receipt))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run_dir")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    import cycle_artifacts as ca
    try:
        receipt = ca.read_json(Path(args.run_dir) / ca.RECEIPT)
        ca.check_receipt(receipt)
        doc = unavailable(receipt)
        raw = ca.dumps(doc)
        if args.json:
            Path(args.json).write_text(raw, encoding="utf-8")
        else:
            print(raw, end="")
        raise ca.Unavailable(doc["reason"])
    except OSError as e:
        problem = ca.Unavailable(str(e))
    except ca.Problem as e:
        problem = e
    print(f"data_back_rank: {ca.describe(problem)}", file=sys.stderr)
    return ca.exit_code(problem)


if __name__ == "__main__":
    sys.exit(main())
