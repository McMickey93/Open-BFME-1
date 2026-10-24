// cl: /DNDEBUG /MD /EHsc /O2 /Ob2
//
// Open-BFME: retail 0x0060B9C0 (125B, ret 0xC). Vtable 0x01115E60, installed
// by the matched Rva0060BBD0 constructor (0x0060BBD0), sends slot 7 through
// ILT 0x0002A58B here. The base table 0x01115C60 (BfmeNamedBG) holds ILT
// 0x00010069 -> 0x0061D2D0 in the same slot, and this body calls that ILT
// directly with the by-value position: a qualified base-class call. The base
// body's matched name declares three ints, so the call goes through the
// existing ILT identity with the by-value Coord3D ABI retail uses instead of
// a new name. The particle-system handle at +0x14 forwards the position to
// ParticleSystem::setPosition, falling back to the lazy null system
// (Make00001B18) when empty. Method name is address-derived.

// BFME Coord3D carries a user copy constructor and destructor; the copy the
// caller builds for the by-value argument keeps its address in a frame slot.
// class-gate: allow Coord3D BFME's user copy constructor and destructor, absent from the canonical header, give retail's 0x10 frame and saved argument address (the trivial copy emits 121 bytes)
struct Coord3D
{
public:
	Coord3D(const Coord3D &that) : x(that.x), y(that.y), z(that.z) {}
	~Coord3D(void) {}
	float x, y, z;
};

class ParticleSystem
{
public:
	void setPosition(const Coord3D *position);
};

ParticleSystem *Make00001B18(void);

void j_00010069();

class Rva0060BBD0ParticleHandle
{
public:
	operator bool() const { return m_system != 0; }
	ParticleSystem *operator->() const { return m_system == 0 ? Make00001B18() : m_system; }

	ParticleSystem *m_system;
	void *m_previous;
	void *m_next;
};

class Rva0060BBD0
{
public:
	virtual void rva0060B9C0(Coord3D position);

private:
	// Base-class slot 7 through ILT 0x00010069. MSVC 7.1 single-inheritance
	// member pointers are one code address with the receiver in ECX.
	void baseSlot7(Coord3D position)
	{
		union { void (*entry)(); void (Rva0060BBD0::*method)(Coord3D); } fn;
		fn.entry = &j_00010069;
		(this->*fn.method)(position);
	}

	unsigned char m_base[0x10];
	Rva0060BBD0ParticleHandle m_particleSystem;
};

void Rva0060BBD0::rva0060B9C0(Coord3D position)
{
	baseSlot7(position);
	if (m_particleSystem)
	{
		Coord3D copy(position);
		m_particleSystem->setPosition(&copy);
	}
}
