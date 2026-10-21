// cl: /O2 /MD
// Two retail dynamic initializers no row claimed, each
// `call [__imp__timeGetTime@0]; mov [global], eax; ret`: the start-up stamp
// of the two Network timers g_012F7718 (Network_init.cpp) and g_012F771C
// (Network_update.cpp). The owning TU of the initializers is unknown, so they
// keep address-derived names.

extern "C" __declspec(dllimport) unsigned long __stdcall timeGetTime(void);

extern unsigned int g_012F7718;
extern unsigned int g_012F771C;

void Rva00C6C420Initialize() { g_012F7718 = timeGetTime(); }
void Rva00C6C430Initialize() { g_012F771C = timeGetTime(); }
