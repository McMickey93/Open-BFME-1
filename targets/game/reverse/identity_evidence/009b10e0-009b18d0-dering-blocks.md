# 0x009B10E0 DeringBlockStrong_C and 0x009B18D0 DeringBlockWeak_C identity

## Boundary (BFME 1 evidence)

Retail disassembly, not the gen-dump extent, fixes both bodies:

- `_DeringBlockStrong_C`: `0x009B10E0..0x009B18CE` exclusive, 2030 bytes. The
  last instruction is `ret` at `0x009B18CD`, followed by two `INT3` bytes
  (`0x9B18CE..0x9B18CF`). The body begins at an `INT3`-aligned start.
- `_DeringBlockWeak_C`: `0x009B18D0..0x009B1EC6` exclusive, 1526 bytes. The
  last instruction is `ret` at `0x009B1EC5`; `INT3` padding follows through
  `0x9B1ECF`, then the independent matched body `rva009B1ED0` starts at
  `0x009B1ED0`.

The gen-dump row `?d_009b10e0@@YAXXZ` claimed `0x009B10E0/3558` because it
spanned both functions and the two padding bytes. That extent was wrong; the
tombstone in `deleted_rows.csv` records the split and this boundary proof.

## BFME 1 caller evidence

`game/GameEngine/Source/Common/BfmeCodecCpuDispatch.cpp` installs the generic
codec tier and fills:

- `slot[16] = &Rva009B18D0` (the 1526-byte body at `0x009B18D0`)
- `slot[24] = &Rva009B10E0` (the 2030-byte body at `0x009B10E0`)

The same TU is byte-matched, so the two slots are real retail dispatch entries.
`symbols.csv` records both addresses with address-derived placeholder names and
no identity; they are the only names for these addresses on BFME 1's side.

## Donor evidence (carried, not BFME 1 facts)

BFME 2 clean-room unit
`Code/Libraries/Source/VP6/DeringBlockStrongC.cpp` at donor revision
`ce1b975697c2f20e514174e3875f8820d1dba612`, which defines both bodies:

- `DeringBlockStrong_C` at donor RVA `0x001C1AD0`, 2030 bytes
  (`reverse/vp6_cleanroom/specs/001c1ad0.md`).
- `DeringBlockWeak_C` at donor RVA `0x001C22C0`, 1526 bytes
  (`reverse/vp6_cleanroom/specs/001c22c0.md`).

The donor dispatch unit
`Code/Libraries/Source/VP6/PostProcMachineSpecificConfig.cpp` fills
`slot[16] = &DeringBlockWeak_C` and `slot[24] = &DeringBlockStrong_C`, and its
declarations carry the notes "(was address-named Rva009B18D0)" and
"(was address-named Rva009B10E0)". This matches BFME 1's slot layout, so the
slot mapping corroborates the names independently of body similarity.

Donor signatures: cdecl
`void DeringBlockStrong_C(void *, const unsigned char *, unsigned char *, int, int, const int *)`
and the same six-argument shape for the weak body.

## Cross-image comparison (structural inference)

Masked whole-body comparison over BFME 1 retail vs the donor-ledger bodies:
`_DeringBlockStrong_C` 2030/2030 bytes, `_DeringBlockWeak_C` 1526/1526 bytes,
score 1.0 in the targeted `bfme2_sweep scan` (exact-unique, one donor alias
each). BFME 1 retail's `ret`/`INT3` boundaries agree with both sizes.

## Data reconciliation

The donor reads `g_vp6SharpenModifier[qIndex]` (a 64-entry `int` table). BFME 1's
matched data row `_Vp6FilterEdgeTagTable` at VA `0x012D8158`
(`data_rows.csv`, source `game/GameEngine/Source/Common/BfmeConv9C2320.cpp`)
already defines that table, and the four matched VP6 filters index it the same
way. Both TUs therefore declare `extern "C" int Vp6FilterEdgeTagTable[64];`;
the array is only indexed, so the layout is fixed. No new data row is needed.

## Compilation and consumer reconciliation

`tools/probe.py` reports:

- `DeringBlockStrongC.cpp _DeringBlockStrong_C 0x009B10E0`: ours 2030 bytes,
  all 2030 bytes equal to retail (+ the two INT3 padding bytes outside the
  claimed extent), one relocation.
- `DeringBlockWeakC.cpp _DeringBlockWeak_C 0x009B18D0`: EXACT, 1526/1526, one
  relocation.

`tools/add_match.py` verified both rows. The BFME 1 dispatch TU is unchanged
and still byte-verifies with the landed rows (`DIR32 addresses: OK`, 84
references); its two slot references keep the pre-existing address-derived
placeholder names recorded in `dir32_addresses.csv`.

Follow-up (not required for these bodies): renaming the two dispatch slot
references to the real C-linkage names needs an admission path for a C function
name in `build.unrecorded_dir32_problem`, which currently proves only manglings
ending in `Z`. Until that exists the placeholders stay the only recorded names
at those VAs; the real identities are the ledger rows and this evidence.
