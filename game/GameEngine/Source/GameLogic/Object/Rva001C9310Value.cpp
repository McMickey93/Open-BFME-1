// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib
// stlport
// Retail 001C9310: 80-byte value query. Retained address-derived owner/name.
// Evidence: targets/game/reverse/identity_evidence/001c9310-native-override.md
#include "PreRTS.h"
#include "Common/Overridable.h"
#include "Common/Override.h"
class Rva001C9310Thing : public Overridable
{
public:
	char m_gap_d0[ 0xD0 - 12 ];
	unsigned m_flags_d0;
	char m_gap_448[ 0x448 - 0xD4 ];
	int m_value_448;
};

class Rva001C9310Scale
{
public:
	char m_gap[ 0x28 ];
	int m_scale;
};

class Rva001C9310
{
public:
	int value();

	void *m_vptr;
	OVERRIDE<Rva001C9310Thing> m_template;
	char m_gap[ 0x210 - 8 ];
	Rva001C9310Scale *m_scaleSrc;
};

int Rva001C9310::value()
{
 int v = m_template->m_value_448;
 if (m_template->m_flags_d0 & 0x2000000)
  return m_scaleSrc->m_scale * v;
 return v;
}
