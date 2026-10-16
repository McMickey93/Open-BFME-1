// cl: /Od /Ob1 /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS
// stlport
// Retail 0x0082D470 is STLport's random-access
//   _STL::__find_if<reverse_iterator<const char*>, _Neq_char_bound<char_traits<char> > >
// (stl/_algobase.c, the four-way unrolled loop), the out-of-line callee of
// find_if at 0x0082DFA0 that basic_string<char>::find_last_not_of(char,
// size_type) uses. BFME linked this STLport code unoptimised (/Od /Ob1).
#include <string>

template _STL::reverse_iterator<const char*> _STL::__find_if(
	_STL::reverse_iterator<const char*>, _STL::reverse_iterator<const char*>,
	_STL::_Neq_char_bound<_STL::char_traits<char> >,
	const _STL::random_access_iterator_tag &);
