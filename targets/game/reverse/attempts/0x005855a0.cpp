// ?cachedPair@Rva005855A0Owner@@QAEXXZ
// partial score=0.9042 date=2026-10-16
// 167/167 bytes; identical code, only the float out local sits at the frame bottom (retail: top).
// cl: /DNDEBUG /DWIN32 /MD /EHsc
struct BfmeCoordESM
{
	BfmeCoordESM(float x, float y) { m_x = x; m_y = y; }
	BfmeCoordESM(const BfmeCoordESM &other) throw() { m_x = other.m_x; m_y = other.m_y; }
	~BfmeCoordESM() {}
	float m_x;
	float m_y;
};

struct Rva005855A0Pair
{
	int first;
	int second;
};

class Rva003C9470Key;

struct Rva003C9470Output
{
	float x;
	float y;
};

class Rva003C9470Owner
{
public:
	bool fallback(Rva003C9470Key *key, Rva003C9470Output *output);
};

class Glo012F1028Type
{
public:
	char pad00[0x28];
	Rva003C9470Owner *m_owner;
};

extern Glo012F1028Type *Glo012F1028;
void bfmeGo1077C(int, float, float);

class BfmeHostESM
{
public:
	virtual void slot00();
	virtual void slot04();
	virtual void slot08();
	virtual void slot0C();
	virtual void slot10();
	virtual void slot14();
	virtual void slot18();
	virtual void slot1C();
	virtual void slot20();
	virtual void slot24(BfmeCoordESM *coord, Rva005855A0Pair *result);
	char bfmeRunESM(BfmeCoordESM coord, float *out);
};

extern BfmeHostESM *g_bfmeStateDF;

class Rva005855A0Owner
{
public:
	void cachedPair();

private:
	char pad00[0x10];
	int m_cachedFirst;
	int m_cachedSecond;
};

void Rva005855A0Owner::cachedPair()
{
	Rva003C9470Owner *owner = Glo012F1028->m_owner;
	Rva003C9470Output position;
	owner->fallback(
		(Rva003C9470Key *)(*(char **)((char *)this + 8) + 4), &position);
	BfmeCoordESM coord(position.x, position.y);
	float out;
	g_bfmeStateDF->bfmeRunESM(coord, &out);
	Rva005855A0Pair result;
	g_bfmeStateDF->slot24(&coord, &result);
	if (result.first != m_cachedFirst || result.second != m_cachedSecond)
	{
		bfmeGo1077C(0, (float)result.first, (float)result.second);
		m_cachedFirst = result.first;
		m_cachedSecond = result.second;
	}
}
