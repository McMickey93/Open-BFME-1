// cl: /O2 /DNDEBUG /MD /EHsc
// Open-BFME5 conversions.

extern "C" unsigned strlen(const char *s);
extern "C" void *memcpy(void *d, const void *s, unsigned n);
#pragma intrinsic(strlen)
#pragma intrinsic(memcpy)

struct BfmeHdrVKI
{
	unsigned short m_bfme00;
	unsigned short m_bfme02;
	unsigned short m_bfme04;
	unsigned short m_bfme06;
};

typedef void *(__cdecl *BfmeAllocFnVKI)(unsigned n);

// Retail 0x01337A30 is the Apt allocator pair defined once as
// g_rva01337A30AllocPair (data_rows.csv, game/Libraries/Source/Apt/Apt.cpp);
// its first slot is the allocate function this body calls.
struct BfmeStringPool3AF0 { void *m_unused; void (__cdecl *free)(void *); };
extern BfmeStringPool3AF0 *g_rva01337A30AllocPair;
// The shared empty EA string block at 0x012D5298 is defined once, as
// EAStringC::StringDataC, in game/GameEngine/Source/Common/Data/Rva012D5298.cpp;
// this TU keeps its own local view of the block and casts at each use.
class Rva8CD130String;
class EAStringC
{
public:
	class StringDataC;
private:
	enum CBPushZero { CB_NO_PUSH_ZERO, CB_PUSH_ZERO };
	void ChangeBuffer(unsigned, unsigned, unsigned, CBPushZero, unsigned);
	friend class Rva8CD130String;
};
extern EAStringC::StringDataC g_rva012D5298Empty;

class BfmeStrVKI
{
public:
	__declspec(noinline) void bfmeSetVKI(const char *s);
	BfmeStrVKI &assignRva00891B50(const char *s);
	BfmeHdrVKI *m_bfme00;
};

void BfmeStrVKI::bfmeSetVKI(const char *s)
{
	if (*s == 0)
	{
		m_bfme00 = (BfmeHdrVKI *)&g_rva012D5298Empty;
		++((BfmeHdrVKI *)&g_rva012D5298Empty)->m_bfme00;
		return;
	}
	int len = strlen(s);
	unsigned sz = (len + 0xc) & ~3;
	m_bfme00 = (BfmeHdrVKI *)(*(BfmeAllocFnVKI *)g_rva01337A30AllocPair)(sz);
	m_bfme00->m_bfme00 = 1;
	m_bfme00->m_bfme04 = (unsigned short)(sz - 9);
	m_bfme00->m_bfme02 = (unsigned short)len;
	m_bfme00->m_bfme06 = 0;
	memcpy((char *)m_bfme00 + 8, s, len + 1);
}

BfmeStrVKI &BfmeStrVKI::assignRva00891B50(const char *s)
{
	bfmeSetVKI(s);
	return *this;
}

struct BfmeStringData3AF0 { unsigned short m_refCount, m_length, m_capacity, m_unknown06; };
template<class T> class StringBase
{
protected:
    BfmeStringData3AF0 *m_data;
    StringBase(const char *text) { ((BfmeStrVKI *)this)->bfmeSetVKI(text); }
    ~StringBase()
    {
        BfmeStringData3AF0 *old = m_data;
        if (--old->m_refCount == 0) g_rva01337A30AllocPair->free(old);
    }
};
class Rva8CD130String : private StringBase<char>
{
public:
    Rva8CD130String(const char *text) : StringBase<char>(text) {}
    ~Rva8CD130String() {}
    Rva8CD130String &operator=(const Rva8CD130String &other)
    {
        ++other.m_data->m_refCount;
        BfmeStringData3AF0 *old = m_data;
        if (--old->m_refCount == 0) g_rva01337A30AllocPair->free(old);
        m_data = other.m_data;
        return *this;
    }
    Rva8CD130String &rva0089EA60Append(const char *text);
};

// Open BFME 2: Code/Libraries/Source/EA/Apt/AptString/EAStringCRefCount.cpp.
Rva8CD130String &Rva8CD130String::rva0089EA60Append(const char *text)
{
    unsigned oldSize = m_data->m_length;
    if (oldSize == 0)
    {
        Rva8CD130String tmp(text);
        operator=(tmp);
        return *this;
    }
    unsigned len = strlen(text);
    if (len == 0) return *this;
    unsigned newSize = oldSize + len;
    ((EAStringC *)this)->ChangeBuffer(newSize, 0, oldSize, EAStringC::CB_NO_PUSH_ZERO, newSize);
    memcpy((char *)m_data + sizeof(BfmeStringData3AF0) + oldSize, text, len + 1);
    return *this;
}

// Retail 0x008922C0: unreferenced cdecl body after int3 padding. It builds an
// EA string from the object's slot 0x40 text in the dead second-argument
// home, runs slot 0x44, and enters string and object into the table at
// g_bfmeMap1024+8 (BfmeConv1024.cpp's view; 0x0089D890). Address-derived
// names; identity unproven.
class Rva008922C0Object
{
public:
	virtual void spare00(void) = 0;
	virtual void spare01(void) = 0;
	virtual void spare02(void) = 0;
	virtual void spare03(void) = 0;
	virtual void spare04(void) = 0;
	virtual void spare05(void) = 0;
	virtual void spare06(void) = 0;
	virtual void spare07(void) = 0;
	virtual void spare08(void) = 0;
	virtual void spare09(void) = 0;
	virtual void spare10(void) = 0;
	virtual void spare11(void) = 0;
	virtual void spare12(void) = 0;
	virtual void spare13(void) = 0;
	virtual void spare14(void) = 0;
	virtual void spare15(void) = 0;
	virtual const char *text40(void) = 0;
	virtual void touch44(void) = 0;
};

class BfmeTab1024
{
public:
	void bfmeAdd1024(int k, int v);
};

struct BfmeMap1024
{
	char m_bfmePad[8];
	BfmeTab1024 m_bfmeTab;
};

extern BfmeMap1024 *g_bfmeMap1024;

void rva008922C0Register(Rva008922C0Object *object, int unused)
{
	Rva8CD130String name(object->text40());
	object->touch44();
	g_bfmeMap1024->m_bfmeTab.bfmeAdd1024((int)&name, (int)object);
}

// Retail 0x00891C60: unreferenced thiscall void body after int3 padding (no
// this in eax, so not a constructor): the string is pointed at the shared
// empty EA string block, whose 16-bit reference count it bumps.
// Address-derived name; identity unproven.
class Rva00891C60String
{
public:
	void setEmpty();
	BfmeHdrVKI *m_data;
};

void Rva00891C60String::setEmpty()
{
	m_data = (BfmeHdrVKI *)&g_rva012D5298Empty;
	++((BfmeHdrVKI *)&g_rva012D5298Empty)->m_bfme00;
}
