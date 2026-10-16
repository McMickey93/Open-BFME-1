# Opaque sound-slot forwarder at 0016A030

Fresh carve output build/sol3_r2_carved.csv proves a direct REL32 target at
0x0016A030. The preceding entry ends at 0016A028 and INT3 padding separates
this entry. PUSH 0x55 / CALL ILT 0001BFD1 / RET occupies exactly eight bytes;
INT3 starts immediately at +8. There are no incoming stack arguments or
receiver adjustments. The full matched callee at 00416FA0 is the native
ThingTemplate::getSound(int) const; its RET 4 consumes the slot argument,
and its const AudioEventRTS pointer result remains in EAX on wrapper return.
Existing canonical pin_consistency reports that binding consistent.

Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b supplies the
single-constant member-call shape in
Code/GameEngine/Source/Common/CallForwarders8B.cpp at 004D0E8B (8 bytes).
The BFME1 source_donors lookup independently serves the same call shape.
No donor class identity or return type is transferred. Retail supplies the
constant 0x55 and checked native getSound ABI. No caller proves an original
wrapper name; Rva0016A030 retains its address. name_oracle has no witness.

repair_queue.py dest selects TinyIndexedForwarders.cpp between the proven
0016A020 and 0016A040 entries. This TU already declares native getSound
without duplicating a receiver layout. All 98 source rows pass strict
verification. No pin or hatch is added. link_check before and after remains
LINKED 0 -> 0 bytes with the same six pre-existing generic provider names
unresolved. Receipts are build/r2_*0016a030* in ds-9.
