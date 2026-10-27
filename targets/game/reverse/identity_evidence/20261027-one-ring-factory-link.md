# OneRingPenaltyUpdate factory lookup binding (2026-10-27)

Scope: game/GameEngine/Source/GameLogic/Object/Update/OneRingPenaltyUpdateRva00299080.cpp.
Served by `tools/link_check.py near` and its full repair packet at census
a0940f921b (2026-10-27 11:50). One caller file, one lookup binding.

## BFME 1 target facts

- The existing caller is `?rva00299080@OneRingPenaltyUpdate@@QAEXXZ`,
  RVA 0x00299080, 257 bytes. Its established identity is documented in
  `00299080-one-ring-penalty-spawn.md`; the opaque method name is retained.
- Retail ILT 0x00028560 reaches RVA 0x00137E80.
- That complete 284-byte provider is already matched in
  `game/GameEngine/Source/Common/Thing/ThingFactoryFindTemplate.cpp` as
  `?findTemplate@BfmeThingFactory@@QAEPBVThingTemplate@@ABVAsciiString@@@Z`.
  The caller's former ThingFactory-owner spelling had no matching definition.
- Both declarations use thiscall, one const AsciiString reference argument,
  and a const ThingTemplate pointer result. The new pointer-only declaration
  introduces no factory fields, objects, vtables, or layout claim.
- The emitted caller now references the provider's exact COFF name; its old
  ThingFactory-owner lookup reference is absent. The provider defines the same
  name. The existing `?TheThingFactory@@3PAVThingFactory@@A` reference and the
  existing ThingFactory::newObject call are preserved.

## BFME 2 reference review

Reviewed donor revision 73898a96342963eac2826836db10649a69e3dbb8:
`Code/GameEngine/Source/GameLogic/Object/Update/OneRingPenaltyUpdate.cpp`
(helper RVA 0x00499AFD) and the lookup row in
`Code/GameEngine/Source/GameClient/Rva002D06CAGet.cpp`.

The donor confirms the spawn-helper relationship and one-argument lookup,
but its 38-byte lookup uses the ThingFactory spelling and a different factory
table offset. BFME 1's 284-byte provider includes its own test-asset path.
No donor body, factory layout, address, pin, or compiler override is imported.
The binding spelling comes from BFME 1's existing provider and repair packet.

## Verification and limits

Native original compiler, normal `tools/build.py`, caller and provider together:
2/2 functions exact before and after; 4 literals plus 1 empty-string reference,
5 DIR32 references, and both body guards pass. The declared-body check passes.
No symbol pin, data owner, shared header, baseline, or matched row is changed.

Before: the normal `tools/link_check.py <caller>` explicitly reports the old
lookup name unresolved. After: that unresolved reference is gone.
Both runs report LINKED PREVIEW UNKNOWN because 22,672 other ledger objects
are unavailable on this host; the published index does not supply those objects.
The index ZIP was downloaded from successful official workflow run 40484077199,
artifact 12739597408, SHA-256
3ccfaa52cd57785e2cb6a12cfe92c9ba33f9381a98ded34d20f020dd392258ad.

This repairs the caller/provider binding. It does not establish a current
whole-program link result or a measured census gain. New C++ exact bytes: +0;
new measured LINKED bytes: +0. No runtime smoke result is claimed.

Agent-Authored: OpenAI Codex
