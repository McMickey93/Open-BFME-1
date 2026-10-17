// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: retail 0x0022E150 (222 bytes), reached through ILT 0x000115A9.
// Eight TransportContain-family constructors install it as slot 0 of the
// interface at complete-object offset +0xD4; no named caller or declaration
// identifies the method, so the class and method names are address-derived.
//
// The body is __thiscall with five stack arguments (ret 0x14) and never reads
// `this'. It builds a zeroed BitFlags<86> status mask, sets bit 54 when the
// sink's slot 0x68 query, TheGlobalData+0xDCD, two ThingTemplate::m_kindof
// bits and TheAI->m_aiData+0xB7 allow it, creates the object through
// ThingFactory::newObject with the creator's team, offers it to the sink's
// slot 0x84, and on acceptance calls the new object's module slot 0x84 with 1
// when the creator's module answers its slot 0x88 query, then the sink's slot
// 0x88. The fourth argument is unused.
//
// Shape notes measured against retail: the mask is cleared by an inline
// memset (one xor and three register stores, as STLport bitset::reset does),
// the team is read into a local before the factory call, and the new object's
// module is read once into a local.

extern "C" void *memset( void *, int, unsigned int );
#pragma intrinsic( memset )

template <int NUMBITS>
class BitFlags
{
public:
	BitFlags() { memset( m_bits, 0, sizeof( m_bits ) ); }
	unsigned int m_bits[ 3 ];
};

class Object;
class Team;

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/ThingTemplate.h
class ThingTemplate
{
public:
	char m_gap00[ 0xC8 ];
	unsigned int m_kindof[ 3 ];
};

class ThingFactory
{
public:
	Object *newObject( const ThingTemplate *tmplate, Team *team, const BitFlags< 86 > &statusBits, unsigned int flags );
};
extern ThingFactory *TheThingFactory;

class GlobalData
{
public:
	char m_gap0000[ 0xDCD ];
	bool m_rvaDCD;
};
// retail 0x012ED5C8 (census 37f19b491b queue 35): the owned name there is
// ?TheWritableGlobalData@@3PAVGlobalData@@A (data_rows.csv line 3).
extern GlobalData *TheWritableGlobalData;

struct Rva0022E150AIData
{
	char m_gap00[ 0xB7 ];
	bool m_rvaB7;
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/AI.h
class AI
{
public:
	char m_gap00[ 0x14 ];
	Rva0022E150AIData *m_aiData;
};
extern AI *TheAI;

class Rva0022E150Module
{
public:
	virtual void v00(); virtual void v01(); virtual void v02(); virtual void v03();
	virtual void v04(); virtual void v05(); virtual void v06(); virtual void v07();
	virtual void v08(); virtual void v09(); virtual void v10(); virtual void v11();
	virtual void v12(); virtual void v13(); virtual void v14(); virtual void v15();
	virtual void v16(); virtual void v17(); virtual void v18(); virtual void v19();
	virtual void v20(); virtual void v21(); virtual void v22(); virtual void v23();
	virtual void v24(); virtual void v25(); virtual void v26(); virtual void v27();
	virtual void v28(); virtual void v29(); virtual void v30(); virtual void v31();
	virtual void v32();
	virtual void slot84( int value );
	virtual bool slot88();
};

class Object
{
public:
	char m_gap000[ 0x200 ];
	Rva0022E150Module *m_rva200Module;
	char m_gap204[ 0x23C - 0x204 ];
	Team *m_team;
};

class Rva0022E150Sink
{
public:
	virtual void v00(); virtual void v01(); virtual void v02(); virtual void v03();
	virtual void v04(); virtual void v05(); virtual void v06(); virtual void v07();
	virtual void v08(); virtual void v09(); virtual void v10(); virtual void v11();
	virtual void v12(); virtual void v13(); virtual void v14(); virtual void v15();
	virtual void v16(); virtual void v17(); virtual void v18(); virtual void v19();
	virtual void v20(); virtual void v21(); virtual void v22(); virtual void v23();
	virtual void v24(); virtual void v25();
	virtual int slot68();
	virtual void v27(); virtual void v28(); virtual void v29(); virtual void v30();
	virtual void v31(); virtual void v32();
	virtual bool slot84( Object *obj, int arg );
	virtual void slot88( Object *obj );
};

class Rva0022E150
{
public:
	Object *method( const ThingTemplate *tmplate, Rva0022E150Sink *sink, Object *creator, int unused, int arg );
};

Object *Rva0022E150::method( const ThingTemplate *tmplate, Rva0022E150Sink *sink, Object *creator, int unused, int arg )
{
	BitFlags< 86 > statusBits;
	if( sink->slot68() && !TheWritableGlobalData->m_rvaDCD
		&& !( tmplate->m_kindof[ 2 ] & 0x2000000 ) && !( tmplate->m_kindof[ 0 ] & 0x400 )
		&& TheAI->m_aiData->m_rvaB7 )
		statusBits.m_bits[ 1 ] |= 0x400000;

	Team *team = creator->m_team;
	Object *obj = TheThingFactory->newObject( tmplate, team, statusBits, 0 );
	if( sink->slot84( obj, arg ) )
	{
		Rva0022E150Module *module = creator->m_rva200Module;
		if( module && module->slot88() )
		{
			Rva0022E150Module *objModule = obj->m_rva200Module;
			if( objModule )
				objModule->slot84( 1 );
		}
		sink->slot88( obj );
	}
	return obj;
}
