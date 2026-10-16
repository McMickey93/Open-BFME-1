// ?update@Rva0044A6A0@@QAEXXZ
// partial score=0.6938 date=2026-10-16
// cl: /O2 /MD /DNDEBUG /D_STLP_USE_STATIC_LIB
// stlport
#define _STLP_NO_EXCEPTIONS 1
#include <list>
class Rva005BA910Anim2D {
public:
 virtual ~Rva005BA910Anim2D();
 void draw(float,float,unsigned char);
 void setAlpha(float value) { alpha=value; }
 void setDimensions(int size) {width=size;height=size;}
 char pad04[0x10-4]; unsigned char status; char pad11[0x1c-0x11];
 float alpha; char pad20[0x2c-0x20]; int width,height;
};
struct Rva0044A6A0Entry { Rva005BA910Anim2D *animation; float x,y; unsigned end; int flags; float vx,vy,drag; int size; };
class Rva00449790Owner { public: void rva0044A2E0(); char pad[0x34]; int x,y; };
class BfmeGameLogicPause { public: bool isGamePaused(); };
class GameLogic; extern GameLogic *TheGameLogic;
class GameClient; extern GameClient *TheGameClient;
class ClientRoot4120 { public:
 virtual void slot00(); virtual void slot01(); virtual void slot02(); virtual void slot03();
 virtual void slot04(); virtual void slot05(); virtual void slot06(); virtual void slot07();
 virtual void slot08(); virtual void slot09(); virtual void slot10(); virtual void slot11();
 virtual void slot12(); virtual void slot13(); virtual void slot14(); virtual void slot15();
 virtual void slot16(); virtual void slot17(); virtual void slot18(); virtual void slot19();
 virtual void slot20(); virtual void slot21(); virtual void slot22(); virtual void slot23();
 virtual void slot24(); virtual void slot25(); virtual unsigned frame();
};
class GameClientRandomVariable { public: float getValue() const; char pad[12]; };
class GlobalData; extern GlobalData *TheWritableGlobalData;
struct Rva0044A6A0Globals { char pad[0xe28]; GameClientRandomVariable random; bool randomized; char pad35[3]; unsigned int opacity; };
class Rva0044A6A0 {
public:
 void update();
 char pad[0x12c4]; std::list<Rva0044A6A0Entry *> entries; Rva00449790Owner owner;
};
void Rva0044A6A0::update()
{
 owner.rva0044A2E0();
 for(std::list<Rva0044A6A0Entry *>::iterator it=entries.begin(); it!=entries.end();) {
  Rva0044A6A0Entry *entry=*it;
  if(!reinterpret_cast<BfmeGameLogicPause *>(TheGameLogic)->isGamePaused()) {
   if(reinterpret_cast<ClientRoot4120 *>(TheGameClient)->frame() >= entry->end || ((entry->flags&2) && (entry->animation->status&4))) {
    delete entry->animation;
    delete entry;
    it=entries.erase(it);
    continue;
   }
  }
  entry->x+=entry->vx;
  entry->vx*=entry->drag;
  entry->y+=entry->vy;
  entry->vy*=entry->drag;
  if(entry->flags&1) {
   unsigned remaining=entry->end-reinterpret_cast<ClientRoot4120 *>(TheGameClient)->frame();
   if(remaining<5) entry->animation->setAlpha(static_cast<float>(remaining)*0.2f);
  }
  int size;
  Rva0044A6A0Globals *globals=reinterpret_cast<Rva0044A6A0Globals *>(TheWritableGlobalData);
  if(globals->randomized) size=static_cast<int>(globals->random.getValue()+0.5f);
  else size=entry->size;
  entry->animation->setDimensions(size);
  entry->animation->draw(entry->x,entry->y,reinterpret_cast<Rva0044A6A0Globals *>(TheWritableGlobalData)->opacity);
  ++it;
 }
 if(entries.size()==0) {owner.x=-1;owner.y=-1;}
}
