// ??0W3DModelDraw@@QAE@PAVThing@@PBVModuleData@@@Z
// partial score=0.9367 date=2026-10-28
// Banked LOD-switch variant: the shared `m_lodResult = r` epilogue moved into
// each case body (per-target stores): 1179/1185B, 75 non-reloc diffs (was 82).
// Single structural residue at +0x43D (retail jump table vs our if-chain).
// Ruled out: goto-free break-only switch (82); no-default (898, layout blowup);
// signed switch without the (unsigned int) cast (906, early drift).
// ??0W3DModelDraw@@QAE@PAVThing@@PBVModuleData@@@Z
// cl: /DNDEBUG /MD /EHsc /O2 /D_STLP_USE_STATIC_LIB /DBFME_STLP_NODE_ALLOC /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WWDebug
// stlport
// Partial reconstruction of retail 0x00773360, complete extent 1185 bytes.
// Identity: constructor and destructor install W3DModelDraw primary/secondary
// vtables; constructor calls DrawableModule(Thing*, ModuleData*) at 00113DA0.
// Improved from preserved alternative c8b1c49e94ecda6b after verified sibling
// 8cbb9ab0 established the exact +130 follower and +13C string-vector layouts.
// Native Vector3, the typed Drawable::getObject accessor, and Matrix3D copy/
// Make_Identity produce 1183 bytes, 82 differing non-relocation bytes, 32
// relocations (three sites drift), first byte mismatch +43A. Shape is 0.989,
// one structural difference: final LOD branch chain instead of the retail
// five-entry jump table. Source equality/identity of all legacy declarations
// is NOT asserted: production landing needs canonical owning-header adoption
// and the full dependent verification gate. No assembly or production edits.
// Native signed/unsigned five-distinct-case and volatile pending-LOD variants
// give 1168 bytes/896 differences; preferred grouped unsigned tail retained.
// Receipts: build/worker2-773360-*-probe.log. model=gpt-6, 2026-10-20.

#define __PLACEMENT_VEC_NEW_INLINE
#include "vector3.h"
#include "matrix3d.h"
#include <string>
#include <list>
#include <set>
#include <vector>
#include <stddef.h>
#include <string.h>


typedef bool Bool;
typedef int ParticleSystemID;

// Retail allocates a 0x1C list node at this+0x48 (the 0x0077B090 destructor
// frees the same node with `push 0x1C`), so the element is 20 bytes with the
// particle-system ID as its first dword -- the value the matched
// W3DModelDraw_updateSubObjectsFromShroud reads at node+8.  The remaining
// 16 bytes are not witnessed by any matched body, so the type keeps the
// address token rather than a guessed name.
struct Rva00773360ParticleEntry
{
	ParticleSystemID m_id;
	unsigned char m_unwitnessed[16];
};

class Thing;
class ModuleData;
class Matrix3D;
class AsciiString
{
public:
	AsciiString() : m_data(0) {}
	~AsciiString();
	void set(const char *, int);
	void releaseBuffer();

	char *m_data;
};

class DrawableModule
{
public:
	DrawableModule(Thing *, const ModuleData *);
	virtual ~DrawableModule();
	virtual void drawModuleAnchor();

private:
	unsigned char m_data[8];
};

class W3DModelDrawInterface
{
public:
	virtual void w3dModelDrawInterfaceAnchor();
};

class BfmeParticleSystemHandle
{
public:
	BfmeParticleSystemHandle() throw(...)
		: m_system(0), m_previous(0), m_next(0)
	{
	}

	~BfmeParticleSystemHandle() throw();

	void *m_system;
	BfmeParticleSystemHandle *m_previous;
	BfmeParticleSystemHandle *m_next;
};

// The three opaque members use the existing unwind pins.  They are each three
// dwords in this object; the retail constructor's explicit stores prove that
// shape even though their gameplay names are not needed here.
class Gen_uwm_00034329
{
public:
	Gen_uwm_00034329() : m_00(0), m_04(0), m_08(0) {}
	~Gen_uwm_00034329();

	int m_00;
	int m_04;
	int m_08;
};

class Gen_uwm_0000b073
{
public:
	Gen_uwm_0000b073() : m_00(0), m_04(0), m_08(0) {}
	~Gen_uwm_0000b073();

	int m_00;
	int m_04;
	int m_08;
};

class Gen_uwm_0000b109
{
public:
	Gen_uwm_0000b109() : m_00(0), m_04(0), m_08(0) {}
	~Gen_uwm_0000b109();

	int m_00;
	int m_04;
	int m_08;
};

class RadiusDecal
{
public:
	RadiusDecal();
	~RadiusDecal();

	unsigned char m_data[0x10];
};

class RadiusDecalTemplate
{
public:
	RadiusDecalTemplate();
	~RadiusDecalTemplate();

