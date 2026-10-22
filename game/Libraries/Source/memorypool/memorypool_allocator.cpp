// Address-derived identity; this is the block-integrity helper called by
// MemoryPool::_VerifyIntegrity at 0x00882D50.
// cl: /O2 /DNDEBUG /MD /Oa

unsigned char bfmeAllSame(
	const unsigned int *data, unsigned int value, unsigned int bytes);
extern "C" void * __cdecl memcpy(void *, const void *, unsigned int);
#pragma intrinsic(memcpy)

// Retail 0x008823E0 (70 B): fill with a repeated dword, finishing a tail of
// fewer than four bytes from the value's own bytes.
void memset32(void *ptr, int value, unsigned int bytesToFill)
{
	int *p = (int *)ptr;
	for (; bytesToFill > 3; bytesToFill -= 4)
		*p++ = value;

	if (bytesToFill != 0)
		memcpy(p, &value, bytesToFill);
}
// Retail check (RVA 0x00882580, 174 bytes) reads these as two dwords
// at VA 0x0130EA00/0x0130EA04 and one byte at VA 0x0130E9F9.
// All three scalars are initially zero in retail .data. The guard-word count
// is file-static: _Allocate (0x00882960) loads it ahead of two unrelated
// stores, which MSVC only does for a datum nothing outside the TU can alias,
// so it has no data row; the other two keep theirs in data_rows.csv.
static int Rva0130EA00GuardWords = 0;
unsigned int g_rva0130EA04 = 0;
unsigned char g_rva0130E9F9 = 0;

class Rva008838F0Owner
{
public:
	void rva008836F0(void *block, char *diagnostic, unsigned int limit);
};
extern Rva008838F0Owner g_bfmeRva0130EA10Owner;

class Rva00882580Block
{
public:
	unsigned char check(void);
	void setUsed(int used);
	void *guardStart(void);
	void rva008824E0(unsigned int size);
private:
	void *m_field00;
	void *m_field04;
	unsigned int m_size08;
};

unsigned char Rva00882580Block::check(void)
{
	char diagnostic[0x1000];
	unsigned char good = 1;
	unsigned int guardWords = Rva0130EA00GuardWords;

	if (guardWords != 0)
	{
		unsigned int guardBytes = guardWords * 4;
		if (bfmeAllSame(
			(const unsigned int *)((unsigned int)this - guardBytes),
			0x0BADF00D, guardBytes) == 0)
			good = 0;
		if (bfmeAllSame(
			(const unsigned int *)((unsigned int)this + m_size08 + 0x0c),
			0x0BADF00D, guardBytes) == 0)
			good = 0;
	}

	if (m_field00 == 0 && *(volatile unsigned int *)&g_rva0130EA04 != 0)
	{
		if (bfmeAllSame(
			(const unsigned int *)((unsigned int)this + 0x0c),
			0xDEADC0DE, m_size08) == 0)
			goto report;
	}

	if (good != 0)
		return 1;

report:
	if (*(volatile unsigned char *)&g_rva0130E9F9 != 0)
		g_bfmeRva0130EA10Owner.rva008836F0(
			(unsigned char *)this + 0x0c, diagnostic, 0x1000);
	return 1;
}

// Retail 0x008824E0 (104 bytes, __thiscall, ret 4): reset a block header to
// an unused block of `size` payload bytes, refill both guard bands and, when
// free-poisoning is on, poison the payload. Address-derived name.
void Rva00882580Block::rva008824E0(unsigned int size)
{
	m_field00 = 0;
	m_size08 = size;
	if (Rva0130EA00GuardWords != 0)
	{
		unsigned int guardBytes = Rva0130EA00GuardWords * 4;
		memset32((char *)this - guardBytes, 0x0BADF00D, guardBytes);
		memset32((char *)this + m_size08 + 0x0c, 0x0BADF00D, guardBytes);
	}
	if (g_rva0130EA04 != 0)
		memset32((char *)this + 0x0c, 0xDEADC0DE, m_size08);
}

void Rva00882580Block::setUsed(int used)
{
	m_size08 = used;
	if (Rva0130EA00GuardWords)
		memset32((char *)this + used + 0x0c, 0x0BADF00D, Rva0130EA00GuardWords * 4);
}

void *Rva00882580Block::guardStart(void)
{
	return (char *)this - Rva0130EA00GuardWords * 4;
}

