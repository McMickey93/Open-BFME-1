// ?rva0079D530@AptPalantir@@QAEXXZ
// partial score=0.9407 date=2026-10-16
// ?rva0079D530@AptPalantir@@QAEXXZ
struct FloatPairBase0079D530 {float x,y;};
class BfmeVec2CY : public FloatPairBase0079D530 { public:
 BfmeVec2CY();BfmeVec2CY(const BfmeVec2CY &);BfmeVec2CY(float,float);~BfmeVec2CY();
 BfmeVec2CY &operator+=(const BfmeVec2CY &); BfmeVec2CY &operator-=(const BfmeVec2CY &);
 float length()const;float toAngle()const;bool IsExactlyEqualTo(const BfmeVec2CY &)const;
};
// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWMath
#include <math.h>
#include <float.h>
inline BfmeVec2CY::BfmeVec2CY(){}
inline BfmeVec2CY::BfmeVec2CY(const BfmeVec2CY &v){x=v.x;y=v.y;}
inline BfmeVec2CY::BfmeVec2CY(float a,float b){x=a;y=b;}
inline BfmeVec2CY::~BfmeVec2CY(){}

inline BfmeVec2CY &BfmeVec2CY::operator+=(const BfmeVec2CY &v){x+=v.x;y+=v.y;return *this;}
inline BfmeVec2CY &BfmeVec2CY::operator-=(const BfmeVec2CY &v){x-=v.x;y-=v.y;return *this;}
inline float BfmeVec2CY::length()const{return (float)sqrt(x*x+y*y);}
inline float BfmeVec2CY::toAngle()const{return (float)atan2(y,x);}
inline bool BfmeVec2CY::IsExactlyEqualTo(const BfmeVec2CY &v)const{return x==v.x && y==v.y;}

extern void j_00002dbf();
typedef BfmeVec2CY *(__cdecl *SubtractCall0079D530)(BfmeVec2CY *,BfmeVec2CY,const BfmeVec2CY &);
#define subtract0079CFF0 ((SubtractCall0079D530)j_00002dbf)

class Display {public:
 virtual void slot00();virtual void slot04();virtual void slot08();virtual void slot0c();
 virtual void slot10();virtual void slot14();virtual void slot18();virtual void slot1c();
 virtual void slot20();virtual void slot24();virtual void slot28();virtual unsigned getWidth();
};
extern Display *TheDisplay;

struct ICoord2D0079D530 {int x,y;};
class Image {public:
 char pad00[0x24]; ICoord2D0079D530 m_imageSize;
};

class AptPalantir {public:
 char pad00[0x4dc]; BfmeVec2CY m_points4dc[4]; char pad4fc[0x20]; const Image *m_image51c;
 char pad520[4]; BfmeVec2CY m_coords524[4],m_coords544[4],m_coords564[4];
 void rva0079D530();
};

static inline float wrapAngle(float a){
 if(a<0.0f)return 6.2831855f-(float)fmod(-a,6.2831855f);
 return (float)fmod(a,6.2831855f);
}
static inline float angleDifference(float a,float b){if(a<b)a+=6.2831855f;return a-b;}

void AptPalantir::rva0079D530(){
 float minimum=FLT_MAX;
 for(int i=0;i<4;i++){
  int fallback = (i - 3);
  int next = (i + 1);
  if(next>=4)next=fallback;
  BfmeVec2CY edge;subtract0079CFF0(&edge,BfmeVec2CY(m_points4dc[next]),m_points4dc[i]);
  float len=edge.length();if(len<minimum)minimum=len;
 }
 // Scale the image width by the display width.
 int rawWidth=m_image51c->m_imageSize.x;
 float width=(float)rawWidth;width=width*(float)TheDisplay->getWidth()/1024.0f;
 if(width>minimum)width=minimum;
 BfmeVec2CY *prev=&m_points4dc[3];
 for(int i=0;i<4;i++){
  int fallback = (i - 3);
  int next = (i + 1);
  if(next>=4)next=fallback;
  BfmeVec2CY &point=m_points4dc[i];
  m_coords544[i]=point;
  m_coords564[i]=point;
  if(!point.IsExactlyEqualTo(m_points4dc[next]) && !point.IsExactlyEqualTo(*prev)){
   BfmeVec2CY firstVector;
   float first=wrapAngle(subtract0079CFF0(&firstVector,m_points4dc[next],point)->toAngle());
   BfmeVec2CY secondVector;
   float second=wrapAngle(subtract0079CFF0(&secondVector,*prev,point)->toAngle());
   float middle=wrapAngle(angleDifference(second,first)*0.5f+first);
   float angle=middle;
   if(angle<first)angle+=6.2831855f;
   angle-=first;
   if(fabs(angle)>0.00001f){
    float distance=width*0.5f/(float)sin(angle);
    // Apply the polar offset to the inner and outer quads.
    BfmeVec2CY offset;offset.x=(float)cos(middle)*distance;offset.y=(float)sin(middle)*distance;
    m_coords544[i].x+=offset.x;m_coords544[i].y+=offset.y;
    m_coords564[i].x-=(float)cos(middle)*distance;m_coords564[i].y-=offset.y;
   }
  }
  prev=&point;
 }
 m_coords524[0]=m_points4dc[0];m_coords524[1]=m_points4dc[1];m_coords524[2]=m_points4dc[2];m_coords524[3]=m_points4dc[3];
}
