# AIGuardRetaliateAttackAggressorState::update

Retail constructor 0x0015F070 pushes the literal at VA 0x0109661C,
`AIGuardRetaliateAttackAggressorState`, and installs vtable 0x010965C8.
That table's slot 2 reaches the matching name getter at 0x0015F0E0, which
returns the same literal. Slot 6, the established State::update position,
contains ILT 0x000300B7, whose complete jump reaches 0x0015F0F0. This proves
`?update@AIGuardRetaliateAttackAggressorState@@UAE?AW4StateReturnType@@XZ`;
the previous dump identity was `?d_0015f0f0@@YAXXZ`. The bank's temporary
`?method@Rva0015F0F0@@QAEHXZ` was an opaque reconstruction, not a second
retail identity. The unrelated small Zero Hour update in the home TU is
replaced by this full BFME implementation.

The entry follows INT3 padding; every conditional branch remains inside the
body. The final virtual jump starts at +0x104 and ends at +0x107, followed
by INT3. The extent is exactly 263 bytes. The constructor and this body
independently witness machine +0x1C, exit conditions +0x24, attack substate
+0x40, and the added object ID +0x44. The address-derived layout views retain
the previous bank's field names rather than assigning semantic names to
unproven slots.

Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b,
Code/GameEngine/Source/GameLogic/AI/AIGuardRetaliateStates.cpp, supplies the
265-byte update at game.dat RVA 0x00545A46. Its normal goal/target checks,
nested null-target return, separate exit tests, boolean extension result,
and inline machine/ID accessors supply the C++ structure. BFME 1's observed
field offsets, virtual slots, deadline increment 20, and four actual direct
callees replace BFME 2's values. The donor's equal-arm controller expression
is unnecessary in BFME 1 and would add eleven bytes.

Checked callees are GameLogic::findObjectByID through ILT 0x0001F253,
StateMachine::getGoalObject through 0x0000E570, the existing opaque
Rva0015EBE0State::queryGuardContain through 0x00046E98, and
AIUpdateInterface::friend_setGoalObject through 0x000125E9. Existing pins
resolve all four; no pin, import alias, or address record is added. The
GameLogic enum spelling already has the same independently recorded ILT as
the int spelling. Its authentic hash lookup is visible but not inlined:
the complete emitted helper separately matches 82 retail bytes at
0x0009A510, with zero relocations. The hash-map object starts at +0xB0 and
its bucket vector at +0xB4.

The former bank emitted 268 bytes with 161 differing bytes. The donor control
flow and real lookup visibility recover the failure block; retaining native
inline machine and ID accessor layers removes the remaining register
rotation. The final named member emits all 263 bytes with six relocations.
The strict home-TU build verifies all eight ledger rows and seven DIR32
references. link_check remains LINKED 0 -> 0 bytes because the pre-existing
home TU has unresolved and duplicate providers; this change loses no linked
bytes. No header, shim, assembly, or escape hatch is changed. Trial receipts
are under build/sol3_guard_* and build/{gate,link}_home_0015f0f0.txt in ds-9.
