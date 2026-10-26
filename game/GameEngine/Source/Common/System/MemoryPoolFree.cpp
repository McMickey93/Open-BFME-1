// Identity: retail export ordinal 1363 names MemoryPool::_Free at RVA 00882BA0.
// The 12-byte block links and size are witnessed by this body and allocator siblings.
// The tracker callee is the landed Rva008838F0Owner::rva008839B0.
// cl: /O2 /DNDEBUG /MD
#include "memory_pool.h"
extern "C" __declspec(dllimport) void __stdcall EnterCriticalSection(void *);
extern "C" __declspec(dllimport) void __stdcall LeaveCriticalSection(void *);
extern "C" __declspec(dllimport) int __stdcall HeapFree(void *, unsigned long, void *);
void memset32(void *, int, unsigned int);
class Rva008838F0Owner { public: void rva008839B0(int, void *); };
struct Rva00882BA0Block {
    Rva00882BA0Block **m_field00;
    Rva00882BA0Block *m_field04;
    unsigned int m_size08;
};
extern Rva008838F0Owner g_bfmeRva0130EA10Owner;
extern unsigned char g_rva0130E9F9;
extern unsigned int g_Va012D4D10Count;
extern unsigned int g_rva0130EA04;
int g_Va0130E9FC;
unsigned int g_Va0130E9F4;
void *g_Va0130E9C4;
char g_Va0130E9D8[24];
// Retail _Init (0x008827D0+0x12F) stores its bucket-array allocation here.
// The four-byte pointer is initially zero in retail .data.
unsigned int *g_Va0130E9B8;
unsigned int *g_Va0130E9BC;
// Retail _Allocate (0x00882960) raises this to the running byte total g_Va0130E9F4.
unsigned int g_Va0130E9C0;
// Byte flag _Allocate turns into HeapAlloc flags 8; Rva00882F20/F30SetFlag set and clear it.
unsigned char g_Va0130E9F8;
unsigned int g_Va0130EA08, g_Va0130E9C8;
unsigned int g_Va012D4D0C = 0x1000;
extern Rva00882BA0Block **g_Va0130E9CC, **g_Va0130E9D4;
void MemoryPool::_Free(void *ptr, AllocType type)
{
    if (!ptr || !g_Va0130E9FC) return;
    unsigned int *large = (unsigned int *)ptr - 1;
    unsigned int size = *large;
    g_Va0130E9F4 -= size;
    if (size > g_Va012D4D10Count * 4) {
        if (g_rva0130E9F9) g_bfmeRva0130EA10Owner.rva008839B0(type, ptr);
        EnterCriticalSection(g_Va0130E9D8);
        HeapFree(g_Va0130E9C4, 0, large);
        LeaveCriticalSection(g_Va0130E9D8);
        return;
    }
    Rva00882BA0Block *block = (Rva00882BA0Block *)ptr - 1;
    --g_Va0130E9BC[(block->m_size08 - 1) >> 2];
    if (g_rva0130E9F9) g_bfmeRva0130EA10Owner.rva008839B0(-666, block + 1);
    EnterCriticalSection(g_Va0130E9D8);
    *block->m_field00 = block->m_field04;
    if (block->m_field04) block->m_field04->m_field00 = block->m_field00;
    unsigned int count = g_rva0130EA04;
    block->m_field00 = 0;
    if (count) {
        memset32(block + 1, 0xDEADC0DE, size);
        if (size >= g_Va0130EA08 && size <= g_Va012D4D0C) {
            Rva00882BA0Block *old = g_Va0130E9CC[g_Va0130E9C8];
            g_Va0130E9CC[g_Va0130E9C8] = block;
            block = old;
            if (++g_Va0130E9C8 == count) g_Va0130E9C8 = 0;
            if (!block) { LeaveCriticalSection(g_Va0130E9D8); return; }
        }
    }
    unsigned int index = (block->m_size08 - 1) >> 2;
    block->m_field04 = g_Va0130E9D4[index];
    g_Va0130E9D4[index] = block;
    LeaveCriticalSection(g_Va0130E9D8);
}


// 0x00882F90: unreferenced cdecl setter after int3 padding that stores its
// three arguments into the delayed-free ring's slot count and the size
// bounds _Free reads above. Address-derived name.
void Rva00882F90SetDelayedFree(unsigned int count, unsigned int low, unsigned int high)
{
    g_rva0130EA04 = count;
    g_Va0130EA08 = low;
    g_Va012D4D0C = high;
}

// 0x008830A0: unreferenced getter after int3 padding for the running byte
// total g_Va0130E9F4 that _Allocate maintains. Address-derived name.
unsigned int Rva008830A0GetTotal()
{
    return g_Va0130E9F4;
}
