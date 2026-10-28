// stlport
// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WWDebug /Igame/Libraries/Source/WWVegas/WWSaveLoad /Igame/Libraries/Source/WWVegas/WW3D2 /Igame/Libraries/Source/Compression /Iinputs/reference/shims/sweep
// Rva00900FF0 table slot 3, retail 0x008FFF40 (889 bytes), with its private
// helper 0x008FF0F0 (181 bytes).  The helpers 0x008FEF60 and 0x008FF060 are
// defined here as TU statics too: VC7.1 then gives them retail's private
// register convention (object in EAX, vector in ECX) at their visible call
// sites.  0x008FF060 is claimed by Rva008FF060WaterMaterialTextureSwap.cpp and
// 0x008FEF60 stays a MASM row (one jump target differs); only 0x008FFF40 and
// 0x008FF0F0 are claimed from this file.  Identities stay address-derived.

#define _OPERATOR_NEW_DEFINED_ 1
#include <string.h>
#include <stddef.h>

#define _STLP_NO_EXCEPTIONS 1
#include <string>
#include <vector>
#include "wwstring.h"
class MeshClass;
class MaterialInfoClass;
class TextureClass
{
public:
	void Release_Ref(void);
};

class BFMEWaterTrackTextureHandle
{
public:
	BFMEWaterTrackTextureHandle() : m_texture(0) {}
	TextureClass *m_texture;
	~BFMEWaterTrackTextureHandle()
	{
		if (m_texture)
			m_texture->Release_Ref();
	}
};

extern BFMEWaterTrackTextureHandle BFMEGetWaterTrackTexture(
	char *name, int mipCount, int format);

typedef _STL::string Rva00900FF0InnerVector;

extern void j_0000b109();
class Rva00900FF0VecOfVec;
static __forceinline void destroyVec008FFF40(Rva00900FF0VecOfVec &value);
class Rva00900FF0VecOfVec : public _STL::_Vector_base<Rva00900FF0InnerVector, _STL::allocator<Rva00900FF0InnerVector> >
{
public:
 Rva00900FF0VecOfVec(const Rva00900FF0VecOfVec &source);
 ~Rva00900FF0VecOfVec() { destroyVec008FFF40(*this); }
 bool empty() const { return _M_start==_M_finish; }
 unsigned size() const { return (unsigned)(_M_finish-_M_start); }
 void pop_back() { if(!empty()) (--_M_finish)->~Rva00900FF0InnerVector(); }
 Rva00900FF0InnerVector *begin() { return _M_start; }
 Rva00900FF0InnerVector *end() { return _M_finish; }
 Rva00900FF0InnerVector &back() { return *(end()-1); }
};
static __forceinline void destroyVec008FFF40(Rva00900FF0VecOfVec &value)
{
 typedef void (Rva00900FF0VecOfVec::*Operation)();
 union { void *address; Operation method; } call;
 call.address = reinterpret_cast<void *>(j_0000b109);
 (value.*call.method)();
}

class Rva00900FF0VectorHolder
{
public:
	int *m_start;
	int *m_finish;
	int *m_endOfStorage;
};

