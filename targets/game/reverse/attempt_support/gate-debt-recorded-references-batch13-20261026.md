# Gate debt repairs, thirteenth batch

Shard 1/5 repair queue served these entries across FXParticleSystem and Common units:

| Retail VA | Retired baseline finding | Fix / Owner |
| --- | --- | --- |
| 0x0110F97C | `?g_vtbl_0110F97C@@3PAPAXA` | Reference recorded owner `??_7?$CategoryModuleInfo@$05@FXParticleSystem@@6B@` in `fx_particle_system_bulk.cpp` |
| 0x0110F9E4 | `?g_vtbl_0110F9E4@@3PAPAXA` | Reference recorded owner `??_7?$CategoryModuleInfo@$02@FXParticleSystem@@6B@` in `fx_particle_system_bulk.cpp` |
| 0x0111098C | `?g_vtbl_0111098C@@3PAPAXA` | Reference recorded owner `??_7LineEmissionVolumeInfo@FXParticleSystem@@6B@` in `fx_particle_system_bulk.cpp` |
| 0x01112218 | `?g_vtbl_01112218@@3PAPAXA` | Reference recorded owner `??_7MidX005ED360@@6B@` in `fx_particle_system_bulk.cpp` |
| 0x01112304 | `?g_vtbl_01112304@@3PAPAXA` | Reference recorded owner `??_7Rva005ED980@@6BV3Slot3@@@` in `fx_particle_system_bulk.cpp` |
| 0x012F6D64 | `?Rva00EF6D64@@3PAXA` | Reference recorded owner `?lineEmissionVolumeSourceAt4@FXParticleSystem@@3PAPAXA` in `Rva00C6BEA0Initializers.cpp` |
| 0x012F6D70 | `?Rva00EF6D70@@3PAXA` | Reference recorded owner `?sphereEmissionVolumeSourceAt8@FXParticleSystem@@3PAPAXA` in `Rva00C6BEA0Initializers.cpp` |
| 0x012F6D78 | `?Rva00EF6D78@@3PAXA` | Reference recorded owner `?cylinderEmissionVolumeSourceAt8@FXParticleSystem@@3PAPAXA` in `Rva00C6BEA0Initializers.cpp` |

Shard 2/5 repair queue served these entries across Common, GameLogic, and WWDebug units:

| Retail VA | Retired baseline finding | Fix / Owner |
| --- | --- | --- |
| 0x012F0898 | `?TheGameLogic0037C030@@3PAUGameLogic0037C030@@A` | Reference recorded owner `?TheGameLogic@@3PAVGameLogic@@A` in `EmotionNugget.cpp` |
| 0x01080294 | `_g_01080294` | Add data match for 2B newline string `_g_01080294` in `DebugExceptionhandler_LogRegisters.cpp` |
| 0x0112B598 | `??_7Rva007F5540VfptrCtor@@6B@` | Reference recorded owner `?g_bfmeVftBTWB@@3PAPAXA` in `UnclaimedVfptrCtors.cpp` |

Each exact keyed `repair_queue.py pass-test` passed and removed its baseline line from `body_guard_baseline.csv`.
All affected functions, data rows, literals, float constants, and DIR32 references verify with zero baselined findings.
11 exceptions retired; no escape hatches added.
