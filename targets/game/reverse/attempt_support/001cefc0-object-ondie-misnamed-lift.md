# 0x001CEFC0 (1493 B): ledgered as ??1InactiveBody, really Object::onDie

Status: blocked (identity proven; rename refused by conversion_gate; C++ not written).

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
