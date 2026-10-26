// ?method@Rva00201D70@@QAEHXZ
// partial score=0.6113 date=2026-10-26
// ?method@Rva00201D70@@QAEHXZ
// cl: /O2 /DNDEBUG /MD /EHsc
class BfmeInnerCPB { public: void bfmeOneCPB(int,int); };
class BfmeSubCPB { public: void bfmeTwoCPB(int); };
class BfmeThingAIA { public: bool bfmeAskAIA(int); };
class BfmeX1011;
class BfmeLook1011 { public: BfmeX1011 *bfmeFind1011(int); };
class BfmeGlob940E { public: void bfmeCall940E(void*); };
extern BfmeLook1011 *TheGameLogic;
struct Rva00201D70Result { char pad[0xb0]; float m_b0; };
#define S(n) virtual void slot##n();
class Rva00201D70ObjectVirtual { public:
 S(00) S(04) S(08) S(0c) S(10) S(14) S(18) S(1c) S(20) S(24)
 virtual Rva00201D70Result *slot28();
};
class Rva00201D70Second { public:
 S(00) S(04) S(08) S(0c) S(10) S(14) S(18) S(1c) S(20) S(24) S(28) S(2c) S(30)
 virtual void slot34(void*);
};
class Rva00201D70First { public:
 S(00) S(04) S(08) S(0c) S(10) S(14) S(18) S(1c) S(20) S(24) S(28) S(2c) S(30)
 S(34) S(38) S(3c) S(40) S(44) S(48) S(4c) S(50) S(54) S(58) S(5c) S(60) S(64)
 virtual Rva00201D70Second *slot68();
};
#undef S
struct Rva00201D70ObjectBytes {
 char pad00[0x78]; int m_78; char pad7c[0x18]; unsigned int m_94;
 char pad98[0x90]; unsigned int m_128; char pad12c[0xd0]; Rva00201D70First *m_1fc;
 char pad200[4]; char *m_204; char pad208[0x13c]; unsigned char m_344;
};
struct Rva00201D70Data { char pad00[8]; unsigned int m_08; };
class Rva00201D70 { public: int method(); Rva00201D70ObjectBytes *getObject() const { return *(Rva00201D70ObjectBytes **)((char*)this-8); } char pad00[16]; unsigned char m_10; char pad11[3]; float m_14; };
int Rva00201D70::method() {
 Rva00201D70Data *data=*(Rva00201D70Data **)((char*)this-12);
 if(getObject()->m_128 & 0x1000) {
  if(!m_10) {
   Rva00201D70ObjectBytes *self=getObject();
   if(!(self->m_94 & 0x20) && self->m_204) {
    ((BfmeInnerCPB *)(self->m_204+0x20))->bfmeOneCPB(0,2);
    ((BfmeSubCPB *)self)->bfmeTwoCPB(0);
   }
   m_10=1;
  }
  Rva00201D70ObjectBytes *object=getObject();
  unsigned int count=data->m_08; if(!count) count=1;
  m_14 -= 1.0f/count;
  if(m_14 < 0.0f) {
   m_14=0;
   Rva00201D70ObjectBytes *target=(Rva00201D70ObjectBytes *)TheGameLogic->bfmeFind1011(object->m_78);
   if(target && ((BfmeThingAIA*)target)->bfmeAskAIA(0x6c)) target->m_1fc->slot68()->slot34(object);
   ((BfmeGlob940E*)TheGameLogic)->bfmeCall940E(object);
  } else {
   Rva00201D70Result *out=((Rva00201D70ObjectVirtual*)object)->slot28();
   if(out) out->m_b0=m_14;
  }
 }
 Rva00201D70ObjectBytes *object=getObject();
 if(object->m_344&1) return 0x3fffffff;
 if(object && (object->m_128&0x1000)) return 1;
 return 5;
}
