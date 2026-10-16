// ?bfmeQuery@Gen01304B64@@QAEHXZ
// partial score=0.1082 date=2026-10-16
// cl: /O2 /MD /DNDEBUG
// stlport
#include <vector>
#include <math.h>
class Drawable;
class Rva00765AC0;
struct Q4Sort00751F50Record {
    char pad00[8]; Drawable *drawable; char pad0c[8]; Rva00765AC0 *state;
    bool compare(const Q4Sort00751F50Record &, int *, int *) const;
};
struct Rva00755A70Animation {
    void *animation; float frame; char pad08[8]; int mode, direction; char tail[4];
};
struct Rva00755A70Drawable { char pad[0x1f8]; float scale; };
struct Rva00755A70Module : Q4Sort00751F50Record {
    Drawable *getObject() const { return drawable; }
    char pad18[0xdc-0x18]; Rva00755A70Animation animations[2];
};
struct Rva00755A70Lod { bool allowed; char pad[3]; int count1,count2; float delta; int count3; };
struct Rva00755A70Data { char pad[0x15c]; Rva00755A70Lod lod[3]; };
class GameLODManager006B8220;
extern GameLODManager006B8220 *TheGameLODManager;
struct Rva00755A70LodManager { char pad[0x170c]; int level; };
static __forceinline int lodIndex() {
 int n=reinterpret_cast<Rva00755A70LodManager *>(TheGameLODManager)->level-1;
 if(n<0)return 0; if(n>2)return 2; return n;
}

struct Entry00755170 {
 Rva00755A70Data *data; Rva00755A70Module *module; int key;
__forceinline bool same(const Entry00755170 &first, float delta) const
{
 if(reinterpret_cast<Rva00755A70LodManager *>(TheGameLODManager)->level==4) return false;
 if(this->data!=first.data || this->key!=first.key) return false;
 Rva00755A70Module *m=this->module,*f=first.module;
 if(reinterpret_cast<Rva00755A70Drawable *>(m->getObject())->scale != reinterpret_cast<Rva00755A70Drawable *>(f->getObject())->scale) return false;
 if(m && f) {
  int a,b;
  if(m->compare(*f,&a,&b)) return a==b;
 }
 for(int i=0;i<=1;++i) {
  const Rva00755A70Animation &a=m->animations[i],&b=f->animations[i];
  if(a.animation!=b.animation)return false;
  if(!a.animation)continue;
  if(a.direction!=b.direction)return false;
  if(a.mode!=b.mode)return false;
 }
 if(fabs(m->animations[0].frame-f->animations[0].frame)>delta)return false;
 if(m->animations[1].animation && fabs(m->animations[1].frame-f->animations[1].frame)>delta)return false;
 return true;
}
};
class Synchronize00755170 { public: void apply(Entry00755170 **, Entry00755170 **); };
class Gen00754850 { public: void handle(); };
class Gen007558B0 { public: void sortAndPrune(); };

class Gen01304B64 {
public:
 int bfmeQuery();
 std::vector<Entry00755170 *> entries;
};
int Gen01304B64::bfmeQuery()
{
 int groups=0;
 reinterpret_cast<Gen00754850 *>(this)->handle();
 reinterpret_cast<Gen007558B0 *>(this)->sortAndPrune();
 if(entries.empty())return 0;
 Entry00755170 **first=entries.begin(),**end=entries.end();
 for(Entry00755170 **p=first;p!=end;) {
  ++p;
  if(p!=end) {
   float delta=(*p)->data->lod[lodIndex()].delta;
   Entry00755170 *head=*first,*mine=*p;
   if(mine->same(*head,delta))continue;
  }
  reinterpret_cast<Synchronize00755170 *>(this)->apply(first,p);
  ++groups; first=p;
 }
 return groups;
}
