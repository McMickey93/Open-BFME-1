"""BFME1 measurement configuration; validity stays with build/link_census.

Dependency hashing deliberately over-binds all production tools and their text
configuration, including subprocess helpers and optional local imports. This is
conservative (an unrelated tool edit can invalidate compatibility), but cannot
silently miss a dynamically imported measurement dependency. No BFME2 policy,
release identity or authority default belongs here.
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
# Phase 2 must configure an authenticated publisher explicitly.
RELEASE_TRUST = None


def text_bytes(path):
    return Path(path).read_bytes().replace(b"\r\n", b"\n")


def text_sha256(path):
    return hashlib.sha256(text_bytes(path)).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def tool_dependencies(root=ROOT, measuring_file=None):
    """Normalized identities, including the actual driver used for a snapshot.

    The other providers are loaded from root/tools. Bind both the driver and
    this adapter as executed, rather than accidentally hashing snapshot copies.
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
    """Compare the whole tuple, never RULES alone. Provider/profile edits break it."""
    return {"id": RULES, "profile": PROFILE, "profile_sha256": digest(PROFILE),
            "implementation_sha256": digest(dependencies)}


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
