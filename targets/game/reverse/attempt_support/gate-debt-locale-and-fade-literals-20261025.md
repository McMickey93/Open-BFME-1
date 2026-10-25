# STLport money_get vtables and ScreenCrossFadeFilter static member references

Input BFME 1 revision: `cec17e320d`.
Edited files:
- `game/Libraries/Source/STLport/MoneyGetConstructors.cpp`
- `game/GameEngineDevice/Source/W3DDevice/GameClient/ScreenCrossFadeFilterUpdateFadeLevelThunk.cpp`

No shared headers, providers, ledger identities, boundaries, layouts or ABI declarations change.

## Evidence

### 1. STLport money_get vtables (VA 0x0112E95C and 0x0112E9D8)

Retail image constructors at 0x00832200 and 0x00832280 install primary vtables at
0x0112E95C (narrow char specialization) and 0x0112E9D8 (wide wchar_t specialization).
Both primary vtables reach authentic matched scalar-deleting destructors in slot 0:
- `??_G?$money_get@DV?$istreambuf_iterator@DV?$char_traits@D@_STL@@@_STL@@@_STL@@MAEPAXI@Z` at RVA 0x00832300 in `MoneyGetCharDeletingDestructor.cpp`
- `??_G?$money_get@GV?$istreambuf_iterator@GV?$char_traits@G@_STL@@@_STL@@@_STL@@MAEPAXI@Z` at RVA 0x008323C0 in `MoneyGetWideDeletingDestructor.cpp`

The primary vtable ownership is fully proven by `dir32_record_guard.function_owner_problem`
via these slot 0 deleting destructors. The keyed pass-tests pass and remove both
exceptions from `targets/game/reverse/body_guard_baseline.csv`.

### 2. ScreenCrossFadeFilter static members (VA 0x01307204, 0x01307208, 0x0130720C)

The data items at VAs 0x01307204, 0x01307208, and 0x0130720C are already matched in
`targets/game/reverse/data_rows.csv` as:
- `?m_fadeDirection@ScreenCrossFadeFilter@@1HA` (0x01307204)
- `?m_fadeFrames@ScreenCrossFadeFilter@@1HA` (0x01307208)
- `?m_curFadeFrame@ScreenCrossFadeFilter@@1HA` (0x0130720C)
as evidenced in `targets/game/reverse/identity_evidence/00f07204-datum-type.md`,
`00f07208-datum-type.md`, and `00f0720c-datum-type.md`.

The consumer `ScreenCrossFadeFilterUpdateFadeLevelThunk.cpp` already correctly
references these exact matched symbols. The stale duplicate-decorated baseline
exceptions `??m_*...@@3HA` are deleted by their keyed pass-tests.

## Acceptance and verification

Scoped builds for both translation units pass with zero baselined findings:
- `MoneyGetConstructors.cpp`: 2/2 functions, 2 DIR32 references OK.
- `ScreenCrossFadeFilterUpdateFadeLevelThunk.cpp`: 2/2 functions, 19 DIR32 references OK.
All 5 keyed `repair_queue.py pass-test` commands succeed and remove their baseline
exceptions (gate debt 969 -> 964).
