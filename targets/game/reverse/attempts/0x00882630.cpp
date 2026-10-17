// ?rva00882630AddBucketBlocks@@YAXII@Z
// partial score=1.0 date=2026-10-17

namespace MemoryPool {

enum AllocType {
    ALLOC_NORMAL = 0,
    ALLOC_PERMANENT
};

void _Exit();
unsigned int _GetBlockSize(void *block);
bool _IsValidBlock(void *block);
void *_Allocate(unsigned int size, AllocType type);
void _Free(void *ptr, AllocType type);
void *_Reallocate(void *ptr, unsigned int size, AllocType type);
void _Init();
void _VerifyIntegrity();

}

#include <string.h>

// `namespace MemoryPool` is retail's own name: the eight `_`-prefixed entry
// points in this file are exported under it (targets/game/reverse/exports.csv ordinals
// 1361-1368, mangled as free functions with an enum AllocType in that scope).
// It is not Zero Hour's `class MemoryPool` (GameMemory.h:280); the two never
// share a TU.
//
// The game does not link these entry points directly. d_00882e10 (0x00882E10,
// still a gen-dump) resolves each export by name at startup into a .bss pointer
// table, and every caller -- global operator new/delete in WWLib/mem_ops.cpp,
// _Reallocate below -- goes through that table, which is why the call sites
// are DIR32 slots rather than REL32 calls. symbols.csv pins two of the slots:
// __gameMemAllocPtr (0x0130E9B4 -> _Allocate) and __gameMemFreePtr
// (0x0130E9AC -> _Free); the block-size slot (0x0130E9B0 -> _GetBlockSize)
// keeps the resolver's address name. The table is defined once, in
// Rva00882E10ResolveMemoryPoolExports.cpp.
extern "C" void *(__cdecl *__gameMemAllocPtr)(unsigned int, int);
extern "C" void (__cdecl *__gameMemFreePtr)(void *, int);
extern "C" unsigned int (__cdecl *g_rva0130E9B0)(void *);

// BFME's heap verifier is a separate owner object, not the Zero Hour
// MemoryPool class.  The validation entry point below calls its already
// matched helper through the fixed global object at 0x0130EA10.
class Rva008838F0Owner
{
public:
	bool isValidBlock(int type, void *block);
};
extern Rva008838F0Owner g_bfmeRva0130EA10Owner;
extern unsigned char g_rva0130E9F9;

#pragma intrinsic(memcpy, memset)

void memset32(void *ptr, int value, unsigned int bytesToFill)
{
	int *p = (int *)ptr;
	for (; bytesToFill > 3; bytesToFill -= 4)
		*p++ = value;

	if (bytesToFill != 0)
		memcpy(p, &value, bytesToFill);
}


static int g_refCount;

void MemoryPool::_Exit()
{
    --g_refCount;
}

unsigned int MemoryPool::_GetBlockSize(void *block)
{
    if (block == 0) {
        return 0;
    }

    return ((unsigned int *)block)[-1];
}

bool MemoryPool::_IsValidBlock(void *block)
{
	if (block == 0)
		return false;

	if (g_rva0130E9F9 != 0)
		return g_bfmeRva0130EA10Owner.isValidBlock(-1, block);

	return true;
}

// Block header shared with MemoryPool::_Free (0x00882BA0): the used-list
// back link, the list link, and the payload size; payload follows at +0xc.
struct Rva00882BA0Block {
    Rva00882BA0Block **m_field00;
    Rva00882BA0Block *m_field04;
    unsigned int m_size08;
};
extern "C" __declspec(dllimport) void __stdcall EnterCriticalSection(void *);
extern "C" __declspec(dllimport) void __stdcall LeaveCriticalSection(void *);
extern "C" __declspec(dllimport) void *__stdcall HeapAlloc(void *, unsigned long, unsigned int);
// Retail 0x008833C0 (still a dump): __cdecl, owner first, five stack
// arguments, records an allocation with the heap tracker.
void rva008833C0(Rva008838F0Owner *owner, int type, void *block, unsigned int size, const char *info);
static int Rva0130EA00GuardWords;
extern unsigned int g_rva0130EA04;
extern unsigned int g_Va012D4D10Count;
extern unsigned char g_Va0130E9F8;
extern unsigned int g_Va0130E9F4;
extern unsigned int g_Va0130E9C0;
extern void *g_Va0130E9C4;
extern char g_Va0130E9D8[24];
extern unsigned int *g_Va0130E9BC;
extern unsigned int *g_Va0130E9B8;
extern Rva00882BA0Block **g_Va0130E9D4;
class Rva00882580Block;
extern Rva00882580Block **g_Va0130E9D0;

// Retail 0x00882630, 415 bytes: carve `count` fresh blocks of bucket `index`
// from one HeapAlloc, guard-fill both ends, optionally poison the payload,
// and push each onto the bucket's free list. Its callers (_Init 0x008827D0
// and _Allocate below) pass the count in EAX and the bucket on the stack:
// VC7.1's private convention for a file-static callee.
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
        block->m_field04 = g_Va0130E9D4[index];
        g_Va0130E9D4[index] = block;
        raw += stride;
        guardWords = Rva0130EA00GuardWords;
    }
}

// Retail export ordinal 1361.
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



void *MemoryPool::_Reallocate(void *ptr, unsigned int size, MemoryPool::AllocType type)
{
    void *newPtr = size ? __gameMemAllocPtr(size, type) : 0;
    unsigned int oldSize = ptr ? g_rva0130E9B0(ptr) : 0;
    if (size != 0 && oldSize != 0) {
        memcpy(newPtr, ptr, size < oldSize ? size : oldSize);
    }
    if (ptr != 0) {
        __gameMemFreePtr(ptr, type);
    }
    return newPtr;
}

// The old _Init lift omitted its loop branch and epilogue. See
// identity_evidence/008827d0-incomplete-initializer.md; native recovery is open.

// Retail export 0x00882D50, full 187-byte extent through the final ret.
// Three walks over the allocator's block tables; +4 links and +0xc payload
// agree with the landed Rva00882580Block::check helper.
class Rva00882580Block
{
public:
    unsigned char check();
};
extern unsigned int g_Va012D4D10Count;
struct Rva00882BA0Block;
// Retail's three block-table pointers are initially zero-filled.
Rva00882BA0Block **g_Va0130E9CC = 0;
Rva00882BA0Block **g_Va0130E9D4 = 0;
Rva00882580Block **g_Va0130E9D0 = 0;
extern unsigned int g_rva0130EA04;

void MemoryPool::_VerifyIntegrity()
{
    unsigned int i;
    for (i = 0; i < g_Va012D4D10Count; ++i) {
        Rva00882580Block *block = g_Va0130E9D0[i];
        while (block) {
            block->check();
            if (g_rva0130E9F9)
                g_bfmeRva0130EA10Owner.isValidBlock(-1, (char *)block + 0x0c);
            block = *(Rva00882580Block **)((char *)block + 4);
        }
    }
    unsigned int count = g_rva0130EA04;
    if (count) {
        for (unsigned int j = 0; j < count; ++j) {
            Rva00882580Block *block = (Rva00882580Block *)g_Va0130E9CC[j];
            if (block) {
                block->check();
                count = g_rva0130EA04;
            }
        }
    }
    for (i = 0; i < g_Va012D4D10Count; ++i) {
        Rva00882580Block *block = (Rva00882580Block *)g_Va0130E9D4[i];
        while (block) {
            block->check();
            block = *(Rva00882580Block **)((char *)block + 4);
        }
    }
}
