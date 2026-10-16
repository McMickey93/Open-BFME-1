# Opaque sound-slot forwarder at 0016A020

The fresh carve independently proves a REL32-target start at 0016A020 and
an eight-byte PUSH 0x54 / CALL ILT 0001BFD1 / RET extent, with INT3 at +8.
checked_callees resolves that call to the existing matched 22-byte
ThingTemplate::getSound(int) const at 00416FA0. That callee consumes one
stack word with RET 4 and returns a const AudioEventRTS pointer in EAX;
the wrapper preserves ECX and returns the same pointer without an adjustment.
There are no branches, other calls, incoming stack parameters, or cleanup
frames. This proof is independent of its neighbouring wrapper.

Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b,
Code/GameEngine/Source/Common/CallForwarders8B.cpp at 004D0E8B supplies the
single constant-argument member-call source shape. The BFME 1 literal is
0x54, and its independently checked native callee determines the pointer
return. The donor's ConnectionManager identity is not transferred. No
original wrapper class or method name is established, so Rva0016A020::get
remains address-qualified. name_oracle has no witness for this class.

The existing native ThingTemplate API declaration and getSound pin from
the preceding verified sibling are reused. repair_queue.py dest places the
body in TinyIndexedForwarders.cpp between the 0016A010 and 0016A040 rows.
All 97 source rows pass strict byte and call verification. link_check before
and after remains LINKED 0 -> 0, with existing forwarding provider debt.
No pin, header, shim, alias, source marker, or assembly is added. Raw brief,
callee/decoder, scoped gate and link receipts are build/*0016a020* in ds-9.
