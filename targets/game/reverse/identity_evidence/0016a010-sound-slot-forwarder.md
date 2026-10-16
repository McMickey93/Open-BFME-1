# Opaque sound-slot forwarder at 0016A010

A refreshed carve proves 0016A010 as a direct REL32 target. Its complete
body is PUSH 0x53 / CALL ILT 0001BFD1 / RET, followed immediately by INT3
at +8. There is no incoming stack argument, adjustment to ECX, branch,
cleanup frame, or instruction after the return. checked_callees resolves
the sole call through that ILT to the matched 22-byte
ThingTemplate::getSound(int) const at 00416FA0. Its RET 4 consumes the
constant and its EAX pointer result survives the wrapper's RET.

Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b,
Code/GameEngine/Source/Common/CallForwarders8B.cpp, supplies the ordinary
single-constant member-call shape at 004D0E8B (8 bytes). BFME 1 independently
supplies slot 0x53 and the real typed callee. No ConnectionManager identity
or void return is transferred. The new receiver remains Rva0016A010:
forwarding the native ThingTemplate interface does not prove its original
wrapper class or method name. name_oracle has no class witness.

The ThingTemplate API declaration is the existing BFME contract from
ThingTemplateSounds.cpp; the Zero Hour header does not declare getSound.
Only this method is declared, without a copied layout or vtable. The wrapper
returns the existing const AudioEventRTS pointer. pin_consistency follows
the existing canonical getSound pin to 00416FA0 and reports consistent.
No new pin, alias, source marker, header, shim, or assembly is introduced.

repair_queue.py dest selects TinyIndexedForwarders.cpp between its proven
00169FF0 and 0016A040 siblings. All 96 source rows pass the strict gate;
all eight bytes and the resolved call agree. link_check remains LINKED
0 -> 0 because the old generic forwarder providers are still unresolved.
Raw brief, decoder, gate and link receipts are build/*0016a010* in ds-9.
