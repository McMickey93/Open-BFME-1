# AIGuardIdleState::update, RVA 0015E510

The matched constructor at0015CE80 passes the literal AIGuardIdleState at
VA01096234 to its State base, then installs table VA010961E0. Slot6 of
that table contains ILT00027FE3, whose JMP reaches0015E510. The exact name
getter at0015CEC0 provides a second literal witness. This establishes the
state identity independently of the byte match. The final RET at0015E631
ends the complete290-byte body at0015E632.

The bank's update logic and BFME team-guard extension were retained. Its
old drop-in context claimed the machine at+20; the retail instruction at
+2D reads it at+1C. The existing complete-destructor TU supplies the actual
State base relationship and novtable policy. The recovered state view puts
its machine at+1C, scan frame at+24 and guarded position at+28. No shared
State header is changed. Both the existing five-byte destructor at0015D180
and the new290-byte update verify in that same translation unit.

The four direct calls independently decode to object lookup0009A510 via
ILT0001F253; Team position average000EDCD0 via000241FE; the guard-machine
inner-target scan0015D530 via000317A5; and team lookup000EF060 via00044C2E.
The inner-target name uses the existing AIGuardMachine pin and is also used
by the matched AIGuardOuterState update. No new binding is introduced.

This body has the same control flow and position-copy shape as the newly
verified GiantBirdGuardIdleState update. With the corrected BFME layout and
the Team helper only declared, it emits290 bytes with14 differing bytes:
object-position loads and local stores interleave. Exposing the genuine
186-byte Team::getEstimateTeamPosition_000EDCD0 as inline
__declspec(noinline) fixes all14. A declaration-only control retains the
mismatch. The helper uses the established ObjectDlinkPmf.h traversal and
writes its Coord3D output without retaining the pointer. Its original ledger
owner remains Common/RTS/Rva000EDCD0TeamEstimatePosition.cpp.

Validation: the scoped gate passes2/2 for the entire destructor TU, including
all290 new bytes, the five existing destructor bytes, both float constants
and all four global references. A separate strict verification of the Team
row against this TU passes186 bytes, its float constant and function-pointer
binding. No assembly, volatile workaround, shared-header edit or new pin
is added. The rejected bank is removed by add_match after verification.
