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
# build is imported where it is used: is_view and ABI_VIEW_RE are read by
# light tools (name_regression, brief, callers_of) that must not pay for it.

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
    or a void view over an EAX value. A register aggregate (EAX or EDX:EAX,
    size unknown) agrees only with another; "?" (extern "C" names) carries no
    return information and agrees."""
    if "?" in (view, canonical) or view == canonical:
        return True
    return view == "v" and canonical == "i"


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
    """The retail image, the function ledger and the pins, loaded once."""

    def __init__(self, rows=None, data=None, sections=None, pins=None):
        import build
        self.data = build.EXE.read_bytes() if data is None else data
        self.sections = build.pe_sections(self.data) if sections is None else sections
        text = next(s for s in self.sections if s["name"] == ".text")
        self.low, self.high = text["rva"], text["rva"] + text["size"]
        self.rows = build.load_all_function_rows() if rows is None else rows
        self.at, self.row_names = {}, set()
        for row in self.rows:
            self.row_names.add(row["name"])
            try:
                self.at.setdefault(int(row["target_rva"], 16), []).append(row)
            except (KeyError, TypeError, ValueError):
                continue
        # {name: [address]} of every symbols.csv pin (views included)
        self.pins = pins if pins is not None else load_pin_addresses()

    def bytes_at(self, rva, size):
        import build
        try:
            offset = build.rva_to_file_offset(self.sections, rva)
        except (ValueError, KeyError):
            return b""
        return self.data[offset:offset + size]

    def names_identity_at(self, rva):
        import pin_consistency
        return any(pin_consistency.names_identity(r) and not r["name"].startswith("?j_")
                   for r in self.at.get(rva, ()))

    def resolve_one(self, rva):
        """The next address of an `E9` jump stub, or None: not past a matched
        row longer than a stub, nor past an address a row names as a function
        (a tail-jumping body is a function, not a stub)."""
        head = self.bytes_at(rva, 5)
        sized = [int(r["target_size"]) for r in self.at.get(rva, ()) if r.get("status") == "matched"]
        if len(head) < 5 or head[0] != 0xE9 or (sized and max(sized) > 5) or self.names_identity_at(rva):
            return None
        return (rva + 5 + struct.unpack_from("<i", head, 1)[0]) & 0xFFFFFFFF

    def resolve(self, rva):
        """The body an address reaches through `E9` jump stubs, or None on a cycle."""
        cur, seen = rva, {rva}
        for _ in range(MAX_HOPS):
            nxt = self.resolve_one(cur)
            if nxt is None:
                return cur
            if nxt in seen:
                return None
            seen.add(nxt)
            cur = nxt
        return None

    @functools.cached_property
    def raw_calls(self):
        """{target: [site]} for every E8 byte in .text (not yet proven an instruction)."""
        import build
        offset = build.rva_to_file_offset(self.sections, self.low)
        text = self.data[offset:offset + (self.high - self.low)]
        out, at = {}, text.find(b"\xe8")
        while 0 <= at <= len(text) - 5:
            target = (self.low + at + 5 + struct.unpack_from("<i", text, at + 1)[0]) & 0xFFFFFFFF
            out.setdefault(target, []).append(self.low + at)
            at = text.find(b"\xe8", at + 1)
        return out

    @functools.cached_property
    def row_extents(self):
        """Sorted (start, end) of matched rows longer than a stub."""
        out = []
        for start, rows in self.at.items():
            sizes = [int(r["target_size"]) for r in rows if r.get("status") == "matched"]
            if sizes and max(sizes) > 5:
                out.append((start, start + max(sizes)))
        return sorted(out)

    def decoded_call(self, site):
        """True when SITE is a `call rel32` instruction in a linear decode of
        the matched row that contains it (from the row's start)."""
        import bisect
        import capstone
        k = bisect.bisect_right(self.row_extents, (site, 1 << 32)) - 1
        if k < 0 or not self.row_extents[k][0] <= site < self.row_extents[k][1]:
            return False
        start, end = self.row_extents[k]
        disassembler = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        for ins in disassembler.disasm(self.bytes_at(start, end - start), start):
            if ins.address == site:
                return ins.mnemonic == "call" and ins.size == 5
            if ins.address > site:
                return False
        return False

    @functools.cached_property
    def call_targets_through(self):
        """{address: {encoded call target}} for every address an encoded
        target's E9 stub chain passes through (the target itself included)."""
        out = {}
        for target in self.raw_calls:
            if not self.low <= target < self.high:
                continue
            cur, seen = target, set()
            for _ in range(MAX_HOPS):
                if cur is None or cur in seen:
                    break
                seen.add(cur)
                out.setdefault(cur, set()).add(target)
                cur = self.resolve_one(cur)
        return out

    def called(self, address):
        """True when a decoded retail `call` encodes ADDRESS, or an E9 stub chain
        that a decoded call encodes passes through ADDRESS."""
        return any(self.decoded_call(site) for target in self.call_targets_through.get(address, ())
                   for site in self.raw_calls[target])


def load_pin_addresses(path=None):
    import build
    out = {}
    with (path or build.SYMBOLS).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle):
            if len(row) > 1 and row[0] != "name":
                try:
                    out.setdefault(row[0], []).append(int(row[1], 16))
                except ValueError:
                    continue
    return out


