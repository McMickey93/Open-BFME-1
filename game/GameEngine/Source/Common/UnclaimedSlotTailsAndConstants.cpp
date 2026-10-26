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
