# Gate debt repairs, eleventh batch

Shard 0/5 repair queue served these entries across GUI and W3DDevice units.

| Retail VA | Retired baseline finding | Fix / Owner |
| --- | --- | --- |
| 0x012B3DC0 | `?TheShellHookNames@@3PAPADA` | Reference recorded owner `?TheShellHookNames@@3PAPBDA` in `AptMainMenuExitGame.cpp` |
| 0x01306E0C | `?nShadowDecalVertsInBuf@@3HA` | Add data match for `?nShadowDecalVertsInBuf@@3HA` in `W3DProjectedShadow.cpp` |
| 0x01306E10 | `?nShadowDecalStartBatchVertex@@3HA` | Add data match for `?nShadowDecalStartBatchVertex@@3HA` in `W3DProjectedShadow.cpp` |

Each exact keyed `repair_queue.py pass-test` passed and removed its baseline line from `body_guard_baseline.csv`.
All affected functions, data rows, literals, float constants, and DIR32 references verify with zero baselined findings.
3 exceptions retired; no escape hatches added.
