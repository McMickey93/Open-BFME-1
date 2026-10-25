# TerrainLogic: obsolete Waypoint vtable exemption

Starting BFME 1 revision ad617ed1dc. This is a verified prerequisite for
removing the historical duplicate Waypoint provider's gate debt, not a new
C++ recovery or a linking repair.

BFME 1 commit 1c572e3cb9 removed Zero Hour's Waypoint constructor/destructor
definitions from TerrainLogic.cpp because they emitted a second, two-slot
vtable rather than retail's one-slot vtable. The current source retains only
the explanatory comment. A literal git grep across game/ and the local shims
finds the decorated vtable name only in that comment. Retail's existing
constructor rows at 001AB600 (550 bytes) and 001AB8B0 (371 bytes), and destructor
at 001ABA80 (235 bytes), belong to WaypointConstructor.cpp. Those established
identities and extents are unchanged; this pass makes no new layout or data
ownership claim and does not add a vtable datum or alias.

The old DIR32 exemption is keyed by VA 0109C3DC and ??_7Waypoint@@6B@.
repair_queue.py pass-test removed precisely that baseline line and ran the
current TerrainLogic.cpp gate successfully: 35/35 function rows, one data row,
28 float constants, 28 DIR32 references and zero baselined findings. The
normal ./build.sh invocation on the same file independently exits zero with
the same results. Both use the dependency-checked current object; no private
diagnostic object was substituted. Gate debt shrinks 1017 -> 1016.

The lease is on TerrainLogic's existing 60-byte parseWaypointData row at
001A7860. The pre-existing same-address WorldHeightMap alias is not modified
or endorsed by this debt repair. No production source, header, compiler flag,
pin, global, ledger row or tool changes.

BFME 2 donor review: read-only master
8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9 splits this subsystem across files.
Reviewed Code/GameEngine/Source/GameLogic/Map/TerrainLogic_parseWaypointData.cpp
and WaypointLinks.cpp; they provide no applicable stale-exemption repair.
No donor source or layout is imported. The repair follows BFME 1's own prior
provider removal and current acceptance test; the pinned donor is unchanged.

link_check.py game/GameEngine/Source/GameLogic/Map/TerrainLogic.cpp before
and after reports 0 of 1 units linking and LINKED 0 -> 0 bytes. Both previews
are UNKNOWN because 22,640 census objects are unavailable here; existing
duplicate/COMDAT/selected-provider blockers remain. The unit has 4,280 own
ledger bytes, all unchanged. No linked-byte improvement is claimed.

The same commit preserves the separate 0036FE10 and 002A9000 failed-trial
handoffs and measurements so the next banked pass need not repeat them.
