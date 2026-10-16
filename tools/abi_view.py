#!/usr/bin/env python3
"""ABI views: a symbols.csv pin that is a compilation view, never an identity.

Approved by the project lead 2026-10-16. Some callers can only be compiled
through a declaration whose decorated name differs from the callee's
canonical ledger name: a typed view of a placeholder body, a class-tag
spelling (`VCoord3D` against `UCoord3D`), an aggregate-return or by-value
argument view. The pin `V,<address>,...;abi-view=<C>;...` says: calls to V
may encode <address>, whose body the ledger names C. It asserts nothing about
what the function is, so no identity check may read it as evidence
(pin_consistency exempts it from one-name-one-body; ilt_guard and the ILT
window generator skip it).

Because a view buys that exemption, it is admitted only when the retail
image proves it (view_verdict):
  (a) retail code calls <address> (an `E8 rel32` site encodes it), and the
      address is the body itself or an `E9` jump-stub chain that reaches it;
  (b) the reached body starts a matched functions.csv row named exactly C, and
      C differs from the view's name;
  (c) the ABI agrees: V and C decode to the same calling convention, the
      body's final `ret` pops what V's parameter list needs (callee-cleaned
      conventions; a by-value aggregate return may add the hidden result
      pointer), and for __cdecl V and C need the same stack bytes; a parameter
      whose by-value size the decoration cannot tell refuses;
  (d) the view's name never counts as identity evidence.

  python3 tools/abi_view.py --check          every abi-view= row, gate exit status
  python3 tools/abi_view.py --migrate        propose abi-view= for legacy view pins
  python3 tools/abi_view.py --migrate --write   ... and write the admissible ones
"""
import argparse
import csv
import functools
import io
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ABI_VIEW_RE = re.compile(r"(?:^|;)\s*abi-view=([^;]+)")
LEGACY_RE = re.compile(r"call view|abi view|aggregate-return view|by-value.*view", re.IGNORECASE)
MAX_HOPS = 16

CALLEE_CLEANS = {"E": "__thiscall", "G": "__stdcall", "I": "__fastcall"}
CONVENTIONS = {"A": "__cdecl", **CALLEE_CLEANS}
STATIC_MEMBER = set("CDKLST")
# Stack-slot kinds: i = one integer/pointer dword, f = float dword, d = double
# (8), q = 64-bit integer (8), v = void, u = by-value aggregate (size unknown).
PRIMITIVE = {"C": "i", "D": "i", "E": "i", "F": "i", "G": "i", "H": "i", "I": "i", "J": "i",
             "K": "i", "M": "f", "N": "d", "O": "d"}
EXTENDED = {"_N": "i", "_J": "q", "_K": "q", "_W": "i", "_D": "i", "_E": "i", "_F": "i",
            "_G": "i", "_H": "i", "_I": "i"}
SLOT_BYTES = {"i": 4, "f": 4, "d": 8, "q": 8}


