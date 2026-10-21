#include "memory_pool.h"

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

#pragma intrinsic(memcpy)

// memset32 (0x008823E0) lives in memorypool_allocator.cpp with the rest of
// the block code it serves.


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

// _Allocate (0x00882960) is in memorypool_allocator.cpp: it shares the
// file-static guard-word count with the block helpers there.



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
