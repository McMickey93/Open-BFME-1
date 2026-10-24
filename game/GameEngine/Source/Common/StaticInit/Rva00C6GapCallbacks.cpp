// cl: /O2 /MD /Igame/Libraries/Source/WWVegas/WWLib
// stlport
#include "ascii_string.h"
#include "unicode_string.h"

// Retail CRT cleanup callbacks. The initializers at 00C6A8F0 and 00C6A910
// register these exact entry points, and their globals occupy 012ED4EC/F0.
extern AsciiString g_rva012ED4EC;
extern AsciiString g_rva012ED4F0;

void Rva00C6FC60Release()
{
    g_rva012ED4EC.~AsciiString();
}

void Rva00C6FC70Release()
{
    g_rva012ED4F0.~AsciiString();
}

// CRT initializer table slot RVA 00EA5E28 points to 00C6E380.
// The registered callback is independently matched at 00C71600.
extern "C" int __cdecl atexit(void (__cdecl *callback)());
void bfmeGoDXE();

void Rva00C6E380Register()
{
    atexit(bfmeGoDXE);
}

// Registered by the push at RVA 0x004555F3 before atexit at 0x004555FB.
// The complete 10-byte callback loads VA 0x012F15CC into ECX and jumps
// through ILT 0x0001F951 to the existing Rva000782A0::invoke body.
// INT3 starts at 0x00C7004A; no semantic owner name is inferred.
class Rva000782A0
{
public:
    void invoke();
};
extern Rva000782A0 g_rva012F15CC;

void Rva00C70040Release()
{
    g_rva012F15CC.invoke();
}

// Registered by the push at RVA 0x0048DE57, followed by the zero store
// constructing this UnicodeString and the atexit call at 0x0048DE6C.
// The callback jumps via ILT 0x0003B304 to its existing destructor;
// INT3 starts at 0x00C700FA, immediately after the 10-byte body.
extern UnicodeString g_rva012F3348;

void Rva00C700F0Release()
{
    g_rva012F3348.~UnicodeString();
}
