# 0x0033B090 is ActionTemplate's default constructor

Retail's matched `??0ScriptEngine@@QAE@XZ` (0x00347E60,
game/GameEngine/Source/GameLogic/ScriptEngine/ScriptEngineRva00347E60.cpp)
builds its `ActionTemplate m_actionTemplates[543]` member with the EH vector
constructor iterator, and the element-ctor operand retail stores there is ILT
0x000030F8, which jumps to 0x0033B090. The same DIR32 is the repair-queue
baseline row `dir32,0x004030F8,??0ActionTemplate@@QAE@XZ`.

The 12-byte body `push esi; mov esi,ecx; call 0x0003AD41; mov eax,esi;
pop esi; ret` is an implicit derived ctor that calls `??0Template@@QAE@XZ`
(matched at 0x00351260) through ILT thunk 0x0003AD41 and returns this — the
`ActionTemplate : public Template` shape the referencing TU declares, and the
upstream EA spelling (BFME2 Code/GameEngine/Source/GameLogic/ScriptEngine/
ScriptEngine.h: class ActionTemplate : public Template). Extent is int3
bounded on both sides.

The prior row at this address, `?forward@Rva0033B090Forwarder@@QAEPAV1@XZ`
(ThisReturningForwarders.cpp, a placement-new Template forwarder), was an
address-derived placeholder for the same 12 bytes; its definition is removed
in the same commit.
