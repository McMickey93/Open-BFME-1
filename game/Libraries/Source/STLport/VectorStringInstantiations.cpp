// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport
//
// Exact STLport 4.5.3 vector<string> member instantiations.
//
// 0x008FF930 (16 B, unreferenced, int3 padded both sides): pop_back steps
// _M_finish back by sizeof(string) (12) and tail-jumps to the out-of-line
// basic_string<char> destructor through ILT 0x0001642D (ilt_oracle-confirmed
// for that name), the shape vector<string>::pop_back compiles to.

#include <string>
#include <vector>

template void _STL::vector<_STL::string>::pop_back();
