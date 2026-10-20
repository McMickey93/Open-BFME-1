// Address-derived identity; this is the block-integrity helper called by
// MemoryPool::_VerifyIntegrity at 0x00882D50.
// cl: /O2 /DNDEBUG /MD /Oa

unsigned char bfmeAllSame(
	const unsigned int *data, unsigned int value, unsigned int bytes);
extern void __cdecl memset32(void *ptr, int value, unsigned int bytesToFill);
// Retail check (RVA 0x00882580, 174 bytes) reads these as two dwords
// at VA 0x0130EA00/0x0130EA04 and one byte at VA 0x0130E9F9.
// All three scalars are initially zero in retail .data; data_rows.csv
// verifies their widths and initial bytes independently of the code match.
int Rva0130EA00GuardWords = 0;
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
	unsigned int guardWords = *(volatile unsigned int *)&Rva0130EA00GuardWords;

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
static void memset32Local(void *ptr, int value, unsigned int bytesToFill)
{
	int *p = (int *)ptr;
	for (; bytesToFill > 3; bytesToFill -= 4)
		*p++ = value;
	if (bytesToFill != 0)
	{
		char *d = (char *)p; const char *s = (const char *)&value;
		for (unsigned int i = 0; i < bytesToFill; ++i) d[i] = s[i];
	}
}
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
            memset32Local(raw, 0x0BADF00D, guardWords * 4);
            memset32Local((char *)(block + 1) + *sizeField, 0x0BADF00D, Rva0130EA00GuardWords * 4);
        }
        if (g_rva0130EA04 != 0)
            memset32Local(block + 1, 0xDEADC0DE, *sizeField);
        block->m_field04 = (Rva00882BA0Block *)g_Va0130E9D4[index];
        g_Va0130E9D4[index] = block;
        raw += stride;
        guardWords = Rva0130EA00GuardWords;
    }
}

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
