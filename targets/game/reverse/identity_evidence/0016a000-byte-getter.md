# Opaque byte getter at 0016A000

A fresh carve finds a direct REL32 target at 0x0016A000. Its entire seven-byte
body is MOV AL,[ECX+29D] / RET; INT3 padding begins at +7. The preceding
00169FF0 entry also ends before padding. There are no callees or incoming
stack arguments. Only AL is defined, supporting the unsigned-byte getter
view; no semantic identity or full receiver layout is asserted.

Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b supplies the
same disp32 byte getter in Code/GameEngine/Source/Common/DispByteFieldGetters.cpp:
Rva0002BAF1ByteField::get at 0002BAF1 (7 bytes). Its ordinary unsigned-byte
member read supplies compiler shape; BFME1 independently fixes offset 29D.
The donor's receiver identity and offset 430 are not transferred. name_oracle
has no witness for Rva0016A000. The receiver and field keep address tokens.

repair_queue.py dest selects TinyIndexedForwarders.cpp between the already
verified 00169FF0 and 0016A010 entries. All 99 rows pass strict verification.
No pin, header, shim, assembly, or hatch changes. link_check before and after
remains LINKED 0 -> 0 bytes with the same six generic provider names unresolved.
Receipts: build/r2_*0016a000* and build/r2_byte_getters_donor.cpp in ds-9.
