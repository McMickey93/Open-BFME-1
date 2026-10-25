# Complete the NET_CRC_INTERVAL ownership repair

BFME 1 commit fe3654c6da8f84a6fea937bd62749be11b976d4b established
the existing matched four-byte int NET_CRC_INTERVAL at VA 012A7040 in
game/GameEngine/Source/GameNetwork/Network.cpp and changed seven matched
consumer units to use it. The data ledger records the release initializer
100, the retail dword 00000064, GameInfo::reset's copy into m_crcInterval,
and the command-line parser's atoi store. Zero Hour GeneralsMD's
GameNetwork/Network.cpp defines this int under the same name; its
GameInfo.cpp reset method establishes the source relationship. Those are
existing identity facts; this repair adds no identity or layout inference.

Three obsolete address records survived that ownership repair:
OpenBFME5_netCRCInterval, g_netCRCInterval and g_value12A7040. No old
identifier occurs in tracked game/ or inputs/reference/shims/ sources.
tools/dir32_record.py retire accepts all three removals for the already
matched NET_CRC_INTERVAL owner. No address record or pin is added. The
provider comment documents its exact external symbol for repair_queue.py's
existing keyed source locator. Function bodies, extents, calling conventions,
data layout, compiler flags and the initializer remain unchanged.

BFME 2 read-only revision 16c3ea885a293dafc872dd5b67a59fa92b1d6407 was
reviewed with narrow symbol searches and GameInfoReset.cpp history
(71e5a5bb79). Its GameLogic/System/GameLogicPopulateGameReport.cpp owns
NET_CRC_INTERVAL and GameNetwork/GameInfoReset.cpp consumes it; that
ownership placement differs from BFME 1's independently established native
Network.cpp owner. No donor source, address, name or provider placement is
imported. The pinned BFME 1 reference remains unchanged.

Acceptance: repair_queue.py pass-test removes the keyed DIR32 exemption
and reports PASS (1015 -> 1014 debts). Network.cpp verifies 17/17 matched
functions, 2/2 data rows and four DIR32 references, with zero body exemptions.
Normal scoped builds of the seven consumers verify 38/38 functions and
173 DIR32 references, also with zero exemptions: GameInfo_resetMethodThunk,
T3CommandLineParsers, RecorderClassConstructor, RecorderLogCRCMismatch,
RecorderDumpCommandHistory, RecorderStartRecording and
GameLogicPopulateGameReport. The dump-command unit also verifies its 13
jump-table entries. CSV integrity, declared-unmatched and whitespace checks
pass. Existing Network funclet label-renumbering notices resolve to matching
emitted bodies; this repair does not change their ledger entries.

link_check.py Network.cpp --compile-limit 0 is run before and after.
Both results display 0 -> 0 linked bytes and LINKED PREVIEW UNKNOWN
because 22,653 census objects are missing or stale. It also reports existing
unresolved Network members and incompatible/duplicate COMDAT providers.
No linked-byte improvement is claimed. The measured improvement is one fewer
gate exemption and three fewer obsolete address records, completing the
existing data-ownership prerequisite; exact C++ coverage grows by zero bytes.
