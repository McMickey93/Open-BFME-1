#!/usr/bin/env python3
"""Close banked near-misses by random source permutation (decomp-permuter style).

A banked attempt (targets/game/reverse/attempts/<rva>.cpp) is a standalone unit whose body
compiles close to, but not exactly, retail's bytes. This mutates the source
text, recompiles each candidate and keeps the ones whose bytes get closer,
until the body matches exactly or the time budget runs out.

Mutations need not be provably semantics-preserving: a candidate is only ever
reported as a win when its resolved bytes equal retail's exactly, and identical
machine code is the proof of identical behaviour. Nothing here lands a row;
a win is written to build/permute/<rva>/win.cpp for tools/add_match.py and the
normal gates.

Every candidate compiles inside build/permute/<rva>/, never to a real source's
object, so the shared object cache (build/match/) is untouched.

Usage:
  python3 tools/permute.py --list [--min-score 0.9]       the queue, best first
  python3 tools/permute.py RVA [RVA ...] [--minutes 10]   permute these attempts
  python3 tools/permute.py --top N [--min-score 0.9] [--minutes 10] [--jobs J]
  python3 tools/permute.py --recheck     compile every banked attempt once; exact ones become wins

Open-BFME-1 port (from Open-BFME-2 f4d49cc629): --land and --pins are left
out. A win is a source to read and land by hand at its proper game/ path with
tools/add_match.py (AGENTS.md: a proven identity, the usual gates); a callee
pin goes through tools/pin_consistency.py by hand, never automatically.
"""
import argparse
import collections
import concurrent.futures
import difflib
import hashlib
import json
import os
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402

ATTEMPTS = ROOT / "targets" / "game" / "reverse" / "attempts"
LOG = ROOT / "targets" / "game" / "reverse" / "re_attempts.log"
OUT = ROOT / "build" / "permute"


# ----------------------------------------------------------------- queue

def attempt_sizes():
    """{(symbol, rva lower): size} from re_attempts.log, last entry wins."""
    sizes = {}
    for line in LOG.open(encoding="utf-8", errors="replace"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) > 3:
            try:
                sizes[(parts[0], parts[1].lower())] = int(parts[2])
            except ValueError:
                pass
    return sizes


def wb_priority(rva):
    """Ordering multiplier. Open-BFME-2 boosts bodies with a WorldBuilder name
    lead (its wb_context); Open-BFME-1 has no such lead table, so 1.0."""
    return 1.0


def wb_note(rva):
    """Open-BFME-2's WorldBuilder lead line; none in Open-BFME-1."""
    return ""


def queue(min_score=0.9):
    """[(score, size, rva, symbol)] for banked attempts, highest score x size first."""
    sizes = attempt_sizes()
    out = []
    for path in ATTEMPTS.glob("0x*.cpp"):
        head = path.read_text(encoding="latin-1", errors="replace")[:400]
        symbol = re.match(r"//\s*(\S+)", head)
        score = re.search(r"score=([0-9.]+)", head)
        if not symbol or not score:
            continue
        rva = path.stem.lower()
        size = sizes.get((symbol.group(1), rva))
        if size and float(score.group(1)) >= min_score:
            out.append((float(score.group(1)), size, rva, symbol.group(1)))
    return sorted(out, key=lambda item: (-item[0] * item[1] * wb_priority(item[2]), item[2]))


# ----------------------------------------------------------------- scoring

class Scorer:
    def __init__(self, rva, symbol, size, workdir):
        self.rva, self.symbol, self.size, self.dir = rva, symbol, size, workdir
        self.symbol_map = build.load_symbol_map()
        self.seen = {}
        self.trials = 0
        self.hits = 0  # consecutive candidates already compiled: the search is spinning
        self.unresolved = False
        self.last = None

    def score(self, text):
        """(fitness 0..1, exact) for a candidate source; (-1, False) if it does not compile."""
        key = hashlib.sha1(text.encode("latin-1", "replace")).hexdigest()
        if key in self.seen:
            self.hits += 1
            return self.seen[key]
        self.hits = 0
        self.trials += 1
        source = self.dir / f"t{self.trials % 4}.cpp"
        output = source.with_suffix(".obj")
        source.write_text(text, encoding="latin-1", errors="replace")
        result = (-1.0, False)
        try:
            ok, _, _ = build.try_compile_source(source, output)
            if ok:
                row = {"name": self.symbol, "target_rva": self.rva, "target_size": str(self.size),
                       "source": source.relative_to(ROOT).as_posix(), "notes": ""}
                got = build.compile_function(row, self.symbol_map, output)
                compiled, target = got["bytes"], got["target"]
                self.unresolved = bool(got["unresolved"])
                self.last = (compiled, target)
                if compiled == target and not got["unresolved"]:
                    result = (1.0, True)
                else:
                    result = (fitness(compiled, target), False)
        except (SystemExit, Exception):  # a symbol the candidate no longer emits, etc.
            result = (-1.0, False)
        self.seen[key] = result
        return result


# Bumped when the search changes enough that bodies it already failed on are
# worth another run (--next --retry). 2: instruction fitness, target-only
# mutations, triage and early stops. 3: width/compound/not/temp mutations.
VERSION = 3

_DISASM = None


def _instructions(blob):
    global _DISASM
    if _DISASM is None:
        import capstone
        _DISASM = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    return [(insn.mnemonic, insn.op_str) for insn in _DISASM.disasm(bytes(blob), 0)]


