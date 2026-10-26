// cl: /O2 /DNDEBUG /MD /EHsc
//
// Unclaimed one-instruction-shape bodies, each alone in a .text gap no ledger
// row covered: a 16-byte-aligned start directly after an int3 pad run, the
// body's last instruction followed by int3 padding, and no call, ILT stub,
// table slot or dir32 name reaching the address. Most sit in the STLport
// facet run (0x0083E000..0x0084A000), where they look like the public
// non-virtual facet wrappers emitted out of line, but nothing here proves
// which facet or member each one is.
//
//   mov eax,[ecx] / jmp [eax+N]             tail call of the receiver's own
//                                           virtual slot N/4, no stack args
//   mov ecx,[ecx+0x40] / mov eax,[ecx] /    the same through the pointer held
//   jmp [eax+N]                             at +0x40
//   xor al,al / ret, xor eax,eax / ret, or eax,-1 / ret, or ax,0xffff / ret,
//   mov eax,imm32 / ret, ret                constant returners and no-ops
//
// IDENTITY IS NOT RECOVERED.  Every name is derived from an address.

// A receiver whose vtable is all that is read; slot k sits at +4k.
class BfmeSlotTailView
{
public:
	virtual int slot00() = 0;
	virtual int slot01() = 0;
	virtual int slot02() = 0;
	virtual int slot03() = 0;
	virtual int slot04() = 0;
	virtual int slot05() = 0;
	virtual int slot06() = 0;
	virtual int slot07() = 0;
	virtual int slot08() = 0;
	virtual int slot09() = 0;
	virtual int slot10() = 0;
	virtual int slot11() = 0;
	virtual int slot12() = 0;
};

#define BFME_SELF_SLOT_TAIL( NAME, SLOT )                                 \
	class NAME : public BfmeSlotTailView                                  \
	{                                                                     \
	public:                                                               \
		int invoke();                                                     \
	};                                                                    \
	int NAME::invoke()                                                    \
	{                                                                     \
		return slot##SLOT();                                              \
	}

#define BFME_MEMBER_SLOT_TAIL( NAME, OFFSET, SLOT )                       \
	class NAME                                                            \
	{                                                                     \
	public:                                                               \
		int invoke();                                                     \
		char m_lead[ OFFSET ];                                            \
		BfmeSlotTailView *m_receiver;                                     \
	};                                                                    \
	int NAME::invoke()                                                    \
	{                                                                     \
		return m_receiver->slot##SLOT();                                  \
	}

BFME_SELF_SLOT_TAIL( Rva0083E860, 08 )
BFME_SELF_SLOT_TAIL( Rva0083E870, 10 )
BFME_SELF_SLOT_TAIL( Rva0083E880, 12 )
BFME_MEMBER_SLOT_TAIL( Rva0083E9B0, 0x40, 08 )
BFME_MEMBER_SLOT_TAIL( Rva0083E9C0, 0x40, 12 )
BFME_SELF_SLOT_TAIL( Rva0083FDE0, 01 )
BFME_SELF_SLOT_TAIL( Rva0083FE40, 10 )
BFME_SELF_SLOT_TAIL( Rva0083FE50, 11 )
BFME_SELF_SLOT_TAIL( Rva0083FE80, 06 )
BFME_SELF_SLOT_TAIL( Rva00840FF0, 04 )
BFME_SELF_SLOT_TAIL( Rva00841000, 05 )
BFME_SELF_SLOT_TAIL( Rva00841010, 07 )
BFME_SELF_SLOT_TAIL( Rva00841020, 04 )
BFME_SELF_SLOT_TAIL( Rva00841030, 05 )
BFME_SELF_SLOT_TAIL( Rva00841040, 07 )
BFME_SELF_SLOT_TAIL( Rva00845CF0, 01 )
BFME_SELF_SLOT_TAIL( Rva00845E80, 01 )
BFME_SELF_SLOT_TAIL( Rva00847CF0, 02 )
BFME_SELF_SLOT_TAIL( Rva00847D00, 01 )
BFME_SELF_SLOT_TAIL( Rva00847D10, 02 )
BFME_SELF_SLOT_TAIL( Rva00847D20, 07 )
BFME_SELF_SLOT_TAIL( Rva00847D70, 01 )
BFME_SELF_SLOT_TAIL( Rva00847D90, 07 )
BFME_SELF_SLOT_TAIL( Rva00847DE0, 01 )
BFME_SELF_SLOT_TAIL( Rva00847DF0, 02 )
BFME_SELF_SLOT_TAIL( Rva00847E00, 07 )
BFME_SELF_SLOT_TAIL( Rva00847E50, 01 )
BFME_SELF_SLOT_TAIL( Rva00847E60, 02 )
BFME_SELF_SLOT_TAIL( Rva00847E70, 07 )
BFME_SELF_SLOT_TAIL( Rva00849D10, 01 )
BFME_SELF_SLOT_TAIL( Rva00849D20, 03 )
BFME_SELF_SLOT_TAIL( Rva00849D30, 02 )
BFME_SELF_SLOT_TAIL( Rva00849D40, 06 )
BFME_SELF_SLOT_TAIL( Rva00849D80, 03 )
BFME_SELF_SLOT_TAIL( Rva00849DC0, 06 )
BFME_SELF_SLOT_TAIL( Rva00881C50, 09 )

