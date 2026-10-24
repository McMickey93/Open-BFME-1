# 0x0095C6E0 / 0x0095C6F0 are Vector3Randomizer's dtor and ??_G

VA 0x0113E098 is recorded in dir32_addresses.csv as `??_7Vector3Randomizer@@6B@`
(and also as the address name `??_7Rva0095C6F0Deleting@@6B@`). It has six slots:

| slot | target |
|---|---|
| 0 | 0x0095C6F0, the 31 B scalar deleting destructor (was `??_GRva0095C6F0Deleting`) |
| 1-5 | `__purecall` (0x0088C500) |

That is WWMath v3_rnd.h's abstract `Vector3Randomizer`, a virtual
`~Vector3Randomizer(void) {}` plus exactly five pure virtuals: Class_ID,
Get_Vector, Get_Maximum_Extent, Scale and Clone.

- 0x0095C6E0, 7 B, unclaimed: `mov [ecx],0x0113E098; ret`. This is the
  inline empty destructor emitted out of line: `??1Vector3Randomizer@@UAE@XZ`.
- 0x0095C6F0, 31 B: slot 0, `??_GVector3Randomizer@@UAEPAXI@Z`.

The real game/Libraries/Source/WWVegas/WWMath/v3_rnd.cpp TU emits both, and
each probes EXACT. (0x00B02140, `mov eax,ecx; mov [eax],0x0113E098; ret`, is
an out-of-line copy of the implicit default constructor in another TU. It is
not claimed here.)