struct Rva00882BA0Block {
    Rva00882BA0Block **m_field00;
    Rva00882BA0Block *m_field04;
    unsigned int m_size08;
};
extern "C" __declspec(dllimport) void *__stdcall HeapAlloc(void *, unsigned long, unsigned int);
extern "C" __declspec(dllimport) void *__stdcall HeapCreate(unsigned long, unsigned long, unsigned long);
extern "C" __declspec(dllimport) int __stdcall HeapSetInformation(void *, int, void *, unsigned long);
extern "C" __declspec(dllimport) void __stdcall InitializeCriticalSection(void *);
void Rva00105DF0();
extern int g_Va0130E9FC;
extern unsigned int g_Va012D4D10Count;
extern unsigned int *g_Va0130E9F0Buf;
extern void *g_Va0130E9C4;
extern char g_Va0130E9D8[24];
extern Rva00882BA0Block **g_Va0130E9CC;
extern Rva00882BA0Block **g_Va0130E9D4;
extern Rva00882580Block **g_Va0130E9D0;
extern unsigned int *g_Va0130E9BC;
extern unsigned int *g_Va0130E9B8;

// Retail 0x00882630 (415 B): carve `count` fresh blocks of bucket `index`
// from one HeapAlloc, guard-fill both ends, optionally poison the payload and
// push each onto the bucket's free list. _Init and _Allocate pass the count in
// EAX and the bucket on the stack, VC7.1's private convention for a
// file-static callee. It and _Allocate are compiled without /Oa: with it the
// stores through block pointers are assumed not to touch the globals they
// reload.
#pragma optimize("a", off)
static __declspec(noinline) void rva00882630AddBucketBlocks(unsigned int index, unsigned int count)
{
    unsigned int blockSize = (index + 1) * 4;
    unsigned int stride = blockSize + Rva0130EA00GuardWords * 8 + 0xc;
    char *mem = (char *)HeapAlloc(g_Va0130E9C4, 0, stride * count);
    if (count == 0)
        return;
    int guardWords = Rva0130EA00GuardWords;
    char *first = mem + guardWords * 4;
    char *raw = mem;
    for (unsigned int i = 0; i != count; ++i) {
        Rva00882BA0Block *block = (Rva00882BA0Block *)(first + i * stride);
        unsigned int *sizeField = &block->m_size08;
        block->m_field00 = 0;
        *sizeField = blockSize;
        if (guardWords != 0) {
            memset32(raw, 0x0BADF00D, guardWords * 4);
            memset32((char *)(block + 1) + *sizeField, 0x0BADF00D, Rva0130EA00GuardWords * 4);
        }
        if (g_rva0130EA04 != 0)
            memset32(block + 1, 0xDEADC0DE, *sizeField);
        block->m_field04 = (Rva00882BA0Block *)g_Va0130E9D4[index];
        g_Va0130E9D4[index] = block;
        raw += stride;
        guardWords = Rva0130EA00GuardWords;
    }
}

#pragma optimize("", on)

namespace MemoryPool { void _Init(); }
void MemoryPool::_Init()
{
    if (g_Va0130E9FC != 0) {
        ++g_Va0130E9FC;
        return;
    }
    Rva00105DF0();
    ++g_Va0130E9FC;
    InitializeCriticalSection(g_Va0130E9D8);
    unsigned int heapSize = (g_rva0130EA04 + g_Va012D4D10Count * 2) * 4;
    if (g_Va0130E9F0Buf != 0) {
        for (unsigned int i = 0; i < g_Va012D4D10Count; ++i)
            heapSize += g_Va0130E9F0Buf[i] * ((i + 1) * 4 + Rva0130EA00GuardWords * 8 + 0xc);
    }
    g_Va0130E9C4 = HeapCreate(5, heapSize, 0);
    unsigned long lowFragmentation = 2;
    HeapSetInformation(g_Va0130E9C4, 0, &lowFragmentation, 4);
    g_Va0130E9D4 = (Rva00882BA0Block **)HeapAlloc(g_Va0130E9C4, 8, g_Va012D4D10Count * 4);
    g_Va0130E9D0 = (Rva00882580Block **)HeapAlloc(g_Va0130E9C4, 8, g_Va012D4D10Count * 4);
    g_Va0130E9CC = (Rva00882BA0Block **)HeapAlloc(g_Va0130E9C4, 8, g_rva0130EA04 * 4);
    g_Va0130E9BC = (unsigned int *)HeapAlloc(g_Va0130E9C4, 8, g_Va012D4D10Count * 4);
    g_Va0130E9B8 = (unsigned int *)HeapAlloc(g_Va0130E9C4, 8, g_Va012D4D10Count * 4);
    if (g_Va0130E9F0Buf != 0) {
        for (unsigned int i = 0; i < g_Va012D4D10Count; ++i) {
            if (g_Va0130E9F0Buf[i] != 0)
                rva00882630AddBucketBlocks(i, g_Va0130E9F0Buf[i]);
        }
    }
}

