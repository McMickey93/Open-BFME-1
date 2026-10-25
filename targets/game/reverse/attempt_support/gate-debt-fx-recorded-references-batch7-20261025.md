# FX recorded references, seventh batch

Shard 2/5 repair queue served these entries in
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`.

| Retail VA | Retired reference | Existing recorded owner |
| --- | --- | --- |
| 0x01110EA4 | `?g_vtbl_01110EA4@@3PAPAXA` | `??_7?$DefaultParticleModuleTemplate@$05@FXParticleSystem@@6B@` |
| 0x0111140C | `?g_vtbl_0111140C@@3PAPAXA` | `??_7ParticleLifeEventModuleTemplate@FXParticleSystem@@6BPLEMT_IfaceB@1@@` |
| 0x01111420 | `?g_vtbl_01111420@@3PAPAXA` | `??_7ParticleLifeEventModuleTemplate@FXParticleSystem@@6BPLEMT_IfaceA@1@@` |
| 0x01111424 | `?g_vtbl_01111424@@3PAPAXA` | `??_7ParticleLifeEventModuleTemplate@FXParticleSystem@@6BPLEMT_Base@1@@` |
| 0x01111DEC | `?g_vtbl_01111DEC@@3PAPAXA` | `??_7MidX005EB830@@6B@` |
| 0x011121D4 | `?g_vtbl_011121D4@@3PAPAXA` | `??_7T1Derived_005E6580@@6BT1P2_005E3950@@@` |
| 0x01112234 | `?g_vtbl_01112234@@3PAPAXA` | `??_7Rva005ED4E0@@6BV3Slot2@@@` |
| 0x011122DC | `?g_vtbl_011122DC@@3PAPAXA` | `??_7Rva005ED7D0@@6BV3Slot1@@@` |
| 0x0111231C | `?g_vtbl_0111231C@@3PAPAXA` | `??_7Rva005ED980@@6BV3Slot1@@@` |
| 0x01112358 | `?g_vtbl_01112358@@3PAPAXA` | `??_7Rva005EDB10@@6BV3Slot2@@@` |
| 0x01112360 | `?g_vtbl_01112360@@3PAPAXA` | `??_7Rva005EDB10@@6BV3Slot0@@@` |

The owner at every listed VA is already recorded in BFME 1's `dir32_addresses.csv`.
Replaced each extern array symbol with direct references to the recorded retail
vtable name via `__identifier("...")`; retained array declaration types, casts,
volatility, store offsets, layout and ABI. Removed the two existing alternate-name
bindings. No new identity or class relationship was inferred.

Each exact keyed `repair_queue.py pass-test` passed and alone removed its
baseline line from `body_guard_baseline.csv`. All 470 bodies, nine data rows,
41 literals, 93 float constants and 1025 DIR32 references verify with zero
baselined findings.
11 exceptions retired; no new body, symbol pin, escape hatch or C++ byte credit
is claimed.
