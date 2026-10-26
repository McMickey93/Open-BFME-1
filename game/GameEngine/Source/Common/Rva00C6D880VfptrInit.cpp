// cl: /O2 /MD
#include <new>

class Rva00848AB0
{
public:
    Rva00848AB0() throw();
    virtual void slot();
};

// retired debt: ?g_bfmeRva0130BCACStatic@@3VRva00848AB0@@A -> ?TheBfmeObject_00C70C80@@3VGen_00C70C80Target@@A
extern "C" Rva00848AB0 __identifier("?TheBfmeObject_00C70C80@@3VGen_00C70C80Target@@A");
#define g_bfmeRva0130BCACStatic __identifier("?TheBfmeObject_00C70C80@@3VGen_00C70C80Target@@A")
void bfmeForward_00C70C80();
extern "C" int __cdecl atexit(void (__cdecl *callback)());

void bfmeRva00C6D880InitializeVfptr()
{
    new (&g_bfmeRva0130BCACStatic) Rva00848AB0;
    atexit(bfmeForward_00C70C80);
}