def unreachable(compiled, target):
    """Why no source reordering can close this body, or None.

    When every instruction already has retail's mnemonic and registers and
    only numbers differ (displacements, immediates), the gap is a layout,
    offset or constant fact: mutations only move statements and operators."""
    try:
        ours, theirs = _instructions(compiled), _instructions(target)
    except Exception:
        return None
    if not ours:
        return None
    if len(ours) != len(theirs) or [m for m, _ in ours] != [m for m, _ in theirs]:
        # Many instructions present on one side only: the source does
        # something else (a type, a check, an inlined helper), which moving
        # statements cannot supply. The bound is set from history: the
        # loosest past win started with 9 of 42 differing; this skips 8 of
        # 120 failed bodies.
        matcher = difflib.SequenceMatcher(None, [m for m, _ in ours], [m for m, _ in theirs],
                                          autojunk=False)
        differ = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in matcher.get_opcodes()
                     if tag != "equal")
        if differ > max(10, len(theirs) // 4):
            return (f"structural: {differ} of {len(theirs)} instruction(s) differ; "
                    "needs reconstruction, not reordering")
        return None
    strip = lambda op: re.sub(r"0x[0-9a-f]+|\b\d+\b", "#", op)
    differing = [(a, b) for (_, a), (_, b) in zip(ours, theirs) if a != b]
    if differing and all(strip(a) == strip(b) for a, b in differing):
        return f"only constants or offsets differ ({len(differing)} instruction(s)): a layout fact, not an order"
    return None


def fitness(compiled, target):
    """0..1 closeness of two bodies (exact is checked separately).

    A byte ratio is nearly flat across the changes a mutation causes: a
    register swap or a reordered pair rewrites many bytes. Instruction
    alignment sees them: the mnemonic sequence carries most of the weight,
    full instructions (operands) refine it, the byte ratio breaks ties."""
    ratio = lambda a, b: difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    try:
        ours, theirs = _instructions(compiled), _instructions(target)
    except Exception:  # no capstone: bytes alone, as before
        return ratio(compiled, target)
    if not ours or not theirs:
        return ratio(compiled, target)
    return (0.5 * ratio([m for m, _ in ours], [m for m, _ in theirs])
            + 0.3 * ratio(ours, theirs)
            + 0.2 * ratio(compiled, target))


# ----------------------------------------------------------------- mutations

BODY_START = re.compile(r"^[^\s#/][^;{}]*\)\s*(?:const\s*)?\{?\s*$")
CMP = re.compile(r"(\b[\w.\->\[\]]+)\s*(<=|>=|<|>)\s*([\w.\->\[\]]+\b)")
EQ = re.compile(r"(\b[\w.\->\[\]]+)\s*(==|!=)\s*([\w.\->\[\]]+\b)")
COMMUTE = re.compile(r"(\b[A-Za-z_][\w.\->\[\]]*)\s*([+*&|^])\s*([A-Za-z_][\w.\->\[\]]*\b)(?!\s*[(\[])")
MIRROR = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}
SIGNS = [("unsigned int ", "int "), ("unsigned char ", "char "), ("unsigned short ", "short "),
         ("unsigned long ", "long ")]
FLAG_SWAPS = [("/O1", "/O2"), ("/O2", "/O1"), ("/O2", "/Ox"), ("/Ox", "/O2"), ("/Ob2", "/Ob1"),
              ("/Ob1", "/Ob2"), ("/G6", "/G7"), ("/G7", "/G6")]
# flags toggled on or off: x87 store/reload order (/Op), frame pointer (/Oy-)
FLAG_TOGGLES = ["/Op", "/Oy-"]


_NOT_DEFINITION = re.compile(r"\b(?:class|struct|union|enum|namespace|typedef)\b")
_STATEMENT_HEAD = ("return", "if", "while", "for", "switch", "else", "do", "sizeof", "delete", "throw")


def _code_of(line):
    return line.split("//")[0]


def _definitions(lines):
    """(header, brace, end) line indexes of every function definition: `header`
    is where the name is, `brace` the line with the opening brace (the same
    line for a one-line definition, further down after a constructor
    initializer list or a split signature), `end` the line closing it. Found by
    counting braces, so indentation, one-line bodies, initializer lists and
    several functions per file do not matter."""
    found, i = [], 0
    while i < len(lines):
        line = _code_of(lines[i])
        stripped = line.strip()
        if stripped.startswith("#") or lines[i].rstrip().endswith("\\"):
            while lines[i].rstrip().endswith("\\") and i + 1 < len(lines):
                i += 1  # a macro definition, continuation lines included
            i += 1
            continue
        if (not stripped or stripped.startswith(("#", "{", "}", "/*", "*")) or "(" not in line
                or _NOT_DEFINITION.search(line)):
            i += 1
            continue
        head = line.split("(")[0]
        if ("=" in head or "." in head or "->" in head
                or re.match(rf"(?:{'|'.join(_STATEMENT_HEAD)})\b", head.strip())):
            i += 1
            continue
        brace = i
        while brace < len(lines) and "{" not in _code_of(lines[brace]) and brace < i + 25:
            if _code_of(lines[brace]).rstrip().endswith(";"):
                brace = len(lines)  # a declaration or call, not a definition
            else:
                brace += 1
        if brace >= len(lines) or "{" not in _code_of(lines[brace]):
            i += 1
            continue
        depth, end = 0, None
        for k in range(i, len(lines)):
            for ch in _code_of(lines[k]):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
            if k >= brace and depth <= 0:
                end = k
                break
        if end is None:
            i += 1
            continue
        found.append((i, brace, end))
        i = end + 1
    return found


