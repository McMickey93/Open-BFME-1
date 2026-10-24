// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /Igame/GameEngine/Include/Precompiled /Igame/Libraries/Source/WWVegas /Igame/Libraries/Source/WWVegas/WWLib
// Retail's base here is SubsystemInterface: the constructor calls 0x009A1A30
// (??0SubsystemInterface@@QAE@XZ) and the vtable it stores, 0x010F9AAC, is
// ??_7Gen_00490100@@6B@ and inherits slots 2, 3, 6 and 8 of
// SubsystemInterface's own vtable at 0x01141640 unchanged. The class is the
// one the matched complete destructor ??1Gen_00490100@@UAE@XZ at 0x00490100
// (Bfme5BodyVectorDtors.cpp) already names. The base is a TU-local
// non-polymorphic view so this TU's Gen_00490100 owns no vftable of its own:
// retail's vtable store is written explicitly below.
#include "PreRTS.h"

// The vtable at 0x010F9AAC is ??_7Gen_00490100@@6B@ (dir32_addresses.csv),
// emitted by Bfme5BodyVectorDtors.cpp alongside the matched ??1Gen_00490100;
// __identifier spells that symbol so the store references the defining name.
extern "C" void *__identifier("??_7Gen_00490100@@6B@")[];

class SubsystemInterface
{
public:
	SubsystemInterface(void);
	// retail 0x009A1A30 writes the SubsystemInterface vtable at +0x00 and
	// zeroes the AsciiString m_name at +0x04.
private:
	int m_bfmeVftable;
	int m_name;
};

class Gen_00490100 : public SubsystemInterface
{
public:
	Gen_00490100();
	volatile int m_bfmeA;
	volatile int m_bfmeB;
	volatile int m_bfmeC;
	volatile int m_bfmeD;
	volatile int m_bfmeE;
	volatile int m_bfmeF;
	volatile int m_bfmeG;
};

// ??0Gen_00490100@@QAE@XZ
Gen_00490100::Gen_00490100()
{
	m_bfmeA = 0;
	// +0x00 is the vptr. The base above is a non-polymorphic TU-local view, so
	// the compiler emits no derived vptr store of its own; retail's own store --
	// 0x010F9AAC is ??_7Gen_00490100@@6B@, a nine-slot SubsystemInterface
	// vtable -- is written here explicitly, between the first and second member
	// zero as retail schedules it.
	*(void *volatile *)this = __identifier("??_7Gen_00490100@@6B@");
	m_bfmeB = 0;
	m_bfmeC = 0;
	m_bfmeD = 0;
	m_bfmeE = 0;
	m_bfmeF = 0;
	// The 0x24-byte object's last dword (+0x20) is left uninitialized, as in
	// retail; InGameUI's constructor measures the allocation at 0x24 bytes.
}
