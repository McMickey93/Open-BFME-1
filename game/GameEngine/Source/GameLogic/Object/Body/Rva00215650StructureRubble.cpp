// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: retail 0x00215650 (283 bytes), reached through ILT 0x00032C54
// from 0x002157C0 and Completion215930.cpp's 0x00215930. It sits among the
// structure-body modules (StructureBody, SymbioticStructuresBody) and is the
// rubble half of Zero Hour's ActiveBody::setCorrectDamageState grown a second
// arm: after copying a linked object's 320-bit mask (Object+0x110) through
// Object::bfmeClearYG and marking the object effectively dead when the
// module's slot 0x54 value is not positive, it either restores the
// template's geometry height and clears status bit 4, or -- when the
// sub-object at +0x10 reports state 3 -- applies
// ThingTemplate::m_structureRubbleHeight (falling back to
// GlobalData::m_defaultStructureRubbleHeight) and sets bit 4; both arms then
// re-register the object with the pathfinder, as Zero Hour does for rubble.
// No named caller or vtable slot identifies the class or the method, so both
// names are address-derived.
//
// Shape notes measured against retail: the state is read into a local before
// the object pointer is reloaded, and the non-rubble arm is the `then' block.

template <int NUMBITS>
class BitFlags
{
public:
	unsigned int m_bits[ ( NUMBITS + 31 ) / 32 ];
};

class Overridable
{
public:
	const Overridable *getFinalOverride() const;
	char m_gap00[ 4 ];
	Overridable *m_nextOverride;
};

class GeometryInfo
{
public:
	float getMaxHeightAbovePosition() const;
};

class ThingTemplate : public Overridable
{
public:
	char m_gap08[ 0x60 - 8 ];
	GeometryInfo m_geometryInfo;
	char m_gap61[ 0x497 - 0x61 ];
	signed char m_structureRubbleHeight;
};

enum ObjectStatusTypes
{
	RVA00215650_OBJECT_STATUS_4 = 4
};

class Object
{
public:
	void bfmeClearYG( const BitFlags< 320 > &flags );
	void setEffectivelyDead( bool dead );
	void setGeometryInfoZ( float z );
	void clearStatus( ObjectStatusTypes status );
	void setStatusBit( int status, bool set );

	const ThingTemplate *getTemplate() const
	{
		const ThingTemplate *t = m_template;
		if( t && t->m_nextOverride )
			t = (const ThingTemplate *)t->m_nextOverride->getFinalOverride();
		return t;
	}

	char m_gap000[ 4 ];
	const ThingTemplate *m_template;
	char m_gap008[ 0x110 - 8 ];
	BitFlags< 320 > m_rva110Flags;
};

class GameLogic
{
public:
	Object *findObjectByID( int id );
};
extern GameLogic *TheGameLogic;

class Pathfinder
{
public:
	void removeObjectFromPathfindMap( Object *obj );
	void addObjectToPathfindMap( Object *obj );
};

class AI
{
public:
	char m_gap00[ 0xC ];
	Pathfinder *m_pathfinder;
	Pathfinder *pathfinder() { return m_pathfinder; }
};
extern AI *TheAI;

class GlobalData
{
public:
	char m_gap000[ 0xBA8 ];
	float m_defaultStructureRubbleHeight;
};
// retail 0x012ED5C8 (census 37f19b491b queue 35): data_rows.csv line 3 owns the
// name ?TheWritableGlobalData@@3PAVGlobalData@@A there, so the reference must use
// it; a bare TheGlobalData mangles to a name nothing defines.
extern GlobalData *TheWritableGlobalData;

class Rva00215650State
{
public:
	virtual void v00(); virtual void v01(); virtual void v02(); virtual void v03();
	virtual void v04(); virtual void v05(); virtual void v06(); virtual void v07();
	virtual int stateType();
};

class Rva00215650Module
{
public:
	virtual void v00(); virtual void v01(); virtual void v02(); virtual void v03();
	virtual void v04(); virtual void v05(); virtual void v06(); virtual void v07();
	virtual void v08(); virtual void v09(); virtual void v10(); virtual void v11();
	virtual void v12(); virtual void v13(); virtual void v14(); virtual void v15();
	virtual void v16(); virtual void v17(); virtual void v18(); virtual void v19();
	virtual void v20();
	virtual float health();

	Object *getObject() const { return m_object; }

	void rva00215650();

	char m_gap04[ 4 ];
	Object *m_object;
	char m_gap0C[ 4 ];
	Rva00215650State m_state;
	char m_gap14[ 0xE4 - 0x14 ];
	int m_rvaE4ObjectID;
};

void Rva00215650Module::rva00215650()
{
	Object *other = TheGameLogic->findObjectByID( m_rvaE4ObjectID );
	if( other == 0 )
		return;
	Object *obj = getObject();
	if( obj == 0 )
		return;

	obj->bfmeClearYG( other->m_rva110Flags );
	obj->setEffectivelyDead( health() <= 0.0f );

	int type = m_state.stateType();
	obj = getObject();
	if( type != 3 )
	{
		obj->setGeometryInfoZ( obj->getTemplate()->m_geometryInfo.getMaxHeightAbovePosition() );
		getObject()->clearStatus( RVA00215650_OBJECT_STATUS_4 );
	}
	else
	{
		float rubbleHeight = obj->getTemplate()->m_structureRubbleHeight;
		if( rubbleHeight <= 0.0f )
			rubbleHeight = TheWritableGlobalData->m_defaultStructureRubbleHeight;
		obj->setGeometryInfoZ( rubbleHeight );
		getObject()->setStatusBit( 4, true );
	}

	TheAI->pathfinder()->removeObjectFromPathfindMap( getObject() );
	TheAI->pathfinder()->addObjectToPathfindMap( getObject() );
}
