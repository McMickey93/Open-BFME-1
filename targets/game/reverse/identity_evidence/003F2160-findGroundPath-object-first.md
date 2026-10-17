# 0x003F2160 is Pathfinder::findGroundPath, object first

Retail body 0x003F2160 (2045 B, `ret 0x10`) was claimed as
`?findGroundPath@Pathfinder@@QAEPAVPath@@PBUCoord3D@@0H_N@Z`, Zero Hour's
`(const Coord3D *from, const Coord3D *rawTo, Int pathDiameter, Bool crusher)`
signature, by a MASM dump. The method is findGroundPath; the parameter list is
BFME's.

## Method identity

The body is Zero Hour's `Pathfinder::findGroundPath` (GeneralsMD
AIPathfind.cpp) step for step:

- `m_zoneManager.clearPassableFlags()` (0x004030E0 on this+0xC9C), then the
  hierarchical pre-pass with `isHuman = true` and LOCOMOTORSURFACE_GROUND (1);
  the returned path is destroyed, otherwise `setAllPassable()` (0x00403140).
- `rawTo->x == 0 && rawTo->y == 0` returns NULL, then `m_isMapReady` (+0x8).
- `adjustTo = *rawTo`, `clipFrom = *from`, `clip(&clipFrom, &adjustTo)`,
  `m_isTunneling = false` (+0x83C), `getLayerForDestination`, `worldToCell`.
- The destination ring search: `clearCellForDiameter` against pathDiameter,
  offsets 1..7 (MAX_OFFSET 8) in Zero Hour's x+, y+, x-, x-, y-, y-, x+, x+
  order, NULL when exhausted.
- getCell/allocateInfo on the goal, getClippedCell/allocateInfo on the start,
  the two effective zones compared, startPathfind, the open/closed list loop,
  buildGroundPath on reaching the goal.
- The groundCellsCallback line walk (0x003E2620), then the eight neighbours of
  Zero Hour's `delta[]` table (retail .data 0x012B4B38 / 0x012B4B10, x then y),
  the `isPassable` test with the four +-3 `clipIsPassable` rescues, the
  `adjacent[5] = {0,1,2,3,0}` diagonal rule, CELL_CLEAR and pinched rejects,
  and `newCostSoFar += 0.6f * (delta * COST_ORTHOGONAL)` when the clear
  diameter is short.

The BFME2 EA label for the aligned body is `Pathfinder::FindGroundPath`.

## Parameter list

- The one caller, matched `AIGroup::checkSpecial` (0x00154F00, +0x0301..0x0313),
  loads `ECX = TheAI->m_pathfinder` and pushes `4`, the destination pointer,
  the address of a local Coord3D and the object, then calls ILT 0x00048C57,
  which jumps to 0x003F2160. Its source names the view
  `rva003F2160(Object *, const Coord3D *, const Coord3D *, Int)`.
- In the body, argument 1 goes to `TerrainLogic::getLayerForDestination(Object *,
  const Coord3D *)` twice and is the receiver of
  `Object::bfmeIsComputerControlled` and two template override reads that fill
  the PathfindMovementProfile. Argument 2 is copied into clipFrom and passed to
  buildGroundPath; argument 3 is the zero-tested, clipped destination; argument
  4 is the diameter every `clearCellForDiameter` result is compared with.

There is no Bool crusher argument: BFME passes 0 as the first
`clearCellForDiameter` argument.

## Decorated name

Retail's incremental-link thunk table contradicts the Zero Hour decoration and
`?findGroundPath@Pathfinder@@QAEPAVPath@@PAVObject@@PBUCoord3D@@1H@Z` alike
(`tools/ilt_oracle.py check`, slots 35919-35944), so BFME's exact spelling
(const, references, Coord3D's class key or a renamed method) is unproven. A
sweep of findGroundPath/FindGroundPath spellings found only chance fits; the
nearest to the evidence is `?FindGroundPath@Pathfinder@@QAEPAVPath@@ABVObject@@ABVCoord3D@@1H@Z`
(BFME2's label, const references), a lead and not proof.

The row therefore takes the address-derived name the matched caller TU already
declares for this body (AIGroup.cpp: `Path *rva003F2160(Object *, const Coord3D *,
const Coord3D *, Int)`), `?rva003F2160@Pathfinder@@QAEPAVPath@@PAVObject@@PBUCoord3D@@1H@Z`,
landed in game/GameEngine/Source/GameLogic/AI/PathfinderFindGroundPath.cpp.

## Helper names replacing the bank's

The banked attempt (attempts/0x003f2160.cpp) called the cell-info release at
0x003F6F10 `finishReset` and `firstLive` and the closed-list insert at
0x003F6C30 `listHelper`. Nothing proves those names: `finishReset` is the
member name of the opaque `Rva003F7380State` view the ledger row carries, and
`firstLive`/`listHelper` were invented for the bank. The conversion calls both
through the pins the matched findSafePath (PathfinderFindSafePathBfme.cpp)
already uses for the same ILTs, `?rva003F6F10@PathfindCell@@QAEXXZ` (ILT
0x0004B3B7) and `?rva003F6C30@PathfindCell@@QAEXPAPAUPathfindCellInfo@@@Z`
(ILT 0x00005E48), address-derived until their identity is proven.
