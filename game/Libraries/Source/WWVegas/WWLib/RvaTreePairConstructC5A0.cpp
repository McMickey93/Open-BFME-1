// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB
// Structural recovery for the retail pair construction body at 0x0094C5A0.

struct Rva0094C5A0Thing
{
	int head;
	unsigned short refs;
};

class Rva0094C5A0Handle
{
	public:
	Rva0094C5A0Handle(void) : value( 0 ) {}
	Rva0094C5A0Handle(const Rva0094C5A0Handle &other)
	{
		Rva0094C5A0Thing *thing = other.value;
		value = thing;
		if ( thing )
			++thing->refs;
	}
	~Rva0094C5A0Handle(void)
	{
		if ( value )
			--value->refs;
	}
	Rva0094C5A0Thing *value;
};

struct Rva0094C5A0Value
{
	unsigned value[ 4 ];
};

struct Rva0094C5A0Pair
{
	Rva0094C5A0Pair(const Rva0094C5A0Handle &first,
		const Rva0094C5A0Value &second)
		: m_first(first), m_second(second)
	{
	}
	Rva0094C5A0Handle m_first;
	Rva0094C5A0Value m_second;
};

Rva0094C5A0Pair __cdecl rva0094C5A0MakePair(
	const Rva0094C5A0Handle *first, const Rva0094C5A0Value *second)
{
	return Rva0094C5A0Pair(*first, *second);
}

// 0x0094C450 (15 bytes), unreferenced: copies the node pointer held at +0,
// steps it back with _Rb_global<bool>::_M_decrement and returns the address
// of the node's value field (+0x10) -- the shape of a reverse iterator's
// operator* over some red-black tree.  The tree's value type is unknown, so
// the name stays address-derived.
namespace _STL
{
struct _Rb_tree_node_base;
template <class _Dummy> struct _Rb_global
{
	static _Rb_tree_node_base *_M_decrement(_Rb_tree_node_base *);
};
}

struct Rva0094C450TreeIterator
{
	_STL::_Rb_tree_node_base *_M_node;
	void _M_decrement() { _M_node = _STL::_Rb_global<bool>::_M_decrement(_M_node); }
};

class Rva0094C450ReverseIterator
{
public:
	char &deref() const;
	Rva0094C450TreeIterator m_current;
};

char &Rva0094C450ReverseIterator::deref() const
{
	Rva0094C450TreeIterator tmp = m_current;
	tmp._M_decrement();
	return *((char *)tmp._M_node + 0x10);
}