void Rva0081D950Noop() {}
unsigned short Rva0083E9A0AllOnes() { return 0xFFFF; }
bool Rva0083EB60False() { return false; }
bool Rva0083EB70False() { return false; }
bool Rva0083EB80False() { return false; }
bool Rva0083EB90False() { return false; }
bool Rva0083EBA0False() { return false; }
bool Rva0083EBB0False() { return false; }
bool Rva00843E90False() { return false; }
bool Rva00843EA0False() { return false; }
bool Rva00843EB0False() { return false; }
bool Rva00843EC0False() { return false; }
bool Rva00843ED0False() { return false; }
bool Rva00843EE0False() { return false; }
unsigned short Rva00844E60AllOnes() { return 0xFFFF; }
int Rva00844E70Value() { return (-2147483647 - 1); }
int Rva00844E80Value() { return 0x7FFFFFFF; }
int Rva00844E90MinusOne() { return -1; }
bool Rva0084A6D0False() { return false; }
int Rva00865750Zero() { return 0; }
int Rva008657B0Zero() { return 0; }
int Rva00865810Zero() { return 0; }
int Rva009E24A0Value() { return 0x10001; }
bool Rva009F2E70False() { return false; }
bool Rva009F2E80False() { return false; }
void Rva009F4BE0Noop() {}
void Rva009F4C90Noop() {}
void Rva009F5430Noop() {}

// Call-free __thiscall and __cdecl leaves from the same kind of gaps. Fields
// are spelled only where the bytes touch them; leads stand for the rest.

// 0x0084A490 / 0x0084A4B0 / 0x0084A4D0: `lea eax,[ecx+N] / ret`
class Rva0084A490
{
public:
	char *address();
	char m_lead[ 0x8 ];
	char m_8;
};

char *Rva0084A490::address() { return &m_8; }

class Rva0084A4B0
{
public:
	char *address();
	char m_lead[ 0x4 ];
	char m_4;
};

char *Rva0084A4B0::address() { return &m_4; }

class Rva0084A4D0
{
public:
	char *address();
	char m_lead[ 0xC ];
	char m_C;
};

char *Rva0084A4D0::address() { return &m_C; }

// 0x0084A710: `xor ax,ax / ret`
unsigned short Rva0084A710Zero() { return 0; }

// 0x00AFE6B0: `mov eax,[ecx+4] / ret`
class Rva00AFE6B0
{
public:
	int get() const;
	int m_0;
	int m_4;
};

int Rva00AFE6B0::get() const { return m_4; }

// 0x0083E950: `mov ax,[ecx+0x54] / ret`
class Rva0083E950
{
public:
	unsigned short get() const;
	char m_lead[ 0x54 ];
	unsigned short m_54;
};

unsigned short Rva0083E950::get() const { return m_54; }

// 0x00845310 / 0x00845450: `mov eax,ecx / ret 4`, returning the receiver
class Rva00845310
{
public:
	Rva00845310 &self( int );
};

Rva00845310 &Rva00845310::self( int ) { return *this; }

class Rva00845450
{
public:
	Rva00845450 &self( int );
};

Rva00845450 &Rva00845450::self( int ) { return *this; }

// 0x00825410 / 0x00825420: cdecl, the low 16 bits of the argument
int Rva00825410Low16( int value ) { return value & 0xFFFF; }
int Rva00825420Low16( int value ) { return value & 0xFFFF; }

// 0x00845460: true when the byte at +4 is clear
class Rva00845460
{
public:
	bool isClear() const;
	int m_0;
	bool m_4;
};

bool Rva00845460::isClear() const { return !m_4; }

// 0x008483E0 / 0x00848400: copies the dword at +0 into a hidden return object
// and pops it with one ignored argument (`ret 8`)
class Rva008483E0
{
public:
	Rva008483E0( const Rva008483E0 &other ) : m_0( other.m_0 ) {}
	Rva008483E0 copy( int );
	int m_0;
};

Rva008483E0 Rva008483E0::copy( int ) { return *this; }

class Rva00848400
{
public:
	Rva00848400( const Rva00848400 &other ) : m_0( other.m_0 ) {}
	Rva00848400 copy( int );
	int m_0;
};

Rva00848400 Rva00848400::copy( int ) { return *this; }

// 0x00845700 / 0x00845710: cdecl, the dword at +0x58 of the sub-object the
// argument's offset table (its first dword) places at entry 1
struct Rva00845700Object
{
	int *m_offsets;
};

void *Rva00845700Load( Rva00845700Object *object )
{
	return *(void **)( (char *)object + object->m_offsets[ 1 ] + 0x58 );
}

void *Rva00845710Load( Rva00845700Object *object )
{
	return *(void **)( (char *)object + object->m_offsets[ 1 ] + 0x58 );
}
