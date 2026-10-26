// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /DBFME_STLP_NODE_ALLOC /Iinputs/reference/shims/stringbaseascii /Iinputs/reference/shims/stlp_nodealloc /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/Generals/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/Generals/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/Generals/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/Generals/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WWLib
// stlport

#include "PreRTS.h"
#include "Common/IgnorePreferences.h"

// ??0?$_Rb_tree@HU?$pair@$$CBHVAsciiString@@@_STL@@U?$_Select1st@U?$pair@$$CBHVAsciiString@@@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHVAsciiString@@@_STL@@@2@@_STL@@QAE@ABV01@@Z
// Emit only the owned underlying tree copy constructor.
template _STL::_Rb_tree<int, _STL::pair<const int, AsciiString>,
	_STL::_Select1st<_STL::pair<const int, AsciiString> >, _STL::less<int>,
	_STL::allocator<_STL::pair<const int, AsciiString> > >::_Rb_tree(
	const _STL::_Rb_tree<int, _STL::pair<const int, AsciiString>,
		_STL::_Select1st<_STL::pair<const int, AsciiString> >, _STL::less<int>,
		_STL::allocator<_STL::pair<const int, AsciiString> > > &);
