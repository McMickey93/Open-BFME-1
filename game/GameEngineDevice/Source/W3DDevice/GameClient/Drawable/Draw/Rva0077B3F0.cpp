// cl: /O2 /Ob2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /Iinputs/reference/shims/sweep /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib /Iinputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WWDebug

// Retail body at RVA 0x0077B3F0, 1209 bytes.
// The owner class is not proven; this address-derived view avoids assigning a false identity.
// ABI and the 0x4C frame follow the direct calls and retail boundary.

#include "matrix3d.h"
#include "ascii_string.h"
#include <stddef.h>

typedef unsigned int U32;
typedef unsigned char U8;

struct Rva0077B3F0Coord { float x, y, z; };
class Rva0077B3F0Particle
{
public:
    void rva005BDE00(const Rva0077B3F0Coord *); // ILT 00021832
    void rva005BDD90();                       // ILT 0000FFD3
    void rva005C1FB0();                       // ILT 0000E525
};
Rva0077B3F0Particle *rva005CFF50();             // ILT 00001B18

class Rva0077B3F0HandleBase
{
public:
    Rva0077B3F0HandleBase &rva005C21D0(const Rva0077B3F0HandleBase &) throw();
    void rva005C2240() throw();
    Rva0077B3F0Particle *p00;
    Rva0077B3F0HandleBase *p04, *p08;
};
class Rva0077B3F0Handle : public Rva0077B3F0HandleBase
{
public:
    ~Rva0077B3F0Handle() throw(); // ILT 00013994 -> 001DA440
    operator bool() const { return p00 != 0; }
    Rva0077B3F0Particle *operator->() const
    {
        if (!p00) return rva005CFF50();
        return p00;
    }
};
struct Rva0077B3F0Template;
class Rva0077B3F0Manager
{
public:
    Rva0077B3F0Template *rva005C9F90(const AsciiString &) const;
    Rva0077B3F0Handle rva005C3A30(const Rva0077B3F0Template *, bool) throw();
};

// Virtual slot names are address-derived. No unrelated virtual identities.
#define SLOT(n) virtual void slot##n();
#define SLOTS_00_0C SLOT(00) SLOT(04) SLOT(08) SLOT(0C)
#define SLOTS_10_1C SLOT(10) SLOT(14) SLOT(18) SLOT(1C)
#define SLOTS_20_2C SLOT(20) SLOT(24) SLOT(28) SLOT(2C)
#define SLOTS_30_3C SLOT(30) SLOT(34) SLOT(38) SLOT(3C)
#define SLOTS_40_4C SLOT(40) SLOT(44) SLOT(48) SLOT(4C)
#define SLOTS_50_5C SLOT(50) SLOT(54) SLOT(58) SLOT(5C)
#define SLOTS_60_6C SLOT(60) SLOT(64) SLOT(68) SLOT(6C)
#define SLOTS_70_7C SLOT(70) SLOT(74) SLOT(78) SLOT(7C)
#define SLOTS_80_8C SLOT(80) SLOT(84) SLOT(88) SLOT(8C)
#define SLOTS_90_9C SLOT(90) SLOT(94) SLOT(98) SLOT(9C)
#define SLOTS_A0_AC SLOT(A0) SLOT(A4) SLOT(A8) SLOT(AC)
#define SLOTS_B0_BC SLOT(B0) SLOT(B4) SLOT(B8) SLOT(BC)
#define SLOTS_C0_CC SLOT(C0) SLOT(C4) SLOT(C8) SLOT(CC)
#define SLOTS_D0_DC SLOT(D0) SLOT(D4) SLOT(D8) SLOT(DC)

