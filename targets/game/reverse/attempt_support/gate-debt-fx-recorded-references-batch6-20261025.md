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

## Additional Shard 2/4 references

Shard 2/4 ranked repair queue served these entries in
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`.

| Retail VA | Retired reference | Existing recorded owner |
| --- | --- | --- |
| 0x01111DB4 | `?g_vtbl_01111DB4@@3PAPAXA` | `??_7GenX005EB6B0@@6B@` |
| 0x01111DF0 | `?g_vtbl_01111DF0@@3PAPAXA` | `??_7GenX005EB830@@6B@` |
| 0x01111E50 | `?g_vtbl_01111E50@@3PAPAXA` | `??_7TailX005EBA30@@6B@` |
| 0x01111E68 | `?g_vtbl_01111E68@@3PAPAXA` | `??_7GenX005EBA30@@6B@` |
| 0x01111FC4 | `?g_vtbl_01111FC4@@3PAPAXA` | `??_7BFMEDistLODClass@@6BPersistClass@@@` |
| 0x01112034 | `?g_vtbl_01112034@@3PAPAXA` | `??_7Rva005EC600@@6BV3Slot3@@@` |
| 0x01112174 | `?g_vtbl_01112174@@3PAPAXA` | `??_7Rva005ECCC0@@6BV3Slot3@@@` |
| 0x011121C0 | `?g_vtbl_011121C0@@3PAPAXA` | `??_7Rva005ED0D0@@6BV3Slot0@@@` |
| 0x01112DE4 | `?g_vtbl_01112DE4@@3PAPAXA` | `??_7Rva005EC160@@6BV3Slot2@@@` |
| 0x01112DEC | `?g_vtbl_01112DEC@@3PAPAXA` | `??_7Rva005EC160@@6BV3Slot0@@@` |

The owner at every listed VA is already recorded in BFME 1's
`dir32_addresses.csv`. Replaced each extern array symbol with direct references
to the recorded retail vtable name via `__identifier("...")`; retained array
declaration types, casts, volatility, store offsets, layout and ABI.
Removed the ten existing alternate-name bindings. No new identity or class
relationship was inferred.

Each exact keyed `repair_queue.py pass-test` passed and alone removed its
baseline line. All 470 bodies, nine data rows, 41 literals, 93 float constants
and 1025 DIR32 references verify with zero baselined findings.
Ten exceptions retired; no new body, symbol pin, escape hatch or C++ byte credit
is claimed.
is claimed.
