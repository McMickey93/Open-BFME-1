// Swap a record's five scalar words, then delegate the non-trivial tail.

struct BfmeSwapTailCJ;

// The tail swap goes through ILT 0x0004918E, the ledger's 5-byte row
// ?j_0004918e@@YAXXZ (game/gen_small/thunks_035.cpp), as tools/callees.py
// 0x196130 81 prints.  Nothing defines the pinned
// ?bfmeSwapTailCJ@@YAXPAUBfmeSwapTailCJ@@0@Z, so the call names the thunk
// through a function pointer cast that keeps the two-argument cdecl shape.
void j_0004918e();
typedef void (__cdecl *BfmeSwapTailCJFn)(BfmeSwapTailCJ *first, BfmeSwapTailCJ *second);

inline void bfmeSwapWordCJ(int &first, int &second)
{
	int value = first;
	first = second;
	second = value;
}

class BfmeRecordCJ
{
public:
	void bfmeSwap(BfmeRecordCJ &other);

private:
	int m_words[5];
	BfmeSwapTailCJ *m_tailStorage;
};

// ?bfmeSwap@BfmeRecordCJ@@QAEXAAV1@@Z
void BfmeRecordCJ::bfmeSwap(BfmeRecordCJ &other)
{
	bfmeSwapWordCJ(m_words[0], other.m_words[0]);
	bfmeSwapWordCJ(m_words[1], other.m_words[1]);
	bfmeSwapWordCJ(m_words[2], other.m_words[2]);
	bfmeSwapWordCJ(m_words[3], other.m_words[3]);
	bfmeSwapWordCJ(m_words[4], other.m_words[4]);

	((BfmeSwapTailCJFn)&j_0004918e)(reinterpret_cast<BfmeSwapTailCJ *>(m_words + 5),
		reinterpret_cast<BfmeSwapTailCJ *>(other.m_words + 5));
}
