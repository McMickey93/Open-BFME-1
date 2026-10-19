# Banked collision counter at 0x009A4740

This iteration banks, but does not land, the new complete 750-byte C++ body in
attempts/0x009a4740.cpp. The source comes from Open-BFME-2 commit
d8961f14c218725a3dc0890fe1dcc313d533d469,
Code/GameEngine/Source/Common/RTS/BfmeThingCGDRva0075A1A0.cpp. Its original
comments about BFME2 template folding are donor context only. BFME1 was linked
without identical-COMDAT folding; they do not justify alias pins here.

The BFME1 constructor at 0x009A45A0 and the bucket walks establish the
address-derived receiver layout. RET at +0x2ED followed by INT3 proves the
750-byte extent, with no stack arguments. The body counts the two pointer
fields of every node in each table and scans unsigned maxima. It reproduces
all instruction bytes, with 14 relocation operands.

Three required container bindings remain unresolved: the native pointer-key,
unsigned-value map operator[] at 0x009A46C0 (115 bytes), recursive erase at
0x009A34A0 (53 bytes), and tree destructor at 0x009A4010 (124 bytes).
Each independently emitted helper also matches its full retail extent modulo
relocations. Existing rows instead name Image* or signed-key/POD containers;
the operator[] recursively requires further container-family identity work.
That repair exceeds the small one-pin dependency rule. Do not manufacture
aliases from the equal bytes or borrow the existing Image* identity.

The strict caller probe fails solely on those three unresolved symbols.
No production collision source, helper ownership, pin or baseline was changed.
The preferred new bank and its measured history remain available for the
container owner to continue. Raw probes are in build/collision-reset-iteration.
