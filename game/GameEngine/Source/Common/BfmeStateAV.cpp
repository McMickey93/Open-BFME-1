// cl: /DNDEBUG /MD /EHsc /O2 /Ob2 /Igame/Libraries/Source/WWVegas/WWLib
//
// Open-BFME5: the exit state constructor at retail 0x00171680, 53 bytes.
// The state name goes straight into the by-value argument the base
// initialiser takes, and the vftable is installed after the field.
//
// Retail reaches the base through its ILT thunk 0x000035B2, whose body is
// 0x000A19E0 -- matched as
// ??0State@@QAE@PAVStateMachine@@VAsciiString@@@Z in
// game/GameEngine/Source/Common/StateConstructor.cpp -- so the base
// initialiser is spelled as that class's constructor and the name argument is
// a real AsciiString, not a TU-local stand-in.
//
// The derived layout is not polymorphic here; its installed table below
// supplies the exact seventeen retail slots at VA 0x01098188.

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/AsciiString.h
#include "../../../Libraries/Source/WWVegas/WWLib/string_base.h"

#include "../../../Libraries/Source/WWVegas/WWLib/ascii_string.h"

class StateMachine;

class State
{
public:
	State( StateMachine *machine, AsciiString name );
};

// Retail table at VA 0x01098188: 17 slots, ending before 0x010981CC.
// Keep each witnessed ILT target symbolic so the table relocates with the image.
extern void j_00044634();
extern void j_00026c60();
extern void j_000131ce();
extern void j_0003992d();
extern void j_0003e6e9();
extern void j_00040a07();
extern void j_0000272f();
extern void j_0000c79d();
extern void j_00028b87();
extern void j_00023416();
extern void j_00015d9d();
extern void j_000273bd();
extern void j_0002cb42();
extern void j_00021a7b();
extern void j_000351b1();
extern void j_00007405();
extern void j_00016b3a();
extern "C" void *bfmeVftableAV[] = {
    reinterpret_cast<void *>(&j_00044634),
    reinterpret_cast<void *>(&j_00026c60),
    reinterpret_cast<void *>(&j_000131ce),
    reinterpret_cast<void *>(&j_0003992d),
    reinterpret_cast<void *>(&j_0003e6e9),
    reinterpret_cast<void *>(&j_00040a07),
    reinterpret_cast<void *>(&j_0000272f),
    reinterpret_cast<void *>(&j_0000c79d),
    reinterpret_cast<void *>(&j_00028b87),
    reinterpret_cast<void *>(&j_00023416),
    reinterpret_cast<void *>(&j_00015d9d),
    reinterpret_cast<void *>(&j_000273bd),
    reinterpret_cast<void *>(&j_0002cb42),
    reinterpret_cast<void *>(&j_00021a7b),
    reinterpret_cast<void *>(&j_000351b1),
    reinterpret_cast<void *>(&j_00007405),
    reinterpret_cast<void *>(&j_00016b3a),
};

class BfmeStateAV : public State
{
public:
	BfmeStateAV(void *owner);

	void *m_bfmeVfptrAV;
	char m_bfmePadAV[32];
	int m_bfmeFieldAV;
};

BfmeStateAV::BfmeStateAV(void *owner)
	: State((StateMachine *)owner, AsciiString("AIExitState"))
{
	m_bfmeFieldAV = 0;

	m_bfmeVfptrAV = bfmeVftableAV;
}