class Rva0077B3F0Terrain
{
public:
    SLOTS_00_0C SLOTS_10_1C SLOTS_20_2C SLOTS_30_3C
    SLOT(40) SLOT(44) SLOT(48)
    virtual bool slot4C(float, float, float *, float *);
};
class Rva0077B3F0Render
{
public:
    SLOTS_00_0C SLOTS_10_1C SLOTS_20_2C SLOTS_30_3C SLOTS_40_4C SLOT(50)
    virtual void slot54(const Matrix3D &);
    SLOT(58) SLOT(5C) SLOTS_60_6C SLOTS_70_7C SLOTS_80_8C SLOTS_90_9C
    SLOTS_A0_AC SLOTS_B0_BC SLOTS_C0_CC SLOT(D0)
    virtual void slotD4(int bone);
    SLOT(D8) SLOT(DC)
    virtual void slotE0(int bone, const Matrix3D &, bool);
};
class Rva0077B3F0Secondary
{
public:
    SLOTS_00_0C SLOTS_10_1C SLOTS_20_2C SLOTS_30_3C SLOTS_40_4C SLOTS_50_5C
    SLOT(60) SLOT(64)
    virtual bool slot68(int); // base -> 00762F40, real ret4
    SLOT(6C)
    virtual void slot70();    // base -> 00764290
};
class Rva0077B3F0Primary
{
public:
    SLOTS_00_0C SLOTS_10_1C SLOTS_20_2C SLOTS_30_3C SLOTS_40_4C SLOTS_50_5C
    SLOTS_60_6C SLOTS_70_7C SLOTS_80_8C SLOTS_90_9C SLOTS_A0_AC SLOTS_B0_BC
    SLOTS_C0_CC SLOTS_D0_DC SLOT(E0) SLOT(E4) SLOT(E8)
    virtual void slotEC();    // base -> 0075CC80
};
class Rva0077B3F0Contain
{
public:
    SLOTS_00_0C SLOTS_10_1C SLOT(20)
    virtual bool slot24();
};
// ILT 0x0000460B -> matched AIUpdateInterface::getTurretRotAndPitch (0x0026EAF0).
enum WhichTurretType { TURRET_INVALID = -1 };
class AIUpdateInterface
{
public:
    bool getTurretRotAndPitch(WhichTurretType tur, float *turretAngle, float *turretPitch) const;
};
struct Rva0077B3F0Object
{
    U8 unknown000[0x1fc];
    Rva0077B3F0Contain *p1fc;
    U8 unknown200[4];
    AIUpdateInterface *p204;
    U8 unknown208[0xc];
    Rva0077B3F0Object *p214;
    U8 unknown218[0x344-0x218];
    U8 b344;
};
class Rva0077B3F0Tint
{
public:
    Rva0077B3F0Tint &rva0075EF90(const Rva0077B3F0Tint &);
};
class Rva0077B3F0Drawable
{
public:
    void rva00411EF0();
    void rva00421830(void *); // not BitFlags; one unused stack arg, ret4
    U8 unknown000[0x68];
    Rva0077B3F0Tint *p068;
    U8 unknown06c[0xfc-0x6c];
    Rva0077B3F0Object *p0fc;
};
class Rva0077B3F0Client
{
public:
    SLOTS_00_0C SLOTS_10_1C SLOT(20) SLOT(24) SLOT(28)
    virtual Rva0077B3F0Drawable *slot2C(U32);
    SLOTS_30_3C SLOTS_40_4C SLOTS_50_5C SLOT(60) SLOT(64)
    virtual U32 slot68();
};
class GameLogic;
extern GameLogic *TheGameLogic;
struct Rva0077B3F0Logic { U8 unknown000[0x10c]; int i10c; };
struct Rva0077B3F0Shadow
{
    U32 unknown000;
    bool b004;
    U8 unknown005[0x34-5];
    int i034;
};
struct Rva0077B3F0Node
{
    U32 unknown000;
    Rva0077B3F0Node *p004, *p008, *p00c;
    U32 value010;
};
Rva0077B3F0Node *rva0082B870(Rva0077B3F0Node *);
bool rva007397E0(Rva0077B3F0Render *, float, float, float);
class Rva0077B3F0Radius
{
public:
    void rva004585F0();
    U8 unknown[0x98];
};
struct Rva0077B3F0Data
{
    U8 unknown000[0x14];
    AsciiString WadingParticleSys;
    U8 unknown018[0x69-0x18];
    bool NoRotate;
    U8 unknown06a[0xdc-0x6a];
    bool ParticlesAttachedToAnimatedBones;
    U8 unknown0dd[0x10a-0xdd];
    bool ShowShadowWhileContained;
    U8 unknown10b[0x131-0x10b];
    bool MultiPlayerOnly;
    U8 unknown132;
    bool HighDetailOnly;
};

class TerrainLogic;
extern TerrainLogic *TheTerrainLogic;
extern Rva0077B3F0Manager *g_va012F64BC;
extern U32 g_rva0075b2e0_value;
// Retail 0x012F1464 is EA's GameClient *TheGameClient, defined once in
// game/GameEngine/Source/GameClient/GameClient.cpp.  Rva0077B3F0Client is a
// TU-local view of that object reached through the canonical global.
class GameClient;
extern GameClient *TheGameClient;
static inline Rva0077B3F0Client *rva0077B3F0Client()
{
    return (Rva0077B3F0Client *)TheGameClient;
}

// Retain the reference-return min shape: retail selects either argument home
// or H+214 by address before loading the unsigned scalar.
inline const U32 &rva0077B3F0Min(const U32 &a, const U32 &b)
{
    return a < b ? a : b;
}
inline bool rva0077B3F0NameNotEmpty(const AsciiString &s)
{
    const U8 *data = *(const U8 *const *)&s;
    return data && *(const unsigned short *)(data+4) != 0;
}

