// cl: /O2 /MD
// Apt-side callbacks no row claimed, each referenced only by the code that
// registers it. Six return the shared fallback value g_bfmeFallbackDB, two
// return a fresh false/zero value, and one clears its object's first dword. Retail links
// without identical-COMDAT folding, so each is its own body; all keep
// address-derived names.

class AptValue;
class AptBoolean { public: static AptBoolean *Create(bool); };
class AptInteger { public: static AptInteger *Create(int); };

extern AptValue *g_bfmeFallbackDB;

AptValue *Rva00898D10Get() { return g_bfmeFallbackDB; }
AptValue *Rva008A99C0Get() { return g_bfmeFallbackDB; }
AptValue *Rva008B2DB0Get() { return g_bfmeFallbackDB; }
AptValue *Rva008B2DC0Get() { return g_bfmeFallbackDB; }
AptValue *Rva008B2DD0Get() { return g_bfmeFallbackDB; }
AptValue *Rva008B2DE0Get() { return g_bfmeFallbackDB; }
AptValue *Rva008B5760Get() { return g_bfmeFallbackDB; }
AptValue *Rva008B6B10Get() { return g_bfmeFallbackDB; }

AptBoolean *Rva008A52E0Create() { return AptBoolean::Create(false); }
AptInteger *Rva008B6C20Create() { return AptInteger::Create(0); }
// 0x008B6FE0: same shape, the native getter the matched Rva008B73B0Properties
// installs for property 27 (DIR32 0x008B7F54).
AptInteger *Rva008B6FE0Create() { return AptInteger::Create(0); }

struct Rva00892B80
{
	int m_value;
	void rva00892B80();
};
void Rva00892B80::rva00892B80() { m_value = 0; }
