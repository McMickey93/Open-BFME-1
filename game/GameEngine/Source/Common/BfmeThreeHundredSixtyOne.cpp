// Retail table at VA 0x010EE4EC: 1 slots, ending before 0x010EE4F0.
// Keep each witnessed ILT target symbolic so the table relocates with the image.
extern "C" void __identifier("?j_0002c7dc@@YAXXZ")();
extern "C" void *bfmeVftVD[] = {
    reinterpret_cast<void *>(&__identifier("?j_0002c7dc@@YAXXZ")),
};


class BfmeThingVD
{
public:
	void *bfmeKillVD(int flags);
	void *m_bfmeVft;
	void *m_bfmeWhat;
	void **m_bfmeSlot;
};

void *BfmeThingVD::bfmeKillVD(int flags)
{
	void **slot = m_bfmeSlot;
	void *what = m_bfmeWhat;
	m_bfmeVft = bfmeVftVD;
	*slot = what;
	if ((flags & 1) != 0)
		::operator delete(this);
	return this;
}
