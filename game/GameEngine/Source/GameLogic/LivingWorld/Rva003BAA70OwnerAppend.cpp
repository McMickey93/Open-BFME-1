// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS
// Rva003BAA70Owner::append (retail 0x0061B960 163 B, ret 4), the routine the
// matched Rva003BAA70ParseArmyMoveToBlock hands each parsed 0x24-byte record
// through ILT 0x00020E64.  The records live in an STLport vector at +0x9C:
// the body walks it (the count re-derived from the two pointers every pass,
// a /36 signed magic divide), skips the new record when an entry has the same
// dword at +8 and the entry's own predicate at 0x003B9200 accepts it, and
// otherwise appends with the inlined push_back of the matched
// vector<Rva0061B4B0Element>::push_back at 0x0061B4B0 (same _Construct at
// ILT 0x00022395, same _M_insert_overflow at ILT 0x00048A45).
//
// One record, several address-derived views: the parser's Rva003BAA70Record,
// the vector element Rva0061B4B0Element and the 0x003B9200 receiver
// Rva003B9200Owner / argument Rva003B9100 are the same 36-byte type, whose
// identity is not recovered.

class Rva003BAA70Record;
class Rva003B9100;

class Rva003B9200Owner
{
public:
	bool rva003B9200( const Rva003B9100 *other ) const;
};

struct Rva0061B4B0Element
{
	char m_lead[ 8 ];
	int m_key;
	char m_rest[ 0x18 ];

	bool isEqual( const Rva0061B4B0Element &other ) const
	{
		return m_key == other.m_key
			&& reinterpret_cast<const Rva003B9200Owner *>( this )->rva003B9200(
				reinterpret_cast<const Rva003B9100 *>( &other ) );
	}
};

namespace _STL
{
template <class Type>
class allocator
{
};

struct __false_type
{
};

template <class Type>
void __cdecl BfmeElementConstruct( Type *destination, const Type &value );

template <class Type, class Allocator>
class vector
{
public:
	unsigned int size() const { return _M_finish - _M_start; }
	Type *begin() { return _M_start; }
	Type &operator[]( unsigned int n ) { return *( begin() + n ); }

	void push_back( const Type &value )
	{
		if ( _M_finish != _M_end_of_storage )
		{
			BfmeElementConstruct( _M_finish, value );
			++_M_finish;
		}
		else
		{
			__false_type tag;
			_M_insert_overflow( _M_finish, value, tag, 1, true );
		}
	}

protected:
	void _M_insert_overflow( Type *position, const Type &value,
		const __false_type &, unsigned int fillLength, bool atEnd );

	Type *_M_start;
	Type *_M_finish;
	Type *_M_end_of_storage;
};
}

class Rva003BAA70Owner
{
public:
	void append( Rva003BAA70Record *record );

private:
	char m_lead[ 0x9c ];
	_STL::vector<Rva0061B4B0Element, _STL::allocator<Rva0061B4B0Element> > m_records;
};

// ?append@Rva003BAA70Owner@@QAEXPAVRva003BAA70Record@@@Z
void Rva003BAA70Owner::append( Rva003BAA70Record *record )
{
	const Rva0061B4B0Element *value = reinterpret_cast<const Rva0061B4B0Element *>( record );

	for ( unsigned int i = 0; i < m_records.size(); ++i )
	{
		if ( m_records[ i ].m_key == value->m_key
			&& reinterpret_cast<const Rva003B9200Owner *>( m_records.begin() + i )->rva003B9200(
				reinterpret_cast<const Rva003B9100 *>( value ) ) )
			return;
	}

	m_records.push_back( *value );
}
