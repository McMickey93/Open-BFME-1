# Gate Debt: Dir32 Recorded References and Data Matches Batch 15

Date: 2026-10-26
Model: gemini-3.8-flash-medium
Shard: 1/5

## Retired Baseline Entries

1. `0x00BF83F0`: `?g_00BF83F0@@YAXXZ`
   - Target line: `dir32,0x00BF83F0,?g_00BF83F0@@YAXXZ,"nothing in the ledger owns 0x00BF83F0. Give the datum a data row first (tools/add_data_match.py), or use an address name (g_Va<VA>)"`
   - Resolution: `functions.csv` records retail 0x00BF83F0 as `?Rva007F83F0Callback@@YAXPAVRva007E8810Message@@PAVBfmeHostBT@@@Z`. Replaced the placeholder reference in `game/GameEngine/Source/GameNetwork/BfmeThingDGDRva007F8400.cpp` with the recorded function name. Pass-test passed and baseline entry removed.

2. `0x01135D68`: `_bfmeVftAptValue`
   - Target line: `dir32,0x01135D68,_bfmeVftAptValue,"retail 0x01135D68 is already recorded as ??_7AptValue@@6B@ (+22 more); reference that name, not a new one"`
   - Resolution: Retail 0x01135D68 is recorded as `??_7AptValue@@6B@`. Replaced `_bfmeVftAptValue` and linker `/alternatename` in `game/Libraries/Source/EA/Apt/Rva008CEE40.cpp` with direct `__identifier("??_7AptValue@@6B@")`. Pass-test passed and baseline entry removed.

3. `0x01306E18`: `?nShadowDecalStartBatchIndex@@3HA`
   - Target line: `dir32,0x01306E18,?nShadowDecalStartBatchIndex@@3HA,"nothing in the ledger owns 0x01306E18. Give the datum a data row first (tools/add_data_match.py), or use an address name (g_Va<VA>)"`
   - Resolution: Added matched data row for `?nShadowDecalStartBatchIndex@@3HA` at 0x01306E18 in `game/GameEngineDevice/Source/W3DDevice/GameClient/Shadow/W3DProjectedShadow.cpp` (size 4, .data). Pass-test passed and baseline entry removed.

4. `0x01306E1C`: `?nShadowDecalPolysInBatch@@3HA`
   - Target line: `dir32,0x01306E1C,?nShadowDecalPolysInBatch@@3HA,"nothing in the ledger owns 0x01306E1C. Give the datum a data row first (tools/add_data_match.py), or use an address name (g_Va<VA>)"`
   - Resolution: Added matched data row for `?nShadowDecalPolysInBatch@@3HA` at 0x01306E1C in `game/GameEngineDevice/Source/W3DDevice/GameClient/Shadow/W3DProjectedShadow.cpp` (size 4, .data). Pass-test passed and baseline entry removed.

5. `0x01336E50`: `?TheEmptyAsciiString@@3VAsciiString@@A`
   - Target line: `dir32,0x01336E50,?TheEmptyAsciiString@@3VAsciiString@@A,"retail 0x01336E50 is already recorded as ?BfmeDefeatScreenTable@@3PAEA (+42 more); reference that name, not a new one"`
   - Resolution: Retail 0x01336E50 is recorded as `?TheEmptyString@AsciiString@@2V1@B` (`AsciiString::TheEmptyString`). Replaced `TheEmptyAsciiString` in `game/GameEngine/Source/Common/RTS/PlayerInit.cpp` with `AsciiString::TheEmptyString`. Pass-test passed and baseline entry removed.
