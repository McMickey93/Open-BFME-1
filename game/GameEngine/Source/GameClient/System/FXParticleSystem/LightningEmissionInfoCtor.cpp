// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Igame/GameEngine/Source/Common/System /Igame/GameEngine/Include/Common /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib
// Retail 0x005FAFE0: the inline EmissionVolumeInfo base clears the flag, the
// two coordinates are zeroed and each random variable gets a 0..0 uniform range.
#include "fx_particle_system.h"

namespace FXParticleSystem {
LightningEmissionInfo::LightningEmissionInfo()
{
    m_coord08.zero();
    m_coord14.zero();
    m_var20.setRange(0.0f, 0.0f, GameClientRandomVariable::UNIFORM);
    m_var2C.setRange(0.0f, 0.0f, GameClientRandomVariable::UNIFORM);
    m_var38.setRange(0.0f, 0.0f, GameClientRandomVariable::UNIFORM);
    m_var44.setRange(0.0f, 0.0f, GameClientRandomVariable::UNIFORM);
    m_var50.setRange(0.0f, 0.0f, GameClientRandomVariable::UNIFORM);
    m_var5C.setRange(0.0f, 0.0f, GameClientRandomVariable::UNIFORM);
    m_var68.setRange(0.0f, 0.0f, GameClientRandomVariable::UNIFORM);
    m_var74.setRange(0.0f, 0.0f, GameClientRandomVariable::UNIFORM);
    m_var80.setRange(0.0f, 0.0f, GameClientRandomVariable::UNIFORM);
}
}
