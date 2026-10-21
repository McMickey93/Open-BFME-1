// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport

#define _BFME_RETAIL_TREE_INSERT_LAYOUT
#include <map>

// The matching four-argument insertion body is owned by
// stlport_rb_tree_ushort_int_insert.cpp (retail 0x0037B600).
typedef _STL::pair<const unsigned short, int> RetailUShortIntPair;
typedef _STL::_Rb_tree<unsigned short, RetailUShortIntPair,
    _STL::_Select1st<RetailUShortIntPair>, _STL::less<unsigned short>,
    _STL::allocator<RetailUShortIntPair> > RetailUShortIntTree;
template <> RetailUShortIntTree::iterator RetailUShortIntTree::_M_insert(
    _STL::_Rb_tree_node_base *, _STL::_Rb_tree_node_base *,
    const RetailUShortIntPair &, _STL::_Rb_tree_node_base *);

typedef _STL::pair<const unsigned short, int> UnsignedShortIntPair;
typedef _STL::_Rb_tree<unsigned short,
	UnsignedShortIntPair,
	_STL::_Select1st<UnsignedShortIntPair>,
	_STL::less<unsigned short>,
	_STL::allocator<UnsignedShortIntPair> > UnsignedShortIntTree;

template _STL::pair<UnsignedShortIntTree::iterator, bool>
UnsignedShortIntTree::insert_unique(const UnsignedShortIntPair &);
