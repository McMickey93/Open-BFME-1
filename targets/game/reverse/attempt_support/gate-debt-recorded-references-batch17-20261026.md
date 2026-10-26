# Gate Debt: Dir32 Recorded References and Data Matches Batch 17

Date: 2026-10-26
Model: gemini-3.8-flash-medium
Shard: 1/5

## Retired Baseline Entries

1. `0x012F7728`: `?g_012F7728@@3IA`
   - Target line: `dir32,0x012F7728,?g_012F7728@@3IA,"nothing in the ledger owns 0x012F7728. Give the datum a data row first (tools/add_data_match.py), or use an address name (g_Va<VA>)"`
   - Resolution: Defined `extern "C" unsigned int __identifier("?g_012F7728@@3IA") = 0;` in `game/GameEngine/Source/GameNetwork/Network_update.cpp` and added matched data row with identity evidence. Keyed pass-test passed and baseline entry removed.

2. `0x0044A4E4`: `??0Rva004029F0@@QAE@XZ`
   - Target line: `dir32,0x0044A4E4,??0Rva004029F0@@QAE@XZ,"retail 0x0044A4E4 is already recorded as ??0PathfindZoneBlock@@QAE@XZ; reference that name, not a new one"`
   - Resolution: Replaced class placeholder `Rva004029F0` with recorded class name `PathfindZoneBlock` in `game/GameEngine/Source/GameLogic/AI/PathfindZoneManager_allocateBlocks_Thunk.cpp`. Keyed pass-test passed and baseline entry removed.

3. `0x012B4FC8`: `?g_lighting012B4FC8@@3URva00748860Triple@@A`
   - Target line: `dir32,0x012B4FC8,?g_lighting012B4FC8@@3URva00748860Triple@@A,"retail 0x012B4FC8 is already recorded as ?HighlightColors@@3PAUColor@@A (+2 more); reference that name, not a new one"`
   - Resolution: Referenced recorded sibling `Value012B4FC8` (`?Value012B4FC8@@3ULightingCoord00747FF0@@A`) in `game/GameEngineDevice/Source/W3DDevice/GameClient/Rva00748860WriteGlobalLighting.cpp`. Keyed pass-test passed and baseline entry removed.
