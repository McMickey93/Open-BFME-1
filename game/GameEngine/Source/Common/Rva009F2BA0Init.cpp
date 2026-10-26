// cl: /O2 /Ob0

struct Rva009F2BA0Node
{
	char pad[0x18];
	void *m_18;
	char pad2[0xF0-0x1C];
	Rva009F2BA0Node *m_F0;
};

class Rva009F2BA0
{
	Rva009F2BA0Node *m_00;
	char pad[0x14];
	void *m_18;
	void *m_1C;

public:
	void init();
};

void Rva009F2BA0::init()
{
	if (m_18)
		return;
	char *p = (char *)m_00 + 0xF0;
	m_18 = p;
	void *q = *(void **)p;
	m_1C = q;
	if (q)
		((void **)q)[6] = &m_1C;
	m_00->m_F0 = (Rva009F2BA0Node *)this;
}

// 0x009F2BD0: unreferenced, after int3 padding: hands the second word to the
// matched PartitionManagerImpl::bfmeDropYQ (0x009F5170) on the manager in the
// first. Address-derived names.
class BfmeThingYQ;
class PartitionManagerImpl
{
public:
	void bfmeDropYQ(BfmeThingYQ *thing);
};

class Rva009F2BD0Link
{
	PartitionManagerImpl *m_manager;
	BfmeThingYQ *m_thing;

public:
	void run();
};

void Rva009F2BD0Link::run()
{
	m_manager->bfmeDropYQ(m_thing);
}
