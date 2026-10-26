# Gate Debt: Dir32 Recorded References and Data Matches Batch 16

Date: 2026-10-26
Model: gemini-3.8-flash-medium
Shard: 1/5

## Retired Baseline Entries

1. `0x012F1298`: `?Elapsed0040E9E0@@3_JA`
   - Target line: `dir32,0x012F1298,?Elapsed0040E9E0@@3_JA,"nothing in the ledger owns 0x012F1298. Give the datum a data row first (tools/add_data_match.py), or use an address name (g_Va<VA>)"`
   - Resolution: Added matched data row for `?Elapsed0040E9E0@@3_JA` in `game/GameEngine/Source/GameClient/MovieFrame0040E9E0.cpp` (size 8, .data, initialized to 0). Pass-test passed and baseline entry removed.

2. `0x011132D4`: `?g_011132D4@@3QBDB`
   - Target line: `dir32,0x011132D4,?g_011132D4@@3QBDB,"retail 0x011132D4 is already recorded as ??_7LightningEmissionModule@FXParticleSystem@@6B@; reference that name, not a new one"`
   - Resolution: Retail 0x011132D4 is recorded as `??_7LightningEmissionModule@FXParticleSystem@@6B@`. Replaced `g_011132D4` in `game/GameEngine/Source/Common/V3CopyCtorForwarders.cpp` with direct reference `__identifier("??_7LightningEmissionModule@FXParticleSystem@@6B@")`. Pass-test passed and baseline entry removed.

3. `0x010A141C`: `?g_010A141C@FXParticleSystem@@3QBDB`
   - Target line: `dir32,0x010A141C,?g_010A141C@FXParticleSystem@@3QBDB,"nothing in the ledger owns 0x010A141C. Give the datum a data row first (tools/add_data_match.py), or use an address name (g_Va<VA>)"`
   - Resolution: Added matched data row for `?g_010A141C@FXParticleSystem@@3QBDB` in `game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp` (size 2, .rdata, "Y\0"). Pass-test passed and baseline entry removed.

4. `0x010F1A0C`: `?g_010F1A0C@FXParticleSystem@@3QBDB`
   - Target line: `dir32,0x010F1A0C,?g_010F1A0C@FXParticleSystem@@3QBDB,"nothing in the ledger owns 0x010F1A0C. Give the datum a data row first (tools/add_data_match.py), or use an address name (g_Va<VA>)"`
   - Resolution: Added matched data row for `?g_010F1A0C@FXParticleSystem@@3QBDB` in `game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp` (size 11, .rdata, "Amplitude1\0"). Pass-test passed and baseline entry removed.

5. `0x010FA90C`: `?g_010FA90C@FXParticleSystem@@3QBDB`
   - Target line: `dir32,0x010FA90C,?g_010FA90C@FXParticleSystem@@3QBDB,"nothing in the ledger owns 0x010FA90C. Give the datum a data row first (tools/add_data_match.py), or use an address name (g_Va<VA>)"`
   - Resolution: Added matched data row for `?g_010FA90C@FXParticleSystem@@3QBDB` in `game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp` (size 7, .rdata, "Radial\0"). Pass-test passed and baseline entry removed.
