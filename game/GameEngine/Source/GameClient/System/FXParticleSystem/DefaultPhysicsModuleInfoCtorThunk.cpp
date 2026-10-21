// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Igame/GameEngine/Source/Common/System /Igame/GameEngine/Include/Common /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib
// BFME-2 EmissionInfoDefaultCtors.cpp supplies the empty coordinate lifetime.
// BFME-1 native unwind metadata independently proves Snapshot cleanup.
#define SNAPSHOT_CPP
#include "fx_particle_system.h"
inline Snapshot::Snapshot() {}
inline Snapshot::~Snapshot() {}

namespace FXParticleSystem {
DefaultPhysicsModuleInfo::DefaultPhysicsModuleInfo()
{
    m_field3 = 0;
    m_coord.zero();
    m_var1.setRange(0.0f, 0.0f, GameClientRandomVariable::UNIFORM);
}
}
