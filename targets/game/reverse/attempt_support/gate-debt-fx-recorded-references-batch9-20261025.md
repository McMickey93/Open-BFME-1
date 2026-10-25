# FX recorded references, ninth batch

Shard 0/5 repair queue served these entries in
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`.

| Retail VA | Retired reference | Existing recorded owner |
| --- | --- | --- |
| 0x0110F9E8 | `?g_vtbl_0110F9E8@@3PAPAXA` | `??_7?$CategoryModuleInfo@$01@FXParticleSystem@@6B@` |
| 0x0111144C | `?g_vtbl_0111144C@@3PAPAXA` | `??_7ParticleTerrainCollisionModuleTemplate@FXParticleSystem@@6BTerrainCollisionTemplateIfaceA@1@@` |
| 0x01111450 | `?g_vtbl_01111450@@3PAPAXA` | `??_7ParticleTerrainCollisionModuleTemplate@FXParticleSystem@@6BTerrainCollisionModuleTemplate@1@@` |
| 0x011121E8 | `?g_vtbl_011121E8@@3PAPAXA` | `??_7MidX005ED230@@6B@` |
| 0x011121EC | `?g_vtbl_011121EC@@3PAPAXA` | `??_7GenX005ED230@@6B@` |
| 0x0111224C | `?g_vtbl_0111224C@@3PAPAXA` | `??_7Rva005ED4E0@@6BV3Slot0@@@` |
| 0x01112264 | `?g_vtbl_01112264@@3PAPAXA` | `??_7T1Derived_005E6850@@6BT1P2_005E3B90@@@` |
| 0x01112294 | `?g_vtbl_01112294@@3PAPAXA` | `??_7T1Derived_005E6940@@6BT1P2_005E3C90@@@` |
| 0x011122A8 | `?g_vtbl_011122A8@@3PAPAXA` | `??_7MidX005ED630@@6B@` |
| 0x011122C4 | `?g_vtbl_011122C4@@3PAPAXA` | `??_7Rva005ED7D0@@6BV3Slot3@@@` |
| 0x011123D8 | `?g_vtbl_011123D8@@3PAPAXA` | `??_7Rva005EDDE0@@6BV3Slot2@@@` |

The owner at every listed VA is already recorded in BFME 1's `dir32_addresses.csv`.
Replaced each extern array symbol with direct references to the recorded retail
vtable name via `__identifier("...")`; retained array declaration types, casts,
volatility, store offsets, layout and ABI. No new identity or class relationship was inferred.

Each exact keyed `repair_queue.py pass-test` passed and alone removed its
baseline line from `body_guard_baseline.csv`. All 470 bodies, 21 data rows,
41 literals, 93 float constants and 1025 DIR32 references verify with zero
baselined findings.
11 exceptions retired; no new body, symbol pin, escape hatch or C++ byte credit
is claimed.
