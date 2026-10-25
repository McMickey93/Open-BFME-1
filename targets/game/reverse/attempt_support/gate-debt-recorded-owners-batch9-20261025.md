# Recorded owners and static data gate-debt retirement, ninth batch

Shard 2/5 repair queue served these entries across four TUs:

| Retail VA | Retired reference | Repair / Existing recorded owner | File |
| --- | --- | --- | --- |
| 0x01113A7C | `?g_01113A7C@FXParticleSystem@@3QBDB` | Exact static string `"IsHollow"` (9 B) added to `data_rows.csv` | `fx_particle_system_bulk.cpp` |
| 0x010C8EF0 | `??_7SupplyTruckAIUpdate@@6BRva010C8EF0Base@@@` | Existing recorded secondary vtable `??_7SupplyTruckAIUpdate@@6BST_Iface4@@@` | `SupplyTruckAIUpdate_ctor.cpp` |
| 0x010C8F0C | `??_7SupplyTruckAIUpdate@@6B?$Rva010C8F20Base@$01@@@` | Existing recorded secondary vtable `??_7SupplyTruckAIUpdate@@6BST_Iface3@@@` | `SupplyTruckAIUpdate_ctor.cpp` |
| 0x010C8F10 | `??_7SupplyTruckAIUpdate@@6BRva010C8F10Base@@@` | Existing recorded secondary vtable `??_7SupplyTruckAIUpdate@@6BST_Iface2@@@` | `SupplyTruckAIUpdate_ctor.cpp` |
| 0x010C8F20 | `??_7SupplyTruckAIUpdate@@6B?$Rva010C8F20Base@$00@@@` | Existing recorded secondary vtable `??_7SupplyTruckAIUpdate@@6BST_Iface1@@@` | `SupplyTruckAIUpdate_ctor.cpp` |
| 0x012F0898 | `?TheBfmeGameLogic@@3PAVBfmeGameLogicLike@@A` | Existing recorded singleton `?TheBfmeGameLogic@@3PAVGameLogic@@A` | `AIUpdateConditionCooldown0027BF60.cpp` |
| 0x012E6010 | `?g_bfmeArgDXE@@3UtagVARIANT@@A` | Existing recorded pointer `?g_bfmeArgDXE@@3PAEA` | `BfmeConv793.cpp` |

All owners and symbols are already recorded in BFME 1's `dir32_addresses.csv` or `data_rows.csv` at the
identical retail VAs. Replaced placeholder external symbol declarations and base class names with direct
references to the canonical recorded names, and added byte-verified static data row for "IsHollow".

Exact keyed `repair_queue.py pass-test` passed for all 7 items and alone removed each baseline line.
Scoped gate checks verify all bodies, literals and DIR32 references with zero baselined findings.
Baseline debt shrank by 7 lines. No escape hatches, pins or new guessed identities were added.
