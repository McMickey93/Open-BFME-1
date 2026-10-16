// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// Recenter the slot positions around a selected slot or their mean.
// Evidence: targets/game/reverse/identity_evidence/0023b9f0-recenter.md
typedef int Int;
typedef unsigned int UnsignedInt;

#include "ascii_string.h"

class ThingTemplate
{
public:
	char m_bfmeHead[ 0xc8 ];
	UnsignedInt m_kindof;
};

class ThingFactory;

// The existing retail lookup body at RVA00137E80, reached via ILT00028560.
class BfmeThingFactory
{
public:
	const ThingTemplate *findTemplate( const AsciiString &name );
};

extern ThingFactory *TheThingFactory;

struct BfmeHordeInner12
{
	// Only the twelve-byte stride is consumed here; these words stay opaque.
	UnsignedInt a, b, c;
};

class BfmeHordeInnerVec
{
public:
	UnsignedInt size( void ) const { return (UnsignedInt)( m_bfmeEnd - m_bfmeBegin ); }

	BfmeHordeInner12 *m_bfmeBegin;
	BfmeHordeInner12 *m_bfmeEnd;
	BfmeHordeInner12 *m_bfmeCap;
};

class BfmeHordeRosterEntry
{
public:
	UnsignedInt m_bfmeKey;
	AsciiString m_bfmeName;
	BfmeHordeInnerVec m_bfmeInner;
};

class BfmeHordeRosterVec
{
public:
	UnsignedInt size( void ) const { return (UnsignedInt)( m_bfmeEnd - m_bfmeBegin ); }
	BfmeHordeRosterEntry *operator[]( UnsignedInt i ) const { return m_bfmeBegin[ i ]; }

	BfmeHordeRosterEntry **m_bfmeBegin;
	BfmeHordeRosterEntry **m_bfmeEnd;
	BfmeHordeRosterEntry **m_bfmeCap;
};

class BfmeHordeRosterOwner
{
public:
	char m_bfmeHead[ 0x224 ];
	BfmeHordeRosterVec m_bfmeRoster;
};

struct BfmeHordePosition0023B9F0
{
	float m_bfmeX, m_bfmeY;

	BfmeHordePosition0023B9F0 &operator-=( const BfmeHordePosition0023B9F0 &other )
	{
		m_bfmeX -= other.m_bfmeX;
		m_bfmeY -= other.m_bfmeY;
		return *this;
	}
};

struct BfmeHordeSlot
{
	UnsignedInt m_bfmeKey;
	BfmeHordePosition0023B9F0 m_bfmePosition;
	float m_bfmeW;
};

class BfmeHordeContainRoster
{
public:
	void rva0023B9F0( void );

private:
	char m_bfmeHead[ 4 ];
	BfmeHordeRosterOwner *m_bfmeOwner;
	char m_bfmeGap[ 0x12c - 0x08 ];
	BfmeHordeSlot *m_bfmeSlotBegin;
	BfmeHordeSlot *m_bfmeSlotEnd;
};

// ?rva0023B9F0@BfmeHordeContainRoster@@QAEXXZ
void BfmeHordeContainRoster::rva0023B9F0( void )
{
	BfmeHordeRosterOwner *owner = m_bfmeOwner;

	BfmeHordeRosterVec &roster = owner->m_bfmeRoster;

	Int total = -1;
	Int count = 0;
	for ( UnsignedInt i = 0; i < roster.size(); ++i )
	{
		const ThingTemplate *t = reinterpret_cast<BfmeThingFactory *>(TheThingFactory)->findTemplate( roster[ i ]->m_bfmeName );
		if ( t && ( t->m_kindof & 0x0800 ) )
		{
			total = count;
			break;
		}

		count += roster[ i ]->m_bfmeInner.size();
	}

	Int cnt = 0;
	Int idx = 0;
	BfmeHordeSlot *begin = m_bfmeSlotBegin;
	BfmeHordePosition0023B9F0 center;
	float &sumX = center.m_bfmeX;
	float &sumY = center.m_bfmeY;
	sumX = 0.0f;
	BfmeHordeSlot *end = m_bfmeSlotEnd;
	sumY = 0.0f;

	for ( BfmeHordeSlot *p = begin; p != end; ++p )
	{
		sumX += p->m_bfmePosition.m_bfmeX;
		++cnt;
		sumY += p->m_bfmePosition.m_bfmeY;
		if ( idx == total )
		{
			center = p->m_bfmePosition;
			cnt = 1;
			break;
		}
		++idx;
	}

	if ( cnt != 0 )
	{
		float inv = 1.0f / (float)cnt;
		sumX *= inv;
		sumY *= inv;
	}

	begin = m_bfmeSlotBegin;
	for ( BfmeHordeSlot *p = begin; p != m_bfmeSlotEnd; ++p )
	{
		p->m_bfmePosition -= center;
	}
}
