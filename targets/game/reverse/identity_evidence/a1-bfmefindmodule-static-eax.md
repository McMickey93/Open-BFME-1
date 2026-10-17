# 0x0028CCD0 bfmeFindModule: signature correction, inline asm retired

Retail 0x0028CCD0 (43 B, `ret` at +0x2A, INT3 at +0x2B) reads its owner from
EAX+0x1F0 on entry, walks the null-terminated behavior-module array and returns
the first non-null result of the BehaviorModuleInterface (module+0xC) virtual
slot +0x78. Its one caller, matched 0x0028CF50 Gen_0028CF50::bfmeRelease,
calls it at +0x1D with EAX still holding the Object* returned by
findObjectByID (retail: `mov esi,eax / test esi,esi / je / call 0x68CCD0`).

The prior row `?bfmeFindModule@@YAPAVBfmeDestroyable@@XZ` declared no
parameter and reproduced the bytes with an `__asm` block that read EAX
implicitly. The function really takes the Object*: an MSVC 7.1 file-static
function gets the private register convention, so `static BfmeDestroyable
*bfmeFindModule(Object *)` called from bfmeRelease emits retail's bytes in
clean C++ (docs/shape_levers.md "Static function with a private register
convention"; same shape as matched 0x00219910, 0x002EFDE0, 0x00297480).

Only the decoration changes (one added `PAVObject@@` parameter); the
placeholder base name stays as it was, no meaning is claimed beyond the
caller relationship above.
