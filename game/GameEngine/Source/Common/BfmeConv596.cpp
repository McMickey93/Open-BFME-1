class BfmeRefCHB;

// retail ILT 0x0003FA7B -> 0x0058C4C0 is the matched ~Rva0058BE30FourString row and
// 0x00881EB0 the matched operator delete
class Rva0058BE30FourString
{
public:
	~Rva0058BE30FourString();
};

class BfmeThingCHB
{
public:
	void bfmeGoCHB(BfmeRefCHB *what);
	BfmeRefCHB *m_bfmeRef;
};


void BfmeThingCHB::bfmeGoCHB(BfmeRefCHB *what)
{
	BfmeRefCHB *cur = m_bfmeRef;
	if (what != cur)
	{
		if (cur != 0)
		{
			((Rva0058BE30FourString *)cur)->~Rva0058BE30FourString();
			operator delete(cur);
		}
		m_bfmeRef = what;
	}
}
