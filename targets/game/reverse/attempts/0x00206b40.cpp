// ?claimNearest@Rva00206B40Owner@@QAEHH@Z
// partial score=0.0407 date=2026-10-18
// ?claimNearest@Rva00206B40Owner@@QAEHH@Z
// partial score=0.2339 date=2026-10-18 (279/295 B, 226 diffs, shape 0.851)
// cl: /O2 /GR- /DNDEBUG /DWIN32 /MD /EHsc- /Igame/Libraries/Include /Igame/GameEngine/Source/GameLogic/Object
typedef float Real;
typedef int Int;
typedef unsigned int UnsignedInt;
typedef bool Bool;

#include <math.h>
#pragma intrinsic(sqrt)

#include "Lib/Coord3D.h"

class Overridable
{
public:
	const Overridable *getFinalOverride() const
	{
		if (m_nextOverride)
			return m_nextOverride->getFinalOverride();
		return this;
	}

	void *m_vtable;
	Overridable *m_nextOverride;
};

class Rva00206B40Template : public Overridable
{
public:
	unsigned char m_pad008[0xd8 - 0x08];
	UnsignedInt m_flagsD8;
};

template <class T>
class OVERRIDE
{
public:
	const T *operator->() const
	{
		if (!m_overridable)
			return 0;
		return (const T *)m_overridable->getFinalOverride();
	}

	T *m_overridable;
};

#define BFME_HAVE_COORD3D
#define OBJECT_TU_MEMBERS \
	const Rva00206B40Template *getTemplate00206B40() const \
	{ \
		return ((const OVERRIDE<Rva00206B40Template> *)&m_template)->operator->(); \
	}
#include "object.h"
#undef OBJECT_TU_MEMBERS

class GameLogic
{
public:
	Object *findObjectByID(Int id);
};
extern GameLogic *TheGameLogic;

class BfmeHostERP
{
public:
	void bfmeSweepERP();
};

struct ArrayItem
{
	void *m_vtable;
	Int m_occupied;
	Coord3D m_pos;
	unsigned char m_pad14[0x20 - 0x14];
	Int m_claimantID;
};

class Rva00206B40Owner
{
public:
	Int claimNearest(Int objectID);

	void *m_vtable;
	ArrayItem **m_begin;
	ArrayItem **m_end;
};

Int Rva00206B40Owner::claimNearest(Int objectID)
{
	Object *obj = TheGameLogic->findObjectByID(objectID);
	if (obj == 0)
		return -1;

	((BfmeHostERP *)((char *)this - 0x20))->bfmeSweepERP();

	ArrayItem **items = m_begin;
	UnsignedInt count = m_end - items;
	Int bestIndex = -1;
	if (count == 0)
		return bestIndex;

	Real bestDist = 99999.0f;
	for (UnsignedInt i = 0; i < count; ++i)
	{
		ArrayItem *item = m_begin[i];
		if (item->m_claimantID != 0)
			continue;
		if (!(obj->getTemplate00206B40()->m_flagsD8 & 0x400) && item->m_occupied != 0)
			continue;

		Coord3D delta;
		delta.x = item->m_pos.x;
		delta.y = item->m_pos.y;
		delta.z = item->m_pos.z;
		delta.x -= obj->m_cachedPos.x;
		delta.y -= obj->m_cachedPos.y;
		delta.z -= obj->m_cachedPos.z;
		Real dist = (Real)sqrt(delta.x * delta.x + delta.y * delta.y + delta.z * delta.z);
		if (dist < bestDist)
		{
			bestDist = dist;
			bestIndex = i;
		}
	}

	if (bestIndex >= 0)
		items[bestIndex]->m_claimantID = objectID;
	return bestIndex;
}
