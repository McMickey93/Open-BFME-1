# FX recorded references, sixth batch

Shard 3/4 repair queue served these entries in
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`.

| Retail VA | Retired reference | Existing recorded owner |
| --- | --- | --- |
| 0x01111E64 | `?g_vtbl_01111E64@@3PAPAXA` | `??_7MidX005EBA30@@6B@` |
| 0x01111EDC | `?g_vtbl_01111EDC@@3PAPAXA` | `??_7Rva005EBCC0Object@@6BV3Slot1@@@` |
| 0x0111204C | `?g_vtbl_0111204C@@3PAPAXA` | `??_7Rva005EC600@@6BV3Slot1@@@` |
| 0x011120B0 | `?g_vtbl_011120B0@@3PAPAXA` | `??_7Rva005ECA20Object@@6BV3Slot3@@@` |
| 0x011120C4 | `?g_vtbl_011120C4@@3PAPAXA` | `??_7Rva005ECA20Object@@6BV3Slot2@@@` |
| 0x01112190 | `?g_vtbl_01112190@@3PAPAXA` | `??_7Rva005ECCC0@@6BV3Slot0@@@` |
| 0x011121A4 | `?g_vtbl_011121A4@@3PAPAXA` | `??_7Rva005ED0D0@@6BV3Slot3@@@` |
| 0x01112E00 | `?g_vtbl_01112E00@@3PAPAXA` | `??_7Rva005EC870@@6BV3Slot3@@@` |
| 0x01112E14 | `?g_vtbl_01112E14@@3PAPAXA` | `??_7Rva005EC870@@6BV3Slot2@@@` |
| 0x01112E44 | `?g_vtbl_01112E44@@3PAPAXA` | `??_7Rva005ECF60@@6BV3Slot2@@@` |

The owner at every listed VA is already recorded in BFME 1's `dir32_addresses.csv`.
Replaced only the extern array symbol and its single vptr store; retained the array
declaration type, casts, volatility, store offset, layout and ABI. Removed the 10
existing alternate-name bindings rather than adding any.

Each exact keyed `repair_queue.py pass-test` passed and alone removed its baseline line.
All 470 bodies, nine data rows, 24 literals, 93 float constants and 1042 DIR32 references
verify. 10 exceptions retired; no new body, symbol pin, escape hatch or C++ byte credit
is claimed.
