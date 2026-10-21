// ?probe@Gen003BFB20Owner@@QAE_NPAX@Z
// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Igame/Libraries/Source/WWVegas/WWLib

#define _STLP_NO_EXCEPTIONS 1
#include "ascii_string.h"

extern "C" __declspec(dllimport) void *__cdecl memmove( void *destination, const void *source, unsigned int count );

struct BfmeObj923GState
{
	char m_pad00[ 0x18 ];
	unsigned char m_active;
};

// Field view of the region returned by the manager lookup.
class BfmeObj923G
{
public:
	char m_pad00[ 0x3C ];
	AsciiString m_name;
	char m_pad40[ 0x40 ];
	int m_value80;
	char m_pad84[ 0x28 ];
	int m_handleAC;
	char m_padB0[ 0x4 ];
	int m_createdB4;
	AsciiString m_messageB8;
	char m_padBC[ 0x30 ];
	BfmeObj923GState *m_stateEC;
};

class LivingWorldRegion;
class LivingWorldRegionManager
{
public:
	LivingWorldRegion *rva003C8A50( const AsciiString &key );
};

extern int __cdecl Rva003C9220( int one, int two );

// ?bfmeMakeBNG@@YAHHH@Z absent-from-retail
static __forceinline int bfmeMakeBNG( int one, int two )
{
	return Rva003C9220( one, two );
}

class BfmeSinkAM
{
public:
	void bfmeDrop( int handle );
};

class BfmeGameCW
{
public:
	// ?removeEntry@BfmeGameCW@@QAEXH@Z absent-from-retail
	void removeEntry( int handle )
	{
		((BfmeSinkAM *)this)->bfmeDrop( handle );
	}
};

class LivingWorldManager;
extern LivingWorldManager *TheLivingWorldManager;

// ?g_bfmeGameCW@@YAPAVBfmeGameCW@@XZ absent-from-retail
static __forceinline BfmeGameCW *g_bfmeGameCW()
{
	return (BfmeGameCW *)TheLivingWorldManager;
}

class Glo012F1028Type
{
public:
	void addValue( int amount )
	{
		m_valueA0 += amount;
	}

	void enterSelectedIlt( AsciiString *name );
	char m_pad00[ 0xA0 ];
	volatile int m_valueA0;
};

class Glo012F1024Type
{
public:
	void enterSelected( AsciiString *name );
};

// ?enterSelectedIlt@Glo012F1028Type@@QAEXPAVAsciiString@@@Z absent-from-retail
__forceinline void Glo012F1028Type::enterSelectedIlt( AsciiString *name )
{
	((Glo012F1024Type *)this)->enterSelected( name );
}

class LivingWorldLogic;
extern LivingWorldLogic *TheLivingWorldLogic;
class LivingWorldCampaignManager;
extern LivingWorldCampaignManager *TheLivingWorldCampaignManager;

struct BfmeStringInlineData
{
	int m_refCount;
	unsigned short m_length;
};

class BfmePointerVector
{
public:
	unsigned int size() const
	{
		return (unsigned int)( m_finish - m_start );
	}

	BfmeObj923G **begin() const
	{
		return m_start;
	}

	void erase( BfmeObj923G **position )
	{
		BfmeObj923G **next = position + 1;
		if ( m_finish != next )
			memmove( position, next, (unsigned int)( (char *)m_finish - (char *)next ) );
		--m_finish;
	}

	BfmeObj923G **m_start;
	BfmeObj923G **m_finish;
};

class Gen003BFB20Storage
{
public:
	void *m_vtable;
	char m_pad04[ 0x10 ];
	BfmePointerVector m_objects;
};

class Gen003BFB20Owner : public Gen003BFB20Storage
{
public:
	bool probe( void *key );
	void recomputeIlt();
};

extern void j_000349f5();

// ?recomputeIlt@Gen003BFB20Owner@@QAEXXZ absent-from-retail
__forceinline void Gen003BFB20Owner::recomputeIlt()
{
	typedef void (Gen003BFB20Owner::*Call)();
	union { void (*raw)(); Call member; } target;
	target.raw = j_000349f5;
	(this->*target.member)();
}

// ?bfmeFind923G@@YAPAVBfmeObj923G@@PAVGen003BFB20Owner@@PAX@Z absent-from-retail
static __forceinline BfmeObj923G *bfmeFind923G( Gen003BFB20Owner *owner, void *key )
{
	return (BfmeObj923G *)((LivingWorldRegionManager *)owner)->rva003C8A50( *(const AsciiString *)key );
}

// ?probe@Gen003BFB20Owner@@QAE_NPAX@Z
bool Gen003BFB20Owner::probe( void *key )
{
	BfmeObj923G *object = bfmeFind923G( this, key );
	if ( object != 0 )
	{
		char *owner = (char *)this;
		int created = bfmeMakeBNG( 1, 1 );
		object->m_createdB4 = created;
		BfmeObj923GState *state = object->m_stateEC;
		state->m_active = 1;
		object->m_messageB8.StringBase<char>::clear();

		for ( unsigned int index = 0; index < ((BfmePointerVector *)( owner + 0x14 ))->size(); ++index )
		{
			if ( ((BfmePointerVector *)( owner + 0x14 ))->begin()[ index ] == object )
			{
				((BfmePointerVector *)( owner + 0x14 ))->erase( ((BfmePointerVector *)( owner + 0x14 ))->begin() + index );
				int handle = object->m_handleAC;
				g_bfmeGameCW()->removeEntry( handle );
				break;
			}
		}

		((Glo012F1028Type *)TheLivingWorldLogic)->addValue( object->m_value80 );
		recomputeIlt();

		AsciiString name = object->m_name;
		if ( *(BfmeStringInlineData **)&name != 0 && (*(BfmeStringInlineData **)&name)->m_length != 0 )
		{
			((Glo012F1028Type *)TheLivingWorldCampaignManager)->enterSelectedIlt( &name );
			return false;
		}
	}

	return true;
}
