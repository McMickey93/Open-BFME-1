# Palantir filename lifetime at VA 0x012F4B00

Retail initializer RVA 0x00C6BCB0 is 27 bytes, ending RET +0x1A before
INT3 +0x1B. It pushes the exact ASCII literal "Palantir.apt" at
VA 0x0110A248, sets ECX to VA 0x012F4B00, calls ILT 0x00012C42
(the matched AsciiString C-string constructor at RVA 0x0005EE70), and
registers cleanup RVA 0x00C701F0 through atexit.

The ten-byte cleanup loads the same global address and tail-jumps through
ILT 0x0000D828 to the matched AsciiString destructor. The four-byte string
object has zero initial .data bytes. AptPalantirRegisterCallbacks reads
this same object as the filename passed to loadAptWindow; its existing
opaque global facade can therefore be replaced by native AsciiString.

Define address-named g_rva012F4B00 in the established Common/StaticInit
file convention. Native ascii_string.h with auto_inline(off), the policy
already used by AsciiStringNative.cpp to emit the retail constructor,
emits _$E1 (27 bytes) and _$E2 (10 bytes), both exact in probe. Register
these compiler labels through add_match.py. No invented semantic global
name, assembly, header change, or additional callee pin is needed.
