# FX initializers and recorded vtable references, eighth batch

Shard 4/5 repair queue served these entries in
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`
and `game/GameEngine/Source/Common/Rva00C6BEA0Initializers.cpp`.

| Retail VA | Retired reference | Existing recorded owner |
| --- | --- | --- |
| 0x011122E0 | `?g_vtbl_011122E0@@3PAPAXA` | `??_7Rva005ED7D0@@6BV3Slot0@@@` |
| 0x012F6C9C | `?Rva00EF6C9C@@3PAXA` | `?defaultModuleTag6SourceAt8@FXParticleSystem@@3PAPAXA` |
| 0x012F6CE4 | `?Rva00EF6CE4@@3PAXA` | `?defaultModuleTag0SourceAt8@FXParticleSystem@@3PAPAXA` |
| 0x012F6CF0 | `?Rva00EF6CF0@@3PAXA` | `?defaultModuleTag3SourceAt4@FXParticleSystem@@3PAPAXA` |
| 0x012F6D00 | `?Rva00EF6D00@@3PAXA` | `?defaultModuleTag2SourceAt4@FXParticleSystem@@3PAPAXA` |
| 0x012F6D18 | `?Rva00EF6D18@@3PAXA` | `?lifeEventSourceAt8@FXParticleSystem@@3PAPAXA` |
| 0x012F6D20 | `?Rva00EF6D20@@3PAXA` | `?renderObjectUpdateSourceAt8@FXParticleSystem@@3PAPAXA` |
| 0x012F6D38 | `?Rva00EF6D38@@3PAXA` | `?sphericalEmissionVelocitySourceAt8@FXParticleSystem@@3PAPAXA` |
| 0x012F6D68 | `?Rva00EF6D68@@3PAXA` | `?boxEmissionVolumeSourceAt8@FXParticleSystem@@3PAPAXA` |
| 0x012F6D84 | `?Rva00EF6D84@@3PAXA` | `?lightningEmissionSourceAt4@FXParticleSystem@@3PAPAXA` |

The owner at every listed VA is already recorded in BFME 1's `dir32_addresses.csv`.
For 0x011122E0, replaced the placeholder extern symbol with a direct reference to
the recorded retail vtable `??_7Rva005ED7D0@@6BV3Slot0@@@` via `__identifier("...")`
in `initializePointEmissionVolumeModule`.
For each listed 0x012F6Dxx VA, replaced the placeholder external symbol references
in `Rva00C6BEA0Initializers.cpp` with their canonical `FXParticleSystem::` namespace
symbols; retained local pointer types, stores, layout and ABI.

Each exact keyed `repair_queue.py pass-test` passed and alone removed its baseline line.
All 470 bodies, 9 data rows, 41 literals, 93 float constants and 1025 DIR32 references
in `fx_particle_system_bulk.cpp` verify. All 67 bodies and 119 DIR32 references in
`Rva00C6BEA0Initializers.cpp` verify. 10 exceptions retired; no escape hatch or C++ byte
credit is claimed.
