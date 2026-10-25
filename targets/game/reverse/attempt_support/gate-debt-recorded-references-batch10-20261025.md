# Gate debt repairs, tenth batch

Shard 0/5 repair queue served these entries across GUI and game logic units.

| Retail VA | Retired baseline finding | Fix / Owner |
| --- | --- | --- |
| 0x004334F6 | `?j_000334f6@@YAXXZ` | Reference recorded `_HorseHordeContainFieldParse` in `HorseHordeContainFriendNewModuleDataThunk.cpp` |
| 0x01111FCC | `?g_vtbl_01111FCC@@3PAPAXA` | Reference recorded `??_7BFMEDistLODClass@@6BCompositeRenderObjClassPrimary@@@` in `fx_particle_system_bulk.cpp` |
| 0x012F3EFC | `?textEntryGameDescriptionID@@3W4NameKeyType@@A` | Add data match for `?textEntryGameDescriptionID@@3W4NameKeyType@@A` in `PopupHostGameInit.cpp` |
| 0x012F3F24 | `?buttonCancel@@3PAVGameWindow@@A` | Add data match for `?buttonCancel@@3PAVGameWindow@@A` in `PopupHostGameInit.cpp` |
| 0x012F3F44 | `?parentPopupID@PopupJoinGameState@@3W4NameKeyType@@A` | Reference recorded `?parentPopupID@PopupJoinGameState@@3HA` in `PopupJoinGameInit.cpp` |
| 0x01336E54 | `?emptyString01336E54@@3VUnicodeString@@A` | Reference canonical `UnicodeString::TheEmptyString` in `PopupHostGameInit.cpp` |

Each exact keyed `repair_queue.py pass-test` passed and removed its baseline line from `body_guard_baseline.csv`.
All affected functions, data rows, literals, float constants, and DIR32 references verify with zero baselined findings.
6 exceptions retired; no escape hatches added.
