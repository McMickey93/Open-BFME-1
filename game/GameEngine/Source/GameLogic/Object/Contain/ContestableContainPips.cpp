// ?getContainerPipsToShow@ContestableContain@@UBE_NAAH00000@Z
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Iinputs/reference/shims/zhcanonascii /Iinputs/reference/shims/sweep /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Include /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWLib
// stlport

#define __PLACEMENT_VEC_NEW_INLINE
#include "Common/GameMemory.h"
#include "Common/Overridable.h"
#include "Common/Override.h"
#include "Common/ThingTemplate.h"
#include <list>

// The canonical header stores the native single-pointer OVERRIDE as a raw pointer.
#define THING_TU_MEMBERS \
    Bool isKindOf(KindOfType kind) const { return reinterpret_cast<const OVERRIDE<ThingTemplate>&>(m_template)->isKindOf(kind); }
#include "../object.h"
#undef THING_TU_MEMBERS

// This view starts at ContainModuleInterface, primary object +0x20.
class OpenContain
{
protected:
    virtual Bool getContainerPipsToShow(Int &numTotal, Int &numFull, Int &numInfantry,
        Int &secondTotal, Int &secondFull, Int &secondInfantry) const;
};

class ContestableContain : public OpenContain
{
public:
    virtual Bool getContainerPipsToShow(Int &numTotal, Int &numFull, Int &numInfantry,
        Int &secondTotal, Int &secondFull, Int &secondInfantry) const;

private:
    char pad[0x99c - 4];
    _STL::list<Object *> objects;
};

// ?getContainerPipsToShow@ContestableContain@@UBE_NAAH00000@Z
Bool ContestableContain::getContainerPipsToShow(Int &numTotal, Int &numFull, Int &numInfantry,
    Int &secondTotal, Int &secondFull, Int &secondInfantry) const
{
    Bool ok = OpenContain::getContainerPipsToShow(numTotal, numFull, numInfantry, secondTotal, secondFull, secondInfantry);
    if (ok)
    {
        secondFull = objects.size();
        secondTotal = numTotal;
        secondInfantry = 0;
        for (_STL::list<Object *>::const_iterator it = objects.begin(); it != objects.end(); ++it)
            if ((*it)->isKindOf(KINDOF_INFANTRY))
                ++secondInfantry;
    }
    return ok;
}