	unsigned char m_data[0x34];
};

// The retail callbacks at ILT 0x3e94b/0x35972 construct and destroy a
// three-dword value.  Keeping this as a POD-shaped non-trivial element lets
// STLport's vector-constructor helper supply the same four-element EH packet.
struct Gen_p12cd
{
public:
	int m_00;
	int m_04;
	int m_08;
};

class BfmeZeroFields10
{
public:
	BfmeZeroFields10()
	{
		memset(this, 0, sizeof(*this));
	}

	int m_00;
	int m_04;
	int m_08;
	int m_0c;
	int m_10;
	int m_14;
	int m_18;
	int m_1c;
	int m_20;
	int m_24;
};

struct BfmeSlot
{
	BfmeSlot() : m_head(0) {}

	int m_head;
	int m_pad[6];
};

class Object;
class Drawable
{
public:
	const Matrix3D *getTransformMatrix() const;

	unsigned char m_data[0xfc];
	Object *m_object;
 Object *getObject() { return m_object; }
};

class Object
{
public:
	int getNightIndicatorColor() const;
	int getIndicatorColor() const;
};

class GlobalData
{
public:
	unsigned char m_data[0x218];
	int m_timeOfDay;
};

class GameLODManager
{
public:
	unsigned char m_data[0x16c4];
	int m_level;
};

extern GlobalData *TheWritableGlobalData;
extern GameLODManager *TheGameLODManager;


class RenderObjClass;
struct Gen_t_00777e90_p32cd
{
 RenderObjClass *m_renderObject;
 std::string m_boneName;
 Vector3 m_rotate;
 int m_countdown;
};
typedef char verifiedFollowerSize[(sizeof(Gen_t_00777e90_p32cd)==32)?1:-1];

class W3DModelDraw : public DrawableModule, public W3DModelDrawInterface
{
public:
	W3DModelDraw(Thing *, const ModuleData *);

	// This is a local ABI probe; keeping the packet public lets the compile-time
	// checks below reject an accidental STL layout drift.
	public:
	void *m_state10;
	void *m_state14;
	BfmeParticleSystemHandle m_particleHandle;
	int m_indicatorColor;
	int m_modelCondition;
	Bool m_hidden;
	Bool m_fullyObscuredByShroud;
	Bool m_isHidden;
	Bool m_hasShadow;
	Bool m_hasTerrainDecal;
	unsigned char m_pad31[3];
	void *m_renderObject;
	AsciiString m_modelName;
	void *m_shadow;
	void *m_terrainDecal;
	void *m_trackRenderObject;
	_STL::list<Rva00773360ParticleEntry> m_particleSystemIDs;
	Gen_uwm_00034329 m_member4c;
	Gen_uwm_00034329 m_member58;
	Bool m_ready;
	Bool m_ready2;
	Bool m_ready3;
	Bool m_ready4;
	int m_flag68;
	int m_field6c;
	float m_field70;
	int m_field74;
	float m_field78;
	float m_field7c;
	float m_field80;
	Bool m_field84;
	int m_field88;
	_STL::set<int> m_tree;
	AsciiString m_string98;
	int m_field9c;
	int m_lodResult;
	int m_lodResult2;
	int m_fielda8;
	_STL::vector<Gen_p12cd> m_recoil[4];
	BfmeSlot m_slots[3];
	std::vector<Gen_t_00777e90_p32cd> m_field130;
	std::vector<std::string> m_field13c;
	BfmeZeroFields10 m_zero148;
	Bool m_field170;
	Bool m_field171;
	Bool m_field172;
	Bool m_field173;
	int m_field174;
	RadiusDecal m_radiusDecal;
	RadiusDecalTemplate m_radiusDecalTemplate;
	RadiusDecal m_radiusDecal2;
	RadiusDecalTemplate m_radiusDecalTemplate2;
	AsciiString m_string200;
	AsciiString m_strings[2];
	int m_field20c;
	Bool m_field210;
	unsigned char m_pad211[3];
	int m_field214;
	int m_field218;
	int m_field21c;
	unsigned char m_pad220[0xc];
	int m_field22c;
	Bool m_field230;
	Bool m_field231;
	Bool m_field232;
	unsigned char m_pad233;
	Matrix3D m_matrix;
 float m_field264;
	int m_field268;
	float m_bounds[4];
};

typedef char W3DScriptedModelDraw_size_check
	[(sizeof(W3DModelDraw) == 0x27c) ? 1 : -1];
typedef char W3DScriptedModelDraw_handle_check
	[(offsetof(W3DModelDraw, m_particleHandle) == 0x18) ? 1 : -1];
typedef char W3DScriptedModelDraw_list_check
	[(offsetof(W3DModelDraw, m_particleSystemIDs) == 0x48) ? 1 : -1];
