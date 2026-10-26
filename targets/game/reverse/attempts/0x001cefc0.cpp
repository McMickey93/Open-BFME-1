// ??1InactiveBody@@UAE@XZ
// partial score=0.0 date=2026-10-26
// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport
#define _STLP_NO_EXCEPTIONS 1
#include <hash_map>
#include <bitset>
#include "../../Common/Thing/GameLogicObjectLookup.h"

// Object::onDie, retail 0x001CEFC0 (1493 bytes).  Identity: retail ILT
// 0x0003369F jumps here and ilt_oracle CONFIRMS ?onDie@Object@@QAEXPAVDamageInfo@@@Z
// there; the body ends `ret 4`.  The old ??1InactiveBody row on this address
// was a misnaming (the InactiveBody destructor ILT 0x0003C867 goes to
// 0x00213B70).  Evidence: identity_evidence/001cefc0-object-ondie.md.
//
// The Zero Hour body (upstream GameLogic/Object/Object.cpp) is the guide: die
// modules first, radar removal, terrain decal fade, spawner notification,
// partition maintenance, team notification, local-player EVA and the idle
// worker list.  BFME adds the victory system hook, influence and container
// cleanup, three model-condition flag edits, pathfind-map removal, a Lua
// "died" event, emotion-system removal and a killer-kind status bit.  Layout
// is read at retail offsets through local views.

typedef bool Bool;
typedef float Real;

class Object;
class Team;
class Player;
class AsciiString;
class DelayedLuaEventList;
struct Coord3D;

// Inline general-purpose bit set: tests and edits compile to one dword op.
template <int N> class BitFlags
{
public:
	enum BogusInitType { kInit = 0 };
	BitFlags() {}
	BitFlags(BogusInitType, int idx1) { m_bits.set(idx1); }
	_STL::bitset<N> m_bits;
};

class ModelConditionFlags
{
public:
	unsigned m_bits[3];
	__forceinline unsigned test(int i) const { return m_bits[i >> 5] & (1u << (i & 31)); }
	__forceinline void set(int i) { m_bits[i >> 5] |= (1u << (i & 31)); }
	__forceinline void clear(int i) { m_bits[i >> 5] &= ~(1u << (i & 31)); }
};

class Overridable
{
public:
	virtual ~Overridable();
	const Overridable *getFinalOverride() const
	{
		if (m_nextOverride)
			return m_nextOverride->getFinalOverride();
		return this;
	}
	Overridable *m_nextOverride;
};

class ThingTemplate : public Overridable
{
public:
	__forceinline unsigned isKindOf(int k) const
	{
		return ((const unsigned *)((const char *)this + 0xC8))[k >> 5] & (1u << (k & 31));
	}
	__forceinline int evaMessage(int offset) const
	{
		return *(const int *)((const char *)this + offset);
	}
};

template <class T> class OVERRIDE
{
public:
	const T *m_value;
	operator const T *() const
	{
		if (!m_value)
			return 0;
		return (const T *)m_value->getFinalOverride();
	}
};

// Damage.h, BFME layout (ActiveBody_Constructor.cpp proves these inline
// constructors byte-exact): input at +4, output at +0x4C.
struct DamageTriple
{
	float x, y, z;
	void zero() { x = 0.0f; y = 0.0f; z = 0.0f; }
};
class DamageInfoInput
{
public:
	virtual void xfer();
	unsigned m_sourceID;
	unsigned short m_sourcePlayerMask;
	int m_damageType, m_damageFXOverride, m_deathType;
	float m_amount;
	bool m_kill, field1D;
	float field20;
	unsigned field24, field28;
	DamageTriple m_shockWaveVector;
	float field38, field3C, field40, field44;
	__forceinline DamageInfoInput()
	{
		m_sourceID = 0; m_sourcePlayerMask = 0; m_damageType = 22; m_damageFXOverride = 15;
		m_deathType = 0; m_amount = 0; m_kill = false; field1D = true; field20 = 0;
		field24 = 0; field28 = 0; m_shockWaveVector.zero(); field38 = 0; field3C = 0;
		field40 = 0; field44 = 1.0f;
	}
};
class DamageInfoOutput
{
public:
	virtual void xfer();
	float m_actualDamageDealt, m_actualDamageClipped;
	bool m_noEffect;
	__forceinline DamageInfoOutput() : m_actualDamageDealt(0), m_actualDamageClipped(0), m_noEffect(false) {}
};
class DamageInfo
{
public:
	__declspec(dllimport) __forceinline DamageInfo() {}
	virtual void xfer();
	DamageInfoInput in;
	DamageInfoOutput out;
};