def _initializer_start(lines, header, brace):
    """Line where a constructor initializer list (`) : m_a(a), ...`) starts
    before the opening brace, or None: a split signature's tail is not code
    worth mutating."""
    depth, seen = 0, False
    for k in range(header, brace + 1):
        code = _code_of(lines[k])
        for pos, ch in enumerate(code):
            if ch == "(":
                depth, seen = depth + 1, True
            elif ch == ")":
                depth -= 1
            elif ch == "{" and seen and depth == 0:
                return None
            elif ch == ":" and seen and depth == 0 and code[pos - 1:pos + 1] != "::" and code[pos:pos + 2] != "::":
                return k
    return None


def body_lines(lines, focus=None):
    """Indexes of lines inside function bodies (between a definition's braces,
    constructor initializer lists included); with `focus` (a regex for the
    target's name), only the target's body, so mutations never spend trials on
    the unit's other functions. Falls back to every body when the target's
    definition cannot be found."""
    out = []
    for header, brace, end in _definitions(lines):
        if focus is not None and not re.search(focus, "\n".join(_code_of(l) for l in lines[header:brace + 1])):
            continue
        first = _initializer_start(lines, header, brace)
        if first is not None:
            out.extend(k for k in range(max(first, header + 1), brace) if lines[k].strip())
        for k in range(brace, end + 1):
            stripped = lines[k].strip()
            if stripped and not stripped.startswith(("//", "#", "}")) and stripped != "{":
                out.append(k)  # `{ stmt; }` on one line is a statement
    out = sorted(set(out))
    if focus is not None and not out:
        return body_lines(lines)
    return out


def focus_of(symbol):
    """Regex for the definition line of the function a mangled name denotes."""
    ctor = re.match(r"\?\?([01])(\w+)@", symbol or "")
    if ctor:
        name = re.escape(ctor.group(2))
        return rf"\b{name}\s*::\s*{'~' if ctor.group(1) == '1' else ''}{name}\s*\("
    found = re.match(r"\?(\w+)@(?:(\w+)@@)?", symbol or "")
    if not found or symbol.startswith("??"):
        return None  # operators: keep every body
    name = rf"\b{found.group(2)}\s*::\s*{found.group(1)}\s*\(" if found.group(2) else rf"\b{found.group(1)}\s*\("
    return name


def statement(line):
    s = line.strip()
    return s.endswith(";") and not re.match(r"(return|break|continue|goto|case|default)\b", s)


WIDTHS = [("int", "long"), ("unsigned int", "unsigned long"), ("char", "bool"),
          ("unsigned char", "bool"), ("short", "unsigned short"), ("int", "unsigned int")]
SIMPLE_RETURN = re.compile(r"^(?:static\s+|inline\s+)*((?:unsigned\s+|signed\s+|const\s+)*"
                           r"(?:int|long|short|char|bool|float|double|DWORD|BOOL|Bool|Int|UnsignedInt|Real))\s+[\w:~]+\s*\(")


def _return_type(lines, i):
    """The simple return type of the function enclosing line i, or None."""
    for header, _brace, end in _definitions(lines):
        if header <= i <= end:
            found = SIMPLE_RETURN.match(lines[header].strip())
            return found.group(1) if found else None
    return None


