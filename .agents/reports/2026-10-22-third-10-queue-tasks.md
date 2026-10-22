# Third batch of ten linking-queue tasks — 2026-10-22

The queue tool kept re-serving rows earlier sessions had already blocked, so these ten came from the published `link_queue.csv` (census 2615147aca). Each has no family owner, has no `re_attempts.log` verdict, and still has an open file. Each was claimed before work. Three made source progress, each in its own pushed commit; seven are recorded as `blocked` in `re_attempts.log`.

| # | Queue row | Result | Commit |
|---|---|---|---|
| 1 | #83 `?dup_00784b10` unresolved (RvaShard2TailThunks.cpp) | Retired the wrong `allocator<int>::deallocate` alias. 0x00784B10 is its own 47-byte body, now clean C++ `rva00784B10Deallocate`; ILT thunk 0x00035FF8 routes to it. | 4bd716b7f2 |
| 2 | #90 `Rva006315E0RequestBuddyAdd` losers | Stale: the sole definer matches 222/222 at HEAD; the census object is 219 bytes. | blocked |
| 3 | #96 `BitFlags<17>::countInverseIntersection` losers | Five wrong names sit on ILT 0x0003291B, which jumps to `Rva00786BD0Owner::find`; the fix is an identity cleanup. | blocked |
| 4 | #113 `??_7WeaponSet` wrong_selected | Retail 4-slot table needs a virtual dtor and three placeholder slot bodies re-identified. | blocked |
| 5 | #115 `??1ShareBufferClass<G>` losers | Real C++ destructor (delete[], no null test) replaces the shim. meshmdlio/meshgeometry no longer emit the Zero Hour copy; 10 funclet labels repinned. | 9b65d89d3d |
| 6 | #116 `??_7MetaMap` losers | 8-slot retail table: three MetaMap no-op overrides and two base slots carry placeholder names. | blocked |
| 7 | #118 `g_bfmeBase1285Vtable` unresolved | A 3-slot vtable with nine installers, not a plain datum. | blocked |
| 8 | #122 `Reset_All_Texture_Mappers` duplicates | The competitor is the pristine Zero Hour reference `mapper.cpp`, used as the source of 34 rows. | blocked |
| 9 | #125 `bfmeAcquirePathfindCellInfo` duplicates | Removed the inline copy from PathfinderInternalFindPath.cpp; it now references the 104-byte owner. | d91e1d4160 |
| 10 | #126 `??_7Rva009F2730Owner{Snapshot}` losers | Four Snapshot-side slots are placeholder bodies. | blocked |

All landed changes passed their scoped `./build.sh` gates (47/47, 1/1, 94/94) and the commit hooks without bypasses. Baselines only shrank. Before/after link evidence comes from saved-census previews (`--census-only`, index e9a5ae5b4c), which predate the new objects. No current whole-program LINKED gain is claimed. Four of the seven blocks (#113, #116, #118, #126) share one blocker family: vtable slots whose bodies carry non-virtual placeholder names. A pass that re-identifies such slot bodies as virtual members would unblock them together.
