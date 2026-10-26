# 0x001CEFC0 (1493 B): ledgered as ??1InactiveBody, really Object::onDie

Status: partial 0.983 (identity proven; rename refused by conversion_gate; C++ bank
targets/game/reverse/attempts/0x001cefc0.cpp, 1483 B of 1493).

## Identity (BFME 1 target evidence)
- Retail ILT 0x0003369F = `E9 1C B9 19 00` -> 0x001CEFC0.
  `tools/ilt_oracle.py check '?onDie@Object@@QAEXPAVDamageInfo@@@Z' 0x3369F`
  -> CONFIRMED p_false=7.18e-04; the `PBVDamageInfo` spelling is CONTRADICTED.
- symbols.csv pins that name at 0x3369F (callee of matched
  InactiveBody::attemptDamage 0x00213E40); ActiveBody_attemptDamage.cpp and
  RespawnBodyInternalChangeHealth.cpp call it with this=Object.
- Body ends `ret 4`: no destructor. The real ??1InactiveBody ILT 0x0003C867
  jumps to 0x00213B70 (currently ??1Rva00213B70NestedDtor, ilt_oracle says
  ??1InactiveBody@@UAE@XZ is CONTRADICTED there, so that one is not simple either).

## Link effect
link_queue #13 (`?onDie@Object@@QAEXPAVDamageInfo@@@Z`, losers, 528 B in
InactiveBody.cpp, census 3d3b068129): the selected definition is the
present-unmatched Zero Hour copy in Object.cpp (probe score 0.20, 760 B vs 1493 B).

## What was tried (session 457, claude-opus-5-5)
Renaming the naked lift in Body/InactiveBodyDestructorThunk.cpp to
`__declspec(naked) void Object::onDie(DamageInfo *)` with
`add_match --replace-rva 0x1CEFC0 --correct-identity '??1InactiveBody@@UAE@XZ'`
byte-verified and Object.cpp (with the ZH copy removed) built 190/190, but
the pre-commit conversion gate (Rule A) counts a renamed naked line as a new
lift and refuses it. Not retried another way.

## Way forward
Write Object::onDie as real C++ in Object.cpp (replacing the ZH copy) and
land with `add_match --replace-rva 0x1CEFC0 --correct-identity
'??1InactiveBody@@UAE@XZ'`, deleting the lift file and its hatch_baseline
emit line. Retail shape notes: SEH frame, 0xBC locals; bool
`damageInfo->m_sourceID(+8) == m_id(+0x74)` saved first; die-module loop over
m_behaviors(+0x1F0) slot +0x18 then onDie; TheVictorySystem(0x12EF734)
rva001DFC10(this,damageInfo); an inline DamageInfo built on the stack (vtable
0x1085DE4/0x1085DE0, 1.0f at +0x48) passed to slot +0x34 of the container at
+0x214; status bit edits through setStatus-like inline (+0x110 BitFlags, calls
0x41343f replaceModelConditionState and 0x43611a); a 3x24 B
DelayedLuaEventList array (eh vector ctor/dtor iterators, vtable 0x1085E10)
passed to bfmeGo939B (0x2E7650) on 0x12F060C; tail calls d_000ee7f0 on the
+0x23C team. All 22 callees are matched rows.

## C++ reconstruction (session 457, same day)
Bank: `targets/game/reverse/attempts/0x001cefc0.cpp`, meant for
`game/GameEngine/Source/GameLogic/Object/Object_onDie.cpp` (cl line as in
SpawnBehaviorOnDie.cpp: `/DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB`, stlport,
GameLogicObjectLookup.h). probe: 1483 B vs 1493, shape 0.983, 0xBC frame, EH
states and every call/reloc in place. Default flags are best (flag_sweep: 90
variants, /G7 drops to 0.919).

Levers that worked (each measured):
- inline `GameLogic::findObjectByID` in the TU: the producer lookup inlines
  and the killer lookup stays out of line, as retail (0.879 -> 0.945).
- DelayedLuaEventList: base class NOT novtable with `virtual ~Base() {}`,
  derived with an inline ctor and NO user dtor. This gives retail's EH
  states 0/1/2 and no vptr stores at the end (dead-store eliminated).
- setStatus mask: ZH `BitFlags<86>(kInit, 70)` temp over `_STL::bitset<86>`.
- DamageInfoInput: the late byte store is m_kill at +0x20 (offsets after
  the push are +4); +0x24 is a float (imm 0 store, not ebx).
- `ObjectID killerID = damageInfo->in.m_sourceID;` before findObjectByID,
  `getID()` accessor for onSpawnDeath, `getContain()` accessor for the
  spawner's contain branch, `owner = getControllingPlayer()` before reading
  ThePlayerList->m_local, `m_id == m_sourceID` operand order.

Residue (all register allocation / scheduling):
1. VC7.1 caches 0x20000000 in EBP (`mov ebp,0x20000000` at +0x78) for the
   +0x94 status test and the model-condition bit 61 test/or; retail keeps
   three immediates and uses EBP as the bit-87 clear temp instead (ours ECX).
   Retail's un-CSE'd `test [r+disp],imm` ... `or r,imm` pair is unique in the
   whole image. Tried without effect: Bool vs mask-returning tests, bitset
   flags (worse 0.941), volatile flags, bitfield or 64-bit status word,
   test-inside set/clear helpers, shift-form status test, no container local.
2. Die-module loop: ours `mov edx,[eax+0xC]; lea ecx,[eax+0xC]; call [edx+18h]`,
   retail `lea ecx,[eax+0xC]; mov eax,[ecx]; call [eax+18h]` (the spawner loop,
   written as an inline Object member, already matches). Tried a module
   local, a forceinline member loop (worse), a while loop (worse).
3. The setStatus temp's third word is stored before the pushes (retail
   after `push 1`).
