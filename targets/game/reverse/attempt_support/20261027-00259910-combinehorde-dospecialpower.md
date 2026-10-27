# 0x00259910 CombineHordeSpecialPower::doSpecialPower bank (2026-10-27, a1 s465)

Identity: targets/game/reverse/identity_evidence/00259910-combinehorde-dospecialpower.md
(slot 11 of interface table 0x010B3D58, ILT 0x0003EE9B, ret 4, 440 B).

Stash: targets/game/reverse/attempts/0x00259910.cpp. Intended home
`game/GameEngine/Source/GameLogic/Object/SpecialPower/CombineHordeSpecialPowerDoSpecialPower.cpp`
(views copied from GrabPassengerSpecialPowerDoSpecialPower.cpp and
VeterancyCrateCollideExecute.cpp; same flags as GrabPassenger).

Recovered semantics (BFME 1 retail disassembly):
- object = [this-8]; return if Object+0x1A4 (m_disabledMask) nonzero.
- virtual this slot 16 (+0x40, table says startPowerRecharge stub 0xDC5B).
- 0x009F2960 iterate(pos=object+0x38, range=data+0x210 (data=[this-0xC]), 0,
  PartitionFilterPlayer(object->getControllingPlayer(), true)
   .link(Rva0025ED50RootFilter().link(KindOfAny(mask bit 108)
   .link(&Rva0025ED50ObjectFilter(object)))), 1).
- loop: other->unidentified_001BFE20() (ILT 0xD3B9); null -> next; its
  slot 27 (+0x6C)(object) false -> next; else
  object[+0x204]+0x20 ->aiBfmeCommand45(other, CMD_FROM_AI) (ILT 0x19628); break.

Result: 440/440 B, all 20 relocations aligned, 19 non-reloc bytes differ:
a pure callee-saved swap. Retail this=EDI/object=ESI (other=EDI, data=EDI,
AI pointer kept in ESI with `lea ecx,[esi+0x20]`); ours this=ESI/object=EDI
and AI via `mov ecx,[edi+0x204]; add ecx,0x20`.

Lever found: a named `KindOfMask mask(kInit,108)` local (before the
iterate statement, or after startPowerRecharge) took 42 -> 19 diffs
(mask zero-temp scheduling). Mask at function top or before the virtual
call: 282+ diffs.

Inert (still 19 / or 42 on the pre-mask base): getObject() inline accessor,
object read after the disabled check, nested if instead of early return,
`Object *const`, `self` copy of this, real MI view (ModuleBase+mux+interface,
getObject()/getData() accessors), for(;;)/while/found-variable loop shapes,
helper inlines for the slot-27 test or the AI command, inner block scope.
Worse: AI pointer local (89-183), Player* local (179-326), data/range local
(112-322), getObject() per use (447-451 B), direct m_object/m_data in MI view
(135).

Next hypotheses: object obtained via a non-inline-looking path that defines it
before `this` in IR (e.g. a by-reference helper), ZH real Object.h /
SpecialPowerModule.h headers with real getAI()/isDisabled(), or a real
SimpleObjectIterator/MemoryPoolObjectHolder spelling of the iterator.
model=claude-opus-5-5 t=45min
