// ?buildCastleStructure@CastleBehavior@@QAEPAVObject@@PAVBuildListInfo@@_N@Z
// partial score=0.4168 date=2026-10-24
// ?buildCastleStructure@CastleBehavior@@QAEPAVObject@@PAVBuildListInfo@@_N@Z
// cl: /EHsc /D_STLP_USE_STATIC_LIB /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WWMath
// stlport
//
// CastleBehavior::buildCastleStructure, retail 0x00371650, 950 bytes.
// Identity: the pinned signature
// ?rva00371650@CastleBehavior@@QAEPAVObject@@PAVBuildListInfo@@_N@Z follows the
// caller chain CastleBehavior::initiateUnpack -> 0x00376590 ->
// Rva00374F20Receiver::instantiateBuildListObjects (landed,
// game/GameEngine/Source/Common/Rva00374F20InstantiateBuildListObjects.cpp),
// which passes a local BuildListInfo and a bool through the CastleBehavior
// receiver and hands the returned Object* to registerOwnedObject. The BFME2
// twin is the byte-matched CastleBehavior::buildCastleStructure
// (Code/GameEngine/Source/GameLogic/Object/Behavior/CastleBehaviorBuildCastleStructure.cpp,
// native 0x00396311, named by WorldBuilder 0xEBC8C0), same mangled signature;
// wb1 names the source file GameEngine/Source/GameLogic/System/CastleSystem.cpp.
//
// BFME1 layout differences against that twin: the KindOf flag words start at
// template+0xC8 (bits 99 and 59 where BFME2 tests 100 and 60), the behavior
// flag lands at this+0xAC (BFME2: +0x44), the module data filter sits at
// +0x3C (BFME2: +0x30) with the fade time at +0x28, the local-player slot is
// ThePlayerList+0x14 (BFME2: +0x18), the frame counter is TheGameLogic+0x3C,
// and the debug gate is TheWritableGlobalData+0xA88. BFME1's retail also
// predates the BFME2 damage-transfer block and the placement query: the body
// creates straight after the filter fallback and has no KINDOF_17 arm. The
// 30.0 frames-per-second datum at 0x0108615C is the one defined as
// BfmeReportWeightScaleHolder::value in
// game/GameEngine/Source/Common/V4GuardedLookupFieldReads.cpp.

#include "ascii_string.h"
#include <math.h>

#define _STLP_NO_EXCEPTIONS 1
#include <bitset>

typedef bool Bool;
typedef int Int;
typedef unsigned int UnsignedInt;
typedef unsigned short UnsignedInt16;
typedef float Real;

#define NULL 0

struct Coord3D
{
	Real x;
	Real y;
	Real z;
};

// Upstream WWMath shapes (game/Libraries/Source/WWVegas/WWMath), declared
// locally because that header pulls in WWLib always.h, which conflicts with
// the STLport placement-new declarations this TU needs for BitFlags.
class Vector3
{
public:
	Vector3(void) {}
	__forceinline Vector3(Real x, Real y, Real z) { X = x; Y = y; Z = z; }
	__forceinline void Set(Real x, Real y, Real z) { X = x; Y = y; Z = z; }

	Real X;
	Real Y;
	Real Z;
};

class Vector4
{
public:
	Real X;
	Real Y;
	Real Z;
	Real W;
};

class Matrix3D
{
public:
	__forceinline const Vector4 &operator [](int i) const { return Row[i]; }

	__forceinline void mulVector3(const Vector3 &in, Vector3 &out) const
	{
		float x = (Row[0].X * in.X + Row[0].Y * in.Y + Row[0].Z * in.Z + Row[0].W);
		float y = (Row[1].X * in.X + Row[1].Y * in.Y + Row[1].Z * in.Z + Row[1].W);
		float z = (Row[2].X * in.X + Row[2].Y * in.Y + Row[2].Z * in.Z + Row[2].W);
		out.Set(x, y, z);
	}

private:
	Vector4 Row[3];
};

// WWLib's StringBase buffer header: an AsciiString holds one pointer to it.
struct AsciiStringBuffer
{
	Int refCount;
	UnsignedInt16 length;
	UnsignedInt16 capacity;
};

static inline bool isStringEmpty(const AsciiString &s)
{
	const AsciiStringBuffer *buffer = *(const AsciiStringBuffer *const *)&s;
	return buffer == 0 || buffer->length == 0;
}

template <class T>
inline T &field(void *p, int n) { return *(T *)((char *)p + n); }

// The 30.0 datum at 0x0108615C (dir32: __real@41f00000).
class BfmeReportWeightScaleHolder
{
public:
	static const float value;
};

class Player;

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/PlayerList.h
class PlayerList
{
public:
	char m_pad00[0x14];
	Player *m_localPlayer;
};

