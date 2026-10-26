# Gate debt repairs, twelfth batch

Shard 0/5 repair queue served these entries across Common and GameNetwork units.

| Retail VA | Retired baseline finding | Fix / Owner |
| --- | --- | --- |
| 0x00BEADA0 | `?rva007EADA0BindCallback@@YAXPAVRva007EA380Owner@@PAX1@Z` | Reference recorded owner `?rva007EADA0BindCallback@@YAXPAVRva007EA380Owner@@PAX1@Z` in `Rva007EAD30Send.cpp` |
| 0x00BF6FA0 | `?Rva007F6FA0BrowserRegionReply@@YAXPAVRva007E8810Message@@PAVRva007F7980Browser@@@Z` | Reference recorded owner `?Rva007F6FA0BrowserRegionReply@@YAXPAVRva007E8810Message@@PAVRva007F7980Browser@@@Z` in `BfmeThingDGDRva007F8400.cpp` |
| 0x012F6CC4 | `?Rva00EF6CC4@@3PAXA` | Reference recorded owner `?lightningDrawSourceAt4@FXParticleSystem@@3PAPAXA` in `Rva00C6BEA0Initializers.cpp` |

Each exact keyed `repair_queue.py pass-test` passed and removed its baseline line from `body_guard_baseline.csv`.
All affected functions, data rows, literals, float constants, and DIR32 references verify with zero baselined findings.
3 exceptions retired; no escape hatches added.