def mutate(text, rng, focus=None):
    lines = text.split("\n")
    body = body_lines(lines, focus)
    kinds = ["swap", "swap", "cmp", "eq", "commute", "incr", "sign", "flag", "move", "ifelse",
             "const", "forwhile", "width", "compound", "not", "temp"]
    body_set = set(body)

    def indent(line):
        return len(line) - len(line.lstrip())

    for _ in range(12):
        kind = rng.choice(kinds)
        if kind == "swap" and len(body) > 1:
            # swap two statements of one block up to 3 lines apart
            i = rng.choice(body[:-1])
            j = i + rng.choice((1, 1, 2, 3))
            if j in body_set and statement(lines[i]) and statement(lines[j]) and \
                    indent(lines[i]) == indent(lines[j]) and \
                    all(k in body_set and indent(lines[k]) >= indent(lines[i]) and "{" not in lines[k]
                        and "}" not in lines[k] for k in range(i, j + 1)):
                lines[i], lines[j] = lines[j], lines[i]
                return "\n".join(lines), kind
        elif kind == "move" and len(body) > 1:
            # move one statement (often a local declaration) up or down one line
            i = rng.choice(body)
            j = i + rng.choice((-1, 1))
            if j in body_set and statement(lines[i]) and indent(lines[i]) == indent(lines[j]) and \
                    "{" not in lines[j] and "}" not in lines[j]:
                line = lines.pop(i)
                lines.insert(j, line)
                return "\n".join(lines), kind
        elif kind == "const" and body:
            # toggle const on a local declaration with an initializer
            i = rng.choice(body)
            found = re.match(r"^(\s*)(const\s+)?([A-Za-z_][\w:<>]*(?:\s+[A-Za-z_]\w*)*\s*\**\s*[A-Za-z_]\w*\s*=[^=].*;)\s*$",
                             lines[i])
            if found and not re.match(r"\s*(return|delete|throw)\b", lines[i]):
                lines[i] = found.group(1) + ("" if found.group(2) else "const ") + found.group(3)
                return "\n".join(lines), kind
        elif kind == "forwhile" and body:
            # for (init; cond; step) { B }  ->  init; while (cond) { B step; }
            i = rng.choice(body)
            found = re.match(r"^(\s*)for \(([^;]*);([^;]*);([^)]*)\)\s*$", lines[i])
            if found and i + 1 < len(lines) and lines[i + 1].strip() == "{":
                pad, init, cond, step = found.group(1), found.group(2).strip(), found.group(3).strip(), found.group(4).strip()
                depth, k = 0, i + 1
                while k < len(lines):
                    depth += lines[k].count("{") - lines[k].count("}")
                    if depth == 0:
                        break
                    k += 1
                inner = lines[i + 2:k]
                if k < len(lines) and cond and step and not any(re.search(r"\bcontinue\b", l) for l in inner):
                    head = ([f"{pad}{init};"] if init else []) + [f"{pad}while ({cond})", f"{pad}{{"]
                    lines[i:k + 1] = head + inner + [f"{pad}\t{step};", f"{pad}}}"]
                    return "\n".join(lines), kind
        elif kind == "ifelse" and body:
            # if (c) { A } else { B }  ->  if (!(c)) { B } else { A }, braces on own lines
            i = rng.choice(body)
            found = re.match(r"^(\s*)if \((.*)\)\s*$", lines[i])
            if found and i + 1 < len(lines) and lines[i + 1].strip() == "{":
                pad = found.group(1)
                depth, k = 0, i + 1
                while k < len(lines):
                    depth += lines[k].count("{") - lines[k].count("}")
                    if depth == 0:
                        break
                    k += 1
                if k + 2 < len(lines) and lines[k + 1].strip() == "else" and lines[k + 2].strip() == "{":
                    depth, m = 0, k + 2
                    while m < len(lines):
                        depth += lines[m].count("{") - lines[m].count("}")
                        if depth == 0:
                            break
                        m += 1
                    if m < len(lines):
                        then_block, else_block = lines[i + 1:k + 1], lines[k + 2:m + 1]
                        lines[i:m + 1] = ([f"{pad}if (!({found.group(2)}))"] + else_block +
                                          [f"{pad}else"] + then_block)
                        return "\n".join(lines), kind
        elif kind in ("cmp", "eq", "commute", "incr", "sign") and body:
            i = rng.choice(body)
            line = lines[i]
            if kind == "cmp":
                new = CMP.sub(lambda m: f"{m.group(3)} {MIRROR[m.group(2)]} {m.group(1)}", line, count=1)
            elif kind == "eq":
                new = EQ.sub(lambda m: f"{m.group(3)} {m.group(2)} {m.group(1)}", line, count=1)
            elif kind == "commute":
                new = COMMUTE.sub(lambda m: f"{m.group(3)} {m.group(2)} {m.group(1)}", line, count=1)
            elif kind == "incr":
                new = re.sub(r"\b(\w+)\+\+", r"++\1", line, count=1)
                if new == line:
                    new = re.sub(r"\+\+(\w+)\b", r"\1++", line, count=1)
                if new == line:
                    new = re.sub(r"\b(\w+)\s*\+=\s*1\s*;", r"++\1;", line, count=1)
            else:
                new = line
                for a, b in rng.sample(SIGNS, len(SIGNS)):
                    if re.match(rf"\s*{re.escape(a)}\w", line):
                        new = line.replace(a, b, 1)
                        break
                    if re.match(rf"\s*{re.escape(b)}\w", line):
                        new = line.replace(b, a, 1)
                        break
            if new != line:
                lines[i] = new
                return "\n".join(lines), kind
        elif kind == "width" and body:
            # same-size spellings MSVC 7.1 can treat differently in register
            # allocation and frame layout (exactness is the only judge)
            i = rng.choice(body)
            line = lines[i]
            for a, b in rng.sample(WIDTHS, len(WIDTHS)):
                for x, y in ((a, b), (b, a)):
                    new = re.sub(rf"^(\s*(?:const\s+)?){x}\b(?=\s+[\w*&])", rf"\g<1>{y}", line, count=1)
                    if new != line:
                        lines[i] = new
                        return "\n".join(lines), kind
        elif kind == "compound" and body:
            i = rng.choice(body)
            line = lines[i]
            new = re.sub(r"^(\s*)([\w.\->\[\]]+)\s*([-+*/|&^])=\s*(.+);", r"\1\2 = \2 \3 (\4);", line, count=1)
            if new == line:
                new = re.sub(r"^(\s*)([\w.\->\[\]]+)\s*=\s*\2\s*([-+*/|&^])\s*\(?([^;()]+)\)?;",
                             r"\1\2 \3= \4;", line, count=1)
            if new != line:
                lines[i] = new
                return "\n".join(lines), kind
        elif kind == "not" and body:
            i = rng.choice(body)
            line = lines[i]
            new = re.sub(r"!\s*([A-Za-z_][\w.\->]*)\b(?!\s*\()", r"(\1 == 0)", line, count=1)
            if new == line:
                new = re.sub(r"\(([A-Za-z_][\w.\->]*) == 0\)", r"!\1", line, count=1)
            if new != line:
                lines[i] = new
                return "\n".join(lines), kind
        elif kind == "temp" and body:
            i = rng.choice(body)
            decl = re.match(r"^(\s*)[\w:<>\s*&]+?\s+\**(\w+)\s*=\s*([^;]+);\s*$", lines[i])
            if decl and i + 1 < len(lines) and re.match(rf"^\s*return\s+{decl.group(2)}\s*;", lines[i + 1]):
                lines[i:i + 2] = [f"{decl.group(1)}return {decl.group(3)};"]
                return "\n".join(lines), kind
            ret = re.match(r"^(\s*)return\s+([^;]+[-+*/&|^<>?][^;]*);\s*$", lines[i])
            rtype = _return_type(lines, i)
            if ret and rtype:
                lines[i:i + 1] = [f"{ret.group(1)}{rtype} result = {ret.group(2)};", f"{ret.group(1)}return result;"]
                return "\n".join(lines), kind
        elif kind == "flag":
            for k, line in enumerate(lines[:12]):
                if line.startswith("// cl:"):
                    words = line.split()
                    if rng.random() < 0.4:
                        flag = rng.choice(FLAG_TOGGLES)
                        words = [w for w in words if w != flag] if flag in words else words + [flag]
                        lines[k] = " ".join(words)
                        return "\n".join(lines), kind
                    a, b = rng.choice(FLAG_SWAPS)
                    if a in words:
                        lines[k] = " ".join(b if w == a else w for w in words)
                        return "\n".join(lines), kind
    return text, None


