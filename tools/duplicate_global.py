#!/usr/bin/env python3
"""Flag game/ TUs that define a global at a VA dir32_addresses.csv names differently.

WHY. Several static-initializer TUs define an INVENTED global (g_rvaXXXXXXXX...)
at an address that targets/game/reverse/dir32_addresses.csv already records under
its real name (?cerr@_STL@@..., ?Gen_g_0130c0b0@@..., ?TheBfmeObject_00C70E10@@...).
The link then carries a SECOND object at that address instead of initializing the
real one. The byte gate cannot see it: compile_function masks every DIR32 operand
by copying retail's bytes, so the initializer still matches exactly.

METHOD. Source scan only: no compiler, no retail image, seconds. For each
game/**/*.cpp and game/**/*.c, at brace depth 0, a non-`extern` line that defines
a variable whose identifier embeds an 8-hex-digit token (the retail VA, e.g.
g_rva0130BF40Object -> 0x0130BF40). When dir32 maps that VA and none of its
recorded names contains the defining identifier, the TU is listed with the VA
and the recorded names. Generated dumps, frozen helpers, float tables and
vtable installers are reviewed per REPAIR-SCOPE below: listed, never fixed.

A hit is a CANDIDATE, not a verdict: confirm in the object that the defined
symbol (storage EXTERNAL, .bss/.data) resolves through a DIR32 relocation to
the flagged VA, e.g. python3 tools/dir32.py <symbol>. Function declarators
(`void f(void);`, `T f() {`) are skipped, as are `extern` declarations and
lines below depth 0.

REPAIR-SCOPE. Only hits whose flagged VA is ALSO the address the same TU's
matched initializer row claims via a DIR32 relocation (the _$E body reads the
global it defines) are in scope: that is the duplicate-global defect, and every
such TU is fixed in this lane. A TU that merely references a dir32 VA it does
not define (callers through pins, vtable installers, float tables) keeps its
source: the name it uses is the link-visible one and agrees with the object.

The full scan is not a gate: a fail-if-any gate would go red fleet-wide until
every hit lands, and a count baseline would record today's debt as tomorrow's
allowance. The hooks judge only what a change ADDS (--staged, --range): a
(identifier, VA) hit that the changed file did not already carry, against the
base side's dir32_addresses.csv, so recording the invented name in the same
commit does not admit it. `static` definitions are not judged (the linker never
sees them). Existing hits stay listed for the repair seat.

  python3 tools/duplicate_global.py                 # every hit (repair seat)
  python3 tools/duplicate_global.py --staged        # pre-commit: index vs HEAD
  python3 tools/duplicate_global.py --range OLD NEW # pre-push
"""
import argparse
import csv
import io
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR32 = ROOT / "targets/game/reverse" / "dir32_addresses.csv"
GAME = ROOT / "game"

VBLOCK = re.compile(r"[0-1][0-9A-Fa-f]{7}")
IDENT = re.compile(r"[A-Za-z_]\w*")
# A function declarator, not a variable definition: empty or void parens
# followed by ; { or end of line. A variable direct-init like Object(0)
# carries arguments, so it is kept.
FUNCY = re.compile(r"\(\s*(void)?\s*\)\s*(;|\{|$)")
# What may follow a variable identifier in a namespace-scope definition:
# direct-init (, copy-init =, array [, or plain ;
DEF_TAIL = re.compile(r"\s*[;=(\[]")

# Generated dumps and frozen helpers define only placeholders by design;
# float tables and vtable installers legitimately name homes there.
SKIP_DIRS = ("game/gen_small/", "game/gen_asm/", "game/masm_dumps/")
SKIP_RECS = ("??_7", "__real@")


def load_dir32(text=None):
    """VA int -> [names] from dir32_addresses.csv (or its `text`)."""
    by_va = {}
    handle = io.StringIO(text) if text is not None else DIR32.open(newline="")
    with handle:
        for row in csv.DictReader(handle):
            by_va.setdefault(int(row["va"], 16), []).append(row["name"])
    return by_va


def strip_comment(line):
    return line.split("//", 1)[0]


def scan_file(path, by_va):
    """[(lineno, identifier, token, va, recorded)] candidates in one source."""
    rel = path.relative_to(ROOT).as_posix()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return scan_text(rel, text, by_va)


def scan_text(rel, text, by_va, skip_static=False):
    """scan_file over `text` as the source `rel`."""
    if rel.startswith(SKIP_DIRS):
        return []
    hits = []
    depth = 0
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = strip_comment(raw)
        if skip_static and line.lstrip().startswith("static"):
            depth += line.count("{") - line.count("}")
            continue
        if depth == 0 and "extern" not in line and "return" not in line:
            for match in IDENT.finditer(line):
                ident = match.group(0)
                tokens = [m.group(0) for m in VBLOCK.finditer(ident)]
                if not tokens:
                    continue
                rest = line[match.end():]
                if FUNCY.match(rest):
                    continue
                if not DEF_TAIL.match(rest):
                    continue
                for token in tokens:
                    va = int(token, 16)
                    names = by_va.get(va)
                    if names is None:
                        continue
                    if all(n.startswith(SKIP_RECS) for n in names):
                        continue
                    if any(ident.lower() in name.lower() for name in names):
                        continue
                    hits.append((lineno, ident, token, va, names))
        depth += line.count("{") - line.count("}")
    return hits


