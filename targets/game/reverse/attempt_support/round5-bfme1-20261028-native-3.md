# Script-condition team-list binding, 2026-10-28

Selected by the normal link queue after the original Object::getAI candidate became foreign-reserved. The existing 820-byte ScriptConditions::rva0032ABC0 owns the whole comparison switch and player/team/member walk. Its unresolved BfmeTeamInstanceLink spelling is a pin-only view of the existing matched ILT 0x00022A70, which jumps to 0x000C8A30 (4 bytes: 8b4114c3, this+0x14 pointer, ret). ScriptConditionsRva0032C990.cpp already forms the same pointer-to-member from j_00022a70, and ScriptConditionsRva00326C00.cpp uses the corresponding direct-call bridge. The trial preserves the existing non-const PMF type and complete caller body, and changes only its address factory. No pin, ledger identity, address admission or baseline changes.

BFME2 donor review: e7abc6a62c786c16dc79a9ee86df40894be49ff0, Code/GameEngine/Source/GameLogic/ScriptEngine/ScriptConditionsPlayerUnitCounts.cpp and ScriptConditions_evaluateTeamStateIs.cpp use Team::dlink_next_TeamInstanceList and a +0x334 prototype list. Those corroborate iteration only; BFME1 sibling, retail thunk and complete getter establish this repair. No BFME2 field offset or address is imported.

Follow-up on the SAME selected task: normal-gated fork blocker e192c3f67b14b9135551375c5c70d8c114ac3b49 / native run 40754078688. Read-only COFF review identified the exact extra section: the standalone static factory emitted six otherwise-unused bytes and shifted the following sections. This trial places the union conversion in the already-existing inline TeamPrototype method, introducing no standalone helper. The supplemental structural comparison remains strict and unchanged. No source from the rejected trial was carried forward.

Native run: https://github.com/McMickey93/Open-BFME-1/actions/runs/40758215934

Original compiler and unchanged ordinary project gates; no new C++ bytes, census measurement or game test.

Outcome: reviewed binding/emitter repair verified; affected source rows remain exact.

Qualification observations:

