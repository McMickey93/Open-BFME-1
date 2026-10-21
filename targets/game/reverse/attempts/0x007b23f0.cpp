// ?d_007b23f0@@YAXXZ
// partial score=0.3015 date=2026-10-21
// ?project007B23F0@W3DProjectedShadowManager@@QAEXPAUShadowPair007B6D30@@@Z
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Iinputs/reference/shims/sweep /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WWMath
// stlport
#define _STLP_NO_EXCEPTIONS 1
#define __PLACEMENT_VEC_NEW_INLINE
#include <vector>
#include <math.h>
#include "vector2.h"
#include "vector3.h"
#include "matrix3d.h"

typedef float Real;
typedef int Int;
typedef unsigned int UnsignedInt;
typedef unsigned short UnsignedShort;
typedef bool Bool;

#define __max(a,b) (((a) > (b)) ? (a) : (b))
#define __min(a,b) (((a) < (b)) ? (a) : (b))

#define MAP_XY_FACTOR 10.0f
#define MAP_HEIGHT_SCALE 0.0390625f

__forceinline long fastFloatToLong007B23F0(float value)
{
	long result;
	__asm
	{
		fld [value]
		fistp [result]
	}
	return result;
}
#define REAL_TO_INT_FLOOR(x) fastFloatToLong007B23F0((float)floor((double)(x)))
#define REAL_TO_INT_CEIL(x) fastFloatToLong007B23F0((float)ceil((double)(x)))

struct Coord3D
{
	float x, y, z;
};

// ---------------------------------------------------------------------------
// Retail 0x007AE900's helper, copied into this TU (docs/shape_levers.md,
// "Compiler-private ABI"): MSVC 7.1 only gives the eax=obj / ebx=ground /
// esi=normal convention when it can see the static body next to its caller.
struct Coord3D007AE900 { float x, y, z; };

class BfmeHolderNS
{
public:
	int bfmeQueryNS(void);
};

void j_0003a391();

struct Rva003FD060TerrainLogic
{
	virtual void bfmeSlot0AAE();
	virtual void bfmeSlot1AAE();
	virtual void bfmeSlot2AAE();
	virtual void bfmeSlot3AAE();
	virtual void bfmeSlot4AAE();
	virtual void bfmeSlot5AAE();
	virtual void bfmeSlot6AAE();
	virtual float bfmeHeightAAE(float x, float y, int layer, Coord3D007AE900 *normal, int clip);
};

class TerrainLogic;
extern TerrainLogic *TheTerrainLogic;
extern const float g_rva01075350;
extern const float g_0109B46C;

#define G_BFME_007AE900_BIAS g_0109B46C

struct Rva007AE900Src
{
	virtual void slot0(void);
	virtual void slot1(void);
	virtual void slot2(void);
	virtual void slot3(void);
	virtual void slot4(void);
	virtual void slot5(void);
	virtual void slot6(void);
	virtual void slot7(void);
	virtual void slot8(void);
	virtual void slot9(void);
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
	virtual void slot27(void);
	virtual void slot28(void);
	virtual void slot29(void);
	virtual void slot30(void);
	virtual void slot31(void);
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
	virtual void slot84(void);
	virtual void slot85(void);
	virtual void *bfmeGetChain007AE900(void) const;
};

static float Rva007AE900Body(Rva007AE900Src *obj, const Coord3D007AE900 *groundPos, Coord3D007AE900 *outNormal)
{
	if (obj)
	{
		void *r1 = obj->bfmeGetChain007AE900();
		if (r1)
		{
			void *r2 = obj->bfmeGetChain007AE900();
			void *field = *(void **)((char *)r2 + 4);
			BfmeHolderNS *holder = *(BfmeHolderNS **)((char *)field + 0xfc);
			if (holder)
			{
				int ns;
				{
					union { void (*raw)(); int (BfmeHolderNS::*m)(void); } call;
					call.raw = j_0003a391;
					ns = (holder->*call.m)();
				}
				if (ns != 1)
				{
					if (TheTerrainLogic)
					{
						Coord3D007AE900 tmp;
						float h = ((Rva003FD060TerrainLogic *)TheTerrainLogic)->bfmeHeightAAE(groundPos->x, groundPos->y, ns, &tmp, 1);
						h += G_BFME_007AE900_BIAS;
						*outNormal = tmp;
						return h;
					}
				}
			}
		}
	}

	float defaultResult = g_rva01075350;
	outNormal->x = 0.0f;
	outNormal->y = 0.0f;
	outNormal->z = 1.0f;
	return defaultResult;
}