enum DamageType { DAMAGE_UNRESISTABLE = 8 };
enum DeathType { DEATH_NORMAL = 0 };

class DieModuleInterface
{
public:
	virtual void onDie(DamageInfo *damageInfo);
};

class SpawnBehaviorInterface
{
public:
	virtual void s00();
	virtual void onSpawnDeath(int deadSpawn, DamageInfo *damageInfo);
};

class BehaviorModuleInterface
{
public:
	virtual void b00();
	virtual void b01();
	virtual void b02();
	virtual void b03();
	virtual void b04();
	virtual void b05();
	virtual DieModuleInterface *getDie();
	virtual void b07();
	virtual void b08();
	virtual void b09();
	virtual void b0A();
	virtual void b0B();
	virtual void b0C();
	virtual void b0D();
	virtual void b0E();
	virtual void b0F();
	virtual void b10();
	virtual void b11();
	virtual void b12();
	virtual void b13();
	virtual void b14();
	virtual void b15();
	virtual void b16();
	virtual void b17();
	virtual void b18();
	virtual void b19();
	virtual void b1A();
	virtual void b1B();
	virtual void b1C();
	virtual SpawnBehaviorInterface *getSpawnBehaviorInterface();
};

class ObjectModule
{
public:
	virtual void om00();
	void *m_moduleData;
	Object *m_object;
};

class BehaviorModule : public ObjectModule, public BehaviorModuleInterface
{
};

class ContainRider
{
public:
	virtual void r00();
	virtual void r01();
	virtual void r02();
	virtual void r03();
	virtual void r04();
	virtual void r05();
	virtual void r06();
	virtual void r07();
	virtual void r08();
	virtual void r09();
	virtual void r0A();
	virtual void r0B();
	virtual void r0C();
	virtual void onContainerDeath(Object *obj);
};

class ContainModuleInterface
{
public:
	virtual void c00();
	virtual void c01();
	virtual void c02();
	virtual void c03();
	virtual void c04();
	virtual void c05();
	virtual void c06();
	virtual void c07();
	virtual void c08();
	virtual void c09();
	virtual void c0A();
	virtual void c0B();
	virtual void c0C();
	virtual void c0D();
	virtual void c0E();
	virtual void c0F();
	virtual void c10();
	virtual void c11();
	virtual void c12();
	virtual void c13();
	virtual void c14();
	virtual void c15();
	virtual void c16();
	virtual void c17();
	virtual void c18();
	virtual void c19();
	virtual ContainRider *getRider();
	virtual void c1B();
	virtual void c1C();
	virtual void c1D();
	virtual void c1E();
	virtual void c1F();
	virtual void c20();
	virtual void c21();
	virtual void c22();
	virtual void c23();
	virtual void removeFromContain(Object *obj, Bool exposeStealthUnits);
};

class BodyModuleInterface
{
public:
	virtual void h00();
	virtual void h01();
	virtual void h02();
	virtual void h03();
	virtual void h04();
	virtual void h05();
	virtual Real getMaxHealth();
};

class AIUpdateInterface
{
public:
	virtual void friend_notifyStateMachineChanged();
};

class Drawable
{
public:
	void replaceModelConditionState(const ModelConditionFlags &flags, unsigned a, unsigned b);
	void setTerrainDecalFadeTarget(Real target, Real rate);
};

class PartitionData
{
public:
	void makeDirty();
};

class Pathfinder
{
public:
	void removeObjectFromPathfindMap(Object *obj);
};

class AI
{
public:
	char m_pad00[0xC];
	Pathfinder *m_pathfinder;
};
extern AI *TheAI;

class Radar
{
public:
	void removeObject(Object *obj);
	enum RadarEventType { RADAR_EVENT_FAKE = 10 };
	bool tryEvent(RadarEventType event, const Coord3D *pos);
};
extern Radar *TheRadar;

class VictorySystem
{
public:
	void rva001DFC10(Object *obj, DamageInfo *damageInfo);
};
extern VictorySystem *TheVictorySystem;

class Team
{
public:
	Player *getControllingPlayer() const;
};

