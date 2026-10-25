# LAN update: leave-handler name and the closing SIB lever

Target: the LAN update tick at RVA 006870F0 (2436 bytes; boundary in
`006870f0-finishing-ilt.md`), landed as `?step@Rva006870F0State@@QAEXXZ`
from `game/GameEngine/Source/GameNetwork/LANAPIUpdate.cpp`.

## Leave handler at 0068BAC0

The body calls 0068BAC0 three times through ILT 0001320F with ECX = the LAN
object, a packet pointer, an endpoint pointer and a Boolean; the callee ends
in RET 12 (the complete ABI decode is in `006870f0-finishing-ilt.md`).

The ledger's handler family names (`?handleX@LANAPI@@IAEXPAULANMessage@@I@Z`
and `...PAUBfmeNetAddress@@@Z`) are all CONTRADICTED by
`tools/ilt_oracle.py`. A joint search over 1815 signature spellings (five
message spellings, 121 second-argument spellings, three access levels) against
the thirteen sibling handler bodies 0068B6A0, 0068B890, 0068B540, 0068B920,
0068B4C0, 0068B380, 0068C110, 0068B1E0, 0068AC20, 0068AEF0, 0068AC80,
0068BFA0 and 0068C400 found exactly one spelling that fits more than one
window: `IAEXPAULANMessage@@ABUIPAddr@@@Z`
(`void handleX(LANMessage *, const IPAddr &)`, protected), which fits all
thirteen. The next best spellings fit one handler each.

With that spelling, 90 leave-handler candidates (five names, six third-argument
types, three access levels) were checked at 0068BAC0. Exactly one fits:
`?handleRequestGameLeave@LANAPI@@IAEXPAULANMessage@@ABUIPAddr@@_N@Z`
(p_false 7.2e-4 at both 0001320F and 0068BAC0). The name is Zero Hour's
`LANAPI::handleRequestGameLeave(LANMessage *, UnsignedInt)` with BFME's
endpoint struct and Boolean. The pin is placed on the body address; the dump
row `?d_0068bac0@@YAXXZ` there is a placeholder. The thirteen sibling renames
are left for the naming lane.

## SIB byte at +0x7A1

Retail `lea ecx,[edi+eax+0x88]` (SIB 07) against the bank's
`[eax+edi+0x88]` (SIB 38) closed with a block-scope reference alias,
`RvaLANGame *const &cg = m_currentGame;`, used through the host-drop loop
(BFME2 `docs/recipes.md`, 0x0052F63F: a reference alias flips MSVC's
base/index choice). Function-scope and block-scope placements used only at
the call or through the loop all match; using the alias across the whole
function breaks the body (2420 bytes). Sixteen index and accessor spellings
and fourteen integer paren nodes were inert.

The leave calls must name `LANAPI::handleRequestGameLeave` at the call sites:
an inline (or `__forceinline`) forwarding member changes the endpoint
argument's register allocation (214 bytes from +0x51D), while direct
`reinterpret_cast` calls compile exact.

t=55 model=claude-opus-5-5
