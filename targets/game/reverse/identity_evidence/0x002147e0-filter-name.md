# 0x002147E0: RespawnBody::internalChangeHealth filter type name

The landed source names the module-data filter type `Rva2225E0Filter`, the
owner of BFME1's matched row `?accepts@Rva2225E0Filter@@QAE_NPAVObject@@PAVPlayer@@@Z`
at 0x003A04A0 (game/GameEngine/Source/GameLogic/Object/Rva003A04A0FilterAccepts.cpp).
symbols.csv also pins that name to the ILT 0x0001DA34 that this body calls.

The banked attempt used a different spelling for the cast
(`Rva003A04A0Filter`) and a `Module` struct for the findModule result. The
landed source still has `Module`, as `class Module;` for findModule. The
name_regression token alignment paired `Module` with `Rva2225E0Filter`, but
no descriptive name was lost.
