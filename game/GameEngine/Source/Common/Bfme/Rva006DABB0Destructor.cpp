// cl: /DNDEBUG /MD /EHsc
// TBuff (EA's name: ea_evidence TBuff::TBuff at 0x006DB470, vtable
// ??_7TBuff@@6B@ and the matched TBuff::xfer slot).
// Retail 0x006DABB0 (92 bytes). Private virtual destructor (??1TBuff@@EAE@XZ): derived vtable 0x0111E134,
// unregister through global 0x012EF4F0, decrement instance count 0x012F801C,
// then base vtable 0x01073744. Scalar deleting dtor at 0x006DB540 calls this.
// Twin constructor is 0x006DB470 (same vtable and counter), 160 bytes: it
// takes a source object and an int, zeroes its state, and copies the source's
// flag (+0x3B1), scale and three-word position when a source is given.

extern int g_012F801C;


class TBuff;

class Manager012EF4F0
{
public:
	void unregister(TBuff *obj);
};

extern Manager012EF4F0 *g_012EF4F0;

class Rva006DABB0Base
{
public:
	virtual ~Rva006DABB0Base() {}
};

#include "../../../../Libraries/Include/Lib/Coord3D.h"

// The source is a Drawable: its calls are Drawable::getScale (ILT 0x0003939C)
// and Drawable::getPosition (ILT 0x0004B12D).
class Drawable
{
public:
	float getScale() const;
	const Coord3D *getPosition() const;

	unsigned char m_unmodelled_000[0x3B1];
	unsigned char m_flag3B1;
};

// The copied position is one member object: retail zeroes it inside the
// constructor's initialisation, before its EH state store.
struct Rva006DABB0Position : public Coord3D
{
	Rva006DABB0Position() { *(int *)&x = 0; *(int *)&y = 0; *(int *)&z = 0; }
	Rva006DABB0Position &operator=(const Coord3D &that)
	{
		*(Coord3D *)this = that;
		return *this;
	}
};

class TBuff : public Rva006DABB0Base
{
public:
	TBuff(Drawable *src, int extra);

private:
	virtual ~TBuff();

public:

	int m_04;
	int m_08;
	int m_0C;
	unsigned char m_10;
	unsigned char m_unmodelled_011[0x44 - 0x11];
	unsigned char m_44;
	Rva006DABB0Position m_48;
	float m_54;
};

TBuff::TBuff(Drawable *src, int extra)
	: m_04(extra), m_08(0), m_0C(0), m_10(0), m_44(0), m_54(1.0f)
{
	if (src)
	{
		m_44 = src->m_flag3B1;
		m_54 = src->getScale();
		m_48 = *src->getPosition();
	}
	++g_012F801C;
}

TBuff::~TBuff()
{
	if (g_012EF4F0)
		g_012EF4F0->unregister(this);
	--g_012F801C;
}
