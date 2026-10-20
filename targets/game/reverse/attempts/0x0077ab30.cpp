// ?stopClientParticleSystems@W3DModelDraw@@IAEXXZ
// partial score=0.1579 date=2026-10-20
// ?stopClientParticleSystems@W3DModelDraw@@IAEXXZ
// cl: /DNDEBUG /DWIN32 /D_STLP_USE_STATIC_LIB /DBFME_STLP_NODE_ALLOC /MD /EHsc /Iinputs/reference/shims/stlp_nodealloc /Igame/Libraries/Source/WWVegas/WW3D2 /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WWDebug /Igame/Libraries/Source/WWVegas/WWSaveLoad /Iinputs/reference/shims
// stlport
// Retail 0x0077AB30, 475 bytes, thiscall, no arguments.
//
// Identity: the matched W3DModelDraw destructor (0x0077B090) calls this body
// through ILT 0x0001B798 where Zero Hour's destructor calls
// stopClientParticleSystems; symbols.csv pins the name here. BFME's version
// tears down the bone-follower entries at +0x130 (the 32-byte records that
// W3DModelDrawRva00779910.cpp walks): each entry's render object leaves the
// scene and is released, then the vector is cleared.

#define __PLACEMENT_VEC_NEW_INLINE  // always.h defines array placement-new itself
#include "rendobj.h"
#include <string>
#include <vector>

// W3DDisplay::m_3DScene is the global at VA 0x012F8058; slot 3 removes a
// render object, as in W3DModelDrawNukeCurrentRender.cpp.
class RTS3DScene
{
public:
	virtual void slot00();
	virtual void slot01();
	virtual void slot02();
	virtual void Remove_Render_Object(RenderObjClass *obj);
};

class W3DDisplay
{
public:
	static RTS3DScene *m_3DScene;
};

struct Gen_t_00777e90_p32cd
{
	RenderObjClass *m_renderObject;  // +0x00
	std::string m_boneName;          // +0x04
	float m_rotateX;                 // +0x10
	float m_rotateY;                 // +0x14
	float m_rotateZ;                 // +0x18
	int m_countdown;                 // +0x1C
};

class W3DModelDraw
{
protected:
	void stopClientParticleSystems();

private:
	unsigned char m_beforeSystems[0x130];
	std::vector<Gen_t_00777e90_p32cd> m_boneFollowers;      // +0x130
};

void W3DModelDraw::stopClientParticleSystems()
{
	for (std::vector<Gen_t_00777e90_p32cd>::iterator it = m_boneFollowers.begin();
		it != m_boneFollowers.end(); ++it)
	{
		Gen_t_00777e90_p32cd entry = *it;
		W3DDisplay::m_3DScene->Remove_Render_Object(entry.m_renderObject);
		entry.m_renderObject->Release_Ref();
		entry.m_renderObject = 0;
	}
	m_boneFollowers.clear();
}
