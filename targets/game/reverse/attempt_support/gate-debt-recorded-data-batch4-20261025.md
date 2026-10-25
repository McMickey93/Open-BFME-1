# Recorded data references, fourth gate-debt batch

Parent a457c32353; repair shard 1/4. Five keyed DIR32 pass tests remove
five exceptions (967 -> 962). All evidence is from BFME 1.

| VA | Previous reference | Repair |
| --- | --- | --- |
| 0x0111235C | `?g_vtbl_0111235C@@3PAPAXA` | Existing `??_7Rva005EDB10@@6BV3Slot1@@@` |
| 0x01112384 | `?g_vtbl_01112384@@3PAPAXA` | Existing `??_7Rva005EDC80@@6BV3Slot3@@@` |
| 0x011123C4 | `?g_vtbl_011123C4@@3PAPAXA` | Existing `??_7Rva005EDDE0@@6BV3Slot3@@@` |
| 0x011136C0 | `?g_011136C0@FXParticleSystem@@3QBDB` | Define the existing array as `OffsetZ` plus NUL, eight bytes |
| 0x0130B19C | `?g_bfmeRva0130B19CStatic@@3VGen_0081c9c0@@A` | Existing `?Rva0130B19CVideoTable@@3V?$vector@UVideo@@V?$allocator@UVideo@@@_STL@@@_STL@@A` |

The four chosen owners already occur at their VAs in dir32_addresses.csv.
Only extern symbol references change; local declaration types, stores and
calls are preserved. This does not infer any class hierarchy or reconcile
private class views. The video initializer still calls the same member
with the same allocator pointer and registers the same destructor callback.

Retail PE data at VA 0x011136C0 starts `OffsetZ\0\0\0\0\0OffsetY\0`.
The source already references this address as the string argument for the
Z-offset in LightningDrawModuleTemplate::writeINI. Preserve its existing
name and type, defining eight bytes through the terminator. add_data_match
independently proves sizeof 8, equal retail bytes, and zero target
relocations before writing its data row. Alignment padding is unclaimed.
The first keyed test could not locate the source because its exact
decorated name was absent; adding its symbol comment makes the second pass.

Every FX test passes 470 functions, nine data rows, 24 literals, 93 float
constants and 1042 DIR32 references. The video initializer test passes two
functions and six DIR32 references. No baseline was edited by hand.
No new function or pin, no C++ byte growth, no linked-byte gain claimed.
The existing FX linking preview is unknown because census objects are
unavailable and other aliases remain unresolved (see first FX batch note).

Thirteen other served keys were examined and recorded blocked in the
attempt log. Their causes: generated vtable declarations (including two
failed template lookup/declaration tests and one failed inline destructor
declaration test), absent vtable owners requiring extent/entry evidence,
static class-object ownership/type reconciliation, an unowned locale
placement-construction object, and a compiler vector ctor closure whose
address is a five-byte ILT thunk rather than data. Failed source edits
were restored and pass-test restored their keys. All skipped claims were
released. Repeat picks with unchanged evidence were left alone.

The ranked next_work repair queue, filtered to shard 1/4, supplies further
same-file recorded-owner leads at 0x011123E0, 0x01112DD0, 0x01112DE8,
0x01112E30, 0x01112E48 and 0x01112E4C. Claim and test each independently.
