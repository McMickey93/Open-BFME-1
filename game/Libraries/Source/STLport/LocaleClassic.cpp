// cl: /O2 /EHsc /MD /D_STLP_USE_STATIC_LIB
// stlport
// Retail 0x008321F0, 6 bytes: mov eax, 0x012C7464; ret. X4NumGetFloat's
// num_get float parser calls it as locale::classic() (symbols.csv pin), so it
// returns the static classic locale object. That 4-byte .data object holds the
// classic _Locale_impl pointer; 0x00C70C90 dispatches through it (vtable+8)
// under the existing address-derived name TheBfmeTarget_00C70C90, which this
// TU defines once. Retail .data initializes it to 0x0130B2A0: the 24-byte .bss
// buffer the classic-locale builder (stlport_classic_locale_impl.cpp)
// placement-constructs the "C" _Locale_impl into. That buffer is raw storage
// until then, so this TU sees _Locale_impl only as its 24 raw bytes.
#include <locale>

class Gen_00C70C90Target;

// 0x0130B2A0 (.bss, 0x18 bytes up to g_classic0130B2B8)
namespace _STL {
class _Locale_impl
{
public:
	char m_bfmeStorage[0x18];
};
}
// Matched data owner: ?g_classic0130B2A0@@3V_Locale_impl@_STL@@A at VA 0x0130B2A0.
_STL::_Locale_impl g_classic0130B2A0;

// 0x012C7464
Gen_00C70C90Target *TheBfmeTarget_00C70C90 = reinterpret_cast<Gen_00C70C90Target *>(
	&g_classic0130B2A0);

namespace _STL {
const locale &locale::classic()
{
	return *reinterpret_cast<const locale *>(&TheBfmeTarget_00C70C90);
}
}