class RenderObjClass
{
public:
	virtual void slot00(void);
	virtual void slot01(void);
	virtual void slot02(void);
	virtual void slot03(void);
	virtual void slot04(void);
	virtual MeshClass *Mesh_Self();
	virtual const char *Get_Name() const;
	virtual void slot07(const char *value);
	virtual void slot08(void);
	virtual void slot09(void);
	virtual void slot10(void);
	virtual void slot11(void);
	virtual void slot12(void);
	virtual void slot13(void);
	virtual void slot14(void);
	virtual void slot15(void);
	virtual void slot16(void);
	virtual void slot17(void);
	virtual void slot18(void);
	virtual void slot19(void);
	virtual void slot20(void);
	virtual void slot21(void);
	virtual void slot22(void);
	virtual void slot23(void);
	virtual void slot24(void);
	virtual void slot25(void);
	virtual void slot26(void);
	virtual int Get_Num_Sub_Objects(void);
	virtual void slot28(void);
	virtual RenderObjClass *Get_Sub_Object(int index);
	virtual void slot30(void);
	virtual RenderObjClass *Get_Sub_Object_By_Name(const char *,int * =0) const;
	virtual void slot32(void);
	virtual void slot33(void);
	virtual void slot34(void);
	virtual void slot35(void);
	virtual void slot36(void);
	virtual void slot37(void);
	virtual void slot38(void);
	virtual void slot39(void);
	virtual void slot40(void);
	virtual void slot41(void);
	virtual void slot42(void);
	virtual void slot43(void);
	virtual void slot44(void);
	virtual void slot45(void);
	virtual void slot46(void);
	virtual void slot47(void);
	virtual void slot48(void);
	virtual void slot49(void);
	virtual void slot50(void);
	virtual void slot51(void);
	virtual void slot52(void);
	virtual void slot53(void);
	virtual void slot54(void);
	virtual void slot55(void);
	virtual void slot56(void);
	virtual void slot57(void);
	virtual void slot58(void);
	virtual void slot59(void);
	virtual void slot60(void);
	virtual void slot61(void);
	virtual void slot62(void);
	virtual void slot63(void);
	virtual void slot64(void);
	virtual void slot65(void);
	virtual void slot66(void);
	virtual void slot67(void);
	virtual void slot68(void);
	virtual void slot69(void);
	virtual void slot70(void);
	virtual void slot71(void);
	virtual void slot72(void);
	virtual void slot73(void);
	virtual void slot74(void);
	virtual void slot75(void);
	virtual void slot76(void);
	virtual void slot77(void);
	virtual void slot78(void);
	virtual void slot79(void);
	virtual void slot80(void);
	virtual void slot81(void);
	virtual void slot82(void);
	virtual void slot83(void);
	virtual MaterialInfoClass *Get_Material_Info() const;
	virtual void slot85(void);
	virtual void slot86(void);
	virtual void slot87(void);
	virtual void slot88(void);
	virtual void slot89(void);
	virtual void slot90(void);
	virtual void slot91(float value);
	virtual void slot92(void);
	virtual void slot93(void);
	virtual void slot94(void);
	virtual void slot95(void);
	virtual void slot96(void);
	virtual void slot97(void);
	virtual void slot98(void);
	virtual void slot99(void);
	virtual void slot100(void);
	virtual void slot101(void);
	virtual void slot102(void);
	virtual void slot103(void);
	virtual void slot104(void);
	virtual void slot105(void);
	virtual void slot106(void);
	virtual void slot107(int value);
	virtual void slot108(void);
	virtual void slot109(void);
	virtual void slot110(void);
	virtual void slot111(void);
	virtual void slot112(void);
	virtual void slot113(void);
	virtual void slot114(void);
	virtual void slot115(void);
	virtual void slot116(void);
	virtual void slot117(void);
	virtual void slot118(void);
	virtual void slot119(void);
	virtual void slot120(void);
	virtual void slot121(void);
	virtual void slot122(void);
	virtual void slot123(void);
	virtual void slot124(void);
	virtual void replaceTexture(const BFMEWaterTrackTextureHandle &oldTexture,
		const BFMEWaterTrackTextureHandle &newTexture);
	virtual void slot126(int value);
	int m_ref_count;
};

extern RenderObjClass *Create_Render_Obj(const char *name);
extern void Rva008FEB90(RenderObjClass *object);


void Rva008FF6A0(RenderObjClass *object, const Rva00900FF0InnerVector &first,
	const Rva00900FF0InnerVector &second, int source);


class BfmeHandleCX
{
public:
	BfmeHandleCX(void) { m_bfmeThing = 0; }
	~BfmeHandleCX(void)
	{
		if (m_bfmeThing)
			m_bfmeThing->Release_Ref();
	}

	TextureClass *m_bfmeThing;			// +0x00
};

class MaterialInfoClass
{
public:
	virtual void Delete_This();
	virtual void _bfme_mi_v1();
	virtual void _bfme_mi_v2();
	virtual void _bfme_mi_v3();
	virtual void _bfme_mi_v4();
	virtual void *_bfme_mi_slot14();

	BfmeHandleCX Get_Texture(int index) const;

	int m_ref_count;
	char m_pad_08[0x30 - 8];
	int m_bfme30;
};

class Rva0092C3E0Trampoline
{
public:
	void invoke(BfmeHandleCX *out, TextureClass **src);
};

class Bfme5TextureArray
{
public:
	void bfmeSetSlot(int i, TextureClass **src);
};

static __declspec(noinline) bool Rva008FEF60Method(RenderObjClass *self, TextureClass **src, int index)
{
	if (!self)
		return false;
	if (!*src)
		return false;

	MaterialInfoClass *material = self->Get_Material_Info();
	if (!material)
		return false;

	if (material->m_bfme30 <= index)
		return false;

	Rva0092C3E0Trampoline *sink = (Rva0092C3E0Trampoline *)self->Mesh_Self();

	BfmeHandleCX handle = material->Get_Texture(index);
	if (handle.m_bfmeThing == *src)
	{
		if (--material->m_ref_count == 0)
			material->Delete_This();

		return false;
	}

	sink->invoke(&handle, src);

	((Bfme5TextureArray *)material)->bfmeSetSlot(index, src);

	if (--material->m_ref_count == 0)
		material->Delete_This();

	return true;
}