class Decode:
    """A small MSVC decoration reader: enough to walk a function's qualified
    name (templates and back-references included) and size its parameters."""

    def __init__(self, sym):
        self.s, self.names, self.types = sym, [], []

    def peek(self, i):
        return self.s[i] if i < len(self.s) else ""

    def name_fragment(self, i):
        j = self.s.index("@", i)
        self.names.append(self.s[i:j])
        return j + 1

    def template_name(self, i):
        """`?$name@args@` with its own back-reference scope."""
        outer_names, outer_types = self.names, self.types
        self.names, self.types = [], []
        i = self.name_fragment(i)
        while self.peek(i) != "@":
            i = self.template_arg(i)
        self.names, self.types = outer_names, outer_types
        return i + 1

    def template_arg(self, i):
        if self.s.startswith("$0", i):           # integral constant
            return self.number(i + 2)
        if self.s.startswith("$1", i):           # address of a symbol
            return self.symbol(i + 2)
        if self.s.startswith("$$C", i):
            return self.skip_type(i + 4)
        _size, i = self.type(i)
        return i

    def number(self, i):
        if self.peek(i) == "?":
            i += 1
        if self.peek(i).isdigit():
            return i + 1
        j = self.s.index("@", i)
        return j + 1

    def symbol(self, i):
        raise ValueError("template symbol arguments are not decoded")

    def qualified(self, i):
        """Step over a qualified name up to and including its `@` terminator."""
        while True:
            ch = self.peek(i)
            if ch == "":
                raise ValueError("unterminated qualified name")
            if ch == "@":
                return i + 1
            if ch.isdigit():
                i += 1
                continue
            if self.s.startswith("?$", i):
                i = self.template_name(i + 2)
                continue
            if ch == "?":
                raise ValueError("nested special name component")
            i = self.name_fragment(i)

    def skip_type(self, i):
        _size, i = self.type(i)
        return i

    def type(self, i):
        """(kind, next index) of one encoded type (kinds: SLOT_BYTES, v, u)."""
        ch = self.peek(i)
        start = i
        if ch == "":
            raise ValueError("truncated type")
        if ch.isdigit():                          # parameter back-reference
            if int(ch) >= len(self.types):
                raise ValueError("dangling type back-reference")
            return self.types[int(ch)], i + 1
        if ch == "_":
            code = self.s[i:i + 2]
            if code not in EXTENDED:
                raise ValueError(f"unknown extended type {code}")
            return EXTENDED[code], i + 2
        if ch in "PAQRSB":                        # pointer / reference (cv)
            j = i + 1
            if self.peek(j) == "E":               # __ptr64
                j += 1
            if self.peek(j) in "ABCD":
                j += 1
            elif self.peek(j) in "68":
                raise ValueError("function pointer type")
            return "i", self.skip_type(j)
        if ch in "VUT":
            return "u", self.qualified(i + 1)
        if ch == "W":
            return "i", self.qualified(i + 2)
        if ch == "?":                             # cv-qualified by-value
            if self.peek(i + 1) not in "ABCD":
                raise ValueError("unknown qualified type")
            return self.type(i + 2)
        if ch in PRIMITIVE:
            return PRIMITIVE[ch], i + 1
        if ch == "X":                             # void: a return, or a pointee
            return "v", i + 1
        raise ValueError(f"unknown type code {ch!r} at {start}")

    def param(self, i):
        kind, j = self.type(i)
        if j - i > 1:                             # one-char types are not memoized
            self.types.append(kind)
        return kind, j


