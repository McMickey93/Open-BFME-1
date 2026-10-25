# 0x009B2190 DiagonalBlur identity

## Boundary (BFME 1 evidence)

Retail `0x009B2190..0x009B2523`: prologue `sub esp,0x2c`, epilogue
`pop edi/esi/ebp/ebx; add esp,0x2c; ret` at +0x38F..+0x393, INT3 padding from
0x009B2524. The preceding body ends `ret` at 0x009B218C and is followed by
INT3, so 0x009B2190 starts a function. This agrees with the carved gen-dump
row (`callers=0`, Ghidra FUN_00db2190) and with the prior attempt records.
Size 916 bytes.

## BFME 1 behaviour evidence

Prior independent decodes of the retail bytes agree on a two-pass 8x8 byte
transform that reads stack arguments 2, 3 and 4 (source, destination, pitch)
and never the first argument, that has no direct callee, no string, no vtable
and no inbound code or data reference. Disassembly at the head shows the
stride-derived `1 - pitch`, `2 - pitch`, `5 - pitch`, `3 - pitch`, `6 - pitch`
constants that precede the diagonal taps.

## Donor evidence (carried, not BFME 1 facts)

BFME 2 unit `Code/Libraries/Source/VP6/DiagonalBlur.cpp` at donor revision
`ce1b975697c2f20e514174e3875f8820d1dba612` is a clean-room reconstruction from
`reverse/vp6_cleanroom/specs/001c2b80.md` plus retail, verified over all 916
bytes of the BFME 2 body at `0x001C2B80` (donor ledger row
`_DiagonalBlur,,0x001C2B80,916,...`). Its cdecl signature is
`void DiagonalBlur(void *instance, unsigned char *source, unsigned char *dest,
int pitch)`.

## Cross-image comparison (structural inference)

Masked whole-body comparison of BFME 2 retail `0x001C2B80` against BFME 1
retail `0x009B2190` over 916 bytes, using the four decoded relocation fields:
score 1.0, zero non-relocation differences, all four relocation destinations
valid in text on both sides, no string conflicts. `bfme2_sweep scan` records
this as an exact-unique placement with one donor alias.

This is the same machine body in both executables. It does not by itself prove
the retail symbol name: no BFME 1 caller, vtable slot or literal names the
function. The name is carried from the verified BFME 2 unit, and the BFME 1
argument behaviour independently agrees with its cdecl signature.

## Compilation

`tools/probe.py game/Libraries/Source/VP6/DiagonalBlur.cpp _DiagonalBlur
0x009B2190` reports ours=916 retail=916, 0 relocations, EXACT modulo relocation
slots, on the first trial. Relocations: none (both passes and all neighbour
loads are inlined).
