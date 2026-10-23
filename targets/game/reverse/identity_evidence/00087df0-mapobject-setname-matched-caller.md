# 0x00087DF0: ?invoke@Rva00087DF0@@QAEXXZ is ?setName@MapObject@@QAEXABVAsciiString@@@Z

Matched-caller evidence (tools/matched_caller.py, census 2026-10-22 16:16 at 2615147aca), approved by the project lead 2026-10-23 after two adversarial review rounds.

- Row at 0x00087DF0: `?invoke@Rva00087DF0@@QAEXXZ` (placeholder name, matched real source).
- Proposed identity: `?setName@MapObject@@QAEXABVAsciiString@@@Z`.
- ILT oracle: `?setName@MapObject@@QAEXABVAsciiString@@@Z` CONFIRMED at 0x00087DF0 (p_false 2.0e-04; exact); no access-letter, cdecl/stdcall or trailing-type variant fits. The current name is CONTRADICTED.
- Matched callers (byte-identical to retail at their ledger home outside relocations, every other relocation landing where the ledger says), each with a REL32 to this body under the new name:
  - `?handleNameChange@@YAXPAVMapObject@@@Z` at 0x388970 (game/GameEngine/Source/Common/GameLogic_resetMethodThunk.cpp)

No other matched caller names this body differently, the name reaches no other body, and the ledger places it nowhere else (row, object-symbol= or pin).
