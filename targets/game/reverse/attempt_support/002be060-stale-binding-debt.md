# Giant Bird normal-flight binding debt

This is a stale-exemption repair of an existing matched body. The binding
was already fixed by BFME 1 commit f6e3ed117a2 through an extern declaration
of g_012F02D4 and a preprocessor synonym for g_Rva012F02D4. Remove that
redundant macro and spell the existing symbol directly at its one use.
No function, global definition, layout, type, callee or compiler setting changes.

Independent BFME 1 retail evidence: GiantBirdNormalFlightState::onEnter at
RVA 002BE060 pushes 1 at +AB, zero at +AD, VA 012F02D4 at +AF and the
goal pointer at +BC, then calls ILT 0000795A at +BF. The existing matched
route provider at RVA 002BCB60 pushes the same VA at +AC and calls the same
ILT at +B8. This establishes the shared argument binding without inventing
a semantic type for the wider memory region. The state's RET at +DB ends
its existing 220-byte extent. Existing state identity and layouts are retained.

The DIR32 ledger records ?g_012F02D4@@3HA at VA 012F02D4. The existing
matched four-byte data row assigns its int definition to
Rva002BCB60GoalRouting.cpp with sizeof 4 and zero-filled initial bytes.
Both that provider's bodies (selector 329 B and route 196 B) and its two
data rows pass the scoped build. No data row or pin is added or edited.
The callee scan confirms the unchanged ILTs 0000795A and 0002191D;
there is no new ABI declaration or callee dependency.

The prior onEnter attempt-log record describes the historical EDI/owner
register-allocation problem before the body landed. This repair does not
retry that reconstruction or alter its current matching control flow.

Donor review: BFME 2 master
8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9 has a matched 233-byte onEnter
at RVA 00369064 in Code/GameEngine/Source/GameLogic/Object/Update/AIUpdate/
GiantBirdNormalFlightStates.cpp, derived from this BFME 1 unit. Its /O1
/arch:SSE /G7 settings, offsets and g_00E01EC0 data access differ. Reviewed
that source and recent commits b7371fd660, e9f91c0e8d and 624568625f;
they offer no applicable stale-exemption repair. No donor code, names,
layouts or compiler changes are imported, and the pinned donor is unchanged.

Acceptance: repair_queue.py pass-test removes the obsolete
?g_Rva012F02D4@@3HA DIR32 exemption and passes all four state-unit rows,
three DIR32 references and zero body exemptions. ./build.sh on the state
unit also passes 4/4; the provider passes 2/2 plus both data items.
find_declared_unmatched.py and check_csv.py pass. Debt shrinks 1018 -> 1017;
progress.py origin/master reports +0 B exact C++.

link_check.py on the state unit before and after reports LINKED PREVIEW
UNKNOWN, LINKED 657 -> 657 bytes, with no unresolved name reported. The
published census lacks over 22,000 current objects here. No new linked-byte
credit is claimed.