```json
{
  "reference": {
    "pinned": "20a0cb6173fd78ede36a2709f44422c73b80cc5a",
    "observed_upstream": "e103586cd8af2298bd5bed59bb9d66249af4e6aa",
    "pointer_changed": false,
    "newer_head_qualified": false,
    "freshness_update_blocked": true,
    "note": "Inspection uses current main BFME2 donor packets in the reviewed manifest; no donor-pointer update or success stamp is claimed."
  },
  "trials": [
    {
      "variant": "inline-ilt",
      "gate_exit": 0,
      "coff_proof": {
        "old_undefined": "?_bfme_nextInInstanceList@BfmeTeamInstanceLink@@QAEPAV1@XZ",
        "new_undefined": "?j_00022a70@@YAXXZ",
        "runtime_sections_identical_after_retarget": true,
        "external_definitions_identical": true,
        "only_reviewed_undefined_retarget": true,
        "retail_ilt_and_body_witness": {
          "0x22a70": {
            "bytes": "e9bb5f0a00",
            "instructions": [
              "jmp 0xc8a30"
            ]
          },
          "0xc8a30": {
            "bytes": "8b4114c3",
            "instructions": [
              "mov eax, dword ptr [ecx + 0x14]",
              "ret "
            ]
          }
        }
      }
    }
  ],
  "object_proof": {
    "old_undefined": "?_bfme_nextInInstanceList@BfmeTeamInstanceLink@@QAEPAV1@XZ",
    "new_undefined": "?j_00022a70@@YAXXZ",
    "runtime_sections_identical_after_retarget": true,
    "external_definitions_identical": true,
    "only_reviewed_undefined_retarget": true,
    "retail_ilt_and_body_witness": {
      "0x22a70": {
        "bytes": "e9bb5f0a00",
        "instructions": [
          "jmp 0xc8a30"
        ]
      },
      "0xc8a30": {
        "bytes": "8b4114c3",
        "instructions": [
          "mov eax, dword ptr [ecx + 0x14]",
          "ret "
        ]
      }
    }
  },
  "previews": [
    {
      "label": "before-link-preview",
      "exit_code": 1,
      "output": "Compile: 0 of 1 TU(s) (deps-cache: 1 current)\nLib members: 182 extracted from 6 archive(s)\nlink_check: 22,710 ledger object(s) new or changed since the census cannot be read here (e.g. game_gen_small_thunks_000.obj); any name may be defined there\ngame/GameEngine/Source/GameLogic/ScriptEngine/ScriptConditionsRva0032ABC0.cpp: does not link  LINKED 0 -> 0 bytes (census 2026-10-28 12:38 at ea2916a82d; file's own bytes 819)\n  LINKED PREVIEW UNKNOWN \u2014 selection census stale for: ??0?$BfmeDlinkIterator@VObject@@@@QAE@PAVObject@@P81@BEPAV1@XZ@Z, ??0?$StringBase@D@@AAE@ABV0@@Z, ??0AsciiString@@QAE@ABV0@@Z, ??0BfmeTeamIterator@@QAE@PAVTeam@@P8BfmeTeamInstanceLink@@AEPAV2@XZ@Z, ??1?$StringBase@D@@AAE@XZ, ??1AsciiString@@QAE@XZ, ??C?$BfmeOverride@VThingTemplate@@@@QBEPBVThingTemplate@@XZ, ?ThePlayerList@@3PAVPlayerList@@A, ?TheScriptEngine@@3PAVScriptEngine@@A, ?_bfme_nextInInstanceList@BfmeTeamInstanceLink@@QAEPAV1@XZ, ?advance@?$BfmeDlinkIterator@VObject@@@@QAEXXZ, ?advance@BfmeTeamIterator@@QAEXXZ, ?begin@PlayerTeamList@@QBEPAUPlayerTeamNode@@XZ, ?cur@?$BfmeDlinkIterator@VObject@@@@QBEPAVObject@@XZ, ?cur@BfmeTeamIterator@@QBEPAVTeam@@XZ, ?didEnterOrExit@Team@@QBE_NXZ, ?dlink_next_TeamMemberList@BfmeObjectDlinkBase@@QBEPAVObject@@XZ, ?done@?$BfmeDlinkIterator@VObject@@@@QBE_NXZ, ?done@BfmeTeamIterator@@QBE_NXZ, ?end@PlayerTeamList@@QBEPAUPlayerTeamNode@@XZ, ?getCustomData@Condition@@QBEHXZ, ?getCustomFrame@Condition@@QBEIXZ, ?getEachPlayerFromMask@PlayerList@@QAEPAVPlayer@@AAG@Z, ?getFinalOverride@Overridable@@QBEPBV1@XZ, ?getFrameObjectCountChanged@ScriptEngine@@QBEIXZ, ?getPlayerTeams@Player@@QBEPBUPlayerTeamList@@XZ, ?getTemplate@Object@@QBEPBVThingTemplate@@XZ, ?hasKind@ThingTemplate@@QBE_NI@Z, ?isInside@Object@@QBE_NPBVPolygonTrigger@@@Z, ?isKindOf@ThingTemplate@@QBE_NI@Z, ?iterate_TeamInstanceList@TeamPrototype@@QBE?AVBfmeTeamIterator@@XZ, ?iterate_TeamMemberList@Team@@QBE?AV?$BfmeDlinkIterator@VObject@@@@XZ, ?releaseBuffer@?$StringBase@D@@AAEXXZ, ?rva0032ABC0@ScriptConditions@@IAE_NPAVCondition@@PAVParameter@@1111@Z, ?setCustomData@Condition@@QAEXH@Z, ?unidentified_0034DB40@ScriptEngine@@QAEGPAVParameter@@@Z, ?validate@?$StringBase@D@@ABEXXZ, ___CxxFrameHandler, __except_list\n  unresolved  ?_bfme_nextInInstanceList@BfmeTeamInstanceLink@@QAEPAV1@XZ\nlink_check: 0 of 1 link cleanly; LINKED 0 -> 0 bytes (129.9s)\n"
    },
    {
      "label": "after-link-preview",
      "exit_code": 1,
      "output": "Compile: 0 of 1 TU(s) (deps-cache: 1 current)\nLib members: 182 extracted from 6 archive(s)\nlink_check: 22,710 ledger object(s) new or changed since the census cannot be read here (e.g. game_gen_small_thunks_000.obj); any name may be defined there\ngame/GameEngine/Source/GameLogic/ScriptEngine/ScriptConditionsRva0032ABC0.cpp: LINKED PREVIEW UNKNOWN  LINKED 0 -> 0 bytes (census 2026-10-28 12:38 at ea2916a82d; file's own bytes 819)\n  LINKED PREVIEW UNKNOWN \u2014 selection census stale for: ??0?$BfmeDlinkIterator@VObject@@@@QAE@PAVObject@@P81@BEPAV1@XZ@Z, ??0?$StringBase@D@@AAE@ABV0@@Z, ??0AsciiString@@QAE@ABV0@@Z, ??0BfmeTeamIterator@@QAE@PAVTeam@@P8BfmeTeamInstanceLink@@AEPAV2@XZ@Z, ??1?$StringBase@D@@AAE@XZ, ??1AsciiString@@QAE@XZ, ??C?$BfmeOverride@VThingTemplate@@@@QBEPBVThingTemplate@@XZ, ?ThePlayerList@@3PAVPlayerList@@A, ?TheScriptEngine@@3PAVScriptEngine@@A, ?advance@?$BfmeDlinkIterator@VObject@@@@QAEXXZ, ?advance@BfmeTeamIterator@@QAEXXZ, ?begin@PlayerTeamList@@QBEPAUPlayerTeamNode@@XZ, ?cur@?$BfmeDlinkIterator@VObject@@@@QBEPAVObject@@XZ, ?cur@BfmeTeamIterator@@QBEPAVTeam@@XZ, ?didEnterOrExit@Team@@QBE_NXZ, ?dlink_next_TeamMemberList@BfmeObjectDlinkBase@@QBEPAVObject@@XZ, ?done@?$BfmeDlinkIterator@VObject@@@@QBE_NXZ, ?done@BfmeTeamIterator@@QBE_NXZ, ?end@PlayerTeamList@@QBEPAUPlayerTeamNode@@XZ, ?getCustomData@Condition@@QBEHXZ, ?getCustomFrame@Condition@@QBEIXZ, ?getEachPlayerFromMask@PlayerList@@QAEPAVPlayer@@AAG@Z, ?getFinalOverride@Overridable@@QBEPBV1@XZ, ?getFrameObjectCountChanged@ScriptEngine@@QBEIXZ, ?getPlayerTeams@Player@@QBEPBUPlayerTeamList@@XZ, ?getTemplate@Object@@QBEPBVThingTemplate@@XZ, ?hasKind@ThingTemplate@@QBE_NI@Z, ?isInside@Object@@QBE_NPBVPolygonTrigger@@@Z, ?isKindOf@ThingTemplate@@QBE_NI@Z, ?iterate_TeamInstanceList@TeamPrototype@@QBE?AVBfmeTeamIterator@@XZ, ?iterate_TeamMemberList@Team@@QBE?AV?$BfmeDlinkIterator@VObject@@@@XZ, ?j_00022a70@@YAXXZ, ?releaseBuffer@?$StringBase@D@@AAEXXZ, ?rva0032ABC0@ScriptConditions@@IAE_NPAVCondition@@PAVParameter@@1111@Z, ?setCustomData@Condition@@QAEXH@Z, ?unidentified_0034DB40@ScriptEngine@@QAEGPAVParameter@@@Z, ?validate@?$StringBase@D@@ABEXXZ, ___CxxFrameHandler, __except_list\nlink_check: 0 of 1 link cleanly; LINKED 0 -> 0 bytes (138.1s)\n"
    }
  ],
  "census_download": "official artifact digest verified"
}
```
