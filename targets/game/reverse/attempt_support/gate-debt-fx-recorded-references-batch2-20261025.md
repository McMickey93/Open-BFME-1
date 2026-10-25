# FX recorded references, second batch

Parent: df2a8a7b0b. Same TU, toolchain, compiler flags and evidence basis as
[the first batch](gate-debt-fx-recorded-references-20261025.md).
This batch uses only gate-debt shard 1/4 entries served by next_work.

| Retail VA | Reference retired | Recorded owner |
| --- | --- | --- |
| 0x01112050 | `?g_vtbl_01112050@@3PAPAXA` | `??_7Rva005EC600@@6BV3Slot0@@@` |
| 0x011120CC | `?g_vtbl_011120CC@@3PAPAXA` | `??_7Rva005ECA20Object@@6BV3Slot0@@@` |
| 0x01112188 | `?g_vtbl_01112188@@3PAPAXA` | `??_7Rva005ECCC0@@6BV3Slot2W@@@` |
| 0x011121BC | `?g_vtbl_011121BC@@3PAPAXA` | `??_7Rva005ED0D0@@6BV3Slot1@@@` |
| 0x01112204 | `?g_vtbl_01112204@@3PAPAXA` | `??_7T1Derived_005E6670@@6BT1P2_005E3A20@@@` |

Each owner is already present at this VA in BFME 1 dir32_addresses.csv.
The first four aliases already named the same owners. The fifth reference
(0x01112204) had no alias; use the existing owner the queue recommends.
No class hierarchy or layout is inferred from these names. Existing array
declaration types, memory-store offsets and callback ABI remain unchanged.

Each exact repair_queue pass-test succeeds: 470 matched bodies, eight data
rows, 24 literals, 93 float constants, 1042 DIR32 references. Only pass-test
removed baseline lines: 977 to 972 debts. All five tests pass on the first
attempt; the helper stopped before editing 0x01112204 when its expected
alias was absent. Inspection confirmed a plain extern array reference,
which was then replaced and tested independently.

The prior donor search supplied no source or additional BFME 1 identity
proof; this batch relies on the BFME 1 records and scoped byte gates.
There are no new bodies or pins, no exact C++ byte growth, and no claimed
linking gain. Linking remains unknown for the reasons in the first note.

Next mechanical leads in shard 1/4 include g_vtbl_0111221C and subsequent
recorded-owner references in this TU. Recheck claims and current queue
before acting. Leave other shards untouched.
