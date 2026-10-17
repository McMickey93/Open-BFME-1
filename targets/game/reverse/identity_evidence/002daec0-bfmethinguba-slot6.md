# 0x002DAEC0: BfmeThingUBA vtable slot 6 (was banked as DamageFieldNugget::doNugget)

- Retail vtable 0x010CE990 holds ILT 0x0000D00D (jmp 0x002DAEC0) in slot 6.
- The only constructor that stores 0x010CE990 is 0x002DB0B0
  (`c7 06 90 e9 0c 01`), matched in the ledger as `??0BfmeThingUBA@@QAE@XZ`
  (game/GameEngine/Source/Common/BfmeConv1329.cpp). Retail was linked without
  ICF, so the slot's method belongs to that constructor's class; the ledger
  names that class BfmeThingUBA, not DamageFieldNugget.
- The INI `DamageFieldNugget =` callback 0x001E5C90 allocates the object
  (WeaponDamageFieldNuggetParse.cpp), but an INI token does not prove the C++
  class name, and that TU keeps the nugget class address-derived on purpose.
- No string, RTTI record, export or matched caller spells `doNugget`; the
  name in the 2026-09-06 bank was a guess. The method therefore lands as
  `rva002DAEC0`.
