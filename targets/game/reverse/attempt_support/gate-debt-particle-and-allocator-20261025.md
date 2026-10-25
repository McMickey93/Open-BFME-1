# Seven DIR32 gate-debt exceptions retired

At BFME 1 31b5aabec1, the gate-debt queue served 252 DIR32 exceptions.
Seven keyed gate-debt baseline entries across shard 2/4 now pass their exact
`tools/repair_queue.py pass-test` and are retired from
`targets/game/reverse/body_guard_baseline.csv`:

1. `__fmode` (0x0134FBAC): Obsolete baseline entry; CRT startup stub and import bindings verified cleanly.
2. `?g_01114410@FXParticleSystem@@3QBDB` (0x01114410): Retail string literal "KillAfterEvent" in `fx_particle_system_bulk.cpp` (LightningDrawModuleTemplate and TerrainCollisionModuleTemplate writeINI).
3. `?g_01114424@FXParticleSystem@@3QBDB` (0x01114424): Retail string literal "PerParticle" in `fx_particle_system_bulk.cpp` (LightningDrawModuleTemplate and TerrainCollisionModuleTemplate writeINI).
4. `?g_vtbl_01111240@@3PAPAXA` (0x01111240): Recorded retail vtable `??_7?$ConcreteModuleTemplate@V?$ModuleTag@$04$E?LIGHTNING_EMISSION_MODULE_KEY@FXParticleSystem@@3QBDB$E?LIGHTNING_EMISSION_MODULE_NAME@2@3QBDBVLightningEmissionModule@2@VLightningEmissionModuleTemplate@2@V?$DefaultParticleModule@$04@2@V?$DefaultParticleModuleTemplate@$04@2@@FXParticleSystem@@@FXParticleSystem@@6B@` in `fx_particle_system_bulk.cpp`.
5. `?g_vtbl_01111258@@3PAPAXA` (0x01111258): Recorded retail vtable `??_7?$ConcreteModuleTemplate@V?$ModuleTag@$04$E?LIGHTNING_EMISSION_MODULE_KEY@FXParticleSystem@@3QBDB$E?LIGHTNING_EMISSION_MODULE_NAME@2@3QBDBVLightningEmissionModule@2@VLightningEmissionModuleTemplate@2@V?$DefaultParticleModule@$04@2@V?$DefaultParticleModuleTemplate@$04@2@@FXParticleSystem@@@FXParticleSystem@@6BLEMCT_VtblBaseA@@@` in `fx_particle_system_bulk.cpp`.
6. `??_7Rva007F0080Owner@@6B@` (0x0112A5C4): Recorded matched data owner `?g_0112A5C4@@3PAPAXA` (24-byte FESL allocator vtable table at VA 0x0112A5C4) referenced in `Rva007F0080DefaultPointers.cpp`.
7. `?g_vtbl_0111227C@@3PAPAXA` (0x0111227C): Recorded retail vtable `??_7GenX005ED510@@6B@` in `fx_particle_system_bulk.cpp` (`initializeCylindricalEmissionVelocityModule`).

## Verification

- Scoped builds pass for all modified translation units (`fx_particle_system_bulk.cpp` and `Rva007F0080DefaultPointers.cpp`) with zero baselined findings.
- Keyed `repair_queue.py pass-test` passed for all seven entries; `body_guard_baseline.csv` reduced by 7 (debt 964 -> 957).
- `link_check` and `progress.py origin/master`: +0 B exact C++, +0 B linked.
- No new aliases, pins, escape hatches, or unrecorded globals introduced.
