# Opaque word getter at 00169F70

Fresh carve build/sol3_r2_carved.csv proves a REL32 entry at 0x00169F70.
The preceding padding ends at the entry, and the complete body is
MOV EAX,[ECX+208] / RET. INT3 begins at +7. There are no calls, stack
arguments, stores, or receiver adjustments. The four-byte return is viewed
as int, without claiming an original scalar, enum, pointer, or receiver type.
No matched caller proves a semantic identity. name_oracle has no witness
for Rva00169F70, so its owner and member retain address tokens.

Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b supplies
Rva00042292DwordField::get at 00042292 (7 bytes), in
Code/GameEngine/Source/Common/DispDwordFieldGetters.cpp. Its ordinary
int member read provides compiler shape. BFME1 independently fixes the
displacement at 208; the donor's 2EC offset is not transferred.
repair_queue.py dest selects TinyIndexedForwarders.cpp from the proven
00169FF0 sibling 128 bytes away. All 100 source rows pass strict byte
verification. link_check remains LINKED 0 -> 0 bytes with the same six
pre-existing generic forwarder providers unresolved. No pin, header, shim,
assembly, or hatch changes. Receipts are build/r2_*00169f70* in ds-9.
