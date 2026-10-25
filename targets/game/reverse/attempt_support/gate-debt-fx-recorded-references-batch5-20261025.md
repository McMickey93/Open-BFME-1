# FX recorded references, fifth batch

Parent: ce5862f6f3. Shard 1/4 ranked repair queue served these entries in
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`.

| Retail VA | Retired reference | Existing recorded owner |
| --- | --- | --- |
| 0x011123E0 | `?g_vtbl_011123E0@@3PAPAXA` | `??_7Rva005EDDE0@@6BV3Slot0@@@` |
| 0x01112DD0 | `?g_vtbl_01112DD0@@3PAPAXA` | `??_7Rva005EC160@@6BV3Slot3@@@;` |
| 0x01112DE8 | `?g_vtbl_01112DE8@@3PAPAXA` | `??_7Rva005EC160@@6BV3Slot1@@@;` |
| 0x01112E30 | `?g_vtbl_01112E30@@3PAPAXA` | `??_7Rva005ECF60@@6BV3Slot3@@@;` |
| 0x01112E48 | `?g_vtbl_01112E48@@3PAPAXA` | `??_7Rva005ECF60@@6BV3Slot1@@@;` |
| 0x01112E4C | `?g_vtbl_01112E4C@@3PAPAXA` | `??_7Rva005ECF60@@6BV3Slot0@@@;` |

The owner at every listed VA is already recorded in BFME 1's
`dir32_addresses.csv`. Replace only the extern array symbol and its single
vptr store; retain the array declaration type, casts, volatility, store offset,
layout and ABI. Remove the five existing alternate-name bindings rather than
adding any. The 0x011123E0 reference had no binding. No new identity or class
relationship is inferred from a spelling.

Each exact keyed `repair_queue.py pass-test` passes on its first attempt and
alone removes its baseline line. All 470 bodies, nine data rows, 24 literals,
93 float constants and 1042 DIR32 references verify. Six exceptions retired;
no new body, symbol pin, escape hatch or C++ byte credit is claimed.

Integration: rebased the preceding four local batches onto 69d6af4071.
Upstream repaired adjacent references in the same TU. Resolved declaration,
vptr-store and callback-table conflicts by retaining both sets of exact
recorded owners. Restored the upstream baseline at each conflicted commit,
then reran all ten original keyed pass tests to remove only this seat's keys.
The later two commits applied without conflicts; the subsequent six keyed
checks verify their combined TU as well. AGENTS.md was unchanged upstream.
The donor reference was not altered or used as identity proof.

Prior skipped ownership, implicit-vtable and code-versus-data cases remain
recorded in the fourth batch note. They require evidence beyond this lane's
mechanical repairs. Linking remains unknown because the local census lacks
required objects; these checks establish byte and keyed-gate correctness.
