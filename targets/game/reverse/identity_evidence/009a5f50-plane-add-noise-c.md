# 0x009A5F50 PlaneAddNoise_C

## Result

BFME 1 RVA `0x009A5F50`, 475 bytes, is the generic-tier VP6 add-noise kernel
installed by `BfmeCodecCpuDispatch.cpp` into dispatch slot 0
(VA `0x01356E60`). The converted body is
`game/Libraries/Source/VP6/PlaneAddNoiseC.cpp`, symbol `_PlaneAddNoise_C`.

## Target evidence

- The previous row `?d_009a5f50@@YAXXZ` is a generated dump in
  `game/gen_asm/d_00968910.asm`; its Ghidra extent is 475 bytes and its bytes
  end with a single `ret` followed by `INT3` padding before the next function at
  `0x009A6130`.
- `BfmeCodecCpuDispatch.cpp` stores `&d_009a5f50` into slot 0 of the dispatch
  table. The sibling installer `0x009B0D60` stores the same VA at the generic
  tier, and caller `0x009A6130` passes five stack arguments: pixel pointer,
  width, height, pitch and scalar quality. That independently proves the same
  five-argument cdecl contract used by the donor.
- The body builds the Gaussian-shaped 256-entry distribution in a 300-byte
  signed table, seeds a 2048-byte noise buffer with `rand() & 0xff`, then adds
  the noise per row, clamping to `[-dist[0], 255 - dist[0]]`.

## Donor evidence

BFME 2 reference checkout `inputs/reference/open-bfme-2` at revision
`ce1b975697c2f20e514174e3875f8820d1dba612`:

- `Code/Libraries/Source/VP6/FilterMath.cpp`, `PlaneAddNoise_C` at donor RVA
  `0x001B69C0`, 475 bytes.
- `Code/Libraries/Source/VP6/PostProcMachineSpecificConfig.cpp` declares
  `PlaneAddNoise_C` with the comment `rowed C body (was address-named
  d_009a5f50)` and installs it at slot[0] for the generic tier, matching
  BFME 1's installer slots and order.
- The donor's Gaussian helper is inlined into this body. BFME 1 keeps the
  standalone helper as the already matched row `?bfmeGaussPdf@@YANNNN@Z` at
  `0x009A5F00` (65 bytes), so the converted TU inlines the same expression by
  hand instead of defining a second helper.

## Verification

`tools/probe.py game/Libraries/Source/VP6/PlaneAddNoiseC.cpp _PlaneAddNoise_C
0x009A5F50 --size 475` reports:

```
size     ours=475 retail=475  relocs=12
result   EXACT (modulo relocation slots)
```

The comparison masks only relocation fields. The 12 object relocations are the
six `__real@` constants, the two absolute `1.0` slots, the two `rand` IAT
operands and the two `__ftol2` call displacements; their instruction encodings
and all non-relocation bytes agree with retail. The landed row will be verified
again by `tools/add_match.py` and the scoped gate.

## Prior attempts

The bank at `targets/game/reverse/attempts/0x009a5f50.cpp` and the handoff
`targets/game/reverse/identity_evidence/009a5f50-frame-lifetime.md` record a
444-byte body against 475 bytes, blocked on the retail `__imp__rand` hoist and
row-pointer lifetime. The donor source is the independent evidence that
handoff requested: its exact register shape, including the reference-bound
`lower`/`negFirst` temporaries, reproduces retail without further experiments.
