// cl: /DNDEBUG /MD /EHsc /O2 /Ob2 /Igame/Libraries/Source/WWVegas/WWLib
//
// Open-BFME5: the second crate pick-up state constructor at retail 0x0018AE00,
// 53 bytes. The state name goes straight into the by-value argument the base
// initialiser takes, and the vftable is installed after the field.
//
// Retail reaches the base through its ILT thunk 0x00032182, whose body is
// 0x0014F280 -- matched as
// ??0AIInternalMoveToState@@QAE@PAVStateMachine@@VAsciiString@@@Z in
// game/GameEngine/Source/GameLogic/AI/AIInternalMoveToStateCtor.cpp -- so the
// base initialiser is spelled as that class's constructor and the name argument
// is a real AsciiString, not a TU-local stand-in.
//
// The vftable store is retail's own (0x0109B748), not one this TU emits: the
// derived class is not polymorphic here, and the extern below has no definition
// anywhere in the tree yet.

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/AsciiString.h
#include "../../../Libraries/Source/WWVegas/WWLib/string_base.h"

#include "../../../Libraries/Source/WWVegas/WWLib/ascii_string.h"

class StateMachine;

class AIInternalMoveToState
{
public:
	AIInternalMoveToState( StateMachine *machine, AsciiString name );
};

// Retail table at VA 0x0109B748: 18 slots, ending before 0x0109B790.
// Keep each witnessed ILT target symbolic so the table relocates with the image.
extern "C" void __identifier("?j_00011f5e@@YAXXZ")();
extern "C" void __identifier("?j_00026c60@@YAXXZ")();
extern "C" void __identifier("?j_00025fa4@@YAXXZ")();
extern "C" void __identifier("?j_0002d411@@YAXXZ")();
extern "C" void __identifier("?j_00033046@@YAXXZ")();
extern "C" void __identifier("?j_00049189@@YAXXZ")();
extern "C" void __identifier("?j_0003d6f4@@YAXXZ")();
extern "C" void __identifier("?j_0000c79d@@YAXXZ")();
extern "C" void __identifier("?j_00028b87@@YAXXZ")();
extern "C" void __identifier("?j_00023416@@YAXXZ")();
extern "C" void __identifier("?j_00015d9d@@YAXXZ")();
extern "C" void __identifier("?j_000273bd@@YAXXZ")();
extern "C" void __identifier("?j_0002cb42@@YAXXZ")();
extern "C" void __identifier("?j_00021a7b@@YAXXZ")();
extern "C" void __identifier("?j_000351b1@@YAXXZ")();
extern "C" void __identifier("?j_00007405@@YAXXZ")();
extern "C" void __identifier("?j_00016b3a@@YAXXZ")();
extern "C" void __identifier("?j_0002ca66@@YAXXZ")();
extern "C" void *bfmeVftableAW[] = {
    reinterpret_cast<void *>(&__identifier("?j_00011f5e@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00026c60@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00025fa4@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0002d411@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00033046@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00049189@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0003d6f4@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0000c79d@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00028b87@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00023416@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00015d9d@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_000273bd@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0002cb42@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00021a7b@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_000351b1@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00007405@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00016b3a@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0002ca66@@YAXXZ")),
};

class BfmeStateAW : public AIInternalMoveToState
{
public:
	BfmeStateAW(void *owner);

	void *m_bfmeVfptrAW;
	char m_bfmePadAW[76];
	int m_bfmeFieldAW;
};

BfmeStateAW::BfmeStateAW(void *owner)
	: AIInternalMoveToState((StateMachine *)owner, AsciiString("AIAttackPickUpCrateState"))
{
	m_bfmeFieldAW = 0;

	m_bfmeVfptrAW = bfmeVftableAW;
}
