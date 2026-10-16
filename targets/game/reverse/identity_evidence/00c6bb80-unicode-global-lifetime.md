# Unicode global lifetime at VA 0x012F48C8

RVA 0x00C6BB80 (22 bytes, RET +0x15, INT3 +0x16) constructs the object
at VA 0x012F48C8 through ILT 0x00041C95, the matched UnicodeString default
constructor at RVA 0x00083D10, and registers callback RVA 0x00C701B0.
That ten-byte callback loads the same address and tail-jumps through
ILT 0x0003B304 to the matched UnicodeString destructor. The constructor
writes one zero dword; retail's four initial .data bytes are zero.

Native UnicodeString g_rva012F48C8 in the address-derived StaticInit TU
emits both functions as _$E1 and _$E2. This is the same independently
verified lifetime shape as RVA 0x00C6BAD0, with its distinct retail object
and callback. No original global name or source owner is claimed. Remove
the obsolete Gen_00C701B0Target declaration/provider from S3SingletonForwarders
and retire its old DIR32 name via dir32_record.py. No new pins or assembly.
