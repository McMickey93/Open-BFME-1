// ?rva0004a444@Rva00615D50Object@@QAE_NPBUICoord2D@@@Z
// partial score=0.3514 date=2026-10-20
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc
// Open-BFME: retail 0x00618C90 (276 bytes, ret 4), reached through ILT
// 0x0004A444 as ?rva0004a444@Rva00615D50Object@@QAE_NPBUICoord2D@@@Z by the
// matched 0x00615D50 lookup (LivingWorldManagerRva00615D50.cpp), which tests
// each living-world object against the screen point before measuring it.
//
// The object's drawable (+0x0C of the holder at +0x0C, else +0x08) supplies a
// bounding box through vslot +0x104; the living-world view (0x012F7048) turns
// the screen point into a pick ray through vslot +0x1C. The ray is stretched
// 3000 units into a WW3D LineSegClass (out-of-line protected recalculate at
// 0x003FE770) and handed to CollisionMath::Overlap_Test; anything but OUTSIDE
// is a hit. Owner and slot names stay address-derived.

struct ICoord2D
{
	int x;
	int y;
};

class Vector3
{
public:
	Vector3() {}
	Vector3( float x, float y, float z ) { X = x; Y = y; Z = z; }
	Vector3 &operator*=( float k ) { X *= k; Y *= k; Z *= k; return *this; }
	Vector3 &operator+=( const Vector3 &v ) { X += v.X; Y += v.Y; Z += v.Z; return *this; }
	friend Vector3 operator+( const Vector3 &a, const Vector3 &b ) { return Vector3( a.X + b.X, a.Y + b.Y, a.Z + b.Z ); }

	float X;
	float Y;
	float Z;
};

class AABoxClass
{
public:
	Vector3 Center;
	Vector3 Extent;
};

class LineSegClass
{
public:
	LineSegClass( const Vector3 &p0, const Vector3 &p1 ) : P0( p0 ), P1( p1 ) { recalculate(); }

protected:
	void recalculate( void );

	Vector3 P0;
	Vector3 P1;
	Vector3 DP;
	Vector3 Dir;
	float Length;
};

class CollisionMath
{
public:
	enum OverlapType
	{
		POS = 0x01,
		NEG = 0x02,
		ON = 0x04,
		BOTH = 0x08,
		OUTSIDE = POS
	};

	static OverlapType Overlap_Test( const AABoxClass &box, const LineSegClass &line );
};

#define V(n) virtual void slot##n();
class Rva00618C90Drawable
{
public:
	V(000) V(004) V(008) V(00C) V(010) V(014) V(018) V(01C)
	V(020) V(024) V(028) V(02C) V(030) V(034) V(038) V(03C)
	V(040) V(044) V(048) V(04C) V(050) V(054) V(058) V(05C)
	V(060) V(064) V(068) V(06C) V(070) V(074) V(078) V(07C)
	V(080) V(084) V(088) V(08C) V(090) V(094) V(098) V(09C)
	V(0A0) V(0A4) V(0A8) V(0AC) V(0B0) V(0B4) V(0B8) V(0BC)
	V(0C0) V(0C4) V(0C8) V(0CC) V(0D0) V(0D4) V(0D8) V(0DC)
	V(0E0) V(0E4) V(0E8) V(0EC) V(0F0) V(0F4) V(0F8) V(0FC)
	V(100)
	virtual const AABoxClass &getBoundingBox();				// +0x104
};

class Gen_00609320
{
public:
	V(00) V(04) V(08) V(0C) V(10) V(14) V(18)
	virtual void getPickRay( const ICoord2D *screen, Vector3 *start, Vector3 *dir );	// +0x1C
};
#undef V

extern Gen_00609320 *g_bfmeStateDF;

struct Rva00618C90Holder
{
	void *m_at00;
	void *m_at04;
	Rva00618C90Drawable *m_fallback;			// +0x08
	Rva00618C90Drawable *m_drawable;			// +0x0C
};

struct Rva00615D50Object
{
	bool rva0004a444( const ICoord2D *point );

	void *m_at00;
	void *m_type;
	int m_id;
	Rva00618C90Holder *m_holder;				// +0x0C
};

bool Rva00615D50Object::rva0004a444( const ICoord2D *point )
{
	if( m_holder == 0 )
		return false;

	Rva00618C90Drawable *drawable = m_holder->m_drawable;
	if( drawable == 0 )
	{
		drawable = m_holder->m_fallback;
		if( drawable == 0 )
			return false;
	}

	AABoxClass box = drawable->getBoundingBox();
	Vector3 start, dir;
	g_bfmeStateDF->getPickRay( point, &start, &dir );
	dir *= 3000.0f;
	LineSegClass ray( start, start + dir );
	return CollisionMath::Overlap_Test( box, ray ) != CollisionMath::OUTSIDE;
}
