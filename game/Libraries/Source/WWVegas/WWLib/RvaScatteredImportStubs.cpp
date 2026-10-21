// cl: /O2 /MD
// Six-byte FF 25 [IAT] import stubs from scattered single import stubs that no row claimed.
// Retail links several copies of some stubs, so each keeps an address-derived
// name, as the matched _mbslen stub at 0x009F7262 does. stdcall stubs take
// the argument bytes their Platform SDK import decoration states; the cdecl
// CRT stubs never touch their arguments. A tail call is exactly `jmp [slot]`.

extern "C" __declspec(dllimport) int __stdcall Sleep(int);
extern "C" __declspec(dllimport) int __cdecl _strcmpi(void);
extern "C" __declspec(dllimport) int __cdecl _wcsicmp(void);
extern "C" __declspec(dllimport) int __cdecl memmove(void);

int __stdcall Rva007E9BB0Sleep(int a0) { return Sleep(a0); }
int Rva00863270_strcmpi(void) { return _strcmpi(); }
int Rva00871710_strcmpi(void) { return _strcmpi(); }
int Rva00871790_strcmpi(void) { return _strcmpi(); }
int Rva009A5960memmove(void) { return memmove(); }
int Rva00B0288C_strcmpi(void) { return _strcmpi(); }
int Rva00B02892_wcsicmp(void) { return _wcsicmp(); }
