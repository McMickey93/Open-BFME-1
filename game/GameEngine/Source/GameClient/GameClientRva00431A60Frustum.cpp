// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib
// GameClient frustum traversal at its address-derived virtual slot.
#include "sphere.h"
#include "frustum.h"

#include "../../../Libraries/Include/Lib/Coord3D.h"

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/Overridable.h
class Overridable
{
private:
	void *m_vtable;
	const Overridable *m_nextOverride;

public:
	const Overridable *getFinalOverride() const
	{
		if (m_nextOverride != 0)
			return m_nextOverride->getFinalOverride();
		return this;
	}
};

class ThingTemplate : public Overridable
{
public:
	unsigned char m_opaque[0xD8 - sizeof(Overridable)];
	unsigned char m_byteD8;
};

template <class T> class OverridePtr
{
private:
	const T *m_overridable;

public:
	operator const T *() const
	{
		if (m_overridable == 0)
			return 0;
		return static_cast<const T *>(m_overridable->getFinalOverride());
	}
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/Thing.h
class Thing
{
private:
	void *m_vtable;
	OverridePtr<ThingTemplate> m_template;

public:
	const ThingTemplate *getTemplate() const { return m_template; }
};

class Object : public Thing
{
};

// Matched 0x0041D150 spelling (BFMERopeDrawableLinearInterpolatedPosition.cpp).
struct BfmeLinearCoord3D
{
	float x;
	float y;
	float z;
};

class BFMERopeDrawableGetPositionShim
{
public:
	const BfmeLinearCoord3D *getPositionLinear() const;
};

// Matched 0x00416B20 spelling (Rva00416B20GetFloat.cpp).
class Rva00416B20
{
public:
	float get();
};

// Matched 0x00410DD0 spelling (BfmeConv923.cpp).
class BfmeThing923B
{
public:
	void bfmeGo923B(char);
};

class Gen_00410BA0
{
public:
	int isDrawableEffectivelyHidden(void) const;
};

class Drawable : public Thing
{
private:
	unsigned char m_opaque[0xFC - sizeof(Thing)];
	Object *m_object;
	unsigned char m_pad100[4];
	Drawable *m_nextDrawable;
	unsigned char m_pad108[0x2E8 - 0x108];

public:
	int m_dword2E8;

	const Object *getObject() const { return m_object; }
	Drawable *getNextDrawable() const { return m_nextDrawable; }
};

typedef void (*GameClientFuncPtr)(Drawable *draw, void *userData);

// The witnessed call consumes AL; the existing owner returns only 0 or 1.
// Keep its canonical symbol while retaining this caller's byte-return ABI.
typedef bool (Gen_00410BA0::*HiddenResult)() const;

class GameClient
{
public:
	virtual void slot00(); virtual void slot01(); virtual void slot02(); virtual void slot03();
	virtual void slot04(); virtual void slot05(); virtual void slot06(); virtual void slot07();
	virtual void slot08(); virtual void slot09(); virtual void slot10(); virtual void slot11();
	virtual Drawable *firstDrawable();
	virtual void slot13(); virtual void slot14(); virtual void slot15();
	virtual void slot16(); virtual void slot17(); virtual void slot18(); virtual void slot19();
	virtual void slot20();
	virtual void rva00431A60(FrustumClass *frustum, float radius, GameClientFuncPtr userFunc, void *userData);

private:
	unsigned char m_pad[0x0C];
	Drawable *m_drawableList;
};

// ?rva00431A60@GameClient@@UAEXPAVFrustumClass@@MP6AXPAVDrawable@@PAX@Z2@Z
void GameClient::rva00431A60(FrustumClass *frustum, float radius, GameClientFuncPtr userFunc, void *userData)
{
	if (radius < 0.0f)
		radius = 25.0f;

	Drawable *draw;
	Drawable *nextDrawable;
	for (draw = m_drawableList; draw; draw = nextDrawable)
	{
		nextDrawable = draw->getNextDrawable();

		bool visible = true;
		const Object *obj = draw->getObject();
		if (!obj || !(obj->getTemplate()->m_byteD8 & 0x20))
		{
			Vector3 pos = *(const Vector3 *)((const BFMERopeDrawableGetPositionShim *)draw)->getPositionLinear();
			SphereClass sphere(Vector3(pos.X, pos.Y, pos.Z), ((Rva00416B20 *)draw)->get() + radius);

			int plane = draw->m_dword2E8;
			if (plane >= 1 && plane <= 4 && frustum->Planes[plane].In_Front(sphere))
				continue;

			visible = !(reinterpret_cast<const Gen_00410BA0 *>(draw)->*reinterpret_cast<HiddenResult>(&Gen_00410BA0::isDrawableEffectivelyHidden))();
			for (int i = 1; i <= 4; i++)
			{
				if (plane == i)
					continue;
				if (frustum->Planes[i].In_Front(sphere))
				{
					draw->m_dword2E8 = i;
					visible = false;
					break;
				}
			}
		}
		if (visible)
		{
			userFunc(draw, userData);
			draw->m_dword2E8 = 0;
			((BfmeThing923B *)draw)->bfmeGo923B(1);
		}
		else
		{
			((BfmeThing923B *)draw)->bfmeGo923B(0);
		}
	}
}