class TeamFactory
{
public:
	Team *findTeam(const AsciiString &name);
};
extern TeamFactory *TheTeamFactory;

enum Relationship { ENEMIES, NEUTRAL, ALLIES };

class Player
{
public:
	void bfmeObjectLeavingInfluence(Object *obj);
	Relationship getRelationship(const Team *that) const;
	char m_pad00[0x24];
	int m_playerIndex;
};

class PlayerList
{
public:
	char m_pad00[0xC];
	Player *m_local;
};
extern PlayerList *ThePlayerList;

enum EvaMessage { EVA_INVALID = -1 };
class Eva
{
public:
	bool setShouldPlay(EvaMessage message, const Coord3D *pos);
};
extern Eva *TheEva;

class InGameUI
{
public:
	virtual void u00();
	virtual void u01();
	virtual void u02();
	virtual void u03();
	virtual void u04();
	virtual void u05();
	virtual void u06();
	virtual void u07();
	virtual void u08();
	virtual void u09();
	virtual void u0A();
	virtual void u0B();
	virtual void u0C();
	virtual void u0D();
	virtual void u0E();
	virtual void u0F();
	virtual void u10();
	virtual void u11();
	virtual void u12();
	virtual void u13();
	virtual void u14();
	virtual void u15();
	virtual void u16();
	virtual void u17();
	virtual void u18();
	virtual void u19();
	virtual void u1A();
	virtual void u1B();
	virtual void u1C();
	virtual void u1D();
	virtual void u1E();
	virtual void u1F();
	virtual void u20();
	virtual void u21();
	virtual void u22();
	virtual void u23();
	virtual void u24();
	virtual void u25();
	virtual void u26();
	virtual void u27();
	virtual void u28();
	virtual void u29();
	virtual void u2A();
	virtual void u2B();
	virtual void u2C();
	virtual void u2D();
	virtual void u2E();
	virtual void u2F();
	virtual void u30();
	virtual void u31();
	virtual void u32();
	virtual void u33();
	virtual void u34();
	virtual void u35();
	virtual void u36();
	virtual void u37();
	virtual void u38();
	virtual void u39();
	virtual void u3A();
	virtual void u3B();
	virtual void u3C();
	virtual void u3D();
	virtual void u3E();
	virtual void u3F();
	virtual void u40();
	virtual void u41();
	virtual void u42();
	virtual void u43();
	virtual void u44();
	virtual void u45();
	virtual void u46();
	virtual void u47();
	virtual void u48();
	virtual void u49();
	virtual void u4A();
	virtual void u4B();
	virtual void u4C();
	virtual void u4D();
	virtual void u4E();
	virtual void u4F();
	virtual void u50();
	virtual void u51();
	virtual void u52();
	virtual void u53();
	virtual void u54();
	virtual void u55();
	virtual void u56();
	virtual void u57();
	virtual void u58();
	virtual void u59();
	virtual void u5A();
	virtual void u5B();
	virtual void u5C();
	virtual void u5D();
	virtual void u5E();
	virtual void u5F();
	virtual void removeIdleWorker(Object *obj, int playerNdx);
};
extern InGameUI *TheInGameUI;

class EmotionSystem;
extern EmotionSystem *TheEmotionSystem;
class BfmeObjectIdOwner
{
public:
	bool removeObject(Object *obj);
};

class LuaScriptEngine;
extern LuaScriptEngine *TheLuaScriptEngine;
class BfmeOwnerBR
{
public:
	void bfmeGo939B(int, Object *, DelayedLuaEventList *);
};

class BfmeDelayedLuaEvent
{
public:
	BfmeDelayedLuaEvent();
	~BfmeDelayedLuaEvent();
	char m_body[0x18];
};

// The base contributes only an unwind state (retail state 0 before the array
// is built and state 2 while it is torn down); the list's own vtable is the
// one store the inlined constructor makes.
class BfmeDelayedLuaEventListBase
{
public:
	virtual ~BfmeDelayedLuaEventListBase() {}
};

class DelayedLuaEventList : public BfmeDelayedLuaEventListBase
{
public:
	__forceinline DelayedLuaEventList() {}
	BfmeDelayedLuaEvent m_events[3];
};

