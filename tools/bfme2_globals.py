"""Typed global rewrite engine adapted from BFME 2 name_globals.py; no alias creation."""
import re

SCALAR = {"H": "int", "I": "unsigned int", "M": "float", "E": "unsigned char", "D": "char",
          "K": "unsigned long", "J": "long", "F": "short", "G": "unsigned short", "_N": "bool",
          "N": "double", "C": "signed char", "X": "void"}
CV = {"A": "", "B": "const ", "C": "volatile ", "D": "const volatile "}
TYPEDEFS = {"Int": "int", "UnsignedInt": "unsigned int", "Real": "float", "UnsignedByte": "unsigned char",
            "Byte": "char", "Bool": "bool", "Short": "short", "UnsignedShort": "unsigned short",
            "DWORD": "unsigned long", "UINT": "unsigned int", "BYTE": "unsigned char", "BOOL": "int",
            "LONG": "long", "ULONG": "unsigned long", "WORD": "unsigned short", "Int32": "int",
            "UnsignedInt32": "unsigned int", "Real64": "double"}


def declare(symbol):
    """(name, type, key, class name, declaration) for a decorated global, or None.

    `type` is the C type a direct-name rewrite must agree with ('GameLogic *',
    'int'); `key` is 'class'/'struct' for a class pointee."""
    found = re.match(r"^\?(\w+)@@3(.*)$", symbol)
    if not found:
        return None
    name, rest = found.groups()
    scalar = re.match(r"^(_N|[CDEFGHIJKMN])([ABCD])$", rest)
    if scalar:
        kind = SCALAR[scalar.group(1)]
        return name, kind, None, None, f"extern {CV[scalar.group(2)]}{kind} {name};"
    pointer = re.match(r"^P([ABCD])(?:(_N|[CDEFGHIJKMNX])|([VU])(\w+)@@)A$", rest)
    if not pointer:
        return None
    pointee_cv, scalar_code, key_code, cls = pointer.groups()
    if scalar_code:
        kind = SCALAR[scalar_code]
        return name, f"{kind} *", None, None, f"extern {CV[pointee_cv]}{kind} *{name};"
    key = "class" if key_code == "V" else "struct"
    return name, f"{cls} *", key, cls, f"extern {CV[pointee_cv]}{key} {cls} *{name};"


def normalise(kind):
    words = kind.replace("*", " * ").split()
    words = [w for w in words if w not in ("const", "volatile", "class", "struct")]
    text = " ".join(TYPEDEFS.get(w, w) for w in words)
    return text.replace(" *", " *").strip()


DIRECT = re.compile(r"\(\s*\*\s*\(\s*([\w ]+?)\s*(\*?)\s*\*\s*\)\s*(0x[0-9A-Fa-f]{6,8})\s*\)")
CAST = re.compile(r"\(\s*([\w ]+?)\s*(\*+)\s*\)\s*(0x[0-9A-Fa-f]{6,8})\b")
VTABLE = re.compile(r"(?<![\w.])0x([0-9A-Fa-f]{6,8})[uU]?(?![\w.])")
LEAD = re.compile(r"(?:[ \t]*//[^\n]*\n|[ \t]*\r?\n)*")
NON_CODE = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/', re.S)


def rewrite(text, index, only=None):
    """(new text, {name: declaration}) for one source; with `only`, rewrite
    just the literals that name those globals (one edit per global)."""
    need = {}

    def unique(literal):
        address = int(literal, 16)
        if address < 0x400000:
            address += 0x400000
        found = [d for d in (declare(s) for s in index.get(address, ())) if d]
        if len(found) != 1 or (only is not None and found[0][0] not in only):
            return None
        return found[0]

    def key_ok(decl):
        name, kind, key, cls, line = decl
        if not cls:
            return True
        other = "struct" if key == "class" else "class"
        return not re.search(rf"\b{other}\s+{cls}\b", text)

    def direct(match):
        decl = unique(match.group(3))
        if not decl or not key_ok(decl):
            return match.group(0)
        cast = normalise(match.group(1) + (" *" if match.group(2) else ""))
        if cast != normalise(decl[1]):
            return match.group(0)
        need[decl[0]] = decl[4]
        return decl[0]

    def cast(match):
        decl = unique(match.group(3))
        if not decl or not key_ok(decl):
            return match.group(0)
        need[decl[0]] = decl[4]
        return f"({match.group(1)} {match.group(2)})&{decl[0]}"

    lines = text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("//"):
            continue
        line = DIRECT.sub(direct, line)
        line = CAST.sub(cast, line)
        if not stripped.startswith("#"):
            code, _, comment = line.partition("//")
            line = code + ("//" + comment if _ else "")
        lines[i] = line
    new = "\n".join(lines)
    if new == text:
        return text, {}
    newline = "\r\n" if "\r\n" in text else "\n"
    # A comment such as "extern spellings above" can otherwise span the
    # rewritten initializer and masquerade as an existing declaration.
    declarations = NON_CODE.sub(" ", new)
    missing = [d.replace("\n", newline) for n, d in sorted(need.items())
               if not re.search(rf"\bextern\b[^;]*\b{n}\s*(\[\])?;", declarations)]
    if missing:
        at = LEAD.match(new).end()
        new = new[:at] + newline.join(missing) + newline + newline + new[at:]
    return new, need



def safe_rewrite(text, index):
    protected = []
    def shield(match):
        key = "BFME2_PROTECTED_LITERAL_" + str(len(protected)) + "_END"
        if key in text:
            raise ValueError("protection token collision")
        protected.append((key, match.group()))
        return key
    masked = NON_CODE.sub(shield, text)
    rewritten, declarations = rewrite(masked, index)
    for key, original in protected:
        rewritten = rewritten.replace(key, original)
    return rewritten, declarations
