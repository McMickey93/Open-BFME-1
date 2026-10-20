// ??$__partial_sort@PAHHUQ4Sort00755050@@@_STL@@YAXPAH000UQ4Sort00755050@@@Z
// partial score=1.0 date=2026-10-20
// Opaque record comparator with the decoded retail layout.
// cl: /O2 /Ob2 /GR- /EHsc- /MD /DNDEBUG
// stlport

#include <algorithm>

enum DrawableID
{
	INVALID_DRAWABLE_ID = 0
};

class Drawable
{
public:
	DrawableID getID( void ) const;
};

class Rva00765AC0
{
public:
	unsigned char ready( void ) const;
};

class GameLODManager
{
public:
	char m_pad[ 0x170c ];
	int m_level;
};

extern GameLODManager *TheGameLODManager;

struct Q4Sort00751F50Record
{
	char m_pad00[ 8 ];
	Drawable *m_drawable;
	char m_pad0c[ 8 ];
	Rva00765AC0 *m_state;

	__declspec(noinline) bool compare( const Q4Sort00751F50Record &other, int *outLeft,
		int *outRight ) const;
};

// ?compare@Q4Sort00751F50Record@@QBE_NABU1@PAH1@Z
// Inline visibility allows reuse of the output slots after the call.
inline bool Q4Sort00751F50Record::compare( const Q4Sort00751F50Record &other,
	int *outLeft, int *outRight ) const
{
	*outRight = 0;
	*outLeft = 0;
	if ( m_state == 0 )
		return false;
	else
	{
		if ( m_state != other.m_state )
			return false;

		int divisor = 3;
		if ( TheGameLODManager->m_level == 0 )
			divisor = 1;
		*outLeft = m_drawable->getID() % divisor;
		*outRight = other.m_drawable->getID() % divisor;
		return m_state->ready();
	}
}

extern "C" void _ReadWriteBarrier();
#pragma intrinsic(_ReadWriteBarrier)
struct Rva007527C0Sub {
 void *m_00; float m_04; char m_08[8]; int m_10; int m_14; char m_18;
};
struct Rva007527C0Data {
 char m_00[8]; struct Rva007527C0Float *m_08; char m_0c[8]; Rva00765AC0 *m_14;
 char m_18[0xc4]; Rva007527C0Sub m_dc[2];
};
struct Rva007527C0Float { char m_00[0x1f8]; float m_1f8; };
struct Rva007527C0 {
 void *m_00; Rva007527C0Data *m_04; int m_08;
 bool method(const Rva007527C0 &) const;
 bool lessThan(const Rva007527C0 &) const;
};
// ?method@Rva007527C0@@QBE_NABU1@@Z
bool Rva007527C0::method(const Rva007527C0 &o) const {
 if(m_00 != o.m_00) return o.m_00 < m_00;
 if(!m_00) return m_04 < o.m_04;
 if(m_08 != o.m_08) return m_08 < o.m_08;
 if(m_04->m_08->m_1f8 != o.m_04->m_08->m_1f8) return m_04->m_08->m_1f8 < o.m_04->m_08->m_1f8;
 if(o.m_04->m_14 != m_04->m_14) return m_04->m_14 < o.m_04->m_14;
 int a,b;
 if(((Q4Sort00751F50Record *)m_04)->compare(*(Q4Sort00751F50Record *)o.m_04,&a,&b)) {
  if(a!=b) return a<b;
  return m_04 < o.m_04;
 }
 int i = 0;
 const Rva007527C0Data * leftBase = m_04;
 const Rva007527C0Data * rightBase = o.m_04;
 for(;i<=1;++i) {
  const Rva007527C0Sub &left=m_04->m_dc[i];
  const Rva007527C0Sub &right=o.m_04->m_dc[i];
  if(left.m_00 != right.m_00) return left.m_00 < right.m_00;
  if(left.m_00) {
   if(left.m_14 != right.m_14) return left.m_14 < right.m_14;
   if(left.m_10 != right.m_10) return left.m_10 < right.m_10;
   if(left.m_18 != right.m_18) return left.m_18 ? true : false;
  }
 }
 // Preserve the retail member reloads after the loop.
 _ReadWriteBarrier();
 Rva007527C0Data *tailLeft=m_04;
 Rva007527C0Data *tailRight=o.m_04;
 float x=(tailLeft->m_dc[1].m_00 ? tailLeft->m_dc[1].m_04 : 0.0f)+tailLeft->m_dc[0].m_04;
 float y=(tailRight->m_dc[1].m_00 ? tailRight->m_dc[1].m_04 : 0.0f)+tailRight->m_dc[0].m_04;
 if(x!=y) return x<y;
 return leftBase<rightBase;
}

