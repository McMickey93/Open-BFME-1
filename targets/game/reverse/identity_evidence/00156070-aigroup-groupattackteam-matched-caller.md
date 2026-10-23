# 0x00156070: ?groupGuardPosition@Open2Group156070@@QAEXPBUCoord3D@@W4GuardMode@1@W4CommandSourceType@1@@Z is ?groupAttackTeam@AIGroup@@QAEXPBVTeam@@HW4CommandSourceType@@@Z

Matched-caller evidence (tools/matched_caller.py, census 2026-10-22 16:16 at 2615147aca), approved by the project lead 2026-10-23 after two adversarial review rounds.

- Row at 0x00156070: `?groupGuardPosition@Open2Group156070@@QAEXPBUCoord3D@@W4GuardMode@1@W4CommandSourceType@1@@Z` (placeholder name, matched real source).
- Proposed identity: `?groupAttackTeam@AIGroup@@QAEXPBVTeam@@HW4CommandSourceType@@@Z`.
- ILT oracle: `?groupAttackTeam@AIGroup@@QAEXPBVTeam@@HW4CommandSourceType@@@Z` CONFIRMED at 0x00156070 (p_false 2.0e-04; exact); no access-letter, cdecl/stdcall or trailing-type variant fits. The current name is CONTRADICTED.
- Matched callers (byte-identical to retail at their ledger home outside relocations, every other relocation landing where the ledger says), each with a REL32 to this body under the new name:
  - `?doAttack@ScriptActions@@IAEXABVAsciiString@@0@Z` at 0x2f2840 (game/GameEngine/Source/GameLogic/ScriptEngine/ScriptActionsTeamOrders.cpp)

No other matched caller names this body differently, the name reaches no other body, and the ledger places it nowhere else (row, object-symbol= or pin).