def confirmed(path, ident):
    """Object proof the defined symbol is a link-visible duplicate-global fix.

    True when the TU's .obj defines `ident` as EXTERNAL storage in .bss/.data
    AND aims a DIR32 relocation at it (some body in the same object takes its
    address, which is what places the second object at the recorded VA).
    None when the TU has no object yet; False when the source hit does not
    survive the object (e.g. a static the linker never sees).
    """
    sys.path.insert(0, str(ROOT / "tools"))
    import build as B
    rel = path.relative_to(ROOT).as_posix()
    obj = B.row_object({"source": rel, "name": ident})
    if not obj.exists():
        return None
    try:
        stat = obj.stat()
        _data, sections, symbols = B._object_layout(
            str(obj), stat.st_mtime_ns, stat.st_size)
    except OSError:
        return None
    hit_syms = [s for s in symbols
                if ident in s["name"] and s["section"] > 0 and s["storage"] == 2
                and sections[s["section"] - 1]["name"] in (".bss", ".data")]
    if not hit_syms:
        return False
    hit_names = {s["name"] for s in hit_syms}
    for sym in symbols:
        if sym["section"] <= 0:
            continue
        if sections[sym["section"] - 1]["name"] not in (
                ".text", ".text$yc", ".text$yd"):
            continue
        try:
            _body, relocs = B.read_object_symbol_bytes(obj, sym["name"], None)
        except ValueError:
            continue
        if any(rtype == 0x0006 and name in hit_names
               for _off, rtype, name in relocs):
            return True
    return False


def git(*args):
    """stdout of a git command in ROOT, or None when it fails."""
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return out.stdout.decode("utf-8", errors="replace") if out.returncode == 0 else None


def show(rev, path):
    """`path` at `rev` (":" is the index), or "" where it does not exist."""
    spec = f":{path}" if rev == ":" else f"{rev}:{path}"
    return git("show", spec) or ""


def changed_sources(base, head):
    """game/ C and C++ sources added or modified from `base` to `head` (":" = index)."""
    args = ["diff", "--name-only", "--diff-filter=ACMR"]
    args += ["--cached", base] if head == ":" else [base, head]
    out = git(*args, "--", "game/") or ""
    return [p for p in out.splitlines() if p.endswith((".cpp", ".c")) and not p.startswith(SKIP_DIRS)]


def added_hits(base, head):
    """[(path, lineno, identifier, va, recorded)] hits in `head` that `base` lacks.

    Recorded names come from base's dir32_addresses.csv: the change cannot
    admit its own invented global by recording it."""
    paths = changed_sources(base, head)
    if not paths:
        return []
    by_va = load_dir32(show(base, DIR32.relative_to(ROOT).as_posix()) or "name,va\n")
    out = []
    for path in paths:
        old = {(h[1], h[3]) for h in scan_text(path, show(base, path), by_va, skip_static=True)}
        for lineno, ident, _token, va, names in scan_text(path, show(head, path), by_va,
                                                          skip_static=True):
            if (ident, va) not in old:
                out.append((path, lineno, ident, va, names))
    return out


def gate(base, head):
    hits = added_hits(base, head)
    for path, lineno, ident, va, names in hits:
        print(f"{path}:{lineno}: defines {ident} at 0x{va:08X}, which "
              f"{DIR32.relative_to(ROOT).as_posix()} records as {', '.join(names[:3])}"
              f"{' ...' if len(names) > 3 else ''}", file=sys.stderr)
    if hits:
        print("duplicate_global: the link would carry a second object at a retail address that "
              "already has a name. Declare the recorded global (extern) and use it, or cast it "
              "to your view; do not define an invented one.", file=sys.stderr)
    return 1 if hits else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--staged", action="store_true", help="judge what the index adds to HEAD")
    ap.add_argument("--range", nargs=2, metavar=("OLD", "NEW"), help="judge what NEW adds to OLD")
    args = ap.parse_args()
    if args.staged:
        return gate("HEAD", ":")
    if args.range:
        return gate(*args.range)
    by_va = load_dir32()
    sources = sorted(GAME.rglob("*.cpp")) + sorted(GAME.rglob("*.c"))
    dirty, clean, unbuilt = 0, 0, 0
    for path in sources:
        rel = path.relative_to(ROOT).as_posix()
        hits = scan_file(path, by_va)
        if not hits:
            clean += 1
            continue
        marks = []
        for lineno, ident, _token, va, names in hits:
            verdict = confirmed(path, ident)
            marks.append((lineno, ident, va, names, verdict))
        if all(mark[4] is False for mark in marks):
            clean += 1
            continue
        dirty += 1
        print(f"{rel}:")
        for lineno, ident, va, names, verdict in marks:
            tag = {True: "duplicate", False: "static-only",
                   None: "unbuilt"}[verdict]
            print(f"    line {lineno}: [{tag}] {ident} claims 0x{va:08X}, "
                  f"dir32 records {', '.join(names)}")
            if verdict is None:
                unbuilt += 1
    print(f"duplicate_global: {dirty} defining TU(s), {clean} clean, "
          f"{unbuilt} unbuilt ({len(sources)} scanned, {len(by_va)} dir32 VAs)")
    return 1 if dirty else 0


if __name__ == "__main__":
    sys.exit(main())
