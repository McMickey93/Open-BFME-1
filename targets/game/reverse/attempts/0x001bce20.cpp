// ?locoUpdate_moveTowardsAngle@Locomotor@@QAEXPAVObject@@M@Z
// partial score=0.9779 date=2026-10-18
// ?locoUpdate_moveTowardsAngle@Locomotor@@QAEXPAVObject@@M@Z
// partial score=0.978 date=2026-10-18 (12 non-reloc diffs: goalAngle EDI load scheduled before the position copy in the minSpeed>0 branch)
// ?locoUpdate_moveTowardsAngle@Locomotor@@QAEXPAVObject@@M@Z
// cl: /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib /O2 /GR- /DNDEBUG /MD /EHsc-
// Retail 0x001BCE20 (542 B, thiscall ret 8): BFME Locomotor::locoUpdate_moveTowardsAngle; ZH spelling with landed callees. symbols.csv pins this address as ?locoUpdate2@Rva002C12E0Locomotor@@QAEXPAX0@Z (same bytes measured under that spelling).

typedef unsigned int UnsignedInt;
typedef float Real;
typedef bool Bool;

#include "coord3d.h"
inline Coord3D::Coord3D() {}
inline Coord3D::~Coord3D() {}
inline Coord3D::Coord3D(const Coord3D &that) { x=that.x; y=that.y; z=that.z; }

#include "matrix3d.h"

class Overridable
{
public:
	void *m_vtable;
	Overridable *m_nextOverride;
	const Overridable *getFinalOverride() const
	{
		if (m_nextOverride)
			return m_nextOverride->getFinalOverride();
		return this;
	}
};

template <class T> class OVERRIDE
{
public:
	const T *operator->() const { return getFinalOverride(); }
	operator const T *() const { return getFinalOverride(); }
	const T *getFinalOverride() const
	{
		if (!m_overridable)
			return 0;
		return (T *)m_overridable->getFinalOverride();
	}

private:
	T *m_overridable;
};

class LocomotorTemplate : public Overridable
{
public:
	char m_pad008[0x80 - 0x08];
	Real m_angleThreshold001BCE20;
};

class PhysicsBehavior
{
public:
	char m_pad000[0x5c];
	unsigned char m_stunned;
};

class MotionNode;

class ObjectModule
{
public:
	virtual void slot00();
	virtual void slot01();
	virtual void slot02();
	virtual void slot03();
	virtual void slot04();
	virtual void slot05();
	virtual void slot06();
	virtual void slot07();
	virtual void slot08();
	virtual void slot09();
	virtual void slot10();
	virtual void slot11();
	virtual void slot12();
	virtual void slot13();
	virtual void slot14();
	virtual void slot15();
	virtual void slot16();
	virtual void slot17();
	virtual void slot18();
	virtual void slot19();
	virtual void slot20();
	virtual void slot21();
	virtual void slot22();
	virtual void slot23();
	virtual void slot24();
	virtual void slot25();
	virtual MotionNode *getMotion();
};

class MotionNode
{
public:
	virtual void slot00();
	virtual void slot01();
	virtual void slot02();
	virtual void slot03();
	virtual void slot04();
	virtual void slot05();
	virtual void slot06();
	virtual void slot07();
	virtual void slot08();
	virtual void slot09();
	virtual void slot10();
	virtual void slot11();
	virtual void slot12();
	virtual void slot13();
	virtual void slot14();
	virtual void beforeUpdate();
	virtual void afterUpdate();
};

class Thing
{
public:
	void *m_vtable;
	char m_pad004[0x08 - 0x04];
	Matrix3D m_transform;
	const Matrix3D *getTransformMatrix() const { return &m_transform; }
	void setTransformMatrix(const Matrix3D *matrix);
};

class Object : public Thing
{
public:
	Coord3D m_cachedPos;
	const Coord3D *getPosition() const { return &m_cachedPos; }
	Real m_angle;
	Real getAngle() const { return m_angle; }
	char m_pad048[0x1fc - 0x48];
	ObjectModule *m_module;
	char m_pad200[0x208 - 0x200];
	PhysicsBehavior *m_physics;
};

class Rva001B4A50Locomotor
{
public:
	void apply(Real angle);
};

struct Rva001B59ScaleContext;

class Rva001B59FloatView
{
public:
	float getScaledFirst(const Rva001B59ScaleContext *context) const;
};

class BfmeD1054;
class BfmeC1054
{
public:
	void bfmeGo1054C(BfmeD1054 *p, int b, int c);
};

class Rva001BC820Locomotor
{
public:
	void locoUpdate_moveTowardsPosition(Object *obj, const Coord3D &goalPos,
		Real onPathDistToGoal, Real desiredSpeed, Bool *blocked);
};

class Rva001BA1C0Handler
{
public:
	Bool behavior(void *object, const Coord3D *position);
};

Real normalizeAngle(Real angle);
Real Cos(Real angle);
Real Sin(Real angle);

class Locomotor
{
public:
	void locoUpdate_moveTowardsAngle(Object *obj, Real goalAngle);

private:
	enum LocoFlag { MAINTAIN_POS_IS_VALID = 2 };
	void setFlag(LocoFlag f, Bool set)
	{
		if (set)
			m_flags |= (1 << f);
		else
			m_flags &= ~(1 << f);
	}

	void *m_vtable;
	OVERRIDE<LocomotorTemplate> m_template;
	char m_pad008[0x40 - 0x08];
	UnsignedInt m_flags;
	char m_pad044[0x64 - 0x44];
	Matrix3D m_savedTransform;
};

void Locomotor::locoUpdate_moveTowardsAngle(Object *obj, Real goalAngle)
{
	setFlag(MAINTAIN_POS_IS_VALID, false);

	if (obj == 0 || m_template == 0)
		return;

	PhysicsBehavior *physics = obj->m_physics;
	if (physics != 0 && physics->m_stunned != 0)
		return;

	m_savedTransform = *obj->getTransformMatrix();

	Real delta = normalizeAngle(goalAngle - obj->getAngle());
	Real angleThreshold = m_template->m_angleThreshold001BCE20;
	Real cosDelta = Cos(delta);
	if (Cos(angleThreshold) > cosDelta)
	{
		ObjectModule *module = obj->m_module;
		MotionNode *motion = module != 0 ? (MotionNode *)module->getMotion() : 0;
		if (motion != 0)
		{
			motion->beforeUpdate();
			((Rva001B4A50Locomotor *)this)->apply(goalAngle);
			obj->setTransformMatrix(&m_savedTransform);
			motion->afterUpdate();
		}
	}

	Real minSpeed = ((const Rva001B59FloatView *)this)->getScaledFirst((const Rva001B59ScaleContext *)obj);
	if (minSpeed > 0)
	{
		Coord3D desiredPos = *obj->getPosition();
		desiredPos.x += Cos(goalAngle) * minSpeed * 2;
		desiredPos.y += Sin(goalAngle) * minSpeed * 2;
		const Real onPathDistToGoal = 99999.0f;
		Bool blocked;
		((Rva001BC820Locomotor *)this)->locoUpdate_moveTowardsPosition(obj, desiredPos, onPathDistToGoal, minSpeed, &blocked);
		return;
	}
	else
	{
		Coord3D desiredPos = *obj->getPosition();
		desiredPos.x += Cos(goalAngle) * 1000.0f;
		desiredPos.y += Sin(goalAngle) * 1000.0f;
		((BfmeC1054 *)this)->bfmeGo1054C((BfmeD1054 *)obj, (int)&desiredPos, 0);
		((Rva001BA1C0Handler *)this)->behavior(obj, obj->getPosition());
	}
}
