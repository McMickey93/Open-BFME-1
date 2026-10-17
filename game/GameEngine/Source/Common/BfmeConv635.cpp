struct BfmeXCRB
{
	unsigned char m_bfmeHead[0xb0];
	float m_bfmeVal;
};

class BfmeSubCRB
{
public:
	virtual void bfmeSpareCRB0();
	virtual void bfmeSpareCRB1();
	virtual void bfmeSpareCRB2();
	virtual void bfmeSpareCRB3();
	virtual void bfmeSpareCRB4();
	virtual void bfmeSpareCRB5();
	virtual void bfmeSpareCRB6();
	virtual void bfmeSpareCRB7();
	virtual void bfmeSpareCRB8();
	virtual void bfmeSpareCRB9();
	virtual BfmeXCRB *bfmeGetCRB();
};

// The base step goes through ILT 0x0000F975, the ledger's 5-byte row
// ?j_0000f975@@YAXXZ (game/gen_small/thunks_007.cpp), jmp to 0x002A8540, as
// tools/callees.py prints for this body.  Nothing defines the pinned
// ?bfmeOneCRB@BfmeThingCRB@@QAEXPAX0@Z, so the call names the thunk through a
// raw pointer bridge that keeps the thiscall shape.
void j_0000f975();
class BfmeThingCRB
{
public:
	void bfmeGoCRB(void *one, void *two);
	unsigned char m_bfmeHead[8];
	BfmeSubCRB *m_bfmeSub;
};

void BfmeThingCRB::bfmeGoCRB(void *one, void *two)
{
	union
	{
		void (*raw)(void);
		void (BfmeThingCRB::*typed)(void *, void *);
	} oneCRB;
	oneCRB.raw = &j_0000f975;
	(this->*oneCRB.typed)(one, two);
	if (m_bfmeSub->bfmeGetCRB() != 0)
		m_bfmeSub->bfmeGetCRB()->m_bfmeVal = 1.0f;
}
