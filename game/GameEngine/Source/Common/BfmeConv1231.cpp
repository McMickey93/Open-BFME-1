// Open-BFME5 conversions.

class AptValue
{
public:
	int toInteger(void) const;
};

class BfmeE1231
{
public:
	virtual void bfmeV1231A();
	virtual void bfmeV1231B();
	unsigned m_bfme04;
};

class BfmeB1231
{
public:
	int m_bfme00;
	void *m_bfme04;
	void *m_bfme08;
};

class BfmeA1231
{
public:
	int m_bfme00;
	int m_bfme04;
	BfmeE1231 **m_bfme08;
};

// The emitter at 0x008CF5A0 is linked as the gen-dump ?d_008cf5a0@@YAXXZ, so
// the thiscall is reached through a member-pointer call (the pattern the Apt
// callers of ?d_008cc940 use).
extern void d_008cf5a0();
typedef void (BfmeA1231::*BfmeEmit1231Fn)(void *a1, void *a2, BfmeE1231 *a3, BfmeE1231 *a4, void *a5, int a6);

void bfmeGo1231(BfmeA1231 *a, BfmeB1231 *b)
{
	BfmeE1231 *e1;
	BfmeE1231 *e2;
	BfmeE1231 *e3;
	BfmeE1231 *e;
	void *v;
	int i;

	e1 = a->m_bfme08[a->m_bfme00 - 1];
	e2 = a->m_bfme08[a->m_bfme00 - 2];
	e3 = a->m_bfme08[a->m_bfme00 - 3];
	v = (void *)((AptValue *)e1)->toInteger();
	union { void (*fn)(); BfmeEmit1231Fn call; } emit = { d_008cf5a0 };
	(a->*emit.call)(b->m_bfme04, b->m_bfme08, e3, e2, v, 0);
	for (i = 1; i <= 3; ++i) {
		e = a->m_bfme08[a->m_bfme00 - i];
		if (!((unsigned char)(e->m_bfme04 >> 30) & 1))
			e->bfmeV1231B();
	}
	a->m_bfme00 -= 3;
}