// The record-pointer sort functor at 0x00752B80 carries its own spelling of
// the same ordering: the key compares left > right and the state pointers
// left first, unlike method above.
// ?lessThan@Rva007527C0@@QBE_NABU1@@Z absent-from-retail
__forceinline bool Rva007527C0::lessThan(const Rva007527C0 &o) const {
 if(m_00 != o.m_00) return m_00 > o.m_00;
 if(!m_00) return m_04 < o.m_04;
 if(m_08 != o.m_08) return m_08 < o.m_08;
 if(m_04->m_08->m_1f8 != o.m_04->m_08->m_1f8) return m_04->m_08->m_1f8 < o.m_04->m_08->m_1f8;
 if(m_04->m_14 != o.m_04->m_14) return m_04->m_14 < o.m_04->m_14;
 int a,b;
 if(((Q4Sort00751F50Record *)m_04)->compare(*(Q4Sort00751F50Record *)o.m_04,&a,&b)) {
  if(a!=b) return a<b;
  return m_04 < o.m_04;
 }
 int i = 0;
 const Rva007527C0Data * leftBase = m_04;
 const Rva007527C0Data * rightBase = o.m_04;
 for(;i<=1;++i) {
  const Rva007527C0Sub &left=m_04->m_dc[i];
  const Rva007527C0Sub &right=o.m_04->m_dc[i];
  if(left.m_00 != right.m_00) return left.m_00 < right.m_00;
  if(left.m_00) {
   if(left.m_14 != right.m_14) return left.m_14 < right.m_14;
   if(left.m_10 != right.m_10) return left.m_10 < right.m_10;
   if(left.m_18 != right.m_18) return left.m_18 ? true : false;
  }
 }
 // Preserve the retail member reloads after the loop.
 _ReadWriteBarrier();
 Rva007527C0Data *tailLeft=m_04;
 Rva007527C0Data *tailRight=o.m_04;
 float x=(tailLeft->m_dc[1].m_00 ? tailLeft->m_dc[1].m_04 : 0.0f)+tailLeft->m_dc[0].m_04;
 float y=(tailRight->m_dc[1].m_00 ? tailRight->m_dc[1].m_04 : 0.0f)+tailRight->m_dc[0].m_04;
 if(x!=y) return x<y;
 return leftBase<rightBase;
}

// Sort functor over four-byte record pointers; the matched median, insertion
// and heap helpers in Q4IntrosortLoop.cpp reach it through ILT 0x0002952D.
// The operator is defined in the class, as for the landed Q4Sort0034BFC0
// sibling: the optimiser emits it out of line (??RQ4Sort00755050@@QBE_NHH@Z,
// retail 0x00752B80) and __partial_sort below keeps comp cached in EBP.
struct Q4Sort00755050
{
 void *m_state;
 bool operator()(int a, int b) const
 {
  return ((const Rva007527C0 *)a)->lessThan(*(const Rva007527C0 *)b);
 }
};

// Retail 0x00754C60: the heap-select fallback of the Q4Sort00755050 sort;
// its __make_heap, __adjust_heap and sort_heap calls go through ILTs
// 0x0003B66F, 0x00036791 and 0x00026C8D, whose bodies reach this comparator.
template void _STL::__partial_sort<int *, int, Q4Sort00755050>(
 int *, int *, int *, int *, Q4Sort00755050);
