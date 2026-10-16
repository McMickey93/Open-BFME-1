# 0x00204ED0 is ReplenishUnitsBehaviorModuleData's constructor, not BattlePlanUpdateModuleData's

Approved by the project lead 2026-10-16 (BattlePlan dir32 operator correction, step 1 of 3).

- Retail's incremental-link thunk 0x0003025B jumps to 0x00204ED0. `tools/ilt_oracle.py check`
  CONFIRMS `??0ReplenishUnitsBehaviorModuleData@@QAE@XZ` at 0x0003025B (exact, p_false 5.87e-04)
  and CONTRADICTS `??0BattlePlanUpdateModuleData@@QAE@XZ` there (outside every window of slot
  38622).
- The matched `?friend_newModuleData@ReplenishUnitsBehavior@@SAPAVModuleData@@PAVINI@@@Z`
  (0x00117420) reaches 0x00204ED0 through that thunk, and the body stores 0x010A5C78, the table
  `??_7ReplenishUnitsBehaviorModuleData@@6B@` is recorded at.
- BattlePlanUpdateModuleData's constructor is 0x00285F10: the ILT CONFIRMS
  `??0BattlePlanUpdateModuleData@@QAE@XZ` there, `friend_newModuleData@BattlePlanUpdate`
  (0x00119D50) news 0xA0 and calls it through ILT 0x000287C7, and it stores 0x010BBFC0, whose
  slot 0 is the matched `??_GBattlePlanUpdateModuleData@@UAEPAXI@Z` (0x00285FE0).

So the second row `??0BattlePlanUpdateModuleData@@QAE@XZ` at 0x00204ED0 (and its pin at the
Replenish thunk 0x0003025B) named the wrong class. The row, its source
(BattlePlanUpdateModuleDataCtorThunk.cpp) and the pin are retired; the matched
`??0ReplenishUnitsBehaviorModuleData@@QAE@XZ` row keeps the body, and the thunk row
`?j_0003025B` (RvaShard2TailThunks.cpp) routes to it by its real name.
