// STLport sort_heap over int with the comparator whose adjust_heap body is
// matched at retail 0x007538A0.
// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport
#define _STLP_NO_EXCEPTIONS 1
#include <algorithm>

struct Q4Cmp00753DD0 { void *m_state; };

// Retail calls the separately rowed heap adjustment; do not instantiate
// another comparator view while emitting this sort helper.
namespace _STL {
template <> void __adjust_heap<int *, int, int, Q4Cmp00753DD0>(
    int *, int, int, int, Q4Cmp00753DD0);
}

template void _STL::sort_heap<int *, Q4Cmp00753DD0>(
	int *, int *, Q4Cmp00753DD0);
