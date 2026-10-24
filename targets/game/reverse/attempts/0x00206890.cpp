// ?d_00206890@@YAXXZ
// partial score=0.3846 date=2026-10-24
// ?d_00206890@@YAXXZ
// partial 147/156B shape 0.938 date=2026-10-24: entry m_20!=0 skips; true on override flag 0x400 or null entry+4
// cl: /DNDEBUG /MD /EHsc

typedef int ObjectID;

class Object;

class GameLogic
{
public:
	Object *findObjectByID( ObjectID id );
};

extern GameLogic *TheBfmeGameLogic;

class Object
{
};

class Overridable
{
public:
	Overridable *getFinalOverride();

	char m_unmodelled_00[ 4 ];
	Overridable *m_nextOverride;
	char m_unmodelled[ 0xd0 ];
	unsigned int m_flags;

	Overridable *finalOverride()
	{
		if( m_nextOverride )
			return m_nextOverride->getFinalOverride();
		return this;
	}
};

class BfmeOverride
{
public:
	Overridable *operator->()
	{
		if( !m_overridable )
			return 0;
		return m_overridable->finalOverride();
	}
	Overridable *m_overridable;
};

class BfmeDockObject
{
public:
	char m_unmodelled_00[ 4 ];
	BfmeOverride m_template;
};

class BfmeSiegeDockEntry
{
public:
	char m_unmodelled_00[ 4 ];
	void *m_at04;
	char m_unmodelled[ 0x18 ];
	unsigned int m_at20;
};

class BfmeOuterCFD
{
public:
	void bfmeTwoCFD();
};

class __declspec( novtable ) Rva00206890SiegeDockingInterface
{
public:
	virtual bool query( ObjectID id );

	unsigned int size() const { return m_finish - m_start; }
	BfmeSiegeDockEntry *at( unsigned int i ) const { return m_start[ i ]; }
private:
	BfmeSiegeDockEntry **m_start;
	BfmeSiegeDockEntry **m_finish;
};

// ?query@Rva00206890SiegeDockingInterface@@QAE_NH@Z
bool Rva00206890SiegeDockingInterface::query( ObjectID id )
{
	Object *object = TheBfmeGameLogic->findObjectByID( id );
	if( object == 0 )
		return false;

	((BfmeOuterCFD *)((char *)this - 0x20))->bfmeTwoCFD();

	unsigned int count = size();
	if( count == 0 )
		return false;

	for( unsigned int i = 0; i < count; ++i )
	{
		BfmeSiegeDockEntry *entry = at( i );
		if( entry->m_at20 != 0 )
			continue;
		if( ( ((BfmeDockObject *)object)->m_template->m_flags & 0x400 ) != 0 || entry->m_at04 == 0 )
			return true;
	}

	return false;
}