namespace MemoryPool
{
	enum AllocType
	{
		ALLOC_NORMAL = 0,
		ALLOC_PERMANENT
	};
	void *_Allocate(unsigned int size, AllocType type);
}

extern "C" __declspec(dllimport) void __stdcall EnterCriticalSection(void *);
extern "C" __declspec(dllimport) void __stdcall LeaveCriticalSection(void *);
extern "C" void * __cdecl memset(void *, int, unsigned int);
#pragma intrinsic(memset)
// Retail 0x008833C0 (still a dump): __cdecl, owner first, five stack
// arguments, records an allocation with the heap tracker.
void rva008833C0(Rva008838F0Owner *owner, int type, void *block, unsigned int size, const char *info);
// The dump's placeholder name is decorated void(void), so it cannot spell the
// five-argument ABI. The pin and that copy both resolve to retail 0x008833C0.
#pragma comment(linker, "/alternatename:?rva008833C0@@YAXPAVRva008838F0Owner@@HPAXIPBD@Z=?d_008833c0@@YAXXZ")
extern unsigned int g_Va0130E9F4;
extern unsigned int g_Va0130E9C0;
extern unsigned char g_Va0130E9F8;

#pragma optimize("a", off)
// Retail 0x00882960 (433 B), export ordinal 1361. Sizes up to the bucket
// limit come off the bucket's free list (refilled 16K at a time by
// rva00882630AddBucketBlocks) onto its used list; larger ones go straight to
// HeapAlloc with a size word in front.
void *MemoryPool::_Allocate(unsigned int size, MemoryPool::AllocType type)
{
    if (size == 0)
        return 0;
    if (size > 0x10000000)
        return 0;

    g_Va0130E9F4 += size;
    if (g_Va0130E9F4 > g_Va0130E9C0)
        g_Va0130E9C0 = g_Va0130E9F4;

    if (size > g_Va012D4D10Count * 4) {
        EnterCriticalSection(g_Va0130E9D8);
        unsigned int *large = (unsigned int *)HeapAlloc(g_Va0130E9C4, g_Va0130E9F8 ? 8 : 0, size + 4);
        *large = size;
        LeaveCriticalSection(g_Va0130E9D8);
        if (g_rva0130E9F9)
            rva008833C0(&g_bfmeRva0130EA10Owner, type, large + 1, size, 0);
        return large + 1;
    }

    unsigned int index = (size - 1) >> 2;
    EnterCriticalSection(g_Va0130E9D8);
    ++g_Va0130E9BC[index];
    if (g_Va0130E9BC[index] > g_Va0130E9B8[index])
        g_Va0130E9B8[index] = g_Va0130E9BC[index];
    if (g_Va0130E9D4[index] == 0)
        rva00882630AddBucketBlocks(index, 0x4000 / (index * 4 + 4));

    Rva00882BA0Block *block = g_Va0130E9D4[index];
    g_Va0130E9D4[index] = block->m_field04;
    block->m_field04 = ((Rva00882BA0Block **)g_Va0130E9D0)[index];
    if (((Rva00882BA0Block **)g_Va0130E9D0)[index])
        ((Rva00882BA0Block **)g_Va0130E9D0)[index]->m_field00 = &block->m_field04;
    block->m_field00 = &((Rva00882BA0Block **)g_Va0130E9D0)[index];
    ((Rva00882BA0Block **)g_Va0130E9D0)[index] = block;
    block->m_size08 = size;
    int guardWords = Rva0130EA00GuardWords;
    if (guardWords != 0)
        memset32((char *)(block + 1) + size, 0x0BADF00D, guardWords * 4);
    if (g_Va0130E9F8)
        memset(block + 1, 0, size);
    LeaveCriticalSection(g_Va0130E9D8);
    if (g_rva0130E9F9)
        rva008833C0(&g_bfmeRva0130EA10Owner, type, block + 1, size, 0);
    return block + 1;
}
#pragma optimize("", on)
