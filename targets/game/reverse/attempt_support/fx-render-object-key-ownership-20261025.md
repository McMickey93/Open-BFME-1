# Render-object INI key ownership repairs

Parent: `be135ec99e96d5471a081b5f7d48d47d400c82e1`.
The repair lane served `?g_01113814@FXParticleSystem@@3QBDB`.
The other nine entries are the same ownership failure in the same source unit.

## Independent BFME 1 evidence

Read each array directly from the retail-1.03-unpacked `lotrbfme.exe` at the
listed VA, including its terminating NUL. Existing `FXParticleSystem` namespace
extern declarations and `writeINI` consumers already establish the exact
COFF symbols and const-character-array type. Define those arrays in place;
retain names, namespace, consumer expressions, function bodies and compiler
settings. No new semantic name, layout, ABI, pin or fixed-address expression
is introduced.

| Retail VA | Exact text | Array extent including NUL |
| --- | --- | --- |
| 0x011137EC | `Shader3` | 8 B |
| 0x01113804 | `NumObjects3` | 12 B |
| 0x01113814 | `RenderGroup3` | 13 B |
| 0x01113830 | `Percent2` | 9 B |
| 0x0111383C | `NumObjects2` | 12 B |
| 0x0111384C | `RenderGroup2` | 13 B |
| 0x01113868 | `Percent1` | 9 B |
| 0x01113874 | `NumObjects1` | 12 B |
| 0x01113884 | `RenderGroup1` | 13 B |
| 0x01113894 | `MultiRenderObjects` | 19 B |

The extents total 120 bytes and exclude inter-array padding. Existing data
rows do not own these addresses. The ten exact keyed DIR32 baseline entries
require data ownership; no change to the recorded DIR32 registry is needed.

## Donor review and limits

Reviewed BFME 2 revision `3252f8ecf0ebd738896f2aea4780279ed29538b8`,
`Code/GameEngine/Source/GameClient/System/FXParticleSystem/RenderObjectDrawModuleTemplateWriteINI.cpp`.
Its three render groups use the same key sequence. This is supporting
cross-repository context only: BFME 1's own bytes establish all addresses,
spellings and extents, and its existing consumers establish the symbols.
No donor offsets, class layout, private declarations, includes or compiler
flags are imported. The donor's separate TU is not a BFME 1 provider.

## Admission and verification

Use `add_data_match.py` for each data row; it must prove emitted symbol size,
initial bytes and relocations before writing the ledger. Retire each exact
keyed baseline entry only through `repair_queue.py pass-test`, then verify
the entire source and run normal commit/publication hooks.
All ten data admissions passed: 120 bytes equal retail, with zero relocations
for each array and the expected emitted symbol extent. Padding is not admitted.

The first baseline pass-test exposed a source-discovery false rejection:
`locate_source` searched only literal decorated names, which these ordinary
C++ declarations do not contain. No baseline was removed by that refusal.
Commit `0b23c5947e` (rebased from `ed2854a6f2`) resolves an exact, unambiguous matched data-ledger owner
before the legacy literal search. Invalid or ambiguous recorded owners fail
closed; the normal build and baseline restoration remain unchanged.

The focused repair-queue tests pass 31/31 with `--noconftest`, including both
repository layouts, successful and failing normal gates, rollback, and invalid
or ambiguous owners. The shared cycle-provenance fixture fails before these
tests run on macOS and OrbStack (the latter cannot resolve `/mnt/rv` in its
mapped-runtime inventory). The broader integration suite is not claimed as
passing; no cycle-provenance code or fixture was changed to hide that failure.

All ten exact baseline pass-tests completed successfully, each running the
ordinary source gate: 470/470 function rows, 31/31 data rows, 41 string literals,
93 floating constants and 1,025 recorded DIR32 references. The body guard reports
zero baselined findings for this source. The baseline shrinks by exactly these
ten keyed entries; no new allowance is added. Existing compiler cleanup labels
are reported as renumbered, with byte-equivalent bodies, not byte mismatches.
The report-only link preview is unknown while the source differs from the
staged state; it is not evidence of linked coverage.

No new C++ body bytes or linked-byte gain are claimed by this repair.

Before publication, upstream advanced through `c0385ef6ba`, including adjacent
FX ownership repairs and alias removal. The initial commit hook correctly
refused the stale source's alias. Parked this batch as a patch, rebased the
locator repair, and applied the source/data/evidence changes onto upstream.
The baseline deletion conflicted with upstream's adjacent deletions; restored
the upstream baseline and reran the ten normal `pass-test` operations instead
of resolving the deletion by hand. Upstream repairs remain intact.
All ten rebased pass-tests passed: 470/470 functions, 32/32 data rows,
44 string literals, 93 float constants, and 1,022 DIR32 references, with zero
baselined body-guard findings. Focused locator tests still pass 31/31.