// TU-local caller: not present in retail (the real caller is the still-dumped
// 0x007B23F0 body). Present only so MSVC 7.1 sees a single call site and can
// choose the eax/ebx/esi register convention the retail body expects.
// absent-from-retail
float Rva007AE900Caller(Rva007AE900Src *obj, const Coord3D007AE900 *pos, Coord3D007AE900 *normal)
{
	return Rva007AE900Body(obj, pos, normal);
}

// ---------------------------------------------------------------------------
// File-static helpers of BFME's W3DProjectedShadow.cpp TU (retail 0x007AF710 /
// 0x007AF7E0 / 0x007AF940), copied from
// game/GameEngineDevice/Source/W3DDevice/GameClient/Shadow/W3DProjectedShadowDecalHelpers.cpp.
static void decalAxesRva007AF7E0(const Matrix3D &objXform, Vector3 &uVector, Vector3 &vVector)
{
	uVector = objXform.Get_X_Vector();
	uVector.Z = 0.0f;
	float vecLength = uVector.Length();
	if (vecLength != 0.0f) {
		uVector *= 1.0f / vecLength;
		vVector.Set(uVector.Y, -uVector.X, 0.0f);
	} else {
		vVector = objXform.Get_Y_Vector();
		vVector.Z = 0.0f;
		vecLength = vVector.Length();
		if (vecLength != 0.0f)
			vVector *= 1.0f / vecLength;
		else
			vVector.Set(0.0f, -1.0f, 0.0f);
		uVector.Set(-vVector.Y, vVector.X, 0.0f);
	}
}

static Vector2 minMax4Rva007AF710(float a, float b, float c, float d)
{
	float lo, hi;
	if (a < b) {
		lo = a;
		hi = b;
	} else {
		lo = b;
		hi = a;
	}
	if (c < d) {
		if (c < lo)
			lo = c;
		if (d > hi)
			hi = d;
	} else {
		if (d < lo)
			lo = d;
		if (c > hi)
			hi = c;
	}
	return Vector2(lo, hi);
}

static void projectRangesRva007AF940(const Vector3 &axisA, const Vector3 &axisB, float sizeA, float sizeB,
	float offA, float offB, Vector2 &xr, Vector2 &yr)
{
	Vector3 a0 = -((offA + 0.5f) * sizeA) * axisA;
	Vector3 a1 = (0.5f - offA) * sizeA * axisA;
	Vector3 b0 = -((offB + 0.5f) * sizeB) * axisB;
	Vector3 b1 = (0.5f - offB) * sizeB * axisB;
	Vector3 c0 = b0 + a0;
	Vector3 c1 = b0 + a1;
	Vector3 c2 = b1 + a1;
	Vector3 c3 = b1 + a0;
	xr = minMax4Rva007AF710(c0.X, c1.X, c2.X, c3.X);
	yr = minMax4Rva007AF710(c0.Y, c1.Y, c2.Y, c3.Y);
}

// ---------------------------------------------------------------------------
class ShadowTexture007B6D30;

struct Shadow007B6D30
{
	char pad00[8];
	Coord3D m_pos08;
	char pad14[0xc];
	float m_angle20;
	char pad24[4];
	unsigned int m_diffuse28;
	char pad2c[4];
	unsigned int m_type34;
	char pad38[0x20];
	float m_decalSizeX58, m_decalSizeY5c;
	char pad60[8];
	ShadowTexture007B6D30 *m_texture68;
	float m_offsetU6c, m_offsetV70;
};

class RenderObjClass;
struct ShadowPair007B6D30
{
	char pad00[8];
	Coord3D m_pos08;
	char pad14[0xc];
	float m_angle20;
	char pad24[4];
	unsigned int m_diffuse28;
	char pad2c[8];
	unsigned int m_type34;
	char pad38[0x20];
	Shadow007B6D30 *m_shadow58, *m_shadow5c;
	RenderObjClass *m_object60;
	ShadowPair007B6D30 *m_next64;
};

