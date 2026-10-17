// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc

struct Rva00891B80Block
{
	unsigned short m_ref;
};

class EAStringC { public: class StringDataC; };
extern EAStringC::StringDataC g_rva012D5298Empty;	// shared empty string block 0x012D5298

struct Rva00891B80Pool
{
	void *m_unused;
	void (__cdecl *free)(void *);
};

struct BfmeStringPool3AF0;
extern BfmeStringPool3AF0 *g_rva01337A30AllocPair;
extern void *(*Rva008C5D70Alloc)(unsigned int bytes);

class BfmeUtf8String008A01F0
{
public:
	BfmeUtf8String008A01F0()
	{
		m_block = (Rva00891B80Block *)&g_rva012D5298Empty;
		++(*(Rva00891B80Block *)&g_rva012D5298Empty).m_ref;
	}

	~BfmeUtf8String008A01F0()
	{
		Rva00891B80Block *block = m_block;
		if (--block->m_ref == 0)
			(*(Rva00891B80Pool **)&g_rva01337A30AllocPair)->free(block);
	}

	BfmeUtf8String008A01F0 &map();

	Rva00891B80Block *m_block;
};

class BfmeStrVKK
{
public:
	void bfmeTruncVKK(unsigned n);
};

struct BfmeStr1233
{
	Rva00891B80Block *m_block;
};

class BfmeE1233
{
public:
	void bfmeName1233(BfmeStr1233 *a);
};

class Rva008A9B00
{
public:
	Rva008A9B00();
    static void operator delete(void *, unsigned);

	void *operator new(unsigned int bytes)
	{
		return Rva008C5D70Alloc(bytes);
	}

	__forceinline void clearRegistered()
	{
		m_flags &= ~0x40000000;
	}

	void *m_vptr;
	unsigned m_flags;
	Rva00891B80Block *m_block;
	Rva008A9B00 *m_next;
};

struct BfmeRegistryKind1
{
	int m_capacity;
	int m_count;
	void **m_entries;

	__forceinline void addOrClear(Rva008A9B00 *obj)
	{
		int index = m_count;
		int *pcount = &m_count;
		int cap = m_capacity;
		if (index >= cap)
		{
			obj->clearRegistered();
			return;
		}

		m_entries[index] = obj;
		++*pcount;
	}
};

struct Rva00899560Pool;
extern Rva00899560Pool *g_rva01337810GcRoots;

// The Apt global node free list at 0x01338478, defined once by
// game/GameEngine/Source/Common/Data/Rva01338478.cpp.  This body keeps its own
// view of a node (Rva008A9B00) and reaches the next link through it.
struct Rva008C3B60Node;
extern Rva008C3B60Node *g_rva01338478NodeHead;
static __forceinline Rva008A9B00 *&rva01338478FreeHead() {
    return *(Rva008A9B00 **)&g_rva01338478NodeHead;
}


class Rva8CD130String;
class Rva8CD130Value { public: void getName(Rva8CD130String *); };
class BfmeString1284;
// The calls at 0x8B9594 (this row) and 0x8B9498
// (game/GameEngine/Source/Common/BfmeStringWriter1284.cpp) reach retail
// 0x008B8E70, whose ledger row is the matched gen dump ?d_008b8e70@@YAXXZ
// (game/gen_asm/d_00882630.asm), as tools/callees.py 0x8b94f0 431 prints for
// the callee.  Nothing defines a member named bfmeBuildString1284, so the calls
// name the dump through the raw pointer bridge; the bridge sits at the call
// site rather than in a member, because a body emitted under the pinned
// placeholder name would be judged against retail's 267-byte body at
// 0x008B8E70 and charged as a comdat loser.
void d_008b8e70();
class BfmeStringWriter1284 {};
class Value008B94F0 {
public:
    void *vptr;
    unsigned flags;
    unsigned char isType(unsigned char t) const { unsigned f=flags; return (f & 0x3f)==t && !((unsigned char)(~(f>>15)) & 1); }
};
struct Rva008AE770Stack { int m_count; };
extern Rva008AE770Stack Rva008AE770TheStack;
class AptValue;
extern AptValue *g_bfmeFallbackDB;
void *joinArray008B94F0(Value008B94F0 *src, int count)
{
    if (src->isType(0x16)) {
        BfmeUtf8String008A01F0 output;
        BfmeUtf8String008A01F0 separator;
        union
        {
            void (*raw)(void);
            void (BfmeStringWriter1284::*typed)(BfmeString1284 *, int);
        } buildString;
        buildString.raw = &d_008b8e70;
        if (count>0) {
            Rva8CD130Value *arg=(*(Rva8CD130Value ***)((char *)&Rva008AE770TheStack + 8))[Rva008AE770TheStack.m_count-1]; arg->getName((Rva8CD130String *)&separator);
            (((BfmeStringWriter1284 *)src)->*buildString.typed)((BfmeString1284 *)&output,(int)((char *)separator.m_block+8));
        } else {
            (((BfmeStringWriter1284 *)src)->*buildString.typed)((BfmeString1284 *)&output,(int)",");
        }
        Rva008A9B00 *obj = rva01338478FreeHead();
        if (obj) {
            rva01338478FreeHead() = obj->m_next;
            ((BfmeRegistryKind1 *)g_rva01337810GcRoots)->addOrClear(obj);
            if (obj->m_block != (Rva00891B80Block *)&g_rva012D5298Empty)
                ((BfmeStrVKK *)&obj->m_block)->bfmeTruncVKK(0);
        } else {
            Rva008A9B00 *fresh = new Rva008A9B00();
            obj = fresh;
        }
        ++output.m_block->m_ref;
        Rva00891B80Block *old=obj->m_block;
        if (--old->m_ref==0) (*(Rva00891B80Pool **)&g_rva01337A30AllocPair)->free(old);
        obj->m_block=output.m_block;
        return obj;
    }
    return (*(void **)&g_bfmeFallbackDB);
}
