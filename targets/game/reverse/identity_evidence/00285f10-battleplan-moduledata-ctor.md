# 0x00285F10 is BattlePlanUpdateModuleData's constructor

Approved by the project lead 2026-10-16 (BattlePlan dir32 operator correction, step 3 of 3).

- Retail ILT 0x000287C7 jumps to 0x00285F10. `tools/ilt_oracle.py check` CONFIRMS
  `??0BattlePlanUpdateModuleData@@QAE@XZ` there (exact, p_false 4.57e-04) and CONTRADICTS
  the old row's name `??0BannerCarrierUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` (outside every
  window of slot 32346). BannerCarrierUpdate's own ctor is pinned at its ILT 0x0003DB36.
- The matched `friend_newModuleData@BattlePlanUpdate` (0x00119D50) allocates 0xA0 bytes and
  constructs them through ILT 0x000287C7; the matched `??_GBattlePlanUpdateModuleData@@UAEPAXI@Z`
  (0x00285FE0) and `??1BattlePlanUpdateModuleData@@UAE@XZ` (0x00286010) follow directly.
- The body stores 0x010BBFC0, now recorded as `??_7BattlePlanUpdateModuleData@@6B@` (operator
  correction, identity_evidence/010bbfc0-battleplan-moduledata-vtable.md), then initialises the
  members in Zero Hour's declaration order (bank targets/game/reverse/attempts/0x00285f10.cpp,
  strictly exact, 1 reloc).

The old row was a naked `__emit` byte lift under the wrong name; it is replaced by the clean C++
in BattlePlanUpdateModuleDataConstructor.cpp.

## Pins retired with it

`?construct@AutoHealBehaviorModuleData@@AAEXXZ` and `?construct@AutoHealBehaviorModuleData@@QAEXXZ`
were pinned at 0x00285F10 (dropped in the preceding commit); no source spells them, and AutoHealBehaviorModuleData's constructor is
the matched 0x00129D50. The ILT 0x000287C7 forwarding row
`??RRva000287C7FactoryCtorThunk@@QAEXXZ` and its address-derived target pin
`?construct@Rva000287C7FactoryCtorTarget@@QAEXXZ` stay (alias spellings, listed for the pin drain).