def signature(sym):
    """[(convention letter, return class, stack-slot kinds)] for each way the
    decorated function can be laid out, or None when it cannot be decoded with
    certainty. A by-value aggregate return is either a hidden result pointer
    (first stack slot, returned in EAX) or a register return (MSVC decides on
    POD-ness, which the decoration does not say), so it yields both forms. A
    by-value aggregate parameter has no known size and refuses."""
    c_name = re.fullmatch(r"([_@])[A-Za-z_$]\w*@(\d+)", sym)
    if c_name:                                   # extern "C": only the byte count is known
        return [("G" if c_name.group(1) == "_" else "I", "?", ("i",) * (int(c_name.group(2)) // 4))]
    try:
        d = Decode(sym)
        if sym.startswith("??$"):                # function template: ??$name@args@scope@
            i = d.qualified(d.template_name(3))
        elif sym.startswith("??"):               # special member: ??<op><class scope>@
            i = d.qualified(4 if sym[2] == "_" else 3)
        elif sym.startswith("?"):
            i = d.qualified(1)
        else:
            return None
        lead = d.peek(i)
        if lead == "Y" or lead in STATIC_MEMBER:
            conv_at = i + 1
        elif lead in "ABEFIJMNQRUV":             # non-static member: access, this-cv
            conv_at = i + 2
        else:
            return None
        convention = d.peek(conv_at)
        if convention not in CONVENTIONS:
            return None
        i = conv_at + 1
        if re.match(r"\?\?[01]", sym) and d.peek(i) == "@":
            ret, i = "v", i + 1
        elif d.peek(i) == "?" and d.peek(i + 1) == "A":
            ret, i = d.type(i + 2)
        else:
            ret, i = d.type(i)
        slots = []
        registers = 2 if convention == "I" else 0
        if sym[i:i + 2] == "XZ":
            i += 1
        else:
            while d.peek(i) not in ("@", "Z", ""):
                kind, i = d.param(i)
                if kind in ("u", "v"):
                    return None
                if registers and kind == "i":
                    registers -= 1
                    slots.append("r")
                    continue
                slots.append(kind)
        if sym[i:] not in ("@Z", "Z"):
            return None
        slots = tuple(slots)
        if ret == "u":
            return [(convention, "i", ("i",) + slots), (convention, "R", slots)]
        return [(convention, {"q": "q", "f": "f", "d": "f", "v": "v"}.get(ret, "i"), slots)]
    except (ValueError, IndexError, KeyError):
        return None


def stack_bytes(slots):
    return sum(SLOT_BYTES.get(kind, 0) for kind in slots)


def returns_agree(view, canonical):
    """A caller of the view reads what the canonical body leaves: equal classes,
    a void view over any EAX value, or a register aggregate over EAX/EDX:EAX;
    "?" (extern "C" names) carries no return information and agrees."""
    if "?" in (view, canonical) or view == canonical:
        return True
    return (view == "v" and canonical in "iq") or (view == "R" and canonical in "iq") \
        or (canonical == "R" and view in "viq")


def final_ret(body):
    """Bytes the body's last instruction pops, or None when it does not end in a ret."""
    import capstone
    disassembler = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    instructions = list(disassembler.disasm(bytes(body), 0))
    if not instructions or sum(ins.size for ins in instructions) != len(body):
        return None
    tail = instructions[-1]
    if tail.mnemonic != "ret":
        return None
    return 0 if tail.bytes == b"\xc3" else struct.unpack_from("<H", tail.bytes, 1)[0]


class Context:
    """The retail image and the function ledger, loaded once."""

    def __init__(self, rows=None, data=None, sections=None):
        self.data = build.EXE.read_bytes() if data is None else data
        self.sections = build.pe_sections(self.data) if sections is None else sections
        text = next(s for s in self.sections if s["name"] == ".text")
        self.low, self.high = text["rva"], text["rva"] + text["size"]
        self.rows = build.load_all_function_rows() if rows is None else rows
        self.at = {}
        for row in self.rows:
            try:
                self.at.setdefault(int(row["target_rva"], 16), []).append(row)
            except (KeyError, TypeError, ValueError):
                continue

    def bytes_at(self, rva, size):
        try:
            offset = build.rva_to_file_offset(self.sections, rva)
        except (ValueError, KeyError):
            return b""
        return self.data[offset:offset + size]

    @functools.cached_property
    def reached_by_calls(self):
        """Every address a retail call reaches: the encoded target, and each
        address along its `E9` jump-stub chain to the body."""
        out = set()
        for target in self.called:
            cur = target
            for _ in range(MAX_HOPS):
                out.add(cur)
                nxt = self.resolve_one(cur)
                if nxt is None or nxt in out:
                    break
                cur = nxt
        return out

    def resolve_one(self, rva):
        head = self.bytes_at(rva, 5)
        sized = [int(r["target_size"]) for r in self.at.get(rva, ()) if r.get("status") == "matched"]
        if len(head) < 5 or head[0] != 0xE9 or (sized and max(sized) > 5):
            return None
        return (rva + 5 + struct.unpack_from("<i", head, 1)[0]) & 0xFFFFFFFF

    @functools.cached_property
    def called(self):
        """Every RVA an `E8 rel32` in .text encodes."""
        offset = build.rva_to_file_offset(self.sections, self.low)
        text = self.data[offset:offset + (self.high - self.low)]
        out, at = set(), text.find(b"\xe8")
        while 0 <= at <= len(text) - 5:
            out.add((self.low + at + 5 + struct.unpack_from("<i", text, at + 1)[0]) & 0xFFFFFFFF)
            at = text.find(b"\xe8", at + 1)
        return out

    def resolve(self, rva):
        """The body an address reaches through `E9` jump stubs (not past a
        matched row longer than a stub)."""
        cur, seen = rva, {rva}
        for _ in range(MAX_HOPS):
            head = self.bytes_at(cur, 5)
            sized = [int(r["target_size"]) for r in self.at.get(cur, ()) if r.get("status") == "matched"]
            if len(head) < 5 or head[0] != 0xE9 or (sized and max(sized) > 5):
                return cur
            nxt = (cur + 5 + struct.unpack_from("<i", head, 1)[0]) & 0xFFFFFFFF
            if nxt in seen:
                return None
            seen.add(nxt)
            cur = nxt
        return None


def view_verdict(ctx, name, address, canonical):
    """None when the abi-view pin is admissible, else why not."""
    if not ctx.low <= address < ctx.high:
        return f"0x{address:08X} is outside .text, so it is not a call target"
    if address not in ctx.reached_by_calls:
        return f"no retail `call` reaches 0x{address:08X} (directly or through its jump stubs)"
    body = ctx.resolve(address)
    if body is None:
        return f"0x{address:08X} does not resolve to a body (jump-stub cycle)"
    if canonical == name:
        return "abi-view names the pin itself; a view differs from its canonical name"
    matched = [r for r in ctx.at.get(body, ()) if r.get("status") == "matched"]
    if any(r["name"] == name for r in matched):
        return (f"{name} is itself a matched row at 0x{body:08X}: the pin is an identity "
                "(or a route=), not a view")
    rows = [r for r in matched if r["name"] == canonical]
    if not rows:
        owned = sorted({r["name"] for r in matched})
        return (f"0x{address:08X} reaches 0x{body:08X}, which no matched row names {canonical} "
                f"(matched there: {', '.join(owned[:3]) or 'nothing'})")
    forms_v = signature(name)
    if not forms_v:
        return f"the view's decoration {name} does not decode to a fixed ABI"
    ret = final_ret(ctx.bytes_at(body, int(rows[0]["target_size"])))
    if ret is None:
        return f"the body at 0x{body:08X} does not end in a ret, so its stack cleanup is unknown"
    import pin_consistency
    if not pin_consistency.names_identity(rows[0]):
        # A generated or ?dup_ stand-in declares no ABI (its decoration is a
        # placeholder), so the body's own cleanup is the only witness; __cdecl
        # leaves none.
        if forms_v[0][0] not in CALLEE_CLEANS:
            return (f"{canonical} is a placeholder with no declared ABI, and a __cdecl view "
                    "cannot be checked against the body's ret 0")
        if not any(stack_bytes(slots) == ret for _c, _r, slots in forms_v):
            return (f"retail pops {ret} bytes; the view needs "
                    f"{sorted({stack_bytes(slots) for _c, _r, slots in forms_v})}")
        return None
    forms_c = signature(canonical)
    if not forms_c:
        return f"the canonical decoration {canonical} does not decode to a fixed ABI"
    if forms_v[0][0] != forms_c[0][0]:
        return (f"calling conventions differ: view {CONVENTIONS[forms_v[0][0]]}, "
                f"canonical {CONVENTIONS[forms_c[0][0]]}")
    callee_cleans = forms_v[0][0] in CALLEE_CLEANS
    if not callee_cleans and ret != 0:
        return f"a __cdecl body must end in ret 0; retail pops {ret}"
    for _cv, ret_v, slots_v in forms_v:
        for _cc, ret_c, slots_c in forms_c:
            agree = (slots_v == slots_c or "?" in (ret_v, ret_c)
                     and stack_bytes(slots_v) == stack_bytes(slots_c))
            if agree and returns_agree(ret_v, ret_c) and (not callee_cleans or stack_bytes(slots_v) == ret):
                return None
    return (f"no layout of the view {[(r, ''.join(s)) for _c, r, s in forms_v]} matches the canonical "
            f"{[(r, ''.join(s)) for _c, r, s in forms_c]} with retail popping {ret} "
            "(stack slots i=int/pointer f=float d=double q=int64 r=register; return v/i/f/q, R=register aggregate)")


def view_rows(path=None):
    """[(name, address, canonical)] for every abi-view= row of symbols.csv."""
    out = []
    with (path or build.SYMBOLS).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            if not row or row[0] == "name":
                continue
            found = ABI_VIEW_RE.search(",".join(row[2:]))
            if found:
                out.append((row[0], int(row[1], 16), found.group(1).strip()))
    return out


def is_view(notes):
    return bool(ABI_VIEW_RE.search(notes or ""))


def check(ctx=None, path=None):
    """[(name, address, canonical, why)] for every inadmissible abi-view row."""
    rows = view_rows(path)
    if not rows:
        return []
    ctx = ctx or Context()
    return [(n, a, c, why) for n, a, c in rows if (why := view_verdict(ctx, n, a, c))]


def canonical_for(ctx, name, address):
    """(canonical, why) for a legacy view pin: the one matched, identity-naming
    row at the body the address reaches; None with a reason otherwise."""
    import pin_consistency
    body = ctx.resolve(address) if ctx.low <= address < ctx.high else None
    if body is None:
        return None, f"0x{address:08X} is not a .text call target"
    matched = [r for r in ctx.at.get(body, ()) if r.get("status") == "matched"]
    named = sorted({r["name"] for r in matched if pin_consistency.names_identity(r)} - {name})
    if not named:
        # no identity row: the one placeholder row is the canonical spelling
        named = sorted({r["name"] for r in matched} - {name})
    if len(named) != 1:
        return None, (f"0x{body:08X} has {len(named)} candidate canonical rows besides the view "
                      f"({', '.join(named[:3]) or 'none'})")
    return named[0], None


def migrate(write=False, path=None):
    """Tag every legacy view pin that validates with abi-view=<canonical>."""
    path = path or build.SYMBOLS
    ctx = Context()
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    done, refused = [], []
    for index, line in enumerate(lines):
        row = next(csv.reader([line]))
        if len(row) < 3 or row[0] == "name" or is_view(",".join(row[2:])):
            continue
        notes = ",".join(row[2:])
        if not LEGACY_RE.search(notes):
            continue
        name, address = row[0], int(row[1], 16)
        canonical, why = canonical_for(ctx, name, address)
        if canonical is not None:
            why = view_verdict(ctx, name, address, canonical)
        if why:
            refused.append((name, address, why))
            continue
        done.append((name, address, canonical))
        # First in the notes, so a reader that splits the row on commas still sees it.
        head = line[:len(row[0]) + len(row[1]) + 2]
        assert head == f"{row[0]},{row[1]},", "symbols.csv row is not name,address,notes"
        lines[index] = head + f"abi-view={canonical};" + line[len(head):]
    if write and done:
        path.write_text("".join(lines), encoding="utf-8", newline="")
    return done, refused


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--migrate", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    if args.check:
        bad = check()
        for name, address, canonical, why in bad:
            print(f"  {name} 0x{address:08X} abi-view={canonical}\n      {why}")
        print(f"abi_view: {'FAIL' if bad else 'OK'} ({len(view_rows())} abi-view row(s), {len(bad)} inadmissible)")
        return 1 if bad else 0
    done, refused = migrate(write=args.write)
    for name, address, canonical in done:
        print(f"view    {name} 0x{address:08X} abi-view={canonical}")
    for name, address, why in refused:
        print(f"refused {name} 0x{address:08X}: {why}")
    print(f"abi_view: {len(done)} legacy view pin(s) validate, {len(refused)} refused"
          + (" (written)" if args.write and done else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
