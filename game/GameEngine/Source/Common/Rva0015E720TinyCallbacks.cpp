// cl: /O2 /MD
// Small callbacks no row claimed, each referenced only by the code that
// registers or installs it: constant returns, a store of 0 through the
// matched Rva00892340::store, the AssetManagerImpl worker-thread entry, an
// accessor of +0x14, a setter of +0x5C returning the old value, and a
// forward to virtual slot 2. All keep address-derived names.

class Rva00892340 { public: static void store(int); };
class AssetManagerImpl { public: void ThreadMain(); };

bool Rva0015E720False() { return false; }
int Rva007832A0Zero() { return 0; }
int Rva00783710One() { return 1; }
void Rva00783200Store() { Rva00892340::store(0); }
void Rva009EFBE0ThreadEntry(void *manager) { ((AssetManagerImpl *)manager)->ThreadMain(); }

class Rva0083E910
{
public:
	int get();
	int swap5C(int value);
	char m_pad00[0x14];
	int m_14;
	char m_pad18[0x44];
	int m_5C;
};
int Rva0083E910::get() { return m_14; }
int Rva0083E910::swap5C(int value) { int old = m_5C; m_5C = value; return old; }

class Rva00847D80
{
public:
	virtual void slot0();
	virtual void slot1();
	virtual void slot2();
	void forward();
};
void Rva00847D80::forward() { slot2(); }
