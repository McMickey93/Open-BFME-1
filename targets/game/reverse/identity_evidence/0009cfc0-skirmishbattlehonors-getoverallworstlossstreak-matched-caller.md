# 0x0009CFC0: ?Rva0009CFC0@Gen000A9490Owner@@QAEXXZ is ?getOverallWorstLossStreak@SkirmishBattleHonors@@QBEHXZ

Matched-caller evidence (tools/matched_caller.py, census 2026-10-22 16:16 at 2615147aca), approved by the project lead 2026-10-23 after two adversarial review rounds.

- Row at 0x0009CFC0: `?Rva0009CFC0@Gen000A9490Owner@@QAEXXZ` (placeholder name, matched real source).
- Proposed identity: `?getOverallWorstLossStreak@SkirmishBattleHonors@@QBEHXZ`.
- ILT oracle: `?getOverallWorstLossStreak@SkirmishBattleHonors@@QBEHXZ` CONFIRMED at 0x0009CFC0 (p_false 4.6e-04; exact); no access-letter, cdecl/stdcall or trailing-type variant fits. The current name is CONTRADICTED.
- Matched callers (byte-identical to retail at their ledger home outside relocations, every other relocation landing where the ledger says), each with a REL32 to this body under the new name:
  - `?_bfme_updateSkirmishBattleHonors@@YAXPAVPlayer@@@Z` at 0xa41f0 (game/GameEngine/Source/Common/BfmeUpdateSkirmishBattleHonors.cpp)
  - `?apply@Rva005674F0Profile@@QAEXVSkirmishPreferences@@@Z` at 0x5674f0 (game/GameEngine/Source/GameClient/GUI/Rva005674F0Profile.cpp)

No other matched caller names this body differently, the name reaches no other body, and the ledger places it nowhere else (row, object-symbol= or pin).
