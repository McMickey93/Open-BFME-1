// ?calculateMaxBlockedSpeed@AIUpdateInterface@@IBEMPAVObject@@@Z
// partial score=0.9758 date=2026-10-28
// cl: /DNDEBUG /MD /EHsc
// AIUpdateInterface::calculateMaxBlockedSpeed, retail 0x0026EED0, 289 B (ret 4).
// ilt_oracle CONFIRMS ?calculateMaxBlockedSpeed@AIUpdateInterface@@IBEMPAVObject@@@Z.
// Zero Hour AIUpdate.cpp:1258 twin; BFME replaces the physics velocity with
// Object::bfmeGetNonnegativePreferredLocomotorHeight (ILT 0x47C8).
// 289/289 B, 7 bytes off: (1) getObject() for the position delta loads ECX,
// retail EAX (+0x2C/+0x32/+0x3C); (2) the second dot fld's vectorToOther,
// retail fld's ourDir (+0xB6..+0xC2). See attempt_support handoff.
typedef float Real;
typedef int Int;
extern "C" double __cdecl sqrt(double value);
#pragma intrinsic(sqrt)
struct Coord3D { Real x, y, z; };
struct Coord2D
{
	Real x, y;
	Real length() const { return (Real)sqrt(x * x + y * y); }
	void normalize()
	{
		Real len = length();
		if (len != 0.0f)
		{
			Real inv = 1.0f / len;
			x *= inv;
			y *= inv;
		}
	}
};
class Thing
{
public:
	const Coord3D *getUnitDirectionVector2D() const;
	const Coord3D *getPosition() const { return &m_position; }
	char m_pad00[0x38];
	Coord3D m_position;
	char m_pad44[0x31c - 0x44];
	Int m_formationID;
};
class Object : public Thing
{
public:
	Real bfmeGetNonnegativePreferredLocomotorHeight() const;
	Int getFormationID() const { return m_formationID; }
};
class AIUpdateInterface
{
protected:
	Real calculateMaxBlockedSpeed(Object *other) const;
	Object *getObject() const { return m_object; }
	char m_pad00[8];
	Object *m_object;
	char m_pad0c[0x170 - 0x0c];
	Real m_curMaxBlockedSpeed;
};
static __forceinline Real projectTowards(Coord2D &v, const Object *to, const Object *from, Real oy, Real ox)
{
	v.x = to->getPosition()->x - from->getPosition()->x;
	v.y = to->getPosition()->y - from->getPosition()->y;
	v.normalize();
	return v.x*ox + v.y*oy;
}
Real AIUpdateInterface::calculateMaxBlockedSpeed(Object *other) const
{
	const Coord3D *dir = getObject()->getUnitDirectionVector2D();
	Coord3D ourDir; ourDir.x = dir->x; ourDir.y = dir->y;
	Coord2D vectorToOther;
	const Coord3D *odir = other->getUnitDirectionVector2D();
	Real dotProduct = projectTowards(vectorToOther, other, getObject(), odir->y, odir->x);
	if (dotProduct<0) return 0; // They are running into us.

	Real speedFactor = dotProduct;
	Real awaySpeed = other->bfmeGetNonnegativePreferredLocomotorHeight() * speedFactor;

	// Now calculate the amount we are moving relative to towards them...
	dotProduct = ourDir.x*vectorToOther.x + ourDir.y*vectorToOther.y;
	if (dotProduct<=0) {
		return m_curMaxBlockedSpeed;
	}
	Real maxSpeed = awaySpeed / dotProduct;
	if (other->getFormationID()!=0 && getObject()->getFormationID()==other->getFormationID()) {
		maxSpeed *= 0.55f;
	}
	if (maxSpeed>m_curMaxBlockedSpeed) return m_curMaxBlockedSpeed;
	return maxSpeed;
}
