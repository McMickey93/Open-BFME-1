# 0x00339590 is ConditionTemplate's destructor

Retail's matched `??0ScriptEngine@@QAE@XZ` (0x00347E60,
game/GameEngine/Source/GameLogic/ScriptEngine/ScriptEngineRva00347E60.cpp)
builds its `ConditionTemplate m_conditionTemplates[184]` member with the EH
vector constructor iterator, whose element-dtor operand retail stores there is
ILT 0x0001053C, which jumps to 0x00339590. The same DIR32 is the repair-queue
baseline row `dir32,0x0041053C,??1ConditionTemplate@@QAE@XZ`.

The 5-byte body `jmp 0x0002FE5F` is a tail-jump: thunk 0x0002FE5F jumps to
0x003394E0, the matched `??1Template@@IAE@XZ` (Template.cpp). So the element
destructor only destroys the protected Template base, the implicit
`ConditionTemplate : public Template` dtor shape the referencing TU declares
(upstream EA spelling, BFME2 Code/GameEngine/Source/GameLogic/ScriptEngine/
ScriptEngine.h). The compiled TU emits exactly `jmp ??1Template@@IAE@XZ`.
Extent is int3 bounded on both sides.

The prior row at this address, `?j_00339590@@YAXXZ` (gen-thunk;gap), was a
generated thunk placeholder for the same 5 bytes.
