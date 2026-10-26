// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/stringbaseascii /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/debug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2 /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWMath /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWSaveLoad /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Main /Igame/Libraries/Source/WWVegas/WWLib
// stlport
//
// Near-twin of ??A?$hash_map@VAsciiString@@PAVSkyboxTextureSet@@...@Z (twin
// 0x000B8BD0, game/GameEngine/Source/Common/INI/INISkyboxTextureSet.cpp):
// identical hash_map<AsciiString, T>::operator[] insertion shape, but T here
// is one byte (stored with a byte mov instead of a dword mov at the pair's
// second-member init). T is bool: ilt_oracle confirms this operator[] at its
// ILT 0x0001859D and pair<const AsciiString,bool>'s dtor at 0x000479D3, the
// ILT its unwind funclet 0x00BFBDF0 jumps to (unsigned char contradicts both).
#include "PreRTS.h"
#include "Common/INI.h"
#include "Common/STLTypedefs.h"
#include "string_base.h"

// Retail inlines ~AsciiString: temporaries are released by a direct call to
// StringBase<char>::releaseBuffer (0x00887940), not the ??1AsciiString stub.
inline AsciiString::~AsciiString() { ((StringBase<char> *)this)->releaseBuffer(); }

typedef std::hash_map< AsciiString, bool, rts::hash<AsciiString>, rts::equal_to<AsciiString> > Rva000F7310Map;

extern Rva000F7310Map TheRva000F7310Map;

// @??A?$hash_map@VAsciiString@@_NU?$hash@VAsciiString@@@rts@@U?$equal_to@VAsciiString@@@2@V?$allocator@U?$pair@$$CBVAsciiString@@_N@_STL@@@_STL@@@_STL@@QAEAA_NABVAsciiString@@@Z 0x000F7310
bool &accessRva000F7310( const AsciiString &key )
{
	return TheRva000F7310Map[ key ];
}
