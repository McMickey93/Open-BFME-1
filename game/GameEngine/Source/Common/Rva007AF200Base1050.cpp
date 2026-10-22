// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD
// Retail 0x007AF200 (100 bytes): BfmeB1050::bfmeBase1050, the base-field
// initializer that BfmeB1050::bfmeGo1050B (BfmeConv1050.cpp) and
// BfmeB1159::initialize (Rva007B44E0ShadowPair.cpp) call through ILT 0xAF38
// before setting the derived fields and the vtable pointer.
//
// The two three-float groups are assigned from constructed temporaries of a
// three-float type with a constructor and an implicit (memberwise) copy
// assignment: retail's dead [esp+4..+0xC] stores and the 1.0f routed through
// the stack are the temporaries' fields, forwarded into the member stores.
// WWMath's Vector3 cannot be the type: its user-written operator= lets VC7.1
// drop the temporaries (58 bytes). The type is unproven, so it keeps an
// address-derived name, as does the method's existing pinned name.

struct Rva007AF200Triple
{
	float x, y, z;
	Rva007AF200Triple() {}
	Rva007AF200Triple(float ax, float ay, float az) { x = ax; y = ay; z = az; }
};

class BfmeB1050
{
public:
	void bfmeBase1050(void);

	void *m_bfmeVfptr;
	unsigned char m_4;
	unsigned char m_5;
	Rva007AF200Triple m_8;
	Rva007AF200Triple m_14;
	int m_20;
	int m_24;
	int m_28;
	int m_2c;
	unsigned char m_30;
	int m_34;
};

void BfmeB1050::bfmeBase1050(void)
{
	m_4 = 1;
	m_5 = 0;
	m_8 = Rva007AF200Triple(0.0f, 0.0f, 0.0f);
	m_14 = Rva007AF200Triple(0.0f, 0.0f, 1.0f);
	m_20 = 0;
	m_28 = -1;
	m_24 = -1;
	m_2c = 0xff;
	m_30 = 1;
	m_34 = 0;
}
