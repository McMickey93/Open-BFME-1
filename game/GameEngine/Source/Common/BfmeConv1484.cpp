// cl: /Od /Ob1 /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS
// stlport
// Retail 0x0082E350 is STLport 4.5.3's
//   _STL::basic_string<char>::find_last_not_of(char, size_type) const
// (stl/_string.c) from the STLport library code BFME linked unoptimised
// (/Od /Ob1). It calls find_if<reverse_iterator<const char*>,
// _Neq_char_bound<char_traits<char> > > at 0x0082DFA0.
#include <string>

template _STL::string::size_type _STL::string::find_last_not_of(char, _STL::string::size_type) const;
