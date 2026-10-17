// ?rva002DB5E0@Made001E5940@@UAEXPAURva002DB5E0Info@@PBUCoord3D@@@Z
// partial score=0.596 date=2026-10-17
// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// stlport
//
// Retail 0x002DB5E0 (495 B), slot 4 of vtable 0x010CE9CC, which the nugget
// ctor ??0Made001E5940@@QAE@XZ (0x002DC520) installs; the INI
// `DamageNugget =` callback 0x001E5940 allocates that object (see
// WeaponDamageNuggetParse.cpp). Spawns GlobalData's template named at +0x14
// for the source's team, then hands its DelayedLuaEventUpdate a three-event
// list (source ID, frames left, the nugget's +0x58 value) with the nugget's
// +0x5C value clamped to at least 1. The method and the argument record keep
// address-derived names: nothing names them.
//
// BANK (shape 0.993, 493/495 B): instruction shape matches except retail's
// `mov edi,eax` after the frame subtraction (+0x117). Registers: retail keeps
// the template/new object/frames in EDI and the source in ESI; this body
// swaps them (196 masked byte diffs, all from the swap). Tried: declaration
// orders, source/obj/team/player/ID locals, a static controllingPlayerOf
// helper, a shared GameLogic local, single-variable frame spellings, flag
// order, int/Real frames (worse). The `m_5C > one ? m_5C : one` spelling fixed
// the compare direction that STLport max() got wrong.

#define _STLP_NO_EXCEPTIONS 1
#include <bitset>
#include <algorithm>

typedef unsigned int UnsignedInt;
typedef int ObjectID;
typedef float Real;
typedef unsigned char Bool;
enum NameKeyType { NAMEKEY_INVALID = 0 };

#include "ascii_string.h"
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

class GlobalData
{
public:
	char pad00[0x14];
	AsciiString m_name14;
};

class ThingTemplate;
class Module;
class Team;

class Player
{
public:
	Team *getDefaultTeam() { return m_defaultTeam; }

private:
	char pad00[0x230];
	Team *m_defaultTeam;
};

class Object
{
public:
	ObjectID getID() const { return m_id; }
	Player *getControllingPlayer() const;
	void setProducer(const Object *obj);
	void setPosition(const Coord3D *pos);
	Module *findUpdateModule(NameKeyType key) const { return findModule(key); }

protected:
	Module *findModule(NameKeyType key) const;

private:
	char pad00[0x74];
	ObjectID m_id;
};

class GameLogic
{
public:
	Object *findObjectByID(ObjectID id);
	void destroyObject(Object *obj);
	UnsignedInt getFrame() const { return m_frame; }

private:
	char pad00[0x3C];
	UnsignedInt m_frame;
};

class ThingFactory
{
public:
	const ThingTemplate *findTemplate(const AsciiString &name);
	Object *newObject(const ThingTemplate *tmplate, Team *team,
		const ObjectStatusMaskType &statusBits = ObjectStatusMaskType(),
		UnsignedInt flags = 0);
};

class NameKeyGenerator
{
public:
	NameKeyType nameToKey(const char *name);
};

class BfmeDelayedLuaEvent
{
public:
	UnsignedInt at00;
	Real at04;
	Bool m_08;
	ObjectID m_objectID;
	AsciiString m_name;
	int m_type;
};

class BfmeDelayedLuaEventList
{
public:
	BfmeDelayedLuaEventList();
	virtual ~BfmeDelayedLuaEventList();

	BfmeDelayedLuaEvent m_events[3];
};

class Gen_0028BFF0
{
public:
	void bfmeSetup(int type, void *events, UnsignedInt a, int value, Bool b, Bool c);
};

struct Rva002DB5E0WeaponTemplate
{
	char pad00[0x4D8];
	UnsignedInt m_flags4D8;
};

struct Rva002DB5E0Info
{
	UnsignedInt at00;
	Rva002DB5E0WeaponTemplate *m_template;
	ObjectID m_sourceID;
	char pad0c[0x1C - 0x0C];
	UnsignedInt m_frame;
};

extern GlobalData *TheGlobalData;
extern GameLogic *TheGameLogic;
extern ThingFactory *TheThingFactory;
extern NameKeyGenerator *TheNameKeyGenerator;

#define NAMEKEY(x) TheNameKeyGenerator->nameToKey(x)

class Made001E5940
{
public:
	virtual void rva002DB5E0(Rva002DB5E0Info *info, const Coord3D *pos);

private:
	char pad04[0x54];
	Real m_58;
	Real m_5C;
};

void Made001E5940::rva002DB5E0(Rva002DB5E0Info *info, const Coord3D *pos)
{
	const AsciiString &name = TheGlobalData->m_name14;
	const ThingTemplate *tmpl = TheThingFactory->findTemplate(name);
	if (tmpl == 0)
		return;

	ObjectID sourceID = info->m_sourceID;
	Object *source = TheGameLogic->findObjectByID(sourceID);
	if (source == 0)
		return;

	Object *obj = TheThingFactory->newObject(tmpl, source->getControllingPlayer()->getDefaultTeam());
	obj->setProducer(source);
	obj->setPosition(pos);

	static NameKeyType key_DelayedLuaEventUpdate = NAMEKEY("DelayedLuaEventUpdate");
	Module *module = obj->findUpdateModule(key_DelayedLuaEventUpdate);
	if (module == 0)
	{
		TheGameLogic->destroyObject(obj);
		return;
	}

	UnsignedInt frames = info->m_frame - TheGameLogic->getFrame();
	UnsignedInt flags = info->m_template->m_flags4D8;
	Bool b1 = (Bool)((flags >> 1) & 1);
	Bool b2 = (Bool)((flags >> 2) & 1);

	BfmeDelayedLuaEventList events;
	events.m_events[0].m_objectID = source->getID();
	events.m_events[0].m_type = 3;
	events.m_events[1].at04 = (Real)frames;
	events.m_events[1].m_type = 1;
	events.m_events[2].at04 = m_58;
	events.m_events[2].m_type = 1;

	const Real one = 1.0f;
	const Real &value = (m_5C > one) ? m_5C : one;
	((Gen_0028BFF0 *)module)->bfmeSetup(9, &events, 0, *(const int *)&value, b1, b2);
}
