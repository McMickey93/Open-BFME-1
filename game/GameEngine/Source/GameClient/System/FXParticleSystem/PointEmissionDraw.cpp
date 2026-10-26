// Point volume callback recovered from the complete retail body at
// retail RVA 0x005FA450 (83 bytes, RET 0xC at +0x50).  The primary
// PointEmissionVolumeModule vtable 0x011122E0 carries ILT 0x0001E22C in
// slot 4, the same slot Box installs for its draw callback
// (BoxEmissionDraw.cpp).  The method name is address-derived.  The body
// draws one TheTacticalView slot-11 line from the point to the point lifted
// by two units (a double literal); it reads no module member.
// The lifted point takes the ground coordinates and is raised with +=:
// that statement schedules the x87 store after the trailing zero push and the
// first ground store, as retail does.  Assigning (float)(z + 2.0) directly
// stores first (9-byte residue).
// cl: /DNDEBUG /MD /GX- /O2 /Ob2

#include "../../../../../Libraries/Include/Lib/Coord3D.h"

class View;
extern View *TheTacticalView;

class View
{
public:
	virtual void slot00(); virtual void slot04(); virtual void slot08();
	virtual void slot0C(); virtual void slot10(); virtual void slot14();
	virtual void slot18(); virtual void slot1C(); virtual void slot20();
	virtual void slot24(); virtual void slot28();
	virtual void Rva0045BA00Slot(const Coord3D *from,
		const Coord3D *to, unsigned int colour,
		unsigned int flags);
};

namespace FXParticleSystem {

class PointEmissionVolumeModule
{
public:
	virtual void slot00();
	virtual void slot01();
	virtual void slot02();
	virtual void slot03();
	virtual void Rva005FA450Draw(float x, float y, float z);

private:
	// The constructor witnesses a 0x24-byte object; this method never
	// dereferences this.
	unsigned char opaquePrimaryTail[0x20];
};

void PointEmissionVolumeModule::Rva005FA450Draw(float x, float y, float z)
{
	Coord3D ground;
	ground.x = x;
	ground.y = y;
	ground.z = z;
	Coord3D lifted;
	lifted.x = x;
	lifted.y = y;
	lifted.z = z;
	lifted.z += 2.0;

	TheTacticalView->Rva0045BA00Slot(&ground, &lifted, 0xccaaffff, 0);
}

} // namespace FXParticleSystem
