"""BFME1 measurement configuration; validity stays with build/link_census.

Rule identity hashes only MEASUREMENT_FILES, traced from link_cycle's executed
providers: build/COFF/case-shim/locking and current-object receipts; census's
verified-data, relocation, alias and pin owners (including ABI/import/ILT route
proof and progress's generated-row identity constants); build's relocation and
definition helpers; and dump/retail relocation producers for the swapped objects. gen_case_shims is also a snapshot subprocess.
Whole provider files are bound, including their optional measurement branches.
CLI-only queues and gates never called by the cycle are not semantic dependencies merely because a provider imports them. The broad tools
inventory remains tool_digest provenance: unrelated fleet edits warn, not refuse.
New local imports in the driver require review of this explicit set (tested).
No BFME2 policy or authority default belongs here.
"""
import hashlib
import json
import os
import platform
from pathlib import Path

ROOT = Path(os.environ.get("LINK_CYCLE_ROOT") or Path(__file__).resolve().parents[1]).resolve()
REVERSE = ROOT / "targets/game/reverse"
RULES = "bfme1-link-cycle-1"
GRAPH_SCHEMA = "bfme1-closure-graph/1"
BAD_TARGETS = ("fill", "stub", "dump")
PROFILE = {"target": "bfme1-retail-1.03", "text_groups": [[0x1000, ".text"]],
           "ilt": [0x1000, 0x5B000], "bad_targets": list(BAD_TARGETS),
           "credit": "real/placed/closed_strict/interval-union", "copy_rule": "bfme1-keep_rule",
           "alias_rule": "bfme1-judge_selected", "fold_exemptions": []}
# Explicit measurement-semantic closure; shared by receipts, bundles and diffs.
MEASUREMENT_FILES = (
    "link_cycle.py", "link_cycle_context.py", "link_census.py", "build.py",
    "census_receipts.py", "data_rows.py", "reloc_ledger.py", "alias_guard.py",
    "pin_consistency.py", "progress.py", "abi_view.py", "import_pin_guard.py", "ilt_oracle.py",
    "body_guard.py", "dir32_record_guard.py", "archive_import.py",
    "coffar.py", "gen_case_shims.py", "portable_lock.py", "target_guard.py",
    "dump_relocs.py", "dump_apply.py", "retail_relocs.py",
)
RUN_OPTIONS = ("allow_dirty", "allow_stale_cache", "measure_only", "snapshot", "remeasure")


def run_authority_failure(receipt):
    """Recompute clean-run eligibility; a receipt's authority claim is insufficient.

    Missing historical evidence fails closed. This is local evidence validation,
    not a signature: mutually consistent fabricated evidence cannot prove execution.
    Ancestry, integrity, rule compatibility and age are checked by the reader.
    """
    start, end = receipt.get("checkout_start"), receipt.get("checkout_end")
    if not isinstance(start, dict) or not isinstance(end, dict):
        return "missing-evidence"
    for label, state in (("start", start), ("end", end)):
        if state.get("dirty") is True:
            return "dirty-" + label
        if state.get("dirty") is not False or state.get("snapshot") not in (True, False):
            return "missing-evidence"
    options = receipt.get("run_options")
    if not isinstance(options, dict) or any(type(options.get(k)) is not bool for k in RUN_OPTIONS):
        return "missing-evidence"
    snapshot = receipt.get("snapshot") is True and start["snapshot"] and end["snapshot"] \
        and bool(start.get("tree_manifest")) and options["snapshot"]
    snapshot_requested = options["snapshot"] or receipt.get("snapshot") or start["snapshot"] or end["snapshot"]
    if any(value for name, value in options.items() if name != "snapshot") \
            or (snapshot_requested and not snapshot) \
            or receipt.get("allow_dirty") or receipt.get("diagnostic") \
            or receipt.get("remeasured_utc") or receipt.get("source_receipt_sha256"):
        return "diagnostic"
    if receipt.get("dirty") is not False:
        return "dirty-start" if receipt.get("dirty") is True else "missing-evidence"
    if start != end or start.get("commit") != receipt.get("commit") or receipt.get("moved_during_run"):
        return "inputs-moved"
    if "compile_failed" not in receipt or not isinstance(receipt.get("warm_start"), dict) \
            or type(receipt["warm_start"].get("stale")) is not bool:
        return "missing-evidence"
    if receipt["compile_failed"]:
        return "compile-failed"
    if receipt["warm_start"]["stale"]:
        return "diagnostic"
    return None


