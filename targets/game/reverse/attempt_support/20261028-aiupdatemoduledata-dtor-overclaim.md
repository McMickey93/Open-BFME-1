# 0x0027E4E0: nine destructor names on one AIUpdateModuleData body

Input revision: origin/master at 56809e70 (2026-10-28). Not repaired yet;
this records the evidence for the identity cleanup.

## Facts (BFME 1 target evidence)

- functions.csv holds nine matched rows on the same 145-byte SEH body at
  0x0027E4E0, one per *DestructorThunk.cpp: ??1{Animal,AssaultTransport,
  DeployStyle,Horde,Transport,Wander}AIUpdateModuleData, ??1CollideModuleModuleData,
  ??1DamageModuleModuleData, ??1UpdateModuleModuleData (all @@UAE@XZ).
  identity_baseline.txt carries these nine keys. Retail was linked without
  identical-COMDAT folding (tools/one_identity.py), so the body has one name.
- tools/ilt_oracle.py at 0x0027E4E0:
  ??1AIUpdateModuleData@@UAE@XZ CONFIRMED (exact, p_false 2.61e-04);
  ??1WanderAIUpdateModuleData@@UAE@XZ CONTRADICTED; ??1UpdateModuleData and
  ??1BehaviorModuleData CONTRADICTED.
- The derived classes' own complete destructors are 5-byte tail jumps
  (`jmp` ILT 0x00029D02 -> 0x0027E4E0), currently rowed as ?j_ gen-thunks:
  0x001244D0 ??1WanderAIUpdateModuleData@@UAE@XZ CONFIRMED,
  0x00123170 ??1AnimalAIUpdateModuleData@@UAE@XZ CONFIRMED,
  0x00123A70 ??1AssaultTransportAIUpdateModuleData@@UAE@XZ CONFIRMED.
  Each class's matched scalar deleting destructor calls that 5-byte body.
- ILT 0x00029D02 is pinned as the invented ??1SupplyTruckAIUpdateModuleDataBase@@UAE@XZ.

## Proposed repair (not done)

1. One row ??1AIUpdateModuleData@@UAE@XZ at 0x0027E4E0, sourced from one of
   the existing identical bodies with the class renamed; retire the other eight.
2. Rename the 0x00029D02 pin to ??1AIUpdateModuleData@@UAE@XZ.
3. Land each derived ??1X@@UAE@XZ at its 5-byte tail-jump body with an
   implicit destructor (see AIAttackActionStates.cpp: implicit dtor = bare jmp,
   no vptr reset; an explicit empty dtor adds a vptr store, measured).
Blocker: no tool retires several matched real-name rows on one address at
once; add_match --correct-identity replaces one.