// Zero Hour GameLogic.h preserves this older BFME hash-map body in a comment;
// as in SpawnBehaviorOnDie.cpp VC7.1 inlines one lookup and keeps the other
// out of line, as retail does.
inline Object *GameLogic::findObjectByID(ObjectID id)
{
	if (id == 0)
		return 0;
	ObjectPtrHash::iterator it = m_objHash.find(id);
	if (it == m_objHash.end())
		return 0;
	return (*it).second;
}
extern GameLogic *TheGameLogic;

// 0x00030AA3 (team death notification, Team in ECX and the dying Object on the
// stack) and 0x000376CD (drawable broadcast) carry only dump names.
extern void j_00030aa3();
extern void d_000376cd();
class Rva000EE7F0Team {};
class Rva004141C0 {};

class Object
{
public:
	void onDie(DamageInfo *damageInfo);
	void setStatus(const BitFlags<86> &bits, Bool set);

	virtual void o00();
	virtual void o01();
	virtual void o02();
	virtual void o03();
	virtual void o04();
	virtual void o05();
	virtual void o06();
	virtual void o07();
	virtual void o08();
	virtual void o09();
	virtual Drawable *getDrawable();
	virtual void o2C();
	virtual void o30();
	virtual void attemptDamage(DamageInfo *damageInfo);

	const ThingTemplate *getTemplate() const { return m_template; }
	ContainModuleInterface *getContain() const { return m_contain; }
	int getID() const { return m_id; }
	unsigned testFlag(int i) const { return m_flags.test(i); }
	__forceinline void notifyFlagsChanged()
	{
		if (m_drawable)
			m_drawable->replaceModelConditionState(m_flags, 0, 0);
		if (m_ai)
			m_ai->AIUpdateInterface::friend_notifyStateMachineChanged();
	}
	__forceinline void setFlag(int i) { m_flags.set(i); notifyFlagsChanged(); }
	__forceinline void clearFlag(int i) { m_flags.clear(i); notifyFlagsChanged(); }

	OVERRIDE<ThingTemplate> m_template;		// +0x04
	char m_pad08[0x38 - 0x08];
	Coord3D *m_positionAnchor;			// +0x38 (address only)
	char m_pad3C[0x74 - 0x3C];
	int m_id;					// +0x74
	int m_producerID;				// +0x78
	char m_pad7C[0x80 - 0x7C];
	Drawable *m_drawable;				// +0x80
	char m_pad84[0x94 - 0x84];
	unsigned m_status94;				// +0x94
	unsigned m_status98;				// +0x98
	char m_pad9C[0x110 - 0x9C];
	ModelConditionFlags m_flags;			// +0x110
	char m_pad11C[0x1F0 - 0x11C];
	BehaviorModule **m_behaviors;			// +0x1F0
	char m_pad1F4[0x1FC - 0x1F4];
	ContainModuleInterface *m_contain;		// +0x1FC
	BodyModuleInterface *m_body;			// +0x200
	AIUpdateInterface *m_ai;			// +0x204
	char m_pad208[0x20C - 0x208];
	void *m_radarData;				// +0x20C
	char m_pad210[0x214 - 0x210];
	Object *m_containedBy;				// +0x214
	char m_pad218[0x23C - 0x218];
	Team *m_team;					// +0x23C
	char m_teamName[4];				// +0x240 AsciiString
	char m_pad244[0x39C - 0x244];
	Bool m_influencing;				// +0x39C
	char m_pad39D[0x3B0 - 0x39D];
	PartitionData *m_partitionData;			// +0x3B0

	SpawnBehaviorInterface *getSpawnBehaviorInterface() const
	{
		for (BehaviorModule **u = m_behaviors; *u; ++u)
		{
			SpawnBehaviorInterface *s = (*u)->getSpawnBehaviorInterface();
			if (s)
				return s;
		}
		return 0;
	}
	Player *getControllingPlayer() const
	{
		return m_team ? m_team->getControllingPlayer() : 0;
	}
};

static __forceinline void notifyTeamOfObjectDeath(Team *team, Object *obj)
{
	typedef void (Rva000EE7F0Team::*Fn)(Object *);
	union { void (*fn)(); Fn call; } u = { j_00030aa3 };
	(((Rva000EE7F0Team *)team)->*u.call)(obj);
}

static __forceinline void drawableBroadcast(Drawable *draw)
{
	typedef void (Rva004141C0::*Fn)();
	union { void (*fn)(); Fn call; } u = { d_000376cd };
	(((Rva004141C0 *)draw)->*u.call)();
}

