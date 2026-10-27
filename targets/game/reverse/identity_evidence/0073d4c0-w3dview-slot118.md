# W3DView slot 118 = retail 0x0073D4C0 (BFME 1 target evidence)

The private W3DView view in W3DViewRva00743CE0.cpp declared vtable slot 118
(+0x1D8) as `slot118()`, the call 0x00743CE0 makes when its mode argument is
false (`call [eax+0x1D8]` at +0x1F8, ECX = this, no arguments). Retail vtable
0x011217A0 slot 118 resolves through its ILT to 0x0073D4C0 (423 B, `ret`):
the body that clears the +0x2439 mode flag and restores the view fields from
the globals 0x012F9DC0..0x012F9DF8 that 0x00743CE0 saved. The slot is now
declared with that body's address-derived name `rva0073D4C0`, which this TU
also defines; the slot-number placeholder named nothing.
