# ??_7BattlePlanUpdateModuleData@@6B@ is 0x010BBFC0, not 0x010A5C78

Operator correction by the project lead, approved 2026-10-16 (BattlePlan dir32 correction,
step 2 of 3; tools/dir32_record_guard.py operator-correction route).

- Recorded old VA 0x010A5C78 is ReplenishUnitsBehaviorModuleData's table: it is also recorded as
  `??_7ReplenishUnitsBehaviorModuleData@@6B@`, and Replenish's constructor 0x00204ED0 stores it
  (identity fix in identity_evidence/00204ed0-replenish-not-battleplan-moduledata-ctor.md). Its
  slots reach no deleting destructor of BattlePlanUpdateModuleData.
- New VA 0x010BBFC0: BattlePlanUpdateModuleData's constructor ctor=0x00285F10 (retail ILT
  CONFIRMS `??0BattlePlanUpdateModuleData@@QAE@XZ` there; `friend_newModuleData@BattlePlanUpdate`
  0x00119D50 news 0xA0 and calls it through ILT 0x000287C7) stores it with
  `mov dword ptr [esi], 0x010BBFC0`.
- Slot 0 of 0x010BBFC0 is the matched, non-generated deleting destructor
  `??_GBattlePlanUpdateModuleData@@UAEPAXI@Z` dtor=0x00285FE0 (BattlePlanUpdate.cpp).
