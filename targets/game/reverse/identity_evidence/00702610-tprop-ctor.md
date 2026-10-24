# 0x00702610 is TProp's default constructor

Retail's matched `??0W3DPropBuffer@@QAE@XZ` (0x00702FF0,
game/GameEngineDevice/Source/W3DDevice/GameClient/W3DPropBufferDestructor.cpp)
builds its `TProp m_props[4000]` member with the EH vector constructor
iterator, and the element-ctor operand retail stores there is ILT 0x00004660,
which jumps to 0x00702610. The same DIR32 is the repair-queue baseline row
`dir32,0x00404660,??0TProp@@QAE@XZ`.

The 3-byte body `mov eax,ecx; ret` is the empty inline `TProp() {}` the
referencing TU declares (upstream EA spelling, ZH
Code/GameEngineDevice/Include/W3DDevice/GameClient/W3DPropBuffer.h: struct
TProp). Extent is int3 bounded on both sides.

The prior row at this address, `?m@Gen_00702610@@QAEPAXXZ` (gen-shim;
skeleton=ret-this in game/gen_small/fun_004.cpp), was a generated placeholder
for the same 3 bytes.
