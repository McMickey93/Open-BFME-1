# Gate debt repairs, fourteenth batch

Shard 1/5 repair queue served these entries across GUI and Body units.

| Retail VA | Retired baseline finding | Fix / Owner |
| --- | --- | --- |
| 0x010A8FB0 | `??_7PorcupineFormationBodyModule@@6BObjectModule@@@` | Use recorded owner `??_7PorcupineFormationBodyModule@@6BBehaviorModule@@@` by deriving `ActiveBody` directly from `BehaviorModule` in `PorcupineFormationBodyModule.cpp` |
| 0x012F3F0C | `?textEntryGamePasswordID@@3W4NameKeyType@@A` | Add matched data row in `PopupHostGameInit.cpp` |
| 0x012F3F2C | `?textEntryLadderPassword@@3PAVGameWindow@@A` | Add matched data row in `PopupHostGameInit.cpp` |

Each exact keyed `repair_queue.py pass-test` passed and removed its baseline line from `body_guard_baseline.csv`.
All affected functions, data rows, literals, float constants, and DIR32 references verify with zero baselined findings.
3 exceptions retired; no escape hatches added.
