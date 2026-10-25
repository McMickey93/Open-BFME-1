# 0x009A8C50 UpdateUMVBorder identity

## Boundary (BFME 1 evidence)

Retail `0x009A8C50..0x009A9066`, 1047 bytes, ending in `ret` at +0x416 with
INT3 padding after. The preceding body ends before the INT3 run that separates
it from 0x009A8C50, and the gen-dump row carried a carved boundary
(`rel32-call/jmp` start, `ret+int3` end, Ghidra FUN_00da8c50). Disassembly
shows the two-argument cdecl frame: `sub esp,0x1c`, context in EBX, frame
buffer from the second stack argument.

## BFME 1 behaviour evidence

Independent BFME 1 decodes (prior attempts) and the four matched callers agree:

- `Rva009A9070CopyStreams` (0x009A9070) calls it with `(self, offset)`.
- `Rva009AA8F0Dispatch` (0x009AA8F0) calls it with `(context, offset)`.
- `Rva009A5800Forward` and `Rva009A6130PostFilterDispatch` call it with
  `(context, frame)`.
- Six-phase Y/U/V plane border extension: field reads at +0x78/+0x7C/+0x80
  (plane offsets), +0x90/+0x94 (fragments), +0x98/+0x9C (strides), +0xB4
  (border). One four-pointer set for all side fills and row copies; U/V row
  copies address the bottom row through the top pointer.

## Donor evidence (carried, not BFME 1 facts)

BFME 2 unit `Code/Libraries/Source/VP6/UpdateUMVBorder.cpp` at donor revision
`ce1b975697c2f20e514174e3875f8820d1dba612`, a clean-room reconstruction from
`reverse/vp6_cleanroom/specs/001b96a0.md` plus retail, verified over all 1047
bytes of the BFME 2 body at `0x001B96A0` (donor ledger row
`_UpdateUMVBorder,,0x001B96A0,1047,...`). cdecl
`void UpdateUMVBorder(UpdateUMVBorderInstance *, unsigned char *)`.

## Cross-image comparison (structural inference)

Masked whole-body comparison of BFME 2 retail `0x001B96A0` against BFME 1
retail `0x009A8C50` over 1047 bytes: score 1.0, zero non-relocation
differences, no string conflicts. The four masked fields are `rel32` internal
conditional branches (both sides decode to text); the linked body has no
external call relocation because `memset`/`memcpy` are inlined at /O2.
`bfme2_sweep scan` records an exact-unique placement with one donor alias.

Same machine body in both executables. The name is carried from the verified
BFME 2 unit; no BFME 1 caller, vtable or literal names the function, and the
BFME 1 callers prove only the two-argument cdecl shape, which agrees.

## Compilation and consumer reconciliation

`tools/probe.py game/Libraries/Source/VP6/UpdateUMVBorder.cpp
_UpdateUMVBorder 0x009A8C50` reports ours=1047 retail=1047, 0 relocations,
EXACT modulo relocation slots, on the first trial. The four BFME 1 callers
previously named the gen-dump symbol `?d_009a8c50@@YAXXZ` through local
`reinterpret_cast` declarations; they now declare the landed
`extern "C" void UpdateUMVBorder(void *, unsigned char *)` and keep the same
two-argument casts, so each caller still byte-verifies unchanged.
