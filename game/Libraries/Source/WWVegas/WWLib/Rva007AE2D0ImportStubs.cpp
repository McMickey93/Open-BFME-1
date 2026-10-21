// cl: /O2 /MD
// Two six-byte import stubs no row claimed, FF 25 [IAT]: MSVCR71 _mbslen
// (slot 0x0135930C) at 0x007AE2D0 and WINMM timeGetTime (slot 0x01359544)
// at 0x007E4810. Retail carries several copies of each stub, so they keep
// address-derived names, as the matched _mbslen stub at 0x009F7262 does.
extern "C" __declspec(dllimport) unsigned int __cdecl _mbslen(const unsigned char *);
extern "C" __declspec(dllimport) unsigned long __stdcall timeGetTime(void);

unsigned int Rva007AE2D0_mbslen(const unsigned char *s) { return _mbslen(s); }
unsigned long __stdcall Rva007E4810timeGetTime(void) { return timeGetTime(); }
