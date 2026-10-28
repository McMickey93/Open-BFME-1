# ??1RefHandle008958D0 (retail 0x00784A70, 35 B; ILT 0x000463AD): inline_depth trials

Session a1/468, 2026-10-28, link queue #7 (census a0940f921b). Prior blocks:
re_attempts.log entries for 0x00895950 and 0x00784A70.

Goal: make each of the four consumer TUs (Rva00893030ManagerFind,
Rva00895A00CreateHandle, Rva00895B20Dependencies, Rva00895D30ManagerSubmit)
emit retail's out-of-line dtor (calls decrement 0x894D90 and bfmeDropA 0x895320)
while their exact main bodies keep the fully inlined `dec [esi]` release.

Scratch TU: Rva00895B20Dependencies.cpp with the dtor rewritten as
`if (m && Rva00894D90Accessor::decrement((unsigned*)m)==0) bfmeDropA(m);`, decrement
and bfmeDropA inline-defined. Measured (probe, method 0x895B20 / dtor vs 0x784A70):

| variant | main 0x895B20 | dtor copy |
|---|---|---|
| dtor defined under inline_depth(0) | 273 B, calls ??1 | EXACT 35 |
| same, __forceinline dtor | 273, calls ??1 | EXACT 35 |
| dtor under inline_depth(1) | 273, dtor inlined but decrement/bfmeDropA called | 38 (callees inlined) |
| dtor under inline_depth(2) | EXACT 294 | 38 |
| callees under inline_depth(0) | 264 | 24 (callees inlined, ??_G called) |
| inline_depth(0) at end of TU | EXACT 294 | 38 |
| callees under auto_inline(off) | 273 | EXACT 35 |

Observed model (MSVC 7.1): a call at chain level k is inlined only when k is <= the
recorded inline_depth of every *caller* in the chain, including the outermost one.
Retail needs the dtor's depth to be 0 (copy) and also >= 2 (main). One TU cannot
satisfy both, so no pragma placement fixes the losing copies. Retail's copies in these
TUs probably lost to the 0x00784A70 TU's copy at link time as well.

Ruled out here: pragma inline_depth / auto_inline placement, __forceinline. Not tried:
moving the release out of the dtor in the main bodies (that would change the
semantics for the matched rows).
