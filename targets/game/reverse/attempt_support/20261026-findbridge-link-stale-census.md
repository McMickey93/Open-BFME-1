# T5 handoff: ?findBridge link repair blocked on stale census (2026-10-26)

Queue: `link_check.py next` #3 — `?findBridge@TerrainRoadCollection@@QAEPAVTerrainRoadType@@VAsciiString@@@Z`,
wrong_selected, est. 2,832 B in `game/GameEngineDevice/Source/W3DDevice/GameClient/W3DBridgeLoad.cpp`.
Claim 0xF9A4E10D released with this handoff (no source edits made).

## Live verdict (this session)

`python3 tools/link_check.py .../W3DBridgeLoad.cpp` (955 s): LINKED PREVIEW UNKNOWN.
Census e9a5ae5b4c (2026-10-19) is stale: 2,167 ledger objects new or changed
since it, so no selection verdict is possible. The reported
`duplicate ?load@W3DBridge@@QAE_NW4BodyDamageType@@@Z` is a staleness artifact:
exactly one TU defines it (W3DBridgeLoad.cpp, matched row 172800 @ 0x006D8C10),
and exactly one TU defines findBridge (TerrainRoads_find.cpp:116, matched rows
52602/52725 for findBridge @ 0x006024E0 / findRoad @ 0x006023A0). No wrong
emitter exists in the current tree.

## Donor evidence reviewed (Open-BFME-2 worktree bf28480b10)

`Code/GameEngine/Source/GameClient/Terrain/TerrainRoads.cpp:438-500`: findRoad
(donor 0x002DB496), findBridge (donor 0x002DB4DA, 68 B, link-clean) and
findRoadOrBridge are the Zero Hour lookups, same loop shape as the BFME-1
retail-proven copies. No transplant needed; BFME-1 bodies stand.

## Next step

On a clean tree run `python3 tools/link_check.py --refresh`, then re-run the
per-file check on W3DBridgeLoad.cpp. If ?findBridge still mis-selects after
the refresh, suspect the caller's local `TerrainRoadCollection` declaration
(W3DBridgeLoad.cpp:36) vs the canonical `GameClient/TerrainRoads.h` view.
model=muse-spark, t=40min.
