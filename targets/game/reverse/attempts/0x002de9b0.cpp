// ?rva002DE9B0@Made001E6170@@UBEXPBVDamageInfo@@PBUCoord3D@@@Z
// partial score=0.6862 date=2026-10-17
// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWDebug /Igame/Libraries/Source/WWVegas
// stlport
//
// Retail 0x002DE9B0 (325 B), slot 6 of vtable 0x010CF1C4, which the 0x6C-byte
// nugget ctor ??0Made001E6170@@QAE@XZ (0x002DE930) installs; the INI
// `SpawnAndFadeNugget =` callback 0x001E6170 allocates that object (see
// WeaponNuggetParse.cpp). Spawns the template named at +0x5C for the damage
// source's team at the source's position plus the +0x60/+0x64 offset rotated
// by the source's orientation, drops it onto its layer, kills the source and
// registers the spawn with the pathfinder when its template has bit 0x400 of
// the word at +0xDC set. The method name stays address-derived, as its
// sibling WeaponDamageFieldNuggetRva002DAEC0.cpp's does.
//
// BANK (shape 0.973, 321/325 B, 94 masked byte diffs): everything through the
// inlined WWMath Vector3::Rotate_Z (retail +0xB2) matches. Retail then adds
// pos-first (`fld pos.x; fadd X` / `fld pos.y; fadd st1`) and keeps offset.Y
// live until the getLayer call (`fstp st0` at +0xCE); this body adds
// offset-first and consumes Y. Tried: +=/explicit/reversed adds, pointer and
// reference adds, inner scopes, operator[], Set(), copy-init, local Vector3
// view, Coord3D temporaries, z adds (all 94 B or worse).

#define _STLP_NO_EXCEPTIONS 1
#include <bitset>
#include <math.h>

typedef unsigned int UnsignedInt;
typedef int ObjectID;
typedef float Real;
typedef bool Bool;
enum DamageType { };
enum DeathType { };

#include "ascii_string.h"
#define _OPERATOR_NEW_DEFINED_
#include "vector3.h"
#include "../../../../Libraries/Include/Lib/Coord3D.h"

template<int NUMBITS>
class BitFlags
{
public:
	BitFlags() { }

private:
	_STL::bitset<NUMBITS> m_bits;
};

typedef BitFlags<86> ObjectStatusMaskType;

class DamageInfo
{
public:
	char m_pad00[8];
	ObjectID m_sourceID;
};

class Overridable
{
public:
	const Overridable *getFinalOverride() const;

	void *m_vtbl;
	Overridable *m_nextOverride;
};

class ThingTemplate
{
public:
	UnsignedInt testFlagsDC(UnsignedInt mask) const { return m_flagsDC & mask; }

private:
	char m_pad00[0xDC];
	UnsignedInt m_flagsDC;
};

class Team;

class Object
{
public:
	const ThingTemplate *getTemplate() const
	{
		const Overridable *tmpl = m_template;
		if (tmpl && tmpl->m_nextOverride)
			tmpl = tmpl->m_nextOverride->getFinalOverride();
		return (const ThingTemplate *)tmpl;
	}
	const Coord3D *getPosition() const { return &m_pos; }
	Real getOrientation() const { return m_angle; }
	Team *getTeam() const { return m_team; }
	int getLayer() const;
	void setPosition(const Coord3D *pos);
	void setOrientation(Real angle);
	void kill(DamageType damageType, DeathType deathType);

private:
	void *m_vtbl;
	Overridable *m_template;
	char m_pad08[0x38 - 8];
	Coord3D m_pos;
	Real m_angle;
	char m_pad48[0x23C - 0x48];
	Team *m_team;
};

class GameLogic
{
public:
	Object *findObjectByID(ObjectID id);
};

class ThingFactory
{
public:
	const ThingTemplate *findTemplate(const AsciiString &name);
	Object *newObject(const ThingTemplate *tmplate, Team *team,
		const ObjectStatusMaskType &statusBits = ObjectStatusMaskType(),
		UnsignedInt flags = 0);
};

class TerrainLogic
{
public:
	virtual void slot0();
	virtual void slot1();
	virtual void slot2();
	virtual void slot3();
	virtual void slot4();
	virtual void slot5();
	virtual void slot6();
	virtual Real getLayerHeight(Real x, Real y, int layer, Coord3D *normal = 0, Bool clip = 1) const;
};

class Pathfinder
{
public:
	void addObjectToPathfindMap(Object *obj);
};

class AI
{
public:
	Pathfinder *pathfinder() { return m_pathfinder; }

private:
	char m_pad00[0xC];
	Pathfinder *m_pathfinder;
};

extern GameLogic *TheGameLogic;
extern ThingFactory *TheThingFactory;
extern TerrainLogic *TheTerrainLogic;
extern AI *TheAI;

class Made001E6170
{
public:
	virtual void rva002DE9B0(const DamageInfo *damageInfo, const Coord3D *pos) const;

private:
	char m_pad04[0x58];
	AsciiString m_spawnName;
	Coord3D m_offset;
};

void Made001E6170::rva002DE9B0(const DamageInfo *damageInfo, const Coord3D *) const
{
	Object *source = TheGameLogic->findObjectByID(damageInfo->m_sourceID);
	const ThingTemplate *tmpl = TheThingFactory->findTemplate(m_spawnName);
	if (tmpl == 0)
		return;

	Object *spawn = TheThingFactory->newObject(tmpl, source->getTeam());

	Vector3 offset(m_offset.x, m_offset.y, m_offset.z);
	Coord3D pos;
	pos.x = source->getPosition()->x;
	pos.y = source->getPosition()->y;
	pos.z = source->getPosition()->z;
	Real angle = source->getOrientation();
	offset.Rotate_Z(angle);
	pos.x += offset.X;
	pos.y += offset.Y;
	pos.z = TheTerrainLogic->getLayerHeight(pos.x, pos.y, source->getLayer());

	spawn->setPosition(&pos);
	spawn->setOrientation(angle);
	source->kill((DamageType)8, (DeathType)22);

	if (spawn->getTemplate()->testFlagsDC(0x400))
		TheAI->pathfinder()->addObjectToPathfindMap(spawn);
}