# ----------------------------------------------------------------- search

def permute(rva, minutes=10.0, seed=None):
    rva = rva.lower()
    path = ATTEMPTS / f"{rva}.cpp"
    try:
        text = path.read_text(encoding="latin-1", errors="replace")
    except FileNotFoundError:
        # landed elsewhere (an upstream merge or another agent) mid-batch
        return {"rva": rva, "error": "banked attempt gone: closed elsewhere"}
    symbol = re.match(r"//\s*(\S+)", text).group(1)
    size = attempt_sizes().get((symbol, rva))
    if not size:
        return {"rva": rva, "error": "no size in re_attempts.log"}
    workdir = OUT / rva
    workdir.mkdir(parents=True, exist_ok=True)
    if (workdir / "flags_best.cpp").exists():  # --flags found better codegen flags
        text = (workdir / "flags_best.cpp").read_text(encoding="latin-1", errors="replace")
    scorer = Scorer(rva, symbol, size, workdir)
    rng = random.Random(seed if seed is not None else int(rva, 16))
    best_text = text
    best, exact = scorer.score(text)
    start_score = best
    if best < 0:
        return {"rva": rva, "symbol": symbol, "error": "banked body does not compile here"}
    if scorer.unresolved and best >= 0.999:
        # Bytes already right; a call the symbol map cannot resolve keeps it
        # from counting as exact, and reordering source cannot fix that.
        result = {"rva": rva, "symbol": symbol, "size": size, "start": round(best, 4),
                  "best": round(best, 4), "exact": False, "trials": scorer.trials,
                  "stop": "unresolved calls: pin the callees"}
        with (OUT / "results.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result) + "\n")
        return result
    reason = unreachable(*scorer.last) if scorer.last else None
    if reason:
        result = {"rva": rva, "symbol": symbol, "size": size, "start": round(best, 4),
                  "best": round(best, 4), "exact": False, "trials": scorer.trials, "stop": reason}
        with (OUT / "results.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result) + "\n")
        return result
    deadline = time.time() + minutes * 60
    focus = focus_of(symbol)
    current_text, current = best_text, best
    stale = 0
    since_gain = 0  # trials since the best improved
    stop = "deadline"
    while not exact and time.time() < deadline:
        # Measured over 520 runs: every win came within 567 trials, and a run
        # whose mutations are exhausted only replays cached candidates.
        if scorer.hits > 200:
            stop = "mutations exhausted"
            break
        if since_gain > 600:
            stop = "no gain in 600 trials"
            break
        trials_before = scorer.trials
        candidate = current_text
        for _ in range(rng.choice((1, 1, 2, 3))):
            candidate, _kind = mutate(candidate, rng, focus)
        fitness, exact = scorer.score(candidate)
        if fitness < 0:
            continue
        if fitness > current or (fitness == current and rng.random() < 0.5):
            current_text, current = candidate, fitness
        if fitness > best or exact:
            best_text, best, stale, since_gain = candidate, fitness, 0, 0
        else:
            stale += 1
            since_gain += scorer.trials - trials_before
        if stale > 150:  # restart from the best so far
            current_text, current, stale = best_text, best, 0
    (workdir / "best.cpp").write_text(best_text, encoding="latin-1", errors="replace")
    if exact:
        (workdir / "win.cpp").write_text(best_text, encoding="latin-1", errors="replace")
    result = {"rva": rva, "symbol": symbol, "size": size, "start": round(start_score, 4),
              "best": round(best, 4), "exact": exact, "trials": scorer.trials,
              "stop": "exact" if exact else stop, "v": VERSION}
    with (OUT / "results.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result) + "\n")
    return result


def recheck(rva):
    """Compile a banked attempt unchanged once: headers, pins and ledger fixes
    landed since it was banked can make it exact with no search at all."""
    rva = rva.lower()
    text = (ATTEMPTS / f"{rva}.cpp").read_text(encoding="latin-1", errors="replace")
    found = re.match(r"//\s*(\S+)", text)
    symbol = found.group(1) if found else ""
    size = attempt_sizes().get((symbol, rva))
    if not size:
        return {"rva": rva, "recheck": "no size"}
    workdir = OUT / rva
    workdir.mkdir(parents=True, exist_ok=True)
    fitness, exact = Scorer(rva, symbol, size, workdir).score(text)
    if exact:
        (workdir / "win.cpp").write_text(text, encoding="latin-1", errors="replace")
    return {"rva": rva, "symbol": symbol, "recheck": round(fitness, 4), "exact": exact}


LITERAL = re.compile(r"(?<![\w.])(0[xX][0-9A-Fa-f]+|\d+)(?![\w.])")
COMMENT_OR_STRING = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', re.S)


def _offset_deltas(compiled, target):
    """Retail number minus ours, for each number that differs between two
    instruction streams of the same shape (the `unreachable` case)."""
    deltas = set()
    for (_, ours), (_, theirs) in zip(_instructions(compiled), _instructions(target)):
        if ours == theirs:
            continue
        a = re.findall(r"0x[0-9a-f]+|\b\d+\b", ours)
        b = re.findall(r"0x[0-9a-f]+|\b\d+\b", theirs)
        for x, y in zip(a, b):
            d = int(y, 0) - int(x, 0)
            if d and abs(d) < 0x10000:
                deltas.add(d)
    return sorted(deltas, key=abs)


def _literal_sites(text):
    """(start, end, value, is_hex) of integer literals outside comments and strings."""
    masked = list(text)
    for found in COMMENT_OR_STRING.finditer(text):
        masked[found.start():found.end()] = " " * (found.end() - found.start())
    masked = "".join(masked)
    return [(m.start(), m.end(), _c_integer(m.group(1)), m.group(1).lower().startswith("0x"))
            for m in LITERAL.finditer(masked)]


def _c_integer(literal):
    """A C integer literal's value: a leading 0 makes it octal ("01", "0777"),
    which int(_, 0) refuses."""
    if literal.lower().startswith("0x"):
        return int(literal, 16)
    if len(literal) > 1 and literal.startswith("0"):
        try:
            return int(literal, 8)
        except ValueError:  # "08": not valid C either; keep its decimal reading
            return int(literal, 10)
    return int(literal, 10)


LOCAL_DECL = re.compile(r"^\s*(?:const\s+|unsigned\s+|signed\s+|struct\s+|class\s+)*[A-Za-z_][\w:<>,\s]*?[\s*&]+"
                        r"[A-Za-z_]\w*\s*(?:\[[^\]]*\])?\s*(?:=[^;]*)?;\s*(?://.*)?$")
NOT_DECL = re.compile(r"^\s*(return|delete|goto|throw|case|else|if|for|while|do|switch)\b")


def _stack_gap(compiled, target):
    """True when the differing instructions are frame-relative ([ebp/esp ...]
    or the prologue's sub esp): a local variable layout fact."""
    for (m1, o1), (m2, o2) in zip(_instructions(compiled), _instructions(target)):
        if (m1, o1) != (m2, o2) and not ("ebp" in o1 or "esp" in o1):
            return False
    return True


def _local_declarations(lines, focus):
    """Indexes of local declaration lines in the target function's body."""
    body = set(body_lines(lines, focus))
    return [i for i in sorted(body) if LOCAL_DECL.match(lines[i]) and not NOT_DECL.match(lines[i])
            and "(" not in lines[i].split("=")[0]]


def stack_search(text, scorer, best, focus, budget):
    """Hill-climb local declaration order: move one declaration to every other
    declaration slot of the same block, keep what scores better. MSVC lays out
    a frame from declaration order and size, so this is the lever a
    frame-offset gap needs; statements are never moved past a use because
    only declaration lines change places."""
    exact = False
    improved = True
    while improved and not exact and scorer.trials < budget:
        improved = False
        lines = text.split("\n")
        decls = _local_declarations(lines, focus)
        for i in decls:
            for j in decls:
                if i == j or scorer.trials >= budget:
                    continue
                indent = lambda k: len(lines[k]) - len(lines[k].lstrip())
                if indent(i) != indent(j):
                    continue
                moved = lines[:]
                line = moved.pop(i)
                moved.insert(j if j < i else j, line)
                candidate = "\n".join(moved)
                fitness, exact = scorer.score(candidate)
                if exact or fitness > best:
                    text, best, improved = candidate, fitness, True
                    break
            if improved or exact:
                break
    return text, best, exact


def offset_search(rva, budget=400):
    """Close a body whose only gap is numbers (offsets, pads, constants): apply
    each retail-minus-ours delta to each integer literal in the source, keep
    what scores better, repeat until exact or the budget is spent. The
    compiler, not the search, decides: only a byte-exact compile is a win."""
    rva = rva.lower()
    try:
        text = (ATTEMPTS / f"{rva}.cpp").read_text(encoding="latin-1", errors="replace")
    except FileNotFoundError:
        return {"rva": rva, "error": "banked attempt gone: closed elsewhere"}
    found = re.match(r"//\s*(\S+)", text)
    symbol = found.group(1) if found else ""
    size = attempt_sizes().get((symbol, rva))
    if not size:
        return {"rva": rva, "error": "no size in re_attempts.log"}
    workdir = OUT / rva
    workdir.mkdir(parents=True, exist_ok=True)
    scorer = Scorer(rva, symbol, size, workdir)
    best, exact = scorer.score(text)
    start = best
    if best < 0:
        return {"rva": rva, "symbol": symbol, "error": "banked body does not compile here"}
    if not exact and not (scorer.last and unreachable(*scorer.last)):
        return {"rva": rva, "symbol": symbol, "skip": "not an offset-only gap", "start": round(start, 4)}
    if _stack_gap(*scorer.last):
        text, best, exact = stack_search(text, scorer, best, focus_of(symbol), budget // 2)
    improved = True
    while not exact and improved and scorer.trials < budget and scorer.last:
        improved = False
        deltas = _offset_deltas(*scorer.last)
        for begin, end, value, is_hex in _literal_sites(text):
            for delta in deltas:
                if value + delta < 0 or scorer.trials >= budget:
                    continue
                new = value + delta
                candidate = text[:begin] + (hex(new).upper().replace("0X", "0x") if is_hex else str(new)) + text[end:]
                fitness, exact = scorer.score(candidate)
                if exact or fitness > best:
                    text, best, improved = candidate, fitness, True
                    break
            if improved or exact:
                break
    if exact:
        (workdir / "win.cpp").write_text(text, encoding="latin-1", errors="replace")
    result = {"rva": rva, "symbol": symbol, "size": size, "start": round(start, 4), "best": round(best, 4),
              "exact": exact, "trials": scorer.trials, "mode": "offsets"}
    with (OUT / "offsets.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result) + "\n")
    return result


# Codegen flags a sibling unit is known to need, each with the flags it
# replaces. Agents found tactic units that match only under /G7 (imul for
# x*5) while the body was otherwise right.
FLAG_CHOICES = [("/G7", ("/G6", "/G5")), ("/G6", ("/G7", "/G5")), ("/O1", ("/O2", "/Ox")),
                ("/O2", ("/O1", "/Ox")), ("/Ob1", ("/Ob2",)), ("/Op", ()), ("/Oy-", ()),
                ("/GX-", ("/EHsc", "/GX"))]


def _with_flags(text, add, remove=()):
    """`text` with `add` on its `// cl:` line (one is inserted when absent) and
    `remove` taken off; None when nothing would change."""
    lines = text.split("\n")
    at = next((k for k, line in enumerate(lines[:12]) if line.startswith("// cl:")), None)
    words = lines[at].split()[2:] if at is not None else []
    if add in words and not any(w in words for w in remove):
        return None
    words = [w for w in words if w not in remove and w != add] + [add]
    line = "// cl: " + " ".join(words)
    if at is None:
        lines.insert(1, line)  # line 0 names the symbol
    else:
        lines[at] = line
    return "\n".join(lines)


def _flag_variants(text):
    for add, remove in FLAG_CHOICES:
        variant = _with_flags(text, add, remove)
        if variant is not None:
            yield variant
    lines = text.split("\n")
    for k, line in enumerate(lines[:12]):  # dropping a toggle already present
        if line.startswith("// cl:"):
            for flag in ("/Op", "/Oy-", "/Ob1"):
                if flag in line.split():
                    yield "\n".join(lines[:k] + [" ".join(w for w in line.split() if w != flag)]
                                     + lines[k + 1:])


def flag_search(rva, rounds=2):
    """Try each codegen flag change on a banked body, keep the best, and go
    one round deeper from it: a few compiles per body, so it can sweep every
    banked attempt. Only a byte-exact compile is a win."""
    rva = rva.lower()
    try:
        text = (ATTEMPTS / f"{rva}.cpp").read_text(encoding="latin-1", errors="replace")
    except FileNotFoundError:
        return {"rva": rva, "error": "banked attempt gone: closed elsewhere"}
    found = re.match(r"//\s*(\S+)", text)
    symbol = found.group(1) if found else ""
    size = attempt_sizes().get((symbol, rva))
    if not size:
        return {"rva": rva, "error": "no size in re_attempts.log"}
    workdir = OUT / rva
    workdir.mkdir(parents=True, exist_ok=True)
    scorer = Scorer(rva, symbol, size, workdir)
    best, exact = scorer.score(text)
    start = best
    if best < 0:
        return {"rva": rva, "symbol": symbol, "error": "banked body does not compile here"}
    for _ in range(rounds):
        if exact:
            break
        round_best = None
        for candidate in _flag_variants(text):
            fitness, exact = scorer.score(candidate)
            if exact:
                text, best = candidate, fitness
                break
            if fitness > best and (round_best is None or fitness > round_best[1]):
                round_best = (candidate, fitness)
        if exact or round_best is None:
            break
        text, best = round_best
    if exact:
        (workdir / "win.cpp").write_text(text, encoding="latin-1", errors="replace")
    result = {"rva": rva, "symbol": symbol, "size": size, "start": round(start, 4), "best": round(best, 4),
              "exact": exact, "trials": scorer.trials, "mode": "flags"}
    if best > start and not exact:
        result["flags"] = next((l for l in text.split("\n")[:12] if l.startswith("// cl:")), "")
        # the random search starts from here (permute reads it)
        (workdir / "flags_best.cpp").write_text(text, encoding="latin-1", errors="replace")
    with (OUT / "flags.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result) + "\n")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("rvas", nargs="*")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--top", type=int, default=0)
    parser.add_argument("--retry", action="store_true",
                        help="with --next: re-run bodies an older search version failed on, best measured score first")
    parser.add_argument("--next", type=int, default=0,
                        help="run the next N untried banked bodies no other agent has claimed, claiming them")
    parser.add_argument("--min-score", type=float, default=0.9)
    parser.add_argument("--minutes", type=float, default=10.0)
    parser.add_argument("--jobs", type=int, default=int(os.environ.get("BUILD_POOL", "1") or 1))
    parser.add_argument("--flags", action="store_true",
                        help="sweep codegen flag changes (/G7, /O1, /Op, ...) over banked attempts not swept yet")
    parser.add_argument("--offsets", action="store_true",
                        help="offset search on bodies the triage found differ only in numbers (or the RVAs given)")
    parser.add_argument("--all", action="store_true",
                        help="with --offsets: every banked attempt (one compile each to find the offset-only ones)")
    parser.add_argument("--recheck", action="store_true",
                        help="compile every banked attempt (any score) unchanged once; exact ones become wins")
    args = parser.parse_args(argv)
    if args.flags:
        rvas = args.rvas
        if not rvas:
            done = set()
            if (OUT / "flags.jsonl").exists():
                done = {json.loads(l)["rva"] for l in (OUT / "flags.jsonl").read_text().splitlines() if l.strip()}
            rvas = [rva for _, _, rva, _ in queue(0.0) if rva not in done]
        wins = 0
        with concurrent.futures.ProcessPoolExecutor(max(1, args.jobs)) as pool:
            for result in pool.map(flag_search, rvas):
                wins += bool(result.get("exact"))
                if result.get("exact") or "flags" in result:
                    print(json.dumps(result), flush=True)
        print(f"permute: flag sweep closed {wins} of {len(rvas)}")
        return 0
    if args.offsets:
        # bodies the triage marked as a layout fact, or the RVAs given
        rvas = args.rvas
        if not rvas and args.all:
            rvas = [rva for _, _, rva, _ in queue(0.0)]
        elif not rvas and (OUT / "results.jsonl").exists():
            seen = set()
            for line in (OUT / "results.jsonl").read_text().splitlines():
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if str(entry.get("stop", "")).startswith("only constants or offsets differ"):
                    seen.add(entry["rva"])
            done = set()
            if (OUT / "offsets.jsonl").exists():
                done = {json.loads(l)["rva"] for l in (OUT / "offsets.jsonl").read_text().splitlines() if l.strip()}
            rvas = sorted(seen - done)
        wins = 0
        with concurrent.futures.ProcessPoolExecutor(max(1, args.jobs)) as pool:
            for result in pool.map(offset_search, rvas):
                wins += bool(result.get("exact"))
                if "skip" not in result:
                    print(json.dumps(result), flush=True)
        print(f"permute: offset search closed {wins} of {len(rvas)}")
        return 0
    if args.recheck:
        rvas = [rva for _, _, rva, _ in queue(0.0)]
        hits = 0
        with concurrent.futures.ProcessPoolExecutor(max(1, args.jobs)) as pool:
            for result in pool.map(recheck, rvas, chunksize=4):
                if result.get("exact"):
                    hits += 1
                    print(f"EXACT {result['rva']} {result['symbol']}", flush=True)
        print(f"permute: recheck found {hits} banked attempt(s) already exact of {len(rvas)}")
        return 0
    items = queue(args.min_score)
    if args.list:
        for score, size, rva, symbol in items:
            print(f"{score:.2f} {size:6d} {rva} {symbol}")
            note = wb_note(rva)
            if note:
                print(f"     {note}")
        print(f"{len(items)} banked attempt(s) at score >= {args.min_score}")
        return 0
    claimed = []
    if args.next:
        # Several agents may run the closer on this fork: take the next
        # untried bodies nobody holds, and claim them before starting.
        import claims
        tried, last = set(), {}
        if (OUT / "results.jsonl").exists():
            for line in (OUT / "results.jsonl").read_text().splitlines():
                try:
                    entry = json.loads(line)
                    tried.add(entry["rva"].lower())
                    last[entry["rva"].lower()] = entry
                except (ValueError, KeyError):
                    pass
        busy = set(claims.active())          # Open-BFME-1: every live claim, ours too
        if args.retry:
            # Bodies an older search failed on, best measured score first:
            # the measured start ranks them better than the banked score.
            live = {rva for _, _, rva, _ in items}
            again = [e for rva, e in last.items()
                     if rva in live and not e.get("exact") and e.get("v", 1) < VERSION
                     and "best" in e and not str(e.get("stop", "")).startswith(("only constants", "unresolved"))]
            again.sort(key=lambda e: -e["best"] * (e.get("size") or 0))
            wanted = [e["rva"] for e in again if int(e["rva"], 16) not in busy][:args.next]
        else:
            wanted = [rva for _, _, rva, _ in items
                      if rva not in tried and int(rva, 16) not in busy][:args.next]
        try:
            got, _refused = claims.claim([int(rva, 16) for rva in wanted], note="permute")
            claimed = rvas = [f"0x{rva:08x}" for rva in got]
        except claims.ClaimsUnavailable as error:
            # Open-BFME-1's claims fail closed: run only what origin accepted
            print(f"permute: {error}; running only the bodies claimed before the failure", file=sys.stderr)
            claimed = rvas = [f"0x{rva:08x}" for rva in error.claimed]
    else:
        rvas = args.rvas or [rva for _, _, rva, _ in items[:args.top]]
    if not rvas:
        parser.error("give RVAs, --top N or --next N (nothing untried and unclaimed left)")
    OUT.mkdir(parents=True, exist_ok=True)
    wins, won = 0, set()
    try:
        with concurrent.futures.ProcessPoolExecutor(max(1, args.jobs)) as pool:
            for result in pool.map(permute, rvas, [args.minutes] * len(rvas)):
                wins += bool(result.get("exact"))
                if result.get("exact"):
                    won.add(result["rva"])
                note = wb_note(result.get("rva"))
                if note:
                    result["wb"] = note
                print(json.dumps(result), flush=True)
    finally:
        if claimed:
            import claims
            # Every claim but a win's is released, even if the batch died;
            # a win stays claimed for the hand landing (add_match, then
            # `claims.py release --landed`) or `claims.py release`.
            claims.release([int(rva, 16) for rva in claimed if rva not in won])
    print(f"permute: {wins} of {len(rvas)} closed exactly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
