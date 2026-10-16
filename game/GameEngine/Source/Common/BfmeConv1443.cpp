// cl: /Od /Ob1 /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS
// stlport
// Retail 0x0082DFA0 is STLport's
//   _STL::find_if<reverse_iterator<const char*>, _Neq_char_bound<char_traits<char> > >
// called by basic_string<char>::find_last_not_of(char, size_type) at
// 0x0082E350, from the STLport library code BFME linked unoptimised
// (/Od /Ob1): the reverse_iterator copies are inlined copy constructors and the
// frame keeps /Ob1's slots for the declined inline __find_if (retail 0x0082D470).
#include <string>

template _STL::reverse_iterator<const char*> _STL::find_if(
	_STL::reverse_iterator<const char*>, _STL::reverse_iterator<const char*>,
	_STL::_Neq_char_bound<_STL::char_traits<char> >);
