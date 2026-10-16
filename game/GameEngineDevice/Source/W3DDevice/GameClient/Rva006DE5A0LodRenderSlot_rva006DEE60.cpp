// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Iinputs/reference/shims/stringbaseascii /Igame/Libraries/Source/WWVegas/WWLib
// stlport
//
// Open-BFME: retail 0x006DEE60 (279 bytes), reached through ILT 0x0002E771
// (prior verdicts name bfmeForward@Gen_006C89D0 as its caller). It is a second
// method of the
// slot table whose 0x006DE5A0 member (Rva006DE5A0LodRenderSlot.cpp) fills
// entries at +0x18 (twelve bytes each, ten of them) and counts them at +0x90;
// this body proves the rest of the object: ten twelve-byte STLport
// set<Rva006DE9B0Target *> at +0x94 (their node counts are read at +4 and
// capped at 1000) and an enable byte at +0x10C, which is exactly where the
// sets end.
//
// It finds the entry whose name matches the record's (case-insensitively),
// adding one through 0x006DE5A0 when none does, then allocates a 0x58-byte
// target for the drawable and that entry index (constructor 0x006DB470,
// reached through ILT 0x00035274: it stores the drawable, its scale and its
// position) and inserts it into the entry's set. Names are address-derived:
// no named caller identifies the class or the method.
//
// Shape notes measured against retail: the name search is a forced-inline
// member (left to the compiler it is emitted out of line), the two guards are
// separate early returns, and the set is handed a scoped copy of the new
// pointer so the returned one stays in a register.

#define _BFME_RETAIL_TREE_INSERT_LAYOUT
#include <set>
#include "Common/AsciiString.h"

class Drawable;

// The 0x58-byte target is a TBuff: its constructor is the matched
// TBuff::TBuff row at 0x006DB470.
class TBuff
{
public:
	TBuff( Drawable *draw, int index );
	unsigned char m_data[ 0x58 ];
};

struct Rva006DE9B0Target
{
	unsigned char m_data[ 0x58 ];
};

typedef Rva006DE9B0Target *Rva006DE9B0Key;

typedef _STL::_Rb_tree<Rva006DE9B0Key,
	Rva006DE9B0Key,
	_STL::_Identity<Rva006DE9B0Key>,
	_STL::less<Rva006DE9B0Key>,
	_STL::allocator<Rva006DE9B0Key> > PointerIdentityTree006DE9B0;

// The tree insert is retail's out-of-line 0x006DE9B0 (RvaTreeInsertUniqueIdentity.cpp).
template <>
_STL::pair<PointerIdentityTree006DE9B0::iterator, bool>
PointerIdentityTree006DE9B0::insert_unique( const Rva006DE9B0Key & );

typedef _STL::set<Rva006DE9B0Key> Rva006DE9B0TargetSet;

struct Rva006DE5A0Input
{
	unsigned char m_pad[ 8 ];
	AsciiString m_name;
	unsigned char m_flag;
};

struct Rva006DE5A0Entry
{
	void *m_obj;
	AsciiString m_name;
	unsigned char m_flag;
	unsigned char m_pad[ 3 ];
};

class Rva006DE5A0LodRenderSlot
{
	unsigned char m_pad[ 0x18 ];
	Rva006DE5A0Entry m_entries[ 10 ];
	int m_count;
	Rva006DE9B0TargetSet m_targets[ 10 ];
	unsigned char m_enabled;

	__forceinline int findEntry( const AsciiString &name ) const
	{
		for( int i = 0; i < m_count; ++i )
		{
			if( m_entries[ i ].m_name.compareNoCase( name ) == 0 )
				return i;
		}
		return -1;
	}

public:
	int rva006DE5A0( AsciiString *name, Rva006DE5A0Input *record );
	Rva006DE9B0Target *rva006DEE60( Drawable *draw, Rva006DE5A0Input *record );
};

Rva006DE9B0Target *Rva006DE5A0LodRenderSlot::rva006DEE60( Drawable *draw, Rva006DE5A0Input *record )
{
	if( draw == 0 )
		return 0;
	if( !m_enabled )
		return 0;

	int index = findEntry( record->m_name );
	if( index < 0 )
	{
		index = rva006DE5A0( &record->m_name, record );
		if( index < 0 )
			return 0;
	}

	Rva006DE9B0TargetSet &targets = m_targets[ index ];
	if( targets.size() >= 1000 )
		return 0;

	Rva006DE9B0Target *target = reinterpret_cast<Rva006DE9B0Target *>( new TBuff( draw, index ) );
	{
		Rva006DE9B0Key key = target;
		targets.insert( key );
	}
	return target;
}
