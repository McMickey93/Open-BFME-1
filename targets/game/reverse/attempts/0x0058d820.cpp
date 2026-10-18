// ?d_0058d820@@YAXXZ
// partial score=1.0 date=2026-10-18
// BANKED 2026-10-18: byte-exact (101/101 modulo relocations) but not landable yet.
// Place in game/GameEngine/Source/GameClient/ to probe. The DIR32 check refuses
// g_bfmeMsgVftDN: retail 0x010F5738 is recorded as ??_7?$BlitTransRemapXlat@E@@6B@
// (+11 more), so the stack object is a BlitTransRemapXlat<unsigned char>-shaped
// blitter whose real class (with virtuals) must install that vtable; keep the
// inline dtor that only resets the vptr (it keeps retail's EH frame, no call).
// Retail 0x0058D820 (101 B, EA file Palantir.cpp): if the indexed bucket slot
// is not the end node, hand ControlBar a stack message carrying its value.
// The earlier name bfmeFireDN is contradicted by ilt_oracle at ILT 0x0001F1AE,
// so the address names it. The message's inline destructor only resets the
// vptr (a dead store), which keeps retail's EH frame without a call.
// The message vtable at VA 0x010F5738 (pinned as g_bfmeMsgVftDN).
extern "C" void *g_bfmeMsgVftDN[];

struct BfmeMsgDN
{
	BfmeMsgDN(void *p)
	{
		m_bfmeVftDN = g_bfmeMsgVftDN;
		m_bfmePtrDN = p;
		m_bfmeFlagDN = 0;
	}

	~BfmeMsgDN() { m_bfmeVftDN = g_bfmeMsgVftDN; }

	void *m_bfmeVftDN;
	void *m_bfmePtrDN;
	int m_bfmeFlagDN;
};

class ControlBar
{
public:
	void bfmeShowDN(BfmeMsgDN *m);
};

extern ControlBar *TheControlBar;

class BfmeNodeDN
{
public:
	unsigned char m_bfmeHeadDN[8];
	void *m_bfmeValDN;
};

class BfmeSlotDN
{
public:
	BfmeNodeDN *m_bfmeFirstDN;
	unsigned char m_bfmeGapDN[0x14];
};

class BfmeBucketDN
{
public:
	unsigned char m_bfmeHeadDN[4];
	BfmeNodeDN *m_bfmeEndDN;
	BfmeSlotDN m_bfmeSlotsDN[1];
};

class BfmeHostDN
{
public:
	void rva0058D820(int unused);

	BfmeBucketDN *m_bfmeBucketDN;
	int m_bfmeIndexDN;
};

void BfmeHostDN::rva0058D820(int unused)
{
	BfmeBucketDN *b = m_bfmeBucketDN;
	BfmeSlotDN &slot = b->m_bfmeSlotsDN[m_bfmeIndexDN];
	BfmeNodeDN *end = b->m_bfmeEndDN;
	BfmeNodeDN *e = slot.m_bfmeFirstDN;
	if (e != end)
	{
		BfmeMsgDN msg(e->m_bfmeValDN);
		TheControlBar->bfmeShowDN(&msg);
	}
}