static __declspec(noinline) bool Rva008FF060Method(RenderObjClass *self, char *name, int index)
{
    if (!self)
        return false;
    bool result = false;
    BFMEWaterTrackTextureHandle handle = BFMEGetWaterTrackTexture(name, 0, 0);
    if (handle.m_texture)
        result = Rva008FEF60Method(self, &handle.m_texture, index);
    return result;
}


static __declspec(noinline) bool Rva008FF0F0Method(RenderObjClass *object, Rva00900FF0VecOfVec *first, Rva00900FF0VecOfVec *second, int index)
{
    if (!object) return false;
    if (first->empty()) return false;
    char *meshName=(char *)first->back().c_str();
    char *textureName=(char *)second->back().c_str();
    bool result=false;
    const char *objectName=object->Get_Name();
    if (strcmp(objectName,meshName)==0)
        result=Rva008FF060Method(object,textureName,index);
    else {
        RenderObjClass *sub=object->Get_Sub_Object_By_Name(meshName);
        if(sub) {
            result=Rva008FF060Method(sub,textureName,index);
            if(--sub->m_ref_count==0) sub->slot00();
        }
    }
    return result;
}

class Rva00900FF0Base
{
public:
	virtual const char *slot00(void);
	virtual void slot01(void);
	virtual void slot02(void);
	char m_base[0x10];
};

class Rva00900FF0 : public Rva00900FF0Base
{
public:
	virtual void Rva008FFF40(void);

private:
	StringClass m_str14;
	StringClass m_str18;
	Rva00900FF0VecOfVec m_vec1c;
	Rva00900FF0VecOfVec m_vec28;
	Rva00900FF0VecOfVec m_vec34;
	Rva00900FF0VecOfVec m_vec40;
	Rva00900FF0VecOfVec m_vec4c;
	Rva00900FF0VectorHolder m_vector58;
	float m_field64;
	int m_field68;
	int m_field6c;
	RenderObjClass *m_render70;
};


void Rva00900FF0::Rva008FFF40(void)
{
    m_render70=Create_Render_Obj(m_str18);
    if(!m_render70) return;
    m_render70->slot07(slot00());
    float delta=m_field64-1.0f;
    *(unsigned *)&delta &= 0x7fffffff;
    bool close=delta>0.01f;
    bool hasFlags=(m_field68&0xffffff)!=0;
    bool hasBoth=!m_vec1c.empty()&&!m_vec28.empty();
    bool hasPerMesh=!m_vec40.empty();
    if(!close&&!hasFlags&&!hasBoth&&!hasPerMesh) return;
    if(close) m_render70->slot91(m_field64);
    if(!m_vec28.empty()&&m_vec1c.empty()) {
        Rva008FEB90(m_render70);
        if(!m_vec34.empty()) {
            Rva00900FF0VecOfVec first(m_vec34);
            Rva00900FF0VecOfVec second(m_vec28);
            while(!first.empty()) {
                Rva008FF0F0Method(m_render70,&first,&second,m_field6c);
                second.pop_back();
                first.pop_back();
            }
        } else {
            char *name=(char *)m_vec28.back().c_str();
            Rva008FF060Method(m_render70,name,m_field6c);
            for(int i=0;i<m_render70->Get_Num_Sub_Objects();++i) {
                RenderObjClass *sub=m_render70->Get_Sub_Object(i);
                if(sub) {
                    Rva008FF060Method(sub,name,m_field6c);
                    if(--sub->m_ref_count==0) sub->slot00();
                }
            }
        }
    } else if(!m_vec40.empty()) {
        Rva008FEB90(m_render70);
        for(unsigned i=0;i<m_vec40.size();++i)
            Rva008FF6A0(m_render70,m_vec40.begin()[i],m_vec4c.begin()[i],m_vector58.m_start[i]);
    } else if(hasBoth) {
        Rva008FEB90(m_render70);
        char *textureName=(char *)m_vec28.back().c_str();
        char *oldTextureName=(char *)m_vec1c.back().c_str();
        m_render70->replaceTexture(BFMEGetWaterTrackTexture(oldTextureName,0,0),BFMEGetWaterTrackTexture(textureName,0,0));
    }
    if(hasFlags) {
        Rva008FEB90(m_render70);
        m_render70->slot126(m_field68);
    }
}
