// Retail table at VA 0x010E1F3C: 1 slots, ending before 0x010E1F40.
// Keep each witnessed ILT target symbolic so the table relocates with the image.
extern "C" void __identifier("?j_0000a0a1@@YAXXZ")();
extern "C" void *bfmeVftVH[] = {
    reinterpret_cast<void *>(&__identifier("?j_0000a0a1@@YAXXZ")),
};


class BfmeSubVH
{
public:
	virtual void bfmeReleaseVH(int what);
};

class BfmeThingVH
{
public:
	void *bfmeKillVH(int flags);
	void *m_bfmeVft;
	BfmeSubVH *m_nextStatus;
};

void *BfmeThingVH::bfmeKillVH(int flags)
{
	BfmeSubVH *sub = m_nextStatus;
	m_bfmeVft = bfmeVftVH;
	if (sub != 0)
		sub->bfmeReleaseVH(1);
	if ((flags & 1) != 0)
		::operator delete(this);
	return this;
}
