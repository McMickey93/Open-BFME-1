# Waypoint and terrain constant-reference repairs

Input BFME 1 revision: `9d0986d781`. These are compatible replacements of
unresolved external float references with independently proven literal
operands. They remove two keyed gate debts, 990 -> 988, with no additional
authored C++ bytes or claimed linked-byte gain.

## BFME 1 evidence and acceptance

`AIFollowWaypointPathState::onEnter`, RVA `0x0017A8E0`, retains 622 bytes.
Its existing identity is established by constructor `0x0017F980` installing
vtable VA `0x0109A7B0`, slot +`0x10` via ILT `0x000306BB`. RET at
`0x0017AB4D` and following INT3 establish the end. Retail FCOM at
`0x0017A9D0` and FDIVR at `0x0017A9DD` read VA `0x0109A028`, whose bytes
`00 00 16 43` independently establish `150.0f`. Both expressions now use
that literal. Layout, comparison direction, division order, aggregate
return lifetime and all calls remain unchanged. The normal scoped build
and keyed `?g_bfmeRva0109A028@@3MB` pass-test verify the row, five strings,
two float operands, eight remaining DIR32 references and zero exceptions.

`HeightMapRenderObjClass::doPartialUpdate`, RVA `0x006D1D80`, retains
416 bytes through RET 0xC at `0x006D1F1D`. Its existing identity comes from
vtable VA `0x0111DC88`, slot 137 via ILT `0x0002E087`, installed by the
landed constructor at `0x006D1C80`. Retail FMUL at `0x006D1DB6`,
`0x006D1DDE`, `0x006D1E0A` and `0x006D1E36` reads VA `0x0109DF58`, whose
bytes `00 00 80 3d` establish `0.0625f`. All four products now use that
literal. Map ownership, dimensions, native x87 conversion helper, tile
stride, stack region and traversal remain unchanged. The normal scoped
build and keyed `?g_rva006D1D80Scale@@3MB` pass-test verify the row, four
float operands, six remaining DIR32 references and zero exceptions.

The readonly bytes were read from BFME 1 retail-1.03-unpacked, using the
PE image base to translate the VAs. No new data rows, definitions, pins,
aliases, names or registry entries were introduced. Comments retain the
former COFF names to let the keyed tests locate the repaired consumers.
The only baseline edits are the two successful test removals.

Compiler context stays MSVC 7.1 with each TU's existing cl controls:
waypoint `/O2 /Ob1 /DNDEBUG /DWIN32 /MD /EHsc` and terrain's existing
`/DNDEBUG /MD /EHsc` plus WWLib and GeneralsMD library includes. Earlier
attempt logs and `20261025-readonly-float-debt.md` were reviewed; the old
locator refusal is resolved by documenting the exact existing COFF name.

## Donor evidence and ruled-out adaptations

Read-only BFME 2 revision `e2fdc5620c5834c1c98de24aa3510d72e2cbcc69`,
`Code/GameEngine/Source/GameLogic/AI/AIFollowWaypointPathStateOnEnter.cpp`,
also expresses the length cap and numerator as `150.0f`. That corroborates
the literal spelling; BFME 1's own operands establish its value and uses.
Donor commit `51c9777d6f` links this TU through callee spelling repairs,
which are unrelated to the constant debt. No donor layouts, SSE flags,
649-byte extent, debug logging or callee changes are imported.

BFME 2 `Code/GameEngineDevice/Source/W3DDevice/GameClient/HeightMap.cpp`
and commit `27dac062bc` were inspected. That same-named method performs a
different vertex-block update, so it is inapplicable to BFME 1's tile walk.
The terrain repair relies solely on BFME 1 target evidence.
