// cl: /DNDEBUG /DWIN32 /MD /EHsc
// Retail 0x003A44A0 (165 bytes, ret 4), reached through ILT 0x00020509 by the
// matched Gen003BDE80Element::process (0x003A51D0), BfmeThingBOC::bfmeGoBOC
// and Transfer003C3D90::load003C4160; the method keeps its pinned
// address-derived name. With the byte flag set it asks bfmeRunESM
// (0x00609DA0) for a height at the +0x0C position, then walks the item
// vector at +0x48, handing each item the position raised by its +0xA8
// offset (slot 7) before calling slot 3.
//
// Shape: the by-value coordinates carry a copy constructor and an empty
// destructor (the saved-esp slot, as in Rva005855A0Refresh.cpp); the item
// count goes through an inline size() so the vector start is reloaded.

struct Rva003A44A0Pos
{
	float x;
	float y;
};

struct BfmeCoordESM
{
	BfmeCoordESM(const Rva003A44A0Pos &p) { m_x = p.x; m_y = p.y; }
	BfmeCoordESM(const BfmeCoordESM &other) throw() { m_x = other.m_x; m_y = other.m_y; }
	~BfmeCoordESM() {}
	float m_x;
	float m_y;
};

class BfmeHostESM
{
public:
	char bfmeRunESM(BfmeCoordESM coord, float *out);
};

class Rva006092D0State;
extern Rva006092D0State *g_rva012F7048LivingWorld;

// class-gate: allow Coord3D the by-value argument needs a user copy constructor and an empty destructor for retail's saved-esp slot; the canonical Lib struct has neither
struct Coord3D
{
	Coord3D() {}
	Coord3D(const Coord3D &other) throw() { x = other.x; y = other.y; z = other.z; }
	~Coord3D() {}
	float x;
	float y;
	float z;
};

class Rva003A44A0Item
{
public:
	virtual void slot00();
	virtual void slot04();
	virtual void slot08();
	virtual void slot0C();
	virtual void slot10();
	virtual void slot14();
	virtual void slot18();
	virtual void slot1C(Coord3D pos);

	char m_gap04[0xa4];
	float m_heightA8;
};

struct Rva003A44A0Items
{
	Rva003A44A0Item **m_start;
	Rva003A44A0Item **m_finish;
	unsigned int size() const { return unsigned int(m_finish - m_start); }
	Rva003A44A0Item *operator[](unsigned int n) const { return *(m_start + n); }
};

class Gen003BDE80Element
{
public:
	void rva003A44A0(bool flag);

	char m_gap00[0xc];
	Rva003A44A0Pos m_pos0C;
	char m_gap14[0x34];
	Rva003A44A0Items m_items48;
};

void Gen003BDE80Element::rva003A44A0(bool flag)
{
	float height;
	if (flag)
		reinterpret_cast<BfmeHostESM *>(g_rva012F7048LivingWorld)->bfmeRunESM(BfmeCoordESM(m_pos0C), &height);
	for (unsigned int i = 0; i < m_items48.size(); ++i) {
		if (flag) {
			Coord3D pos;
			pos.x = m_pos0C.x;
			pos.y = m_pos0C.y;
			pos.z = height + m_items48[i]->m_heightA8;
			m_items48[i]->slot1C(pos);
		}
		m_items48[i]->slot0C();
	}
}
