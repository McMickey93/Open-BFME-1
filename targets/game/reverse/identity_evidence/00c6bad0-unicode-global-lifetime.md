# Unicode global lifetime at VA 0x012F3DC4

Retail initializer RVA 0x00C6BAD0 is 22 bytes: it loads ECX with
VA 0x012F3DC4, calls ILT 0x00041C95 (the matched UnicodeString default
constructor at RVA 0x00083D10), pushes VA 0x01070160, and calls atexit.
RET is at +0x15; INT3 starts at +0x16. The constructor writes one zero
dword. The initial four retail .data bytes at VA 0x012F3DC4 are zero.

The 10-byte callback at RVA 0x00C70160 loads that same global address and
tail-jumps through ILT 0x0003B304 to the matched UnicodeString destructor.
Its RET-free tail ends at +0x0A, followed by INT3. These two independently
named callees establish the type and four-byte extent; the original global
name and original source TU remain unknown. Replace the old Gen_00C70160Target view with the address-named
g_rva012F3DC4 UnicodeString definition, and use the established Common/StaticInit
address-derived file convention rather than guessing a semantic owner.

Defining the native UnicodeString in Rva012F3DC4Global.cpp makes MSVC 7.1
emit _$E1 (22 bytes, four relocations) and _$E2 (10 bytes, two relocations).
Both probe exactly. Register the compiler labels through add_match.py's
supported object-symbol path; this removes the separate handwritten
cleanup provider. No callee pin, assembly, or header change is required.
