// ?d_00c6b120@@YAXXZ
// partial score=0.0 date=2026-10-16
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Ob0 /D_STLP_USE_STATIC_LIB
// stlport
//
// The registry of live LargeGroupAudioUpdateModuleData objects at VA
// 0x012EFFA0: their matched constructors insert `this` and the destructor
// removes it. Retail's initializer 0x00C6B120 default-constructs it through
// ILT 0x0000B1F9 and registers the cleanup 0x00C6FE10, which tail-jumps to
// the destructor at ILT 0x000390C7; ilt_oracle confirms both ILT names as
// set<LargeGroupAudioUpdateModuleData *>. The other TUs still reach it
// through their LGA_Global stand-in declaration.
#include <set>

class LargeGroupAudioUpdateModuleData;

_STL::set<LargeGroupAudioUpdateModuleData *> g_lgaGlobal;
