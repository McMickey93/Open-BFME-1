// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// stlport

// The symbol pin and the SubsystemLegend copy callers identify this as the
// STLport vector<AsciiString> copy constructor at retail 0x000D2E70.
#define _STLP_NO_EXCEPTIONS 1
#include <new>
#include "ascii_string.h"
#include <vector>

// Assignment has a separate retail owner at 0x000DE2C0. Instantiating the
// copy constructor's vector must not supply an incompatible assignment copy.
namespace _STL {
template <> vector<AsciiString> &vector<AsciiString>::operator=(
    const vector<AsciiString> &);
}

template class _STL::vector<AsciiString,
	_STL::allocator<AsciiString> >;
