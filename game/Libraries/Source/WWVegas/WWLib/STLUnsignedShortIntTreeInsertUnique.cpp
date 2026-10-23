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

// The binary calls the independently matched insertion ILT.
extern void j_0001f32a();

template <>
inline _STL::pair<UnsignedShortIntTree::iterator, bool>
UnsignedShortIntTree::insert_unique(const UnsignedShortIntPair &__v)
{
    union {
        void (*raw)();
        iterator (UnsignedShortIntTree::*insert)(_STL::_Rb_tree_node_base *,
            _STL::_Rb_tree_node_base *, const UnsignedShortIntPair &,
            _STL::_Rb_tree_node_base *);
    } target;
    target.raw = j_0001f32a;
    _Link_type __y = this->_M_header._M_data;
    _Link_type __x = _M_root();
    bool __comp = true;
    while (__x != 0) {
        __y = __x;
        __comp = _M_key_compare(_STL::_Select1st<UnsignedShortIntPair>()(__v), _S_key(__x));
        __x = __comp ? _S_left(__x) : _S_right(__x);
    }
    iterator __j = iterator(__y);
    if (__comp && __j == begin())
        return _STL::pair<iterator, bool>((this->*target.insert)(__y, __y, __v, 0), true);
    if (__comp)
        --__j;
    if (_M_key_compare(_S_key(__j._M_node), _STL::_Select1st<UnsignedShortIntPair>()(__v)))
        return _STL::pair<iterator, bool>((this->*target.insert)(__x, __y, __v, 0), true);
    return _STL::pair<iterator, bool>(__j, false);
}

// Retain the specialization as this TU's matched out-of-line provider.
template _STL::pair<UnsignedShortIntTree::iterator, bool>
UnsignedShortIntTree::insert_unique(const UnsignedShortIntPair &);