class RenderObjClass
{
public:
	virtual void Delete_This();
	virtual void v01(); virtual void v02(); virtual void v03();
	virtual void v04(); virtual void v05(); virtual void v06(); virtual void v07();
	virtual void v08(); virtual void v09(); virtual void v10(); virtual void v11();
	virtual void v12(); virtual void v13(); virtual void v14(); virtual void v15();
	virtual void v16(); virtual void v17(); virtual void v18(); virtual void v19();
	virtual void Validate_Transform() const;
	virtual void v21(); virtual void v22(); virtual void v23(); virtual void v24();
	virtual void v25(); virtual void v26(); virtual void v27(); virtual void v28();
	virtual void v29(); virtual void v30(); virtual void v31(); virtual void v32();
	virtual void v33(); virtual void v34(); virtual void v35(); virtual void v36();
	virtual void v37(); virtual void v38(); virtual void v39(); virtual void v40();
	virtual void v41(); virtual void v42(); virtual void v43(); virtual void v44();
	virtual void v45(); virtual void v46(); virtual void v47(); virtual void v48();
	virtual void v49(); virtual void v50(); virtual void v51(); virtual void v52();
	virtual void v53(); virtual void v54(); virtual void v55(); virtual void v56();
	virtual void v57(); virtual void v58(); virtual void v59(); virtual void v60();
	virtual void v61(); virtual void v62(); virtual void v63(); virtual void v64();
	virtual void v65(); virtual void v66(); virtual void v67(); virtual void v68();
	virtual void v69(); virtual void v70(); virtual void v71(); virtual void v72();
	virtual void v73(); virtual void v74(); virtual void v75(); virtual void v76();
	virtual void v77(); virtual void v78(); virtual void v79(); virtual void v80();
	virtual void v81(); virtual void v82(); virtual void v83(); virtual void v84();
	virtual void v85(); virtual void v86(); virtual void v87(); virtual void v88();
	virtual void v89(); virtual void v90(); virtual void v91(); virtual void v92();
	virtual void v93(); virtual void v94(); virtual void v95(); virtual void v96();
	virtual void v97(); virtual void v98(); virtual void v99(); virtual void v100();
	virtual void v101(); virtual void v102(); virtual void v103(); virtual void v104();
	virtual void v105(); virtual void v106(); virtual void v107(); virtual void v108();
	virtual void v109(); virtual void v110(); virtual void v111(); virtual void v112();
	virtual void v113(); virtual void v114(); virtual void v115(); virtual void v116();
	virtual void v117(); virtual void v118(); virtual void v119(); virtual void v120();
	virtual void v121(); virtual void v122(); virtual void v123(); virtual void v124();
	virtual void v125(); virtual void v126(); virtual void v127(); virtual void v128();
	virtual void v129(); virtual void v130(); virtual void v131(); virtual void v132();
	virtual void v133(); virtual void v134(); virtual void v135(); virtual void v136();
	virtual void v137(); virtual void v138(); virtual void v139(); virtual void v140();
	virtual void v141(); virtual void v142(); virtual void v143(); virtual void v144();
	virtual void v145(); virtual void v146(); virtual void v147(); virtual void v148();
	virtual void v149(); virtual void v150(); virtual void v151(); virtual void v152();
	virtual void v153(); virtual void v154(); virtual void v155(); virtual void v156();
	virtual void v157(); virtual void v158(); virtual void v159(); virtual void v160();
	char pad04[0x14];
	Vector3 Get_Position(void) const;
	Matrix3D Transform;
};

struct SHADOW_DECAL_DUAL_VERTEX
{
	float x, y, z;
	unsigned int diffuse;
	float u0, v0;
	float u1, v1;
};

class ShadowDecalBuffer007B23F0
{
public:
	virtual void v00(); virtual void v01(); virtual void v02(); virtual void v03();
	virtual void v04(); virtual void v05(); virtual void v06(); virtual void v07();
	virtual void v08(); virtual void v09(); virtual void v10();
	virtual long __stdcall Lock(unsigned int offset, unsigned int size, void **data, unsigned int flags);
	virtual long __stdcall Unlock();
};

