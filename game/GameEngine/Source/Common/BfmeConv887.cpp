// Retail calls 0x0082E5F0 directly: STLport's private static
// __node_alloc<true,0>::_M_deallocate(void *, size_t), matched under that
// mangled name, so the call spells it.
extern "C" void __cdecl __identifier("?_M_deallocate@?$__node_alloc@$00$0A@@_STL@@CAXPAXI@Z")(void *p, unsigned int n);
#define NodeAllocDeallocate __identifier("?_M_deallocate@?$__node_alloc@$00$0A@@_STL@@CAXPAXI@Z")

struct BfmeNodeEXB
{
	BfmeNodeEXB *m_bfmeNext;
	BfmeNodeEXB *m_bfmePrev;
};

struct BfmeThingEXBa
{
	void bfmeGoEXBa();
	unsigned char m_bfmeHead[0xc];
	BfmeNodeEXB *m_bfmeHead2;
};

void BfmeThingEXBa::bfmeGoEXBa()
{
	BfmeNodeEXB *head = m_bfmeHead2;
	BfmeNodeEXB *n = head->m_bfmeNext;
	while (n != head)
	{
		BfmeNodeEXB *p = n;
		n = n->m_bfmeNext;
		NodeAllocDeallocate(p, 0x10);
		head = m_bfmeHead2;
	}
	m_bfmeHead2->m_bfmeNext = m_bfmeHead2;
	m_bfmeHead2->m_bfmePrev = m_bfmeHead2;
}

struct BfmeThingEXBb
{
	void bfmeGoEXBb();
	unsigned char m_bfmeHead[0x2c];
	BfmeNodeEXB *m_bfmeHead2;
};

void BfmeThingEXBb::bfmeGoEXBb()
{
	BfmeNodeEXB *head = m_bfmeHead2;
	BfmeNodeEXB *n = head->m_bfmeNext;
	while (n != head)
	{
		BfmeNodeEXB *p = n;
		n = n->m_bfmeNext;
		NodeAllocDeallocate(p, 0xc);
		head = m_bfmeHead2;
	}
	m_bfmeHead2->m_bfmeNext = m_bfmeHead2;
	m_bfmeHead2->m_bfmePrev = m_bfmeHead2;
}