// The state record at owner+0x10: two 0x18-byte turret entries at +0xF0
// (two words, two floats, two bone indices) and a ready byte at +0x124.
struct Rva0075F400Turret
{
    U32 unknown000[2];
    float f008, f00c;
    int i010, i014;
};
struct Rva0075F400State
{
    U8 unknown000[0xf0];
    Rva0075F400Turret turrets[2];
    U8 unknown120[4];
    bool b124;
};
// Retail 0x012ED524 is EA's GameEngine *TheGameEngine; +0x38 is the float
// AttachmentTransform007629F0.cpp reads as value38.
class GameEngine;
extern GameEngine *TheGameEngine;
struct Rva0075F400Engine { U8 unknown000[0x38]; float f038; };

class Rva0077B3F0
{
public:
    void method(const Matrix3D *transform);
    void rva0076C080();
    void rva007629F0(Matrix3D &);
    void rva0075F400();
    void rva00779F10();
    void rva0076EFF0();
    void rva0075C9F0(Rva0077B3F0Render *);
    void rva0075F810();

    void *p000;
    Rva0077B3F0Data *p004;
    Rva0077B3F0Drawable *p008;
    Rva0077B3F0Secondary s00c;
    const Rva0075F400State *p010;
    void *p014;
    Rva0077B3F0Handle h018;
    U8 unknown024[0x2e-0x24];
    bool b02e, b02f;
    U8 unknown030[4];
    Rva0077B3F0Render *p034;
    U32 unknown038;
    Rva0077B3F0Shadow *p03c;
    U8 unknown040[0xc];
    void *p04c, *p050;
    U32 unknown054;
    void *p058, *p05c;
    U8 unknown060[0x24];
    bool b084;
    U8 unknown085[3];
    U32 u088;
    Rva0077B3F0Node *p08c;
    U32 u090, unknown094, unknown098, u09c, u0a0;
    U8 unknown0a4[0x164-0xa4];
    U8 b164;
    U8 unknown165[0x170-0x165];
    bool b170, b171;
    U8 unknown172[6];
    Rva0077B3F0Radius s178;
    bool b210;
    U8 unknown211[3];
    U32 u214, u218, u21c;
    float f220, f224, f228;
    U8 unknown22c[0x26c-0x22c];
    float f26c, f270, f274, f278;
};
typedef char check_handle_size[sizeof(Rva0077B3F0Handle)==12 ? 1 : -1];
typedef char check_matrix_size[sizeof(Matrix3D)==48 ? 1 : -1];
typedef char check_config_131[offsetof(Rva0077B3F0Data,MultiPlayerOnly)==0x131 ? 1 : -1];
typedef char check_owner_018[offsetof(Rva0077B3F0,h018)==0x18 ? 1 : -1];
typedef char check_owner_034[offsetof(Rva0077B3F0,p034)==0x34 ? 1 : -1];
typedef char check_owner_178[offsetof(Rva0077B3F0,s178)==0x178 ? 1 : -1];
typedef char check_owner_210[offsetof(Rva0077B3F0,b210)==0x210 ? 1 : -1];
typedef char check_owner_26c[offsetof(Rva0077B3F0,f26c)==0x26c ? 1 : -1];
typedef char check_object_204[offsetof(Rva0077B3F0Object,p204)==0x204 ? 1 : -1];
typedef char check_state_124[offsetof(Rva0075F400State,b124)==0x124 ? 1 : -1];