extern ShadowDecalBuffer007B23F0 *shadowDecalVertexBufferD3D;
extern ShadowDecalBuffer007B23F0 *shadowDecalIndexBufferD3D;
extern int nShadowDecalVertsInBuf;
extern int nShadowDecalStartBatchVertex;
extern int nShadowDecalIndicesInBuf;
extern int nShadowDecalStartBatchIndex;
extern int nShadowDecalPolysInBatch;
extern int nShadowDecalVertsInBatch;
extern int drawEdgeX, drawEdgeY, drawStartX, drawStartY;

#define SHADOW_DECAL_VERTEX_SIZE 32768
#define SHADOW_DECAL_INDEX_SIZE 65536
#define D3DLOCK_NOOVERWRITE 0x1000
#define D3DLOCK_DISCARD 0x2000
#define D3D_OK 0

// Height-map side of the terrain object: border at +0x10, the out-of-line
// bounded word lookup (retail 0x006BE030) and the flip-state bit plane
// (retail 0x0074B410). Both keep their ledger class names.
class BfmeHeightMap007B23F0
{
public:
	char pad00[0x10];
	int m_borderSize;
};
class Rva006BE030LookupWord
{
public:
	unsigned short lookup(int x, int y) const;
};
class Gen_0074B410
{
public:
	bool bfmeBitA(int x, int y) const;
};

class BaseHeightMapRenderObjClass;
extern BaseHeightMapRenderObjClass *TheTerrainRenderObject;

struct BfmeTerrainRenderObject007B23F0
{
	char pad0000[0x2ff4];
	BfmeHeightMap007B23F0 *m_map;
};

class W3DProjectedShadowManager
{
public:
	void flush007B14A0(unsigned, ShadowTexture007B6D30 *, ShadowTexture007B6D30 *, int);
	void project007B23F0(ShadowPair007B6D30 *pair);
};

