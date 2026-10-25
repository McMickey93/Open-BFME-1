# Two AI state vtable ownership debts

This is the gate-debt fallback for the convert seat. The source already uses
compiler-emitted primary vtable symbols. Retire two unused stand-in records and
remove only their two DIR32 exceptions through the sanctioned tools. This
completes the existing ownership repair; no source, layout, ABI, name, address,
function row, symbol pin or executable byte changes.

## BFME 1 identity and boundaries

Evidence is from the BFME 1 retail-1.03-unpacked image and current matched rows:

| Primary vtable VA | Dedicated slot zero | Matched deleting destructor RVA | Named constructor RVA / size |
| --- | --- | --- | --- |
| `0x0109A640` | VA `0x00449BBB` jumps to VA `0x00585410` | `0x00185410` / 30 B, `??_GAIAttackFireDuringApproachState@@UAEPAXI@Z` | `0x0017F780` / 72 B |
| `0x0109A738` | VA `0x0043E30B` jumps to VA `0x00585490` | `0x00185490` / 30 B, `??_GAIAttackMeleeSquishState@@UAEPAXI@Z` | `0x0017F860` / 70 B |

The constructors have literal class names and install these table addresses.
The tables independently reach matched, non-generated deleting destructors of
exactly their respective classes. `dir32_record_guard.function_owner_problem`
checks the primary-table starts, slot bounds, exact class identity and absence
of foreign deleting destructors. The sanctioned `dir32_record.py retire`
accepted both ownership proofs and found no active source mentions of either
obsolete name, including bare identifiers:

- `?g_AIAttackFireDuringApproachStateVTable@@3HA`
- `?g_AIAttackMeleeSquishStateVTable@@3HA`

Consumers are `game/GameEngine/Source/GameLogic/AI/` files
`AIAttackFireDuringApproachStateCtor.cpp` and
`AIAttackMeleeSquishStateCtor.cpp`. The existing canonical provider is
`AITargetMovementDeletingDestructors.cpp`. Existing complete-destructor rows
at RVAs `0x00185440` and `0x001854C0` and FireDuringApproach `onExit` at
`0x00176A40` remain unchanged. No class-layout inference is needed for this
record-only repair.

## Donor review

Reviewed read-only BFME 2 revision
`16c3ea885a293dafc872dd5b67a59fa92b1d6407`,
`Code/GameEngine/Source/GameLogic/AI/AIStates.cpp`, the declarations around
lines 748 and 795, and its recent path history. The same class family exists,
but its table addresses (`0x00C12798`, `0x00C12868`) are executable-specific.
No donor layout, name, source or address was imported. The ownership proof
above is independently established by BFME 1 matched rows and retail slots.
The donor pointer and all compiler settings remain unchanged.

## Acceptance and measurements

- Both `repair_queue.py pass-test LINE` checks pass, each removing its exact
  DIR32 baseline line and running the consumer's normal scoped byte gate:
  1/1 matched, one verified literal, one verified DIR32 reference and zero
  body-guard findings each.
- `./build.sh game/GameEngine/Source/GameLogic/AI/AITargetMovementDeletingDestructors.cpp`
  passes 11/11 matched rows, with zero body-guard findings.
- Record size decreases 17,305 -> 17,303. Gate debts decrease 1,004 -> 1,002.
  Exact C++ and linked byte deltas are zero; this is a verified ownership
  prerequisite repair, not a conversion.
- `link_check.py` is run on both constructors and the provider. The published
  census cannot read 22,616 new/changed ledger objects; linking coverage is
  unknown where those objects affect dependency resolution. No newly linked
  bytes are claimed. Both constructors additionally report their existing
  selected-vtable mismatch (the selected definition is not retail's); this
  record-only debt repair does not repair COMDAT selection or establish that
  either complete unit links.

The earlier data-owner sweep did not inspect primary vtables. Its remaining
active aliases are not retired: absence of a reference was checked separately
for each of these two obsolete identities. Other primary-table candidates
retain active aliases or lack a complete ownership proof and are unchanged.
