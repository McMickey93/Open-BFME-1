// cl: /DNDEBUG /MD /EHs /I game/Libraries/Source/WWVegas/WWLib /I game/Libraries/Source/WWVegas/WWMath /I game/Libraries/Source/WWVegas/WWDebug /I game/Libraries/Source/WWVegas/WWSaveLoad /I game/Libraries/Source/WWVegas/WW3D2 /I game/Libraries/Include
//
// Open-BFME: retail 0x0061DF60 (221B, ret at +0xDC). Slot 4 of vtable
// 0x01115C60 (installed by the BfmeNamedBG constructor) and of the derived
// tables 0x01115E60/0x01115E90 that inherit it. When the byte at +0x4C is set
// and the mode at +0x44 is non-zero, it takes the primary render object's
// translation, adds the vector from +0x50 to +0x5C scaled by +0x68 (negated
// for mode 2), and hands the result to slot 7, the by-value position setter
// whose base body is 0x0061D2D0. No caller, string or RTTI names the method,
// so it keeps an address-derived name; the field names describe their use.

#include "rendobj.h"

// class-gate: allow Coord3D slot 7 takes BFME's Coord3D by value; its user copy constructor and destructor give retail's saved argument address at +0xB0 (the WWMath Vector3 argument emits 217 bytes)
struct Coord3D
{
public:
	Coord3D(const Coord3D &that) : x(that.x), y(that.y), z(that.z) {}
	Coord3D(const Vector3 &v) : x(v.X), y(v.Y), z(v.Z) {}
	~Coord3D(void) {}
	float x, y, z;
};

class BfmeAnimationHolder
{
public:
	virtual void slot00();
	virtual void slot01();
	virtual void slot02();
	virtual void slot03();
	virtual void rva0061DF60();
	virtual void slot05();
	virtual void slot06();
	virtual void slot07(Coord3D position);

private:
	unsigned char m_before08[4];
	RenderObjClass *m_primary;
	unsigned char m_before44[0x44 - 0x0C];
	int m_mode;
	unsigned char m_before4C[4];
	bool m_enabled;
	unsigned char m_before50[3];
	Vector3 m_from;
	Vector3 m_to;
	float m_amount;
};

// ?rva0061DF60@BfmeAnimationHolder@@UAEXXZ
void BfmeAnimationHolder::rva0061DF60()
{
	if (m_enabled && m_mode != 0)
	{
		m_primary->Validate_Transform();
		Vector3 position;
		RenderObjClass *primary = m_primary;
		if (primary)
		{
			Matrix3D transform(primary->Get_Transform());
			position = transform.Get_Translation();
		}
		Vector3 delta(m_to);
		delta -= m_from;
		if (m_mode == 1)
			delta *= m_amount;
		else if (m_mode == 2)
			delta *= -m_amount;
		delta += position;
		slot07(Coord3D(delta));
	}
}
