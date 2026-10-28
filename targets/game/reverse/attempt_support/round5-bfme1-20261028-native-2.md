# Script-condition team-list binding, 2026-10-28

Selected by the normal link queue after the original Object::getAI candidate became foreign-reserved. The existing 820-byte ScriptConditions::rva0032ABC0 owns the whole comparison switch and player/team/member walk. Its unresolved BfmeTeamInstanceLink spelling is a pin-only view of the existing matched ILT 0x00022A70, which jumps to 0x000C8A30 (4 bytes: 8b4114c3, this+0x14 pointer, ret). ScriptConditionsRva0032C990.cpp already forms the same pointer-to-member from j_00022a70, and ScriptConditionsRva00326C00.cpp uses the corresponding direct-call bridge. The trial preserves the existing non-const PMF type and complete caller body, and changes only its address factory. No pin, ledger identity, address admission or baseline changes.

BFME2 donor review: e7abc6a62c786c16dc79a9ee86df40894be49ff0, Code/GameEngine/Source/GameLogic/ScriptEngine/ScriptConditionsPlayerUnitCounts.cpp and ScriptConditions_evaluateTeamStateIs.cpp use Team::dlink_next_TeamInstanceList and a +0x334 prototype list. Those corroborate iteration only; BFME1 sibling, retail thunk and complete getter establish this repair. No BFME2 field offset or address is imported.

Native run: https://github.com/McMickey93/Open-BFME-1/actions/runs/40754078688

Original compiler and unchanged ordinary project gates; no new C++ bytes, census measurement or game test.

Outcome: blocked; game source restored.
Blocker: Every reviewed candidate failed byte or retained-COFF verification

Qualification observations:

```json
{
  "reference": {
    "pinned": "20a0cb6173fd78ede36a2709f44422c73b80cc5a",
    "observed_upstream": "fe2d68f81a692083b6e7ace45cfae2ef44f76129",
    "pointer_changed": false,
    "newer_head_qualified": false,
    "freshness_update_blocked": true,
    "note": "Inspection uses current main BFME2 donor packets in the reviewed manifest; no donor-pointer update or success stamp is claimed."
  },
  "trials": [
    {
      "variant": "retail-ilt",
      "gate_exit": 0,
      "structural_refusal": "Runtime COFF sections, definitions or bindings differ beyond the reviewed retarget"
    }
  ],
  "object_proof": null,
  "previews": [
    {
      "label": "before-link-preview",
      "exit_code": 1,
      "output": "link_check: no census index at build/link_census/link_index.pkl (134 MB, never tracked).\n  fetch the daily workflow's:  python3 tools/link_check.py fetch-index   (then preview with --census-only)\n  or copy a local census's:   mkdir -p build/link_census && cp 'D:/a/Open-BFME-1/Open-BFME-1/source/build/wt_link/build/link_census/link_index.pkl' build/link_census/\n  or build one (~35 min):   python3 tools/link_census.py --build --history\n  `link_check.py next` needs neither: it reads targets/game/reverse/link_queue.csv\n"
    }
  ],
  "census_download": "unavailable: HTTP Error 401: Server failed to authenticate the request. Please refer to the information in the www-authenticate header."
}
```
