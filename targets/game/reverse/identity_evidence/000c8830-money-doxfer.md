# 0x000C8830 is Money::DoXfer

Baseline: `inputs/baselines/bfme1/retail-1.03-unpacked/files/lotrbfme.exe`,
image base 0x00400000. Investigator: claude-opus-5-5 (worker w2), 2026-10-20.

## Old claim

`?bfmeSeed@Gen_000C8830@@QAEXPAVBfmeSeedTarget@@@Z` in
`game/GameEngine/Source/Common/S3SeedPairsShort.cpp`: an opaque,
address-derived placeholder grouped with three byte-similar twins. It names
no owner class and no method.

## Vtable evidence

Money's vftable at VA 0x01083D18, read from the retail image:

| Slot | Pointer | ILT target | Ledger row |
| --- | --- | --- | --- |
| 0 | 0x00442B27 | 0x000CD530 | `??_GMoney@@MAEPAXI@Z` |
| 1 | 0x004461D2 | 0x000CBAC0 | `?loadPostProcess@Money@@MAEXXZ` |
| 2 | 0x0044237F | 0x000CBAD0 | |
| 3 | 0x00435594 | 0x000C8830 | this body |

The table is stored by the matched copy constructor
`??0Money@@QAE@ABV0@@Z` (0x000E1540, store at RVA 0x000E1548) and by four
other Money installers (0x000CBAA6, 0x000DD9DF, 0x000E2EB5, 0x000E37A0).
Slot 3 is the BFME Snapshot DoXfer slot, as for GhostObject (0x001B3B70),
TeamFactory (0x000EF0D0) and GarrisonContain (0x0021DAA0).

## ILT oracle

`python3 tools/ilt_oracle.py check '?DoXfer@Money@@MAEXAAVXfer@@@Z'
0x000C8830` prints `CONFIRMED p_false=5.87e-04 (exact)`.

## Body

48 bytes, `ret 4` at +0x2D. It writes the version pair {1, 1} into a frame
slot, calls Xfer slot 10 (`operator==(Version&)`), then Xfer slot 29
(`operator==(unsigned int&)`, xferUnsignedInt) on `this+4`. That is GeneralsMD
`Money::xfer`: version 1, then `xferUnsignedInt(&m_money)`. Money's first data
member after the vptr is `m_money`.

`game/GameEngine/Source/Common/RTS/Money_xfer.cpp` reproduces all 48 bytes
(`tools/probe.py`: EXACT).
