// cl: /O2 /DNDEBUG /MD /EHsc

extern "C" void _ReadWriteBarrier(void);
#pragma intrinsic(_ReadWriteBarrier)

struct BfmeSwapTailCJ;
// The tail swap goes through ILT 0x0004918E, the ledger's 5-byte row
// ?j_0004918e@@YAXXZ (game/gen_small/thunks_035.cpp), as tools/callees.py
// 0xde160 57 prints.  Nothing defines the pinned
// ?bfmeSwapTailCJ@@YAXPAUBfmeSwapTailCJ@@0@Z, so the call names the thunk
// through a function pointer cast that keeps the two-argument cdecl shape.
void j_0004918e();
typedef void (__cdecl *BfmeSwapTailCJFn)(BfmeSwapTailCJ *first, BfmeSwapTailCJ *second);

struct Rva000DE160
{
	unsigned int m_word00;
	unsigned int m_word04;
	unsigned int m_word08;
	char m_tail[4];

	void swap(Rva000DE160 &other);
};

void Rva000DE160::swap(Rva000DE160 &other)
{
	unsigned int t0 = m_word00;
	m_word00 = other.m_word00;
	other.m_word00 = t0;

	_ReadWriteBarrier();

	unsigned int t1 = m_word04;
	m_word04 = other.m_word04;
	other.m_word04 = t1;

	_ReadWriteBarrier();

	unsigned int t2 = m_word08;
	m_word08 = other.m_word08;
	other.m_word08 = t2;

	((BfmeSwapTailCJFn)&j_0004918e)(reinterpret_cast<BfmeSwapTailCJ *>(m_tail),
		reinterpret_cast<BfmeSwapTailCJ *>(other.m_tail));
}
