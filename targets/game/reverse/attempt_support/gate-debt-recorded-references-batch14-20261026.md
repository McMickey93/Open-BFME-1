# Gate debt repairs, fourteenth batch

Shard 1/5 repair queue served these entries across GUI and Body units:

| Retail VA | Retired baseline finding | Fix / Owner |
| --- | --- | --- |
| 0x010A8FB0 | `??_7PorcupineFormationBodyModule@@6BObjectModule@@@` | Use recorded owner `??_7PorcupineFormationBodyModule@@6BBehaviorModule@@@` by deriving `ActiveBody` directly from `BehaviorModule` in `PorcupineFormationBodyModule.cpp` |
| 0x012F3F0C | `?textEntryGamePasswordID@@3W4NameKeyType@@A` | Add matched data row in `PopupHostGameInit.cpp` |
| 0x012F3F2C | `?textEntryLadderPassword@@3PAVGameWindow@@A` | Add matched data row in `PopupHostGameInit.cpp` |

Shard 2/5 repair queue served these entries across FXParticleSystem module templates in `fx_particle_system_bulk.cpp`:

| Retail VA | Retired baseline finding | Fix / Owner |
| --- | --- | --- |
| 0x011136D8 | `?g_011136D8@FXParticleSystem@@3QBDB` | Define `g_011136D8` as `"OffsetX"` (8 B) in `fx_particle_system_bulk.cpp` and register matched data row |
| 0x011136CC | `?g_011136CC@FXParticleSystem@@3QBDB` | Define `g_011136CC` as `"OffsetY"` (8 B) in `fx_particle_system_bulk.cpp` and register matched data row |
| 0x011136A0 | `?g_011136A0@FXParticleSystem@@3QBDB` | Define `g_011136A0` as `"TileTexture"` (12 B) in `fx_particle_system_bulk.cpp` and register matched data row |
| 0x01113C94 | `?g_01113C94@FXParticleSystem@@3QBDB` | Define `g_01113C94` as `"Length"` (7 B) in `fx_particle_system_bulk.cpp` and register matched data row |
| 0x01114440 | `?g_01114440@FXParticleSystem@@3QBDB` | Define `g_01114440` as `"EventTime"` (10 B) in `fx_particle_system_bulk.cpp` and register matched data row |
| 0x01113E14 | `?g_01113E14@FXParticleSystem@@3QBDB` | Define `g_01113E14` as `"EndPoint"` (9 B) in `fx_particle_system_bulk.cpp` and register matched data row |
| 0x011142EC | `?g_011142EC@FXParticleSystem@@3QBDB` | Define `g_011142EC` as `"Frequency1"` (11 B) in `fx_particle_system_bulk.cpp` and register matched data row |
| 0x011142D4 | `?g_011142D4@FXParticleSystem@@3QBDB` | Define `g_011142D4` as `"Frequency2"` (11 B) in `fx_particle_system_bulk.cpp` and register matched data row |
| 0x011142AC | `?g_011142AC@FXParticleSystem@@3QBDB` | Define `g_011142AC` as `"Frequency3"` (11 B) in `fx_particle_system_bulk.cpp` and register matched data row |
| 0x01113FD4 | `?g_01113FD4@FXParticleSystem@@3QBDB` | Define `g_01113FD4` as `"OtherSpeed"` (11 B) in `fx_particle_system_bulk.cpp` and register matched data row |

Each exact keyed `repair_queue.py pass-test` passed and removed its baseline line from `body_guard_baseline.csv`.
All affected functions (470), data rows (43), literals (44), float constants (93), and DIR32 references (1022) verify with zero baselined findings.
13 exceptions retired; no escape hatches added.
