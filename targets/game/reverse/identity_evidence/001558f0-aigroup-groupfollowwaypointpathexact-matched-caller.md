# 0x001558F0: ?notifyMembers@Rva001558F0Owner@@QAEXHH@Z is ?groupFollowWaypointPathExact@AIGroup@@QAEXPBVWaypoint@@W4CommandSourceType@@@Z

Matched-caller evidence (tools/matched_caller.py, census 2026-10-22 16:16 at 2615147aca), approved by the project lead 2026-10-23 after two adversarial review rounds.

- Row at 0x001558F0: `?notifyMembers@Rva001558F0Owner@@QAEXHH@Z` (placeholder name, matched real source).
- Proposed identity: `?groupFollowWaypointPathExact@AIGroup@@QAEXPBVWaypoint@@W4CommandSourceType@@@Z`.
- ILT oracle: `?groupFollowWaypointPathExact@AIGroup@@QAEXPBVWaypoint@@W4CommandSourceType@@@Z` CONFIRMED at 0x001558F0 (p_false 5.2e-04; exact); no access-letter, cdecl/stdcall or trailing-type variant fits. The current name is CONTRADICTED.
- Matched callers (byte-identical to retail at their ledger home outside relocations, every other relocation landing where the ledger says), each with a REL32 to this body under the new name:
  - `?doTeamFollowWaypointsExact@ScriptActions@@IAEXABVAsciiString@@0_N@Z` at 0x2f3240 (game/GameEngine/Source/GameLogic/ScriptEngine/ScriptActionsTeamMovement.cpp)

No other matched caller names this body differently, the name reaches no other body, and the ledger places it nowhere else (row, object-symbol= or pin).