typedef char W3DScriptedModelDraw_tree_check
	[(offsetof(W3DModelDraw, m_tree) == 0x8c) ? 1 : -1];
typedef char W3DScriptedModelDraw_recoil_check
	[(offsetof(W3DModelDraw, m_recoil) == 0xac) ? 1 : -1];
typedef char W3DScriptedModelDraw_decal_check
	[(offsetof(W3DModelDraw, m_radiusDecal) == 0x178) ? 1 : -1];
typedef char W3DScriptedModelDraw_strings_check
	[(offsetof(W3DModelDraw, m_string200) == 0x200) ? 1 : -1];
typedef char W3DScriptedModelDraw_string_array_check
	[(offsetof(W3DModelDraw, m_strings) == 0x204) ? 1 : -1];
typedef char W3DScriptedModelDraw_zero_packet_check
	[(offsetof(W3DModelDraw, m_zero148) == 0x148) ? 1 : -1];

// ??0W3DScriptedModelDraw@@QAE@PAVThing@@PBVModuleData@@@Z
W3DModelDraw::W3DModelDraw(Thing *thing,
	const ModuleData *moduleData)
	: DrawableModule(thing, moduleData)
	, m_particleHandle()
	, m_particleSystemIDs()
	, m_member4c()
	, m_member58()
	, m_tree()
	, m_string98()
	, m_recoil()
	, m_slots()
	, m_field130()
	, m_field13c()
	, m_zero148()
	, m_radiusDecal()
	, m_radiusDecalTemplate()
	, m_radiusDecal2()
	, m_radiusDecalTemplate2()
	, m_string200()
	, m_strings()
{
	m_flag68 = 1;
	m_ready = true;
	m_ready2 = false;
	m_state14 = 0;
	m_state10 = 0;
	m_indicatorColor = 0;
	m_renderObject = 0;
	m_modelName.set("", 0);
	m_shadow = 0;
	m_isHidden = true;
	m_hasShadow = false;
	m_hasTerrainDecal = false;
	m_terrainDecal = 0;
	m_trackRenderObject = 0;
	m_modelCondition = -1;
	m_hidden = false;
	m_fullyObscuredByShroud = false;
	extern int g_Va012F8064;
	m_field9c = ~g_Va012F8064;
	m_field84 = true;
	m_field88 = 0;
	m_field170 = false;
	m_field171 = false;
	m_field172 = false;
	m_field6c = 0;
	m_field74 = 0;
	m_field78 = 1.0f;
	m_field7c = 1.0f;
	m_field80 = 1.0f;
	m_field70 = 0.0f;
	m_lodResult = 0;
	m_lodResult2 = 0;
	*((unsigned char *)this + 0x1fc) = 1;
	m_field230 = false;
	m_field231 = true;
	m_field232 = false;
	m_fielda8 = 5;
	m_string200.releaseBuffer();
	for (int i = 0; i < 2; ++i)
		m_strings[i].releaseBuffer();

	Drawable *drawable = *(Drawable **)((unsigned char *)this + 8);
	m_field20c = 0;
	m_field22c = 0;
	m_bounds[0] = -9999.0f;
	m_bounds[1] = -9999.0f;
	m_bounds[2] = -9999.0f;
	m_bounds[3] = -9999.0f;

	Object *object = drawable ? drawable->getObject() : 0;
	if (object)
	{
		if (TheWritableGlobalData->m_timeOfDay == 4)
			m_indicatorColor = object->getNightIndicatorColor();
		else
			m_indicatorColor = object->getIndicatorColor();
	}

	m_field173 = false;
	m_field174 = 0;
	*(int *)((unsigned char *)this + 0x1b8) = -1;
	if (*(ModuleData **)((unsigned char *)this + 4) && drawable)
	{
		unsigned char *module = *(unsigned char **)((unsigned char *)this + 4);
		unsigned char *draw = (unsigned char *)drawable;
		draw[0xe4] = module[0x10d];
		*(int *)(draw + 0xe8) = *(int *)(module + 0x110);
		*(int *)(draw + 0xec) = *(int *)(module + 0x114);
	}
	m_field210 = false;
	m_field214 = 0;
	m_field218 = 0;
	m_field21c = 0;

	if (drawable)
		m_matrix = *drawable->getTransformMatrix();
	else
		m_matrix.Make_Identity();
	m_field264 = 1.0f;
	m_field268 = -1;

	{
		switch ((unsigned int)TheGameLODManager->m_level)
		{
		case 0:
		case 1:
			m_lodResult = 2;
			break;
		case 2:
			m_lodResult = 1;
			break;
		case 3:
		case 4:
		default:
			m_lodResult = 0;
			break;
		}
	}
}
