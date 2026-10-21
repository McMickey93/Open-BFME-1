// cl: /O2 /MD
// Address-derived MemoryPool start-up initializer, retail 0x008823C0
// (30 bytes), a dynamic initializer no row claimed. It resolves the
// MemoryPool exports (Rva00882E10ResolveMemoryPoolExports.cpp), registers
// the resolved _Exit with atexit, runs the resolved _Init and tail-calls the
// loader patch 0x008821D0.

#include <stdlib.h>

void rva00882E10ResolveMemoryPoolExports();
void rva008821d0LoaderPatch();

extern "C" {
extern void (__cdecl *g_rva0130E9A4)(void);   // _Exit
extern void (__cdecl *g_rva0130E9A8)(void);   // _Init
}

void Rva008823C0Initialize()
{
	rva00882E10ResolveMemoryPoolExports();
	atexit( g_rva0130E9A4 );
	g_rva0130E9A8();
	rva008821d0LoaderPatch();
}
