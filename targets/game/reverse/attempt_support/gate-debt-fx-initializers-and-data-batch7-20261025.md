# FX initializers and recorded data references, seventh batch

Shard 3/4 repair queue served these entries in
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`
and `game/GameEngine/Source/Common/Rva00C6BEA0Initializers.cpp`.

| Retail VA | Retired reference | Repair / Existing recorded owner |
| --- | --- | --- |
| 0x011136B0 | `?g_011136B0@FXParticleSystem@@3QBDB` | Define existing `MultiChance` array (12 retail bytes with NUL, zero relocations) via add_data_match |
| 0x012F6D28 | `?Rva00EF6D28@@3PAXA` | Existing recorded owner `?terrainCollisionSourceAt8@FXParticleSystem@@3PAPAXA` |
| 0x012F6D2C | `?Rva00EF6D2C@@3PAXA` | Existing recorded owner `?terrainCollisionSourceAt4@FXParticleSystem@@3PAPAXA` |
| 0x012F6D3C | `?Rva00EF6D3C@@3PAXA` | Existing recorded owner `?sphericalEmissionVelocitySourceAt4@FXParticleSystem@@3PAPAXA` |
| 0x012F6D58 | `?Rva00EF6D58@@3PAXA` | Existing recorded owner `?pointEmissionVolumeSourceAt4@FXParticleSystem@@3PAPAXA` |
| 0x012F6D7C | `?Rva00EF6D7C@@3PAXA` | Existing recorded owner `?cylinderEmissionVolumeSourceAt4@FXParticleSystem@@3PAPAXA` |

The owner at every listed 0x012F6Dxx VA is already recorded in BFME 1's `dir32_addresses.csv`
and used across FXParticleSystem module TUs. Replaced only the placeholder external symbol
references with their canonical `FXParticleSystem::` namespace symbols; retained local
pointer types, stores, layout and ABI.

For 0x011136B0, retail PE `.rdata` contains `MultiChance\0` (12 bytes) passed to
`u4Next005F5120` in `fx_particle_system_bulk.cpp`. `add_data_match` verified 12 bytes
equal to retail with zero relocations.

Each exact keyed `repair_queue.py pass-test` passed and alone removed its baseline line.
All 470 bodies, 10 data rows, 24 literals, 93 float constants and 1025 DIR32 references
in `fx_particle_system_bulk.cpp` verify. All 67 bodies and 119 DIR32 references in
`Rva00C6BEA0Initializers.cpp` verify. Six exceptions retired; no escape hatch or C++ byte
credit is claimed.
