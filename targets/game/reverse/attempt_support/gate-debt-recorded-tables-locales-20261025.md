# Recorded table and locale-reference gate debts

Parent: 27bb9b337c. Served by the shard 1/4 repair queue.

Only external references change. Every replacement name already appears at
the same retail VA in BFME 1 dir32_addresses.csv; no new identity is inferred.
Retain the original array/pointer access type, indexing, calls and values.
Two declarations use MSVC __identifier to reference the exact recorded
linkage spelling while preserving their existing source types. No alias
bindings, symbol pins, data definitions, class changes or donor input added.
Comments preserve the retired key for provenance and pass-test discovery.

| Retail VA | Retired key | Recorded owner |
| --- | --- | --- |
| 0x0112B680 | `?Rva0112B680@@3PAPBXA` | `?g_0112B680@@3PAPBXA` |
| 0x010F9830 | `?g_010F9830@@3QBUFieldParse@@B` | `?g_010F9830@@3QBEB` |
| 0x012C83A0 | `_g_Rva012C83A0` | `?g_Rva012C83A0@@3PBDB` |
| 0x0130C0D8 | `_locale_buffer_00850560` | `_locale_buffer_0084ECE0` |
| 0x0130C4E8 | `_locale_buffer_008504C0` | `_locale_buffer_0084ECA0` |

All five exact keyed pass tests succeed and alone remove their exceptions:

- Rva007F56C0TableStores.cpp: 5/5 functions, 5 DIR32 references.
- HeaderTemplateCreation.cpp: 2/2 functions, 3 DIR32 references.
- stlport_LocaleFacets.cpp: 11/11 functions, 10 strings, 102 DIR32 references.
- LocaleCodePageQueries.c: 31/31 functions, 8 nonempty and 2 empty strings,
  63 DIR32 references; both buffer keys tested individually.

The first locale-pointer attempt used an ordinary C++ const-pointer declaration.
It preserved 11/11 function bodies but emitted ?g_Rva012C83A0@@3QBDB, which
the DIR32 test rejected and restored the exemption. The second attempt retains
the original const-char-pointer type and uses the exact recorded symbol
?g_Rva012C83A0@@3PBDB through __identifier; all references then verify.
No third attempt or gate workaround was needed.

Scoped build.sh runs verify all four final units; normal commit hooks recheck
the combined batch. Baseline entries shrink 932 to 927. progress.py reports
+0 B exact C++; retiring five keyed exceptions is credited gate repair work.
Linking improvement is unclaimed: missing/stale local census dependencies
make current linking previews unknown.