extern PlayerList *ThePlayerList;

class GameLogic
{
public:
	char m_pad00[0x3c];
	Int m_frame;
};

extern GameLogic *TheGameLogic;

class GlobalData
{
public:
	char m_pad00[0xa88];
	Int m_debugAI;
};

extern GlobalData *TheWritableGlobalData;

// The 0x0039F0A0 filter body reached through ILT 0x0001B437.
class Rva0039F0A0
{
public:
	Bool accepts(const void *thing, Player *a, Player *b);
};

// Body 0x001BE220 reached through ILT 0x0002852E: signed condition word and
// unsigned duration on the created object.
class BfmeItemRY
{
public:
	void bfmeDoRY(void *condition, void *duration);
};

// Body 0x000D3EB0 reached through ILT 0x00032DEE.
class BfmeRva9140Member
{
public:
	void setMode(Int mode, Int value);
};

// Drawable body 0x00410D80 reached through ILT 0x00046A1F.
class Drawable
{
public:
	void bfmeDelayB(Int frames);
};

// Body 0x0041AA90 reached through ILT 0x0002D439.
class DrawableApplyPendingThunk
{
public:
	void apply(Bool immediate);
};

enum KindOfType
{
	KINDOF_59 = 59,
	KINDOF_99 = 99
};

// Native BitFlags over the STLport bitset, as the upstream
// GameEngine/Include/Common/BitFlags.h spells it.
template <int NUMBITS>
class BitFlags
{
public:
	inline Bool test(Int i) const { return m_bits.test(i); }

private:
	_STL::bitset<NUMBITS> m_bits;
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/ThingTemplate.h
class Overridable
{
public:
	void *m_vtable;
	Overridable *m_nextOverride;
};

class ThingTemplate : public Overridable
{
public:
	__forceinline Bool isKindOf(KindOfType t) const { return m_kindOf.test(t); }

private:
	char m_pad08[0xc8 - 0x08];
	BitFlags<218> m_kindOf;
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/ThingFactory.h
class ThingFactory
{
public:
	const ThingTemplate *findTemplate(const AsciiString &name);
};

extern ThingFactory *TheThingFactory;

class BuildListInfo
{
public:
	AsciiString getTemplateName() const;

	void *m_vtable;
	char m_pad04[0x0c - 0x04];
	Coord3D m_location;
	Real m_rallyOffsetX;
	Real m_rallyOffsetY;
	Real m_angle;
	char m_pad24[0x48 - 0x24];
	Int m_objectID;
	Int m_completionFrame;
};

class ExitInterface
{
public:
	virtual void slot00();
	virtual void slot01();
	virtual void slot02();
	virtual void slot03();
	virtual void slot04();
	virtual void slot05();
	virtual void slot06();
	virtual void slot07(const Coord3D *pos);
	virtual void slot08();
	virtual Bool slot09(Coord3D *pos, Bool a);
};

class ExitInterfaceSub;
class ExitInterfaceResult
{
public:
	virtual void slot00();
	virtual void slot00b();
};
class ExitInterfaceSub
{
public:
	virtual void slot00();
	virtual void slot01();
	virtual void slot02();
	virtual void *slot03();
};

class ExitInterfaceEntry
{
public:
	char m_pad00[0x0c];
	ExitInterfaceSub m_sub;
};

class Drawable;

class Thing
{
public:
	virtual void vslot00();
	virtual void vslot04();
	virtual void vslot08();
	virtual void vslot0c();
	virtual void vslot10();
	virtual void vslot14();
	virtual void vslot18();
	virtual void vslot1c();
	virtual void vslot20();
	virtual void vslot24();
	virtual Drawable *getDrawable() const;

	const Matrix3D *getTransformMatrix() const { return &m_transform; }
	Real getOrientation() const { return m_cachedAngle; }

private:
	char m_pad04[0x08 - 0x04];
	Matrix3D m_transform;
	char m_pad38[0x44 - 0x38];
	Real m_cachedAngle;
};

class Object : public Thing
{
public:
	Player *getControllingPlayer() const;
	Int getID() const { return m_id; }
	ExitInterface *getObjectExitInterface() const;

private:
	char m_pad48[0x74 - 0x48];
	Int m_id;
	char m_pad78[0x1f0 - 0x78];
	ExitInterfaceEntry **m_exitEntries;
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/ScriptEngine.h
class ScriptEngine
{
public:
	virtual void slot00();
	virtual void slot01();
	virtual void slot02();
	virtual void slot03();
	virtual void slot04();
	virtual void slot05();
	virtual void slot06();
	virtual void slot07();
	virtual void slot08();
	virtual void slot09();
	virtual void slot10();
	virtual void slot11();
	virtual void slot12();
	virtual void slot13();
	virtual void slot14();
	virtual void slot15();
	virtual void slot16();
	virtual void slot17();
	virtual void slot18();
	virtual void slot19();
	virtual void slot20();
	virtual void slot21();
	virtual void slot22();
	virtual void slot23();
	virtual void slot24();
	virtual void slot25();
	virtual void slot26();
	virtual void slot27();
	virtual void slot28();
	// vtable slot 29 (+0x74) -> ILT 0x00031F25 -> body 0x00349730.
	virtual void rva00349730(Object *obj, const AsciiString &name);

