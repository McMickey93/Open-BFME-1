// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Iinputs/reference/shims/asciistringsetoutofline /Iinputs/reference/shims/psplayerstats /Iinputs/reference/shims/peerdefs /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/debug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad /Igame/Libraries/Source/WWVegas/WWLib
// stlport
// Retail 0x007722F0 is an implicit assignment operator for a 32-byte value.
// Its only nontrivial member is this STLport string at +4; the callee is
// basic_string<char>::_M_assign_dispatch. No named caller or surviving symbol
// identifies the owner, so the class name deliberately remains address-based.
#include <string>

struct Rva007722F0StringMemberAssign
{
	struct Tail
	{
		int first;
		int second;
		int third;
	};

	Rva007722F0StringMemberAssign &operator=(
			const Rva007722F0StringMemberAssign &other);

	int m_head;
	_STL::basic_string<char> m_text;
	Tail m_tail;
	int m_tail3;
};

Rva007722F0StringMemberAssign &Rva007722F0StringMemberAssign::operator=(
		const Rva007722F0StringMemberAssign &other)
{
	m_head = other.m_head;
	m_text = other.m_text;
	m_tail = other.m_tail;
	m_tail3 = other.m_tail3;
	return *this;
}