def text_bytes(path):
    return Path(path).read_bytes().replace(b"\r\n", b"\n")


def text_sha256(path):
    return hashlib.sha256(text_bytes(path)).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def tool_dependencies(root=ROOT, measuring_file=None):
    """Normalized identities, including the actual driver used for a snapshot.

    Providers are loaded from root/tools. Frozen snapshot subprocesses execute
    their own driver and adapter; bind those actual files.
    """
    base = Path(root) / "tools"
    files = {p.relative_to(base).as_posix(): p for p in base.rglob("*")
             if p.is_file() and not {"tests", "__pycache__"}.intersection(p.relative_to(base).parts)
             and p.suffix in (".py", ".sh", ".json", ".txt", ".csv", ".tsv", ".cmd")}
    files["link_cycle_context.py"] = Path(__file__)
    if measuring_file is not None:
        files["link_cycle.py"] = Path(measuring_file)
    return {name: text_sha256(path) for name, path in sorted(files.items())}


def rule_identity(dependencies):
    """Compare the semantic tuple, never RULES alone or the broad tool digest.

    Missing providers are explicitly bound as None; real receipts must carry
    every provider (bundle validation enforces that completeness).
    """
    return {"id": RULES, "profile": PROFILE, "profile_sha256": digest(PROFILE),
            "measurement_files": list(MEASUREMENT_FILES),
            "implementation_sha256": digest({name: dependencies.get(name) for name in MEASUREMENT_FILES})}


def input_paths(root=ROOT):
    """Ledger/evidence identities, with absence bound explicitly for optional inputs.

    Derived relocation tables are evidence only, never verified ownership.
    Inventory their names as well as contents to detect additions/removals.
    """
    root = Path(root)
    reverse = root / "targets/game/reverse"
    paths = {str(p.relative_to(root)): p for p in reverse.iterdir()
             if p.is_file() and p.suffix in (".csv", ".tsv", ".txt", ".json")}
    for name in ("functions.csv", "symbols.csv", "data_rows.csv", "ghidra_functions.csv",
                 "dir32_addresses.csv", "dir32_consistency_whitelist.txt", "imports.csv", "exports.csv"):
        paths[f"targets/game/reverse/{name}"] = reverse / name
    # Derive the target-manifest location from BFME1's owner, never a donor path.
    import build
    manifest = Path(build.MANIFEST).relative_to(build.ROOT)
    paths[manifest.as_posix()] = root / manifest
    for name in ("dir32_addresses.csv", "reloc_names.generated.csv"):
        paths[f"build/{name}"] = root / "build" / name
    for directory in ("build/reloc_ledger", "build/dump_relocs", "build/startup"):
        top = root / directory
        # Generated object bytes are bound separately; these are their evidence/config.
        if top.exists():
            for p in top.rglob("*"):
                if p.is_file() and p.suffix in (".csv", ".json", ".tsv"):
                    paths[p.relative_to(root).as_posix()] = p
    return dict(sorted(paths.items()))


def input_hashes(root=ROOT):
    return {name: text_sha256(path) if path.is_file() else None for name, path in input_paths(root).items()}


def measure_env():
    import capstone
    import pefile
    return {"python": platform.python_version(), "pefile": pefile.__version__, "capstone": capstone.__version__}


def target_identity(path):
    import pefile
    raw = Path(path).read_bytes()
    pe = pefile.PE(data=raw, fast_load=True)
    try:
        return {"sha256": hashlib.sha256(raw).hexdigest(), "image_base": pe.OPTIONAL_HEADER.ImageBase,
                "machine": pe.FILE_HEADER.Machine, "size_of_image": pe.OPTIONAL_HEADER.SizeOfImage}
    finally:
        pe.close()


def current_object(source, obj, **kwargs):
    import build
    return build.compile_is_current(source, obj, **kwargs)


def source_kind(row):
    import link_cycle
    return link_cycle.row_kind(row)


def retail_imports():
    import link_cycle
    return link_cycle.retail_imports()


def ilt_window():
    import link_cycle
    return link_cycle.ILT