	void AppendDebugMessage(const AsciiString &strToAdd, Bool mustAdd);
};

extern ScriptEngine *TheScriptEngine;

class CastleBehaviorModuleData
{
public:
	char m_pad00[0x28];
	Real m_fadeInTime;
	char m_pad2c[0x3c - 0x2c];
	Rva0039F0A0 m_filter;
};

class CastleFactoryView
{
public:
	virtual void slot00();
	virtual void slot01();
	virtual void slot02();
	virtual void slot03();
	virtual Object *create(Object *owner, const void *definition, const Coord3D *position,
		Real angle, Player *player, Bool instant);
};

class CastleBehavior
{
public:
	Object *buildCastleStructure(BuildListInfo *record, Bool instant);

	Object *getOwner() const { return m_object; }
	void *getData() const { return m_moduleData; }

private:
	void *m_vtable;
	void *m_moduleData;
	Object *m_object;
	char m_pad0c[0x20 - 0x0c];
	CastleFactoryView m_ownedObjectFactory;
	char m_pad24[0xac - 0x24];
	Bool m_flagAC;
};

Real normalizeAngle(Real angle);

Object *CastleBehavior::buildCastleStructure(BuildListInfo *record, Bool instant)
{
	CastleBehaviorModuleData *data = (CastleBehaviorModuleData *)getData();
	Object *created = NULL;
	AsciiString name = record->getTemplateName();
	if (isStringEmpty(name))
		return created;
	const ThingTemplate *type = TheThingFactory->findTemplate(name);
	if (!type)
		return created;
	if (type->isKindOf(KINDOF_99))
		return created;
	if (type->isKindOf(KINDOF_59))
		m_flagAC = true;
	Player *player = getOwner()->getControllingPlayer();
	if (!data->m_filter.accepts(type, NULL, NULL))
		player = ThePlayerList->m_localPlayer;
	if (!player)
		return created;
	Coord3D pos;
	getOwner()->getTransformMatrix()->mulVector3(
		Vector3(record->m_location.x, record->m_location.y, record->m_location.z),
		*(Vector3 *)&pos);
	Real angle = normalizeAngle(record->m_angle + getOwner()->getOrientation());
	created = m_ownedObjectFactory.create(getOwner(), type, &pos, angle, player, instant);
	if (created)
	{
		record->m_objectID = created->getID();
		record->m_completionFrame = TheGameLogic->m_frame + 1;
		if (TheWritableGlobalData->m_debugAI)
		{
			AsciiString message;
			message.concat(name);
			message.concat(" - Building completed.");
			TheScriptEngine->AppendDebugMessage(name, false);
		}
		TheScriptEngine->rva00349730(created, AsciiString(""));
		if (!instant)
		{
			Int frames = (Int)(field<Real>(getData(), 0x28) * BfmeReportWeightScaleHolder::value);
			created->getDrawable()->bfmeDelayB(frames);
			reinterpret_cast<BfmeItemRY *>(created)->bfmeDoRY((void *)0xcf, (void *)frames);
			reinterpret_cast<BfmeRva9140Member *>(created)->setMode(5, 1);
			reinterpret_cast<DrawableApplyPendingThunk *>(created->getDrawable())->apply(false);
		}
		ExitInterface *exit = created->getObjectExitInterface();
		if (exit)
		{
			Bool hasOffset = false;
			if (fabs(record->m_rallyOffsetX) > 1.0f || fabs(record->m_rallyOffsetY) > 1.0f)
				hasOffset = true;
			Coord3D rally;
			if (!exit->slot09(&rally, true))
				rally = record->m_location;
			if (hasOffset)
			{
				rally.x += record->m_rallyOffsetX;
				rally.y += record->m_rallyOffsetY;
				exit->slot07(&rally);
			}
		}
		if (instant)
		{
			ExitInterfaceEntry **list = field<ExitInterfaceEntry **>(created, 0x1f0);
			for (ExitInterfaceEntry **entry = list; *entry; ++entry)
			{
				ExitInterfaceResult *result = (ExitInterfaceResult *)(*entry)->m_sub.slot03();
				if (result)
					result->slot00b();
			}
		}
	}
	return created;
}