void Object::onDie(DamageInfo *damageInfo)
{
	Bool selfInflicted = ((unsigned)m_id == damageInfo->in.m_sourceID);

	// FIRST, call our die modules.
	for (BehaviorModule **d = m_behaviors; *d; ++d)
	{
		DieModuleInterface *die = (*d)->getDie();
		if (die)
			die->onDie(damageInfo);
	}

	if (TheVictorySystem)
		TheVictorySystem->rva001DFC10(this, damageInfo);

	if (m_influencing)
	{
		Player *player = getControllingPlayer();
		if (m_status94 & 0x20000000)
		{
			Team *team = TheTeamFactory->findTeam(*(const AsciiString *)m_teamName);
			if (team)
				player = team->getControllingPlayer();
		}
		if (player)
		{
			player->bfmeObjectLeavingInfluence(this);
			m_influencing = false;
		}
	}

	// When objects die we remove from the radar as they're really not interesting anymore
	if (m_radarData)
		TheRadar->removeObject(this);

	Object *container = m_containedBy;
	if (container)
	{
		container->m_contain->removeFromContain(this, false);
		if (testFlag(87))
			clearFlag(87);
		if (getTemplate()->isKindOf(54))
		{
			DamageInfo damage;
			damage.in.m_damageType = DAMAGE_UNRESISTABLE;
			damage.in.m_deathType = DEATH_NORMAL;
			damage.in.m_sourceID = 0;
			damage.in.m_amount = container->m_body->getMaxHealth();
			damage.in.m_kill = true;
			container->attemptDamage(&damage);
		}
	}

	if (!testFlag(61))
		setFlag(61);
	if (testFlag(60))
		clearFlag(60);

	if (!(m_status98 & 0x40000))
		TheAI->m_pathfinder->removeObjectFromPathfindMap(this);

	// Just in case I have been sporting one of thise fancy Terrain Decals,
	//I naturally lose it now, because I'm dead.
	Drawable *draw = getDrawable();
	if (draw)
		draw->setTerrainDecalFadeTarget(0.0f, -0.03f);

	// objects that were spawned from something, need to tell their spawner that they have died
	Object *spawner = TheGameLogic->findObjectByID(m_producerID);
	if (spawner)
	{
		SpawnBehaviorInterface *spawnerBehavior = spawner->getSpawnBehaviorInterface();
		if (spawnerBehavior)
			spawnerBehavior->onSpawnDeath(getID(), damageInfo);
		else if (spawner->getContain() && spawner->getContain()->getRider())
			spawner->getContain()->getRider()->onContainerDeath(this);
	}

	if (m_partitionData)
		m_partitionData->makeDirty();

	DelayedLuaEventList events;
	((BfmeOwnerBR *)TheLuaScriptEngine)->bfmeGo939B(1, this, &events);

	if (getTemplate()->isKindOf(143) || getTemplate()->isKindOf(89))
		((BfmeObjectIdOwner *)TheEmotionSystem)->removeObject(this);

	if (m_team)
		notifyTeamOfObjectDeath(m_team, this);

	if (!selfInflicted)
	{
		const ThingTemplate *tmpl = getTemplate();
		if (tmpl)
		{
			Player *owner = getControllingPlayer();
			Player *local = ThePlayerList->m_local;
			int message;
			if (owner == local)
				message = tmpl->evaMessage(0x44C);
			else if (local && local->getRelationship(m_team) == ALLIES)
				message = tmpl->evaMessage(0x450);
			else
				message = tmpl->evaMessage(0x454);
			if (message != EVA_INVALID)
			{
				if (TheEva->setShouldPlay((EvaMessage)message, 0))
					TheRadar->tryEvent(Radar::RADAR_EVENT_FAKE, (const Coord3D *)&m_positionAnchor);
			}
		}
	}

	TheInGameUI->removeIdleWorker(this, getControllingPlayer()->m_playerIndex);

	if (getTemplate()->isKindOf(8))
	{
		int killerID = damageInfo->in.m_sourceID;
		Object *killer = TheGameLogic->findObjectByID(killerID);
		if (killer && killer->getTemplate()->isKindOf(164))
		{
			setStatus(BitFlags<86>(BitFlags<86>::kInit, 70), true);
		}
	}

	if (draw)
		drawableBroadcast(draw);
}
