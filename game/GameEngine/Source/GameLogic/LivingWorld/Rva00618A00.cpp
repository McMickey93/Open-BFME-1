// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib
// stlport
#include "PreRTS.h"
#include "Common/Overridable.h"
#include "Common/Override.h"

extern bool __cdecl Rva007397E0(void *, float, float, float);
struct BfmeThingGN : Overridable {
    unsigned int wordC;
    float float10, float14;
};
struct BfmeSourceGN {
    unsigned int word0, word4;
    void *ptr8;
};
class Rva00618A00Object {
public:
    unsigned int word0;
    OVERRIDE<BfmeThingGN> data4;
    unsigned int word8;
    BfmeSourceGN *ptrC;
    bool byte10;
    unsigned char pad11[3];
    float float14, float18;
    void rva00618a00(char on);
};
// Address-qualified entry; no semantic owner identity is asserted.
// Evidence: targets/game/reverse/identity_evidence/00618a00-native-override.md
void Rva00618A00Object::rva00618a00(char on)
{
    if (float18 != 0.0f && on == 0) {
        float18 = 0.0f;
        float14 = 0.0f;
        float color = data4->float10;
        Rva007397E0(ptrC->ptr8, color, color, color);
    } else if (!byte10 && on != 0) {
        float18 = 1.0f;
        float14 = 0.0f;
    }
}
