# FX recorded references, third batch

Resumed preserved work at parent 8203a6e408. Shard 1/4 only.
The preceding session recorded successful keyed pass-tests for these five keys
and left their source changes and machine-removed baseline lines uncommitted.
This session independently reran the scoped build successfully.

| Retail VA | Retired reference | Existing recorded owner |
| --- | --- | --- |
| 0x0111221C | `?g_vtbl_0111221C@@3PAPAXA` | `??_7GenX005ED360@@6B@` |
| 0x01112248 | `?g_vtbl_01112248@@3PAPAXA` | `??_7Rva005ED4E0@@6BV3Slot1@@@` |
| 0x01112278 | `?g_vtbl_01112278@@3PAPAXA` | `??_7MidX005ED510@@6B@` |
| 0x011122D8 | `?g_vtbl_011122D8@@3PAPAXA` | `??_7Rva005ED7D0@@6BV3Slot2@@@` |
| 0x01112320 | `?g_vtbl_01112320@@3PAPAXA` | `??_7Rva005ED980@@6BV3Slot0@@@` |

Each owner is independently recorded at that VA in BFME 1
`targets/game/reverse/dir32_addresses.csv`. Replace the extern array and its
use with the existing exact decorated name through MSVC `__identifier`.
No inferred class identities, layout changes, new names, aliases or pins.
Store offsets and declaration types remain unchanged.

Verification: `./build.sh game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`
passes 470/470 functions, 24 literals, 93 float constants, 1042 DIR32 references
and the body guard (zero baselined findings in this TU).
Five baseline exceptions retired (972 -> 967). No authored C++ byte growth or
linking gain claimed. The pre-existing renumbered funclet labels are recognized
and verified by the build without ledger changes.
