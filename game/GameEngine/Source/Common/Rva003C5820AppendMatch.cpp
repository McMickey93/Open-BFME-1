// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB
// Address-derived reconstruction of the STLport vector append at 0x003C5820.
// The owning vector is at this+0 and the destination vector is at output+4.
// stlport

#define _STLP_NO_EXCEPTIONS 1
#define _M_insert_overflow j_000100d7
#include <vector>
#undef _M_insert_overflow

extern char Rva006A16B0Empty[];

// Refcounted string data: length word at +4, text at +8.
struct Rva003C5270Blob
{
	void *m_00;
	unsigned short m_len;
	unsigned short m_pad;
	char m_data[ 1 ];
};

class Rva003C5890Item
{
public:
	Rva003C5270Blob *m_blob;
};

typedef Rva003C5890Item Rva003C5820Item;

class Rva003C5820Key
{
public:
	Rva003C5270Blob *m_blob;
};

extern "C" int memcmp( const void *, const void *, unsigned int );
#pragma intrinsic( memcmp )

class Rva003C5270BorrowedView
{
public:
	Rva003C5270Blob *m_blob;

	int compare( const Rva003C5820Item &that ) const
	{
		int thatLength = that.m_blob ? that.m_blob->m_len : 0;
		const char *thatText = that.m_blob ? that.m_blob->m_data : Rva006A16B0Empty;
		int thisLength = m_blob ? m_blob->m_len : 0;
		const char *thisText = m_blob ? m_blob->m_data : Rva006A16B0Empty;
		int length = thisLength < thatLength ? thisLength : thatLength;
		int difference = memcmp( thisText, thatText, length );
		if( difference != 0 )
			return difference;
		return thisLength - thatLength;
	}
};

class Rva003C5820Output
{
private:
    char m_pad00[ 4 ];

public:
    _STL::vector<Rva003C5820Item *> m_items;
    void append( Rva003C5820Item *item );
};

class Rva003C5820Owner;
int __stdcall Rva003C5270Find( Rva003C5820Owner *owner, Rva003C5820Key *key );

class Rva003C5820Owner
{
public:
    void appendMatch( Rva003C5820Output *output, Rva003C5820Key *key );
    friend int __stdcall Rva003C5270Find( Rva003C5820Owner *owner, Rva003C5820Key *key );

private:
    _STL::vector<Rva003C5820Item *> m_items;
};

// Retail 0x003C5270, 181 bytes: index of the first item whose string equals
// the key's, or -1. The loop re-tests the vector's size() each pass; caching
// raw begin/end pointers instead puts the owner in EAX rather than EDX.
int __stdcall Rva003C5270Find( Rva003C5820Owner *owner, Rva003C5820Key *key )
{
    for( unsigned int i = 0; i < owner->m_items.size(); ++i )
    {
        Rva003C5270BorrowedView query = { key->m_blob };
        if( query.compare( *owner->m_items[ i ] ) == 0 )
            return i;
    }
    return -1;
}

void Rva003C5820Owner::appendMatch( Rva003C5820Output *output,
                                    Rva003C5820Key *key )
{
    int index = Rva003C5270Find( this, key );
    if( index != -1 )
    {
        Rva003C5820Item *item = m_items[ index ];
        output->m_items.push_back( item );
    }
}
