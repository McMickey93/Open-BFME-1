// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport

// The retail loop advances a deque iterator by a 20-byte value over 0x78-byte
// nodes and performs no destructor call; this is the trivial-payload overload
// of STLport's range __destroy.

#include <deque>

struct Gen_t_008fb350_p12pod { char m_body[20]; };

namespace _STL
{
template void __destroy<
	_Deque_iterator<Gen_t_008fb350_p12pod,
		_Nonconst_traits<Gen_t_008fb350_p12pod> >,
	Gen_t_008fb350_p12pod>(
	_Deque_iterator<Gen_t_008fb350_p12pod,
		_Nonconst_traits<Gen_t_008fb350_p12pod> >,
	_Deque_iterator<Gen_t_008fb350_p12pod,
		_Nonconst_traits<Gen_t_008fb350_p12pod> >,
	Gen_t_008fb350_p12pod *);
}

// Complete wrapper at008FAED0. The native iterator contract is two values,
// each16 bytes; the established element/callee view is20 bytes, not12.
typedef _STL::deque<Gen_t_008fb350_p12pod>::iterator Rva008FAED0Iterator;
void Rva008FAED0(Rva008FAED0Iterator first, Rva008FAED0Iterator last)
{
    _STL::_Destroy(first, last);
}

// Complete wrapper at 0x008FAF20 (78 B, unreferenced): the same STLport range
// destroy over a deque of 8-byte elements. Here __destroy_aux stays out of line
// and the call reaches 0x008FA480, whose loop steps 8 bytes over 0x80-byte
// nodes; the element keeps the type token the 0x008FA480 pin is spelled with.
struct Gen_t_008fb410_p16pod { int a[2]; };
typedef _STL::deque<Gen_t_008fb410_p16pod>::iterator Rva008FAF20Iterator;
void Rva008FAF20(Rva008FAF20Iterator first, Rva008FAF20Iterator last)
{
    _STL::_Destroy(first, last);
}
