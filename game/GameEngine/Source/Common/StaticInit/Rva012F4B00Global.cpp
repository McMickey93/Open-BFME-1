// cl: /O2 /MD /Igame/Libraries/Source/WWVegas/WWLib
// Retail 0x00C6BCB0 constructs "Palantir.apt" at VA 0x012F4B00 and
// registers cleanup 0x00C701F0. Retail calls AsciiString's out-of-line
// C-string constructor, as emitted by AsciiStringNative.cpp.
#include "ascii_string.h"
#pragma auto_inline(off)
AsciiString g_rva012F4B00("Palantir.apt");
#pragma auto_inline(on)
