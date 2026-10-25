# Recorded owners and vtable references gate-debt retirement, eighth batch

Shard 0/5 repair queue served these entries across five TUs:

| Retail VA | Retired reference | Repair / Existing recorded owner | File |
| --- | --- | --- | --- |
| 0x012F4B58 | `?shell004B1C80@@3PAUShell004B1C80@@A` | Existing recorded singleton `?TheShell@@3PAVShell@@A` | `AnimateButtons004B1C80.cpp` |
| 0x01110A4C | `?g_vtbl_01110A4C@@3PAPAXA` | Existing recorded vtable `??_7CylinderEmissionVolumeInfo@FXParticleSystem@@6B@` | `fx_particle_system_bulk.cpp` |
| 0x012F19E8 | `?g_theWindowManager@@3PAVBfmeC977@@A` | Existing recorded owner `?g_theWindowManager@@3PAVWindowManager@@A` | `LivingWorldManagerUpdate.cpp` |
| 0x012F6D5C | `?Rva00EF6D5C@@3PAXA` | Existing recorded owner `?pointEmissionVolumeSourceAt8@FXParticleSystem@@3PAPAXA` | `Rva00C6BEA0Initializers.cpp` |
| 0x012F6D74 | `?Rva00EF6D74@@3PAXA` | Existing recorded owner `?sphereEmissionVolumeSourceAt4@FXParticleSystem@@3PAPAXA` | `Rva00C6BEA0Initializers.cpp` |
| 0x010966F8 | `_bfmeVftAIHarvestApproachSiteState` | Existing recorded vtable `??_7Rva0015FD00State@@6B@` | `AIHarvestMachine.cpp` |

All owners are already recorded in BFME 1's `dir32_addresses.csv` or `data_rows.csv` at the
identical retail VAs. Replaced placeholder external symbol declarations and `/alternatename`
pragmas with direct references to the canonical recorded names.

Exact keyed `repair_queue.py pass-test` passed for all 6 items and alone removed each baseline line.
Scoped gate checks verify all bodies, literals and DIR32 references with zero baselined findings.
Baseline debt shrank by 6 lines. No escape hatches, pins or new identities were added.
