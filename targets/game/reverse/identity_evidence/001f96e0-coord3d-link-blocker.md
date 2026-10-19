# DynamicPortal coordinate ABI mismatch (2026-10-19)

The fresh plain link at e9a5ae5b4c refers to the class-key (PAVCoord3D)
Object::getMultiLogicalBonePosition name from DynamicPortalBehaviourRva001F96E0.cpp.
The matched callee at 0x001BFAC0 defines the struct-key (PAUCoord3D) name.
These are distinct COFF symbols despite equal pointer ABIs. This is an unresolved
link, not an absent address pin: symbols.csv already pins the class view to
0x001BFAC0. Adding another address pin cannot define that name for link.exe.

## Bounded experiments

The unmodified caller passes build.sh, including both its 979-byte parent and
22-byte cleanup row, literals, DIR32 bindings and body guard. The actual callee
body and declarations are in Object_bfmeGetMultiLogicalBonePosition.cpp.

Replacing only the caller's coord3d.h include with the registered data-only
Libraries/Include/Lib/Coord3D.h was tested in build/task3-canonical-coord.cpp.
It emits 920 bytes versus retail 979, with 762 non-relocation differences and
25 displaced relocation sites. The first divergence is +0x1F, where retail
passes the constructor/destructor callbacks for sixteen 12-byte elements.
POD adoption removes those array lifetime calls and is not an acceptable repair.

A second scratch-only experiment declares a 12-byte struct Coord3D containing
x/y/z and external default constructor/destructor declarations. No new methods
are implemented. build/task3-nontrivial-coord.cpp emits all 979 parent bytes
exactly outside the 34 relocation slots. This is instruction-shape evidence,
not a full strict relocation/unwind verification or a landed conversion.
It demonstrates that the struct-key type and nontrivial lifetime are compatible;
a data-only canonical header is missing the required lifetime declarations.
The scratch type is not installed in game/: that would duplicate an existing
header-owned type instead of repairing the shared declaration.

## Remaining blocker

WWMath/coord3d.h declares class Coord3D : public Coord3DBase with external
constructors/destructor, whereas the registered Coord3D.h declares a POD struct
without a base or special members. docs/header_adoption.md specifically defers
Coord3D adoption while its headers disagree. header_adopt_lane.py gate-cost
reports 190 dependent ledger sources for WWMath/coord3d.h; changing its tag
requires coordinated symbol and call-binding checks across those sources.
The repository also pauses bulk renames. A single caller alias or naked jump
would hide the inconsistency, not repair it. No production source, shared
header, pin, function claim, generated file or baseline was changed here.

Next work: settle the evidenced struct declaration and its native lifetime
members in the registered header workflow; migrate the affected declarations
with matching symbol identities, verify all affected rows and EH bindings, then
measure per-file LINKED using the completed census index.

## Reproduction

- BUILD_POOL=8 ./build.sh game/GameEngine/Source/GameLogic/Object/Behavior/DynamicPortalBehaviourRva001F96E0.cpp
- python3 tools/probe.py build/task3-canonical-coord.cpp '?createWaypoints@DynamicPortalBehaviour@@QAEXXZ' 0x001F96E0 --size 979
- python3 tools/probe.py build/task3-nontrivial-coord.cpp '?createWaypoints@DynamicPortalBehaviour@@QAEXXZ' 0x001F96E0 --size 979
- python3 tools/header_adopt_lane.py gate-cost --header game/Libraries/Source/WWVegas/WWMath/coord3d.h

Production source SHA256: 1518de699fbec23270d72f8a0437d16ed71510814b84824678d006498659eaa4
