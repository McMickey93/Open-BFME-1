# 0x004AF9B0: dup_004af9b0 inline asm -> file-static rva004AF9B0(GameWindow *)

Retail 0x004AF9B0 (46 B; INT3 padding before it from 0x004AF990 and its last
`ret` at +0x2D) takes its window in ESI on entry: `mov ecx,esi / call
j_0003a5b7` (ILT -> 0x00478410 GameWindow::winIsHidden), returns `xor al,al`
when hidden, else `push esi / call j_00010e88` (ILT -> 0x004BBEE0
GadgetButtonGetData, cdecl, `add esp,4`) and returns 1 when the result is
non-null and its int at +0x144 is positive, 0 otherwise. callers_of.py finds no
direct caller: every retail use is inlined.

The prior row `?dup_004af9b0@@YAXXZ` reproduced the bytes with an `__asm` block
that read ESI implicitly, an escape hatch. An MSVC 7.1 file-static function
receives the private register convention (docs/shape_levers.md "Static function
with a private register convention"), so `static bool rva004AF9B0(GameWindow *)`
with a TU-local caller compiles to retail's 46 bytes exactly (probe.py EXACT,
2 relocations). The `xor al,al` / `mov eax,1` mix fixes the return type as bool.

The meaning beyond the two callees is unproven, so the name stays
address-derived (`rva004AF9B0`).