def qualified_prefix(sym):
    """The decoration up to the end of its qualified name (function name and
    scopes), or None when it cannot be read."""
    try:
        d = Decode(sym)
        if sym.startswith("??$"):
            return sym[:d.qualified(d.template_name(3))]
        if sym.startswith("??"):
            return sym[:d.qualified(4 if sym[2] == "_" else 3)]
        if sym.startswith("?"):
            return sym[:d.qualified(1)]
    except (ValueError, IndexError):
        return None
    return None


def spells_address(name, addresses):
    """True when NAME spells one of ADDRESSES (RVA or VA) as a hex run."""
    wanted = set(addresses) | {a + 0x400000 for a in addresses}
    for run in re.findall(r"[0-9A-Fa-f]{5,}", name):     # maximal hex runs ("a001C86B0")
        for width in range(5, 9):
            if any(int(run[k:k + width], 16) in wanted for k in range(len(run) - width + 1)):
                return True
    return False


def placeholder_canonical(ctx, row):
    """A canonical row whose decoration is no proven ABI: a generated or
    ?dup_ stand-in, or a naked __emit lift (its declaration is free text)."""
    import pin_consistency
    if not pin_consistency.names_identity(row):
        return True
    import progress
    from pathlib import Path as _P
    import build
    source = row.get("source") or ""
    try:
        text = (build.ROOT / source).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if "naked" not in text and "__emit" not in text and "_emit" not in text:
        return False
    key = (row["name"], row["target_rva"])
    return key in progress.naked_cpp_rows({key: (int(row["target_size"]), source)}, {source: text})


def view_verdict(ctx, name, address, canonical):
    """None when the abi-view pin is admissible, else why not."""
    if not ctx.low <= address < ctx.high:
        return f"0x{address:08X} is outside .text, so it is not a call target"
    body = ctx.resolve(address)
    if body is None:
        return f"0x{address:08X} does not resolve to a body (jump-stub cycle)"
    if not ctx.called(address):
        return f"no decoded retail `call` reaches 0x{address:08X} (directly or through its jump stubs)"
    if canonical == name:
        return "abi-view names the pin itself; a view differs from its canonical name"
    # One name, one function: a view name is nobody's ledger name, and every
    # address pinned to it reaches this one body.
    if name in ctx.row_names:
        return f"{name} is a functions.csv row's name: a view may not borrow a ledger identity"
    elsewhere = sorted({hex(a) for a in ctx.pins.get(name, ()) if ctx.resolve(a) != body})
    if elsewhere:
        return f"{name} is also pinned at {', '.join(elsewhere)}, which reach another body"
    matched = [r for r in ctx.at.get(body, ()) if r.get("status") == "matched"]
    rows = [r for r in matched if r["name"] == canonical]
    if not rows:
        owned = sorted({r["name"] for r in matched})
        return (f"0x{address:08X} reaches 0x{body:08X}, which no matched row names {canonical} "
                f"(matched there: {', '.join(owned[:3]) or 'nothing'})")
    # A view's name is not identity evidence, so it may not read like one: it
    # is the canonical function respelt (same qualified name) or it spells the
    # address it views.
    prefix = qualified_prefix(name)
    same_function = prefix is not None and prefix == qualified_prefix(canonical)
    addressed = prefix is not None and spells_address(prefix, (address, body))  # in the name, not a type
    if not (same_function or addressed):
        return (f"{name} names a function the canonical {canonical} does not; a view must be the "
                "canonical's qualified name respelt or spell its address (name-correction candidate)")
    forms_v = signature(name)
    if not forms_v:
        return f"the view's decoration {name} does not decode to a fixed ABI"
    ret = final_ret(ctx.bytes_at(body, int(rows[0]["target_size"])))
    if ret is None:
        return f"the body at 0x{body:08X} does not end in a ret, so its stack cleanup is unknown"
    if placeholder_canonical(ctx, rows[0]):
        # No declared ABI to compare: the body's own cleanup is the only
        # witness, __cdecl leaves none, and the view must spell its address.
        if not addressed:
            return (f"{canonical} declares no proven ABI, so only an address-derived view name may "
                    "stand on the body's cleanup alone")
        if forms_v[0][0] not in CALLEE_CLEANS:
            return (f"{canonical} declares no proven ABI, and a __cdecl view cannot be checked "
                    "against the body's ret 0")
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
    if not callee_cleans and (len(forms_v) > 1) != (len(forms_c) > 1):
        # __cdecl leaves no cleanup to tell a hidden result pointer from a
        # first argument, nor EAX from EDX:EAX: refuse the mixed pair.
        return "a __cdecl aggregate return on one side only is ambiguous without a cleanup witness"
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
    import build
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
    ctx = ctx or Context(pins=load_pin_addresses(path))
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
    import build
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