// ---------------------------------------------------------------------------
// Retail 0x007B23F0, 4823 bytes, ret 4 at +0x12D4. The matched renderShadows
// caller (0x007B6D30) passes the paired-shadow record, and the body is Zero
// Hour's queueDualDecal statement for statement with BFME's separate
// vertex/index locks, its four-argument flush and the paired vertex format.
void W3DProjectedShadowManager::project007B23F0(ShadowPair007B6D30 *pair)
{
	Shadow007B6D30 *shadow0 = pair->m_shadow58;
	Shadow007B6D30 *shadow1 = pair->m_shadow5c;
	ShadowTexture007B6D30 *texture0 = shadow0 ? shadow0->m_texture68 : 0;
	ShadowTexture007B6D30 *texture1 = shadow1 ? shadow1->m_texture68 : 0;
	if (!texture0 || !texture1)
		return;

	Real decalSizeX[2], decalSizeY[2];
	decalSizeX[0] = shadow0->m_decalSizeX58;
	decalSizeY[0] = shadow0->m_decalSizeY5c;
	decalSizeX[1] = shadow1->m_decalSizeX58;
	decalSizeY[1] = shadow1->m_decalSizeY5c;
	if ((decalSizeX[0] == 0.0f || decalSizeY[0] == 0.0f) && (decalSizeX[1] == 0.0f || decalSizeY[1] == 0.0f))
		return;

	Matrix3D objXform(true);
	Vector3 objPos;
	Vector3 normal;
	Real layerHeight = 0.0f;
	RenderObjClass *robj = pair->m_object60;
	if (robj)
	{
		objPos = robj->Get_Position();
		objPos.Z = 0.0f;
		robj->Validate_Transform();
		objXform = robj->Transform;
		layerHeight = Rva007AE900Body(reinterpret_cast<Rva007AE900Src *>(robj),
			reinterpret_cast<const Coord3D007AE900 *>(&objPos),
			reinterpret_cast<Coord3D007AE900 *>(&normal));
	}
	else
	{
		Coord3D pos = pair->m_pos08;
		objPos.X = pos.x;
		objPos.Y = pos.y;
		objPos.Z = 0.0f;
		objXform.Rotate_Z(pair->m_angle20);
	}

	Matrix3D rotations[2];
	rotations[0].Make_Identity();
	rotations[1].Make_Identity();
	rotations[0].Rotate_Z(shadow0->m_angle20 + pair->m_angle20);
	rotations[1].Rotate_Z(shadow1->m_angle20 + pair->m_angle20);

	Vector3 uVector[2], vVector[2];
	decalAxesRva007AF7E0(rotations[0], uVector[0], vVector[0]);
	decalAxesRva007AF7E0(rotations[1], uVector[1], vVector[1]);

	Vector3 decalPos[2];
	Coord3D pos;
	pos = shadow0->m_pos08;
	decalPos[0].X = pos.x;
	decalPos[0].Y = pos.y;
	decalPos[0].Z = 0.0f;
	pos = shadow1->m_pos08;
	decalPos[1].X = pos.x;
	decalPos[1].Y = pos.y;
	decalPos[1].Z = 0.0f;
	objXform.mulVector3(decalPos[0]);
	objXform.mulVector3(decalPos[1]);

	Real uOffset[2], vOffset[2];
	if (shadow0)
	{
		uOffset[0] = shadow0->m_offsetU6c;
		vOffset[0] = shadow0->m_offsetV70;
	}
	if (shadow1)
	{
		uOffset[1] = shadow1->m_offsetU6c;
		vOffset[1] = shadow1->m_offsetV70;
	}

	Vector2 xRange[2], yRange[2];
	projectRangesRva007AF940(uVector[0], vVector[0], decalSizeX[0], decalSizeY[0], uOffset[0], vOffset[0], xRange[0], yRange[0]);
	projectRangesRva007AF940(uVector[1], vVector[1], decalSizeX[1], decalSizeY[1], uOffset[1], vOffset[1], xRange[1], yRange[1]);

	decalPos[0].X += objPos.X;
	decalPos[1].X += objPos.X;
	decalPos[0].Y += objPos.Y;
	decalPos[1].Y += objPos.Y;

	Vector2 boundsX(WWMath::Min(xRange[0].X + decalPos[0].X, xRange[1].X + decalPos[1].X),
		WWMath::Max(xRange[0].Y + decalPos[0].X, xRange[1].Y + decalPos[1].X));
	Vector2 boundsY(WWMath::Min(yRange[0].X + decalPos[0].Y, yRange[1].X + decalPos[1].Y),
		WWMath::Max(yRange[0].Y + decalPos[0].Y, yRange[1].Y + decalPos[1].Y));

	if (decalSizeX[0] == 0.0f)
		uVector[0].X = uVector[0].Y = uVector[0].Z = 0.0f;
	else
		uVector[0] /= decalSizeX[0];
	if (decalSizeX[1] == 0.0f)
		uVector[1].X = uVector[1].Y = uVector[1].Z = 0.0f;
	else
		uVector[1] /= decalSizeX[1];
	if (decalSizeY[0] == 0.0f)
		vVector[0].X = vVector[0].Y = vVector[0].Z = 0.0f;
	else
		vVector[0] /= decalSizeY[0];
	if (decalSizeY[1] == 0.0f)
		vVector[1].X = vVector[1].Y = vVector[1].Z = 0.0f;
	else
		vVector[1] /= decalSizeY[1];

	uOffset[0] += 0.5f;
	uOffset[1] += 0.5f;
	vOffset[0] += 0.5f;
	vOffset[1] += 0.5f;

	Real mapScaleInv = 1.0f / MAP_XY_FACTOR;
	BfmeHeightMap007B23F0 *hmap = reinterpret_cast<BfmeTerrainRenderObject007B23F0 *>(TheTerrainRenderObject)->m_map;
	Int borderSize = hmap->m_borderSize;

	Int startX = REAL_TO_INT_FLOOR(boundsX.X * mapScaleInv) + borderSize;
	Int endX = REAL_TO_INT_CEIL(boundsX.Y * mapScaleInv) + borderSize;
	Int startY = REAL_TO_INT_FLOOR(boundsY.X * mapScaleInv) + borderSize;
	Int endY = REAL_TO_INT_CEIL(boundsY.Y * mapScaleInv) + borderSize;

	startX = __max(startX, drawStartX);
	startX = __min(startX, drawEdgeX);
	startY = __max(startY, drawStartY);
	startY = __min(startY, drawEdgeY);
	endX = __max(endX, drawStartX);
	endX = __min(endX, drawEdgeX);
	endY = __max(endY, drawStartY);
	endY = __min(endY, drawEdgeY);

	Int numExtraX = (endX - startX + 1) - 104;
	if (numExtraX > 0)
	{
		Int numStartExtraX = REAL_TO_INT_FLOOR((float)numExtraX / 2.0f);
		Int numEdgeExtraX = numExtraX - numStartExtraX;
		startX += numStartExtraX;
		endX -= numEdgeExtraX;
	}
	Int numExtraY = (endY - startY + 1) - 104;
	if (numExtraY > 0)
	{
		Int numStartExtraY = REAL_TO_INT_FLOOR((float)numExtraY / 2.0f);
		Int numEdgeExtraY = numExtraY - numStartExtraY;
		startY += numStartExtraY;
		endY -= numEdgeExtraY;
	}

	Int vertsPerRow = endX - startX + 1;
	Int vertsPerColumn = endY - startY + 1;
	if (vertsPerRow <= 1 || vertsPerColumn <= 1)
		return;

	Int numVerts = vertsPerRow * vertsPerColumn;
	Int numIndex = (endX - startX) * (endY - startY) * 6;

	SHADOW_DECAL_DUAL_VERTEX *pvVertices;
	if (nShadowDecalVertsInBuf > (SHADOW_DECAL_VERTEX_SIZE - numVerts))
	{
		flush007B14A0(pair->m_type34, texture0, texture1, 0);

		if (shadowDecalVertexBufferD3D->Lock(0, numVerts * sizeof(SHADOW_DECAL_DUAL_VERTEX), (void **)&pvVertices, D3DLOCK_DISCARD) != D3D_OK)
			return;

		nShadowDecalStartBatchVertex = 0;
		nShadowDecalPolysInBatch = 0;
		nShadowDecalVertsInBatch = 0;
		nShadowDecalVertsInBuf = 0;
	}
	else
	{
		if (shadowDecalVertexBufferD3D->Lock(nShadowDecalVertsInBuf * sizeof(SHADOW_DECAL_DUAL_VERTEX), numVerts * sizeof(SHADOW_DECAL_DUAL_VERTEX), (void **)&pvVertices, D3DLOCK_NOOVERWRITE) != D3D_OK)
			return;
	}

	Vector3 hmapVertex;
	Vector3 decalVertex[2];
	UnsignedInt diffuse = pair->m_diffuse28;

	if (pvVertices)
	{
		Int i, j;
		if (layerHeight)
			for (j = startY; j <= endY; j++)
			{
				hmapVertex.Y = (float)(j - borderSize) * MAP_XY_FACTOR;

				for (i = startX; i <= endX; i++)
				{
					hmapVertex.X = (float)(i - borderSize) * MAP_XY_FACTOR;
					hmapVertex.Z = __max((float)reinterpret_cast<const Rva006BE030LookupWord *>(hmap)->lookup(i, j) * MAP_HEIGHT_SCALE, layerHeight);
					decalVertex[0] = hmapVertex - decalPos[0];
					decalVertex[1] = hmapVertex - decalPos[1];
					pvVertices->x = hmapVertex.X;
					pvVertices->y = hmapVertex.Y;
					pvVertices->z = hmapVertex.Z;
					pvVertices->diffuse = diffuse;
					pvVertices->u0 = Vector3::Dot_Product(uVector[0], decalVertex[0]) + uOffset[0];
					pvVertices->v0 = Vector3::Dot_Product(vVector[0], decalVertex[0]) + vOffset[0];
					pvVertices->u1 = Vector3::Dot_Product(uVector[1], decalVertex[1]) + uOffset[1];
					pvVertices->v1 = Vector3::Dot_Product(vVector[1], decalVertex[1]) + vOffset[1];
					pvVertices++;
				}
			}
		else
			for (j = startY; j <= endY; j++)
			{
				hmapVertex.Y = (float)(j - borderSize) * MAP_XY_FACTOR;

				for (i = startX; i <= endX; i++)
				{
					hmapVertex.X = (float)(i - borderSize) * MAP_XY_FACTOR;
					hmapVertex.Z = (float)reinterpret_cast<const Rva006BE030LookupWord *>(hmap)->lookup(i, j) * MAP_HEIGHT_SCALE + 0.01f * MAP_XY_FACTOR;
					decalVertex[0] = hmapVertex - decalPos[0];
					decalVertex[1] = hmapVertex - decalPos[1];
					pvVertices->x = hmapVertex.X;
					pvVertices->y = hmapVertex.Y;
					pvVertices->z = hmapVertex.Z;
					pvVertices->diffuse = diffuse;
					pvVertices->u0 = Vector3::Dot_Product(uVector[0], decalVertex[0]) + uOffset[0];
					pvVertices->v0 = Vector3::Dot_Product(vVector[0], decalVertex[0]) + vOffset[0];
					pvVertices->u1 = Vector3::Dot_Product(uVector[1], decalVertex[1]) + uOffset[1];
					pvVertices->v1 = Vector3::Dot_Product(vVector[1], decalVertex[1]) + vOffset[1];
					pvVertices++;
				}
			}
	}

	shadowDecalVertexBufferD3D->Unlock();

	unsigned short *pvIndices;
	if (nShadowDecalIndicesInBuf > (SHADOW_DECAL_INDEX_SIZE - numIndex))
	{
		flush007B14A0(pair->m_type34, texture0, texture1, 0);

		if (shadowDecalIndexBufferD3D->Lock(0, numIndex * sizeof(unsigned short), (void **)&pvIndices, D3DLOCK_DISCARD) != D3D_OK)
			return;

		nShadowDecalStartBatchIndex = 0;
		nShadowDecalPolysInBatch = 0;
		nShadowDecalVertsInBatch = 0;
		nShadowDecalIndicesInBuf = 0;
	}
	else
	{
		if (shadowDecalIndexBufferD3D->Lock(nShadowDecalIndicesInBuf * sizeof(unsigned short), numIndex * sizeof(unsigned short), (void **)&pvIndices, D3DLOCK_NOOVERWRITE) != D3D_OK)
			return;
	}

	if (pvIndices)
	{
		Int rowStart;
		Int i, j, k;
		for (j = startY, rowStart = 0; j < endY; j++, rowStart += vertsPerRow)
		{
			for (i = rowStart, k = startX; k < endX; i++, k++)
			{
				if (reinterpret_cast<const Gen_0074B410 *>(hmap)->bfmeBitA(k, j))
				{
					pvIndices[0] = i + 1 + nShadowDecalVertsInBatch;
					pvIndices[1] = i + vertsPerRow + nShadowDecalVertsInBatch;
					pvIndices[2] = i + nShadowDecalVertsInBatch;
					pvIndices[3] = i + 1 + nShadowDecalVertsInBatch;
					pvIndices[4] = i + 1 + vertsPerRow + nShadowDecalVertsInBatch;
					pvIndices[5] = i + vertsPerRow + nShadowDecalVertsInBatch;
				}
				else
				{
					pvIndices[0] = i + nShadowDecalVertsInBatch;
					pvIndices[1] = i + 1 + vertsPerRow + nShadowDecalVertsInBatch;
					pvIndices[2] = i + vertsPerRow + nShadowDecalVertsInBatch;
					pvIndices[3] = i + nShadowDecalVertsInBatch;
					pvIndices[4] = i + 1 + nShadowDecalVertsInBatch;
					pvIndices[5] = i + 1 + vertsPerRow + nShadowDecalVertsInBatch;
				}
				pvIndices += 6;
			}
		}
	}

	shadowDecalIndexBufferD3D->Unlock();

	nShadowDecalPolysInBatch += (endX - startX) * (endY - startY) * 2;
	nShadowDecalVertsInBuf += numVerts;
	nShadowDecalVertsInBatch += numVerts;
	nShadowDecalIndicesInBuf += numIndex;
}
