// cl: /DNDEBUG /MD /EHsc /O2 /Ob2
//
// Open-BFME5: the AIMoveToState constructor at retail 0x00185700, 50 bytes.
// The state name goes straight into the by-value argument the base
// initialiser takes, and the vftable is installed after the flag.

// The state name is built by the real AsciiString: retail's copy sites build
// the temporary with a direct `call StringBase<char>::StringBase(char const*)`,
// and ascii_string.h's inline AsciiString(const char *) is exactly that call --
// no intermediate body, so the bytes are unchanged.
#include "../../../Libraries/Source/WWVegas/WWLib/ascii_string.h"

class StateMachine;

// The base initialiser this constructor calls is reached through ILT 0x00032182,
// whose jump lands on rva 0x0014F280: the 149-byte matched
// AIInternalMoveToState(StateMachine *, AsciiString) ctor
// (game/GameEngine/Source/GameLogic/AI/AIInternalMoveToStateCtor.cpp), whose
// signature is the by-value state name this body pushes.  Only that ctor is
// known here, so the base declares nothing else and the derived view below keeps
// the two stores at the offsets retail writes (+0 vftable, +0x50 flag).
class AIInternalMoveToState
{
public:
	AIInternalMoveToState(StateMachine *machine, AsciiString name);
};

// Retail table at VA 0x0109B370: 18 slots, ending before 0x0109B3B8.
// Keep each witnessed ILT target symbolic so the table relocates with the image.
extern "C" void __identifier("?j_0003959a@@YAXXZ")();
extern "C" void __identifier("?j_00026c60@@YAXXZ")();
extern "C" void __identifier("?j_0002178d@@YAXXZ")();
extern "C" void __identifier("?j_0001cfcb@@YAXXZ")();
extern "C" void __identifier("?j_00036903@@YAXXZ")();
extern "C" void __identifier("?j_0000c027@@YAXXZ")();
extern "C" void __identifier("?j_0001d403@@YAXXZ")();
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
extern "C" void __identifier("?j_0002c89a@@YAXXZ")();
extern "C" void *bfmeVftableAT[] = {
    reinterpret_cast<void *>(&__identifier("?j_0003959a@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00026c60@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0002178d@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0001cfcb@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_00036903@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0000c027@@YAXXZ")),
    reinterpret_cast<void *>(&__identifier("?j_0001d403@@YAXXZ")),
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
    reinterpret_cast<void *>(&__identifier("?j_0002c89a@@YAXXZ")),
};

class BfmeMoveToStateAT : public AIInternalMoveToState
{
public:
	BfmeMoveToStateAT(void *owner);

	void *m_bfmeVfptrAT;
	char m_bfmePadAT[0x4c];
	char m_bfmeReadyBfmeAT;
};

BfmeMoveToStateAT::BfmeMoveToStateAT(void *owner)
	: AIInternalMoveToState(reinterpret_cast<StateMachine *>(owner),
		AsciiString("AIMoveToState"))
{
	m_bfmeReadyBfmeAT = 1;

	m_bfmeVfptrAT = bfmeVftableAT;
}