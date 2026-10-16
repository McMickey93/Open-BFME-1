// ??1?$_Vector_base@URva009F5600Element@@V?$allocator@URva009F5600Element@@@_STL@@@_STL@@QAE@XZ
// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport
// Retail 0x009F5600 (45 bytes, unreferenced): the STLport _Vector_base
// destructor for an 8-byte element (sar/shl by 3, node allocator up to 128
// bytes), the shape of _Vector_base<int> at 0x0081D920. Nothing calls it, so
// the element type is unknown and keeps the address.
#define _STLP_NO_EXCEPTIONS 1
#include <vector>

struct Rva009F5600Element
{
	int first;
	int second;
};

template class _STL::_Vector_base<Rva009F5600Element, _STL::allocator<Rva009F5600Element> >;
