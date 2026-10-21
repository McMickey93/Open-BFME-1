// cl: /DNDEBUG /MD /EHa /Oy-
// BFME Debug static bootstrap, retail 0x0088AF20 (59 bytes), a dynamic
// initializer no row claimed. Zero Hour's debug_debug.cpp jams
// Debug::PreStaticInit into .CRT$XCB; BFME instead runs this initializer:
// it sets up the debug critical section (0x01336E60), resolves
// "?PreStaticInit@Debug@@CAPAV1@XZ" by name in the executable so a module
// exporting its own can take over, falls back to the linked PreStaticInit,
// stores the singleton in the shared pointer 0x01336E5C and registers
// Debug::StaticExit with atexit. The initializer's own name is address-derived.

#include <windows.h>
#include <stdlib.h>

struct BfmeCsDWA
{
	CRITICAL_SECTION m_section;
};
extern BfmeCsDWA g_bfmeCsDWC;

// Canonical four-byte pointer cell at retail VA 0x01336E5C.
extern void *g_Rva00F36E5C;

class Debug
{
	static Debug *PreStaticInit();
	static void StaticExit();

	friend void Rva0088AF20Initialize();
};

void Rva0088AF20Initialize()
{
	InitializeCriticalSection( &g_bfmeCsDWC.m_section );
	HMODULE module = GetModuleHandleA( NULL );
	Debug *(*preStaticInit)() = (Debug *(*)())GetProcAddress( module, "?PreStaticInit@Debug@@CAPAV1@XZ" );
	if ( !preStaticInit )
		preStaticInit = Debug::PreStaticInit;
	g_Rva00F36E5C = preStaticInit();
	atexit( Debug::StaticExit );
}
