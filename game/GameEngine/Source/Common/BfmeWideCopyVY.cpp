// cl: /DNDEBUG /DWIN32 /MD /EHsc
// Open-BFME5: the wide-text copy constructor at retail 0x0049A070, 87 bytes.
//
// The table store lands between the unwind state and the string copy, not at
// the head of the body, so it is issued from the string member's own
// initializer rather than from the table member's.

extern int g_bfmeVtableVY[];					// retail 0x010EDAD8

class BfmeWideVY
{
public:
	BfmeWideVY(const BfmeWideVY &other);
	~BfmeWideVY(void);

private:
	unsigned short *m_bfmeData;
};

// An empty base with a destructor: it adds no bytes but gives the body the
// unwind frame and state 0 retail carries.
class BfmeGuardVY
{
public:
	~BfmeGuardVY(void);
};

class Gen_0049A070;
class Rva00499F30Result;

__forceinline const BfmeWideVY &bfmeInstallVY(Gen_0049A070 *self,
	const BfmeWideVY &value);

class Gen_0049A070 : public BfmeGuardVY
{
public:
	Gen_0049A070(const Gen_0049A070 &other);
	Rva00499F30Result bfmeDuplicateInto();

	int *m_bfmeVtable;					// +0x00
	BfmeWideVY m_bfmeText;					// +0x04
	int m_bfmeValue;					// +0x08
};

__forceinline const BfmeWideVY &bfmeInstallVY(Gen_0049A070 *self,
	const BfmeWideVY &value)
{
	self->m_bfmeVtable = g_bfmeVtableVY;

	return value;
}


// One-word owning result; 0x00499F30 deletes its pointee through virtual slot0.
class Rva00499F30Pointee { public: virtual ~Rva00499F30Pointee(); };
class Rva00499F30Result {
public:
 Rva00499F30Result(Gen_0049A070 *p) : m_ptr(p) {}
 Rva00499F30Result(Rva00499F30Result &other):m_ptr(other.m_ptr) { other.m_ptr=0; }
 ~Rva00499F30Result() { delete reinterpret_cast<Rva00499F30Pointee *>(m_ptr); }
 Gen_0049A070 *m_ptr;
};
Rva00499F30Result Gen_0049A070::bfmeDuplicateInto()
{
 Rva00499F30Result temp(new Gen_0049A070(*this));
 return temp;
}

// ??0Gen_0049A070@@QAE@ABV0@@Z
Gen_0049A070::Gen_0049A070(const Gen_0049A070 &other)
	: m_bfmeText(bfmeInstallVY(this, other.m_bfmeText)),
	  m_bfmeValue(other.m_bfmeValue)
{
}
