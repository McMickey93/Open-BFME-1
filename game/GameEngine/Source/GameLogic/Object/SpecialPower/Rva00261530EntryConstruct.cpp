// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/bfmekindof /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib
// stlport
// Retail 0x00261440 (90 B): the copy constructor of the 16-byte entry that
// vector<Rva00262120Entry>::_M_insert_overflow (0x00262120) grows.
// Retail 0x00261530 (66 B): STLport's _Construct placing one copy through it.
// 0x00261530 is called by that overflow, the push_back at 0x00262280 and the
// element walks at 0x00261590/0x002615D0; it calls 0x00261440, which copies the
// inner vector<Rva002622D0Subject *> through 0x001D95A0/0x001D95B0.
// Rva00262120EntryVector.cpp forces _Construct inline for the overflow, so the
// out-of-line instance lives here.

#define _STLP_USE_STATIC_LIB 1
#define _STLP_NO_EXCEPTIONS 1
#define BFME_STLP_NODE_ALLOC 1
#define __PLACEMENT_VEC_NEW_INLINE
#include <vector>
#include "PreRTS.h"

class Object;
class Rva002622D0Subject;

struct Rva00262120Entry
{
	Object *object;
	std::vector<Rva002622D0Subject *> grouped;

	__declspec(noinline) Rva00262120Entry(const Rva00262120Entry &that)
		: object(that.object), grouped(that.grouped) {}
};

template void _STL::_Construct<Rva00262120Entry, Rva00262120Entry>(
	Rva00262120Entry *, const Rva00262120Entry &);