void Rva0077B3F0::method(const Matrix3D *transform)
{
    if (!b084 && u088) return;
    const Rva0077B3F0Data *data = p004;
    if (data->MultiPlayerOnly && ((Rva0077B3F0Logic *)TheGameLogic)->i10c != 1 && ((Rva0077B3F0Logic *)TheGameLogic)->i10c != 5)
        return;
    if (data->HighDetailOnly && u0a0) return;
    // Preserve retail order: clear the update byte before testing the state byte.
    volatile U8 *fieldBytes = (volatile U8 *)this;
    fieldBytes[0x84] = 0;

    if ((fieldBytes[0x164] & 0x10) && rva0077B3F0NameNotEmpty(data->WadingParticleSys))
    {
        const Vector3 translation = transform->Get_Translation();
        Rva0077B3F0Coord pos;
        pos.x = translation.X;
        pos.y = translation.Y;
        pos.z = translation.Z;
        reinterpret_cast<Rva0077B3F0Terrain *>(TheTerrainLogic)->slot4C(pos.x, pos.y, &pos.z, 0);
        if (h018)
            h018->rva005BDE00(&pos);
        else
        {
            Rva0077B3F0Template *t = g_va012F64BC->rva005C9F90(data->WadingParticleSys);
            if (t)
            {
                h018.rva005C21D0(g_va012F64BC->rva005C3A30(t,true));
                if (h018)
                {
                    h018->rva005BDE00(&pos);
                    h018->rva005BDD90();
                }
            }
        }
    }
    else if (h018)
    {
        h018->rva005C1FB0();
        h018.rva005C2240();
    }

    if (g_rva0075b2e0_value != u09c) rva0076C080();
    if (p034)
    {
        Matrix3D mtx(true);
        if (data->NoRotate) mtx.Set_Translation(transform->Get_Translation());
        else mtx = *transform;
        rva007629F0(mtx);
        p034->slot54(mtx);
        if (b210)
        {
            U32 now = rva0077B3F0Client()->slot68();
            U32 delta = now - u21c;
            u21c = now;
            u218 = rva0077B3F0Min(u218 + delta,u214);
            float fraction = float(u218) / float(u214);
            rva007397E0(p034, fraction*f220, fraction*f224, fraction*f228);
            if (u218 >= u214) b210 = false;
        }
    }
    rva0075F400();
    rva00779F10();
    if (data->ParticlesAttachedToAnimatedBones) s00c.slot68(0);
    if (u090)
    {
        for (Rva0077B3F0Node *n=p08c->p008; n!=p08c; n=rva0082B870(n))
        {
            Rva0077B3F0Drawable *child = rva0077B3F0Client()->slot2C(n->value010);
            if (child)
            {
                if (p008->p068 && child->p068)
                    child->p068->rva0075EF90(*p008->p068);
                child->rva00411EF0();
                child->rva00421830(0);
            }
        }
    }
    ((Rva0077B3F0Primary*)this)->slotEC();
    rva0076EFF0();
    Rva0077B3F0Object *object=p008->p0fc;
    Rva0077B3F0Object *containing;
    if (object && (containing=object->p214) && !data->ShowShadowWhileContained &&
        !containing->p1fc->slot24())
    {
        if (!b02f) b02f=true;
    }
    else if (b02e && b02f) b02f=false;
    if (object && p03c && p03c->i034==1 && (object->b344 & 1))
    {
        b02f=true;
        p03c->b004=false;
    }
    if ((p058!=p05c && b171) || (p04c!=p050 && b170)) s00c.slot70();
    rva0075C9F0(p034);
    s178.rva004585F0();
    rva0075F810();
}

// Retail 0x0075F400 (823 bytes), reached from method() through ILT 0x00043329.
// For each of the two turret entries with a bone, it asks the object's AI for
// the turret angle and pitch and poses the bones on the render object. With
// owner+0x14 set, it adds the entry's base angle and pitch and keeps a
// previous/current pair per axis (+0x26C/+0x274 angle, +0x270/+0x278 pitch,
// below -1000 means unset). Each new 1.0 engine fraction shifts the pair;
// between frames the angle is interpolated along the short arc.
void Rva0077B3F0::rva0075F400()
{
    if (!p010 || !p010->b124)
        return;

    for (int slot = 0; slot < 2; ++slot)
    {
        const Rva0075F400Turret &tur = p010->turrets[slot];
        float angle = 0;
        float pitch = 0;
        if (tur.i010 || tur.i014)
        {
            float fraction = ((Rva0075F400Engine *)TheGameEngine)->f038;
            Rva0077B3F0Object *obj = p008->p0fc;
            if (obj && obj->p204)
                obj->p204->getTurretRotAndPitch((WhichTurretType)slot, &angle, &pitch);

            if (tur.i010)
            {
                float rotation = 0.0f;
                if (p014)
                {
                    angle += tur.f008;
                    if (f26c < -1000.0f)
                    {
                        f274 = angle;
                        f26c = angle;
                        rotation = angle;
                    }
                    else if (fraction == 1.0f)
                    {
                        f26c = f274;
                        f274 = angle;
                        rotation = f26c;
                    }
                    else
                    {
                        float delta = f274 - f26c;
                        if (delta > 3.14159265f)
                            delta -= 6.28318531f;
                        else if (delta < -3.14159265f)
                            delta += 6.28318531f;
                        rotation = delta * fraction + f26c;
                    }
                }
                Matrix3D turretXfrm(1);
                turretXfrm.Rotate_Z(rotation);
                if (p034)
                {
                    p034->slotD4(tur.i010);
                    p034->slotE0(tur.i010, turretXfrm, false);
                }
            }

            if (tur.i014)
            {
                if (p014)
                {
                    pitch += tur.f00c;
                    if (f270 < -1000.0f)
                        f270 = f278 = pitch;
                    else if (fraction == 1.0f)
                    {
                        f270 = f278;
                        f278 = pitch;
                    }
                }
                Matrix3D turretPitchXfrm(1);
                turretPitchXfrm.Rotate_Y(-pitch);
                if (p034)
                {
                    p034->slotD4(tur.i014);
                    p034->slotE0(tur.i014, turretPitchXfrm, false);
                }
            }
        }
    }
}
