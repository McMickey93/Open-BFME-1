# Recorded references and vtable owners, eighth batch

Shard 1/5 repair queue served these entries in various translation units.

| Retail VA | Retired reference | Repair / Existing recorded owner | Source TU |
| --- | --- | --- | --- |
| 0x0112B568 | `?g_0112B568@@3QBDB` | Reference recorded owner `?g_0112B568@@3PADA` (char array) | `game/GameEngine/Source/GameNetwork/Rva00809E40FeslAdmission.cpp` |
| 0x012D6DA8 | `?g_012D6DA8@@3_NA` | Reference recorded owner `?g_flag12D6DA8@@3_NA` (bool flag) | `game/GameEngineDevice/Source/W3DDevice/GameClient/CreateModifiedRenderObj00901B00.cpp` |
| 0x0110F9CC | `?g_vtbl_0110F9CC@@3PAPAXA` | Reference recorded owner `??_7?$CategoryModuleInfo@$03@FXParticleSystem@@6B@` | `game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp` |
| 0x01341288 | `?_TriVertexLocationOrientationTable@PointGroupClass@@0PAY02VVector3@@A` | Reference recorded public owner `?_TriVertexLocationOrientationTable@PointGroupClass@@2PAY02VVector3@@A` | `game/Libraries/Source/WWVegas/WW3D2/PointGroupClass_Init.cpp` |
| 0x010BE9EC | `??_7PartitionFilterFlammable@@6B@` | Reference recorded owner `?g_target_00292520@@3HA` | `game/GameEngine/Source/GameLogic/Object/Update/FireSpreadUpdate.cpp` |

All owners are established in BFME 1's `dir32_addresses.csv` and `data_rows.csv`.
Only placeholder or mismatched external symbol references were updated to use their recorded names;
underlying types, initializers, layouts and ABIs are preserved.

Each exact keyed `repair_queue.py pass-test` succeeded and alone removed its baseline line.
Baseline entries shrink 888 -> 882. No escape hatches, header modifications or linked byte credits claimed.
