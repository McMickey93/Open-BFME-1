# 0x002A9000: first-result join, 2026-10-25

The preferred bank is unchanged: 833 bytes, 22 relocations, 70 differing
non-relocation bytes, normalized shape 1.000. No conversion, linking gain or
new production definition is claimed. BFME 1 starting revision ad617ed1dc;
MSVC 7.1 through compile_cached, default BFME 1 /O2 context and the bank's
/DNDEBUG /MD. Every diagnostic object used a private build/experiments path.

## Independent target evidence

The previous investigation in
`targets/game/reverse/identity_evidence/0x002a9000-native-accessor.md`
establishes the 833-byte boundary (last RET +340, INT3 +341), primary vtable
010C37B8 slot 12, and the oracle-confirmed protected virtual bool decoration
`?approachTarget@SpecialAbilityUpdate@@MAE_NXZ`. The synthetic bfmeTwo940B
caller spelling does not establish a competing identity. This session read
all prior attempt entries and the ninety-trial native-accessor handoff.
`callees.py 0x002A9000 833` still reports nine direct targets. The coordinate
helper 002A5FB0 remains an unpinned thiscall with Coord3D* and float stack
arguments; its complete-body ABI evidence is in the earlier note.

The private baseline changes only the proven protected/bool declaration and
reproduces all 70 differences. Memory displacements and complete instruction
shape agree, with ESI/EDI receiver exchange and scratch-register differences.
No source, header, name, pin, global or ledger was changed.

## Donor applicability and compile refusal

Reviewed read-only BFME 2 revision
8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9,
`Code/GameEngine/Source/GameLogic/Object/Update/SpecialAbilityUpdate.cpp`,
matched approach step rva00450AE9 (689 bytes), and Zero Hour's Common/
Overridable.h and SpecialPower.h. The donor supports the override-resolution
relationship and target/AI control flow, but its approach-frame counter,
extra branches, field layout and /O1 /arch:SSE context differ. Its name and
layout were not imported as BFME 1 evidence.

The required donor compile stopped with `header dependency set changed during
trial`. Its diagnostics are in ignored
`build/bfme2_sweep/trials/492bb131f74b4b069cca14a5dc30b91f/`.
No usable trial.json was created, so no match command was run on its object.
This is a dependency-stability false-reject, not proof against the donor.
No tool, dependency receipt or path-check workaround was made.

## New tests and result

Both native mutable and const recursive friend_getFinalOverride overloads
again select the retail EDI receiver but emit 835 bytes. The first-result
join still uses `je +174; call; jmp +174; mov eax,ecx; cmp [eax+14],27`
where retail has `je +170; call; mov ecx,eax; cmp [ecx+14],27`.
The former adds two bytes and shifts later branches.

Six fresh field-lvalue tests asked whether preserving the resolved field's
address through the getter would change that join: return const int&, int&,
const int*, int*, or return int through a local const reference or pointer.
Pointer-return consumers dereference immediately. Every test retains the
same 835-byte/397-difference result (395 differing overlapping bytes plus
the two-byte extent delta), first difference +107. These are diagnostic
source forms, not proposals to change the real getter ABI.

Eight range-lifetime tests varied the saved comparison's scalar type, a float
intermediate, deferred comparison, and ordering relative to the resolver or
kind-of branch. None improves the bank; scalar narrowing leaves the same
join, while widening/deferment changes other instructions. Together with
the baseline and native reproduction, the paired trials CSV records sixteen
measurements and exact source hashes. Sources, objects, assembly and JSON
remain in ignored `build/banked-approach-20261025/`. The unchanged stronger
tracked bank is the resumable candidate.

Reopen for independently evidenced compiler context or a different cause of
the first-result join; do not repeat field-reference/pointer or range-type
variants. No necessity for assembly has been established.
