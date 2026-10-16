# Opaque six-word initializer at 005CB1B0

Fresh carve build/sol3_r2_carved.csv proves a direct REL32 target at
0x005CB1B0. The full 22-byte body copies ECX to EAX, clears ECX, writes
zero at EAX+0, +4, +8, +C, +10 and +14, and returns EAX unchanged. INT3
padding starts at +16. It has no calls, stack arguments, hidden result,
vtable store, or receiver adjustment. An explicit initializer returning
its receiver expresses exactly those observed effects without asserting
an original constructor or type identity. name_oracle has no layout
witness for Rva005CB1B0; all field labels are address-derived offsets.

Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b supplies the
six-zero-field source at 001DBC61 (22 bytes), Rva00489BC0's constructor,
in Code/GameEngine/Source/Common/R3ScalarFieldConstructors1.cpp.
BFME1 independently fixes ascending store order and the returned receiver;
those details replace the donor's out-of-order +14 store. The standalone
explicit initializer first probes 22/22 bytes with no relocation. The
production TU then independently verifies it alongside every existing row.

repair_queue.py dest selects aabtreebuilder.cpp from its EA/Zero Hour
source-file hint. That placement hint does not prove AABTreeBuilderClass
identity: the native named constructor already owns the distinct retail
body at 0096B350. The new initializer retains its own opaque address.
The pre-existing untyped b_005cb1b0 symbol pin is not used as ABI evidence.

All 35 production source rows pass strict checks, including ten jump-table
entries, ten float constants, three local readonly loads, and five DIR32
references. link_check before: LINKED 5482 -> 5482; after: 5482 -> 5504.
No pin, header, shim, assembly, or hatch changes. Receipts are
build/r2_*005cb1b0* and build/r2_init_trial* in ds-9.
