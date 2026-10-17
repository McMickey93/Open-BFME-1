// ?get_deformed_vertices@MeshGeometryClass@@IAEXPAVVector3@@PBVHTreeClass@@@Z
// partial score=0.9697 date=2026-10-17
// cl: /DNDEBUG /MD /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WWSaveLoad /Igame/Libraries/Source/WWVegas/WW3D2 /Igame/Libraries/Source/WWVegas/Wwutil /Igame/Libraries/Source/WWVegas/WWDownload /Igame/Libraries/Source/Compression /Igame/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/shims/sweep
// ?get_deformed_vertices@MeshGeometryClass@@IAEXPAVVector3@@PBVHTreeClass@@@Z -- retail 0x00925860, 1199 B (ret 8 at +0x4AC).
// Land in game/Libraries/Source/WWVegas/WW3D2/meshgeometry.cpp in place of the ZH body.
#include "meshgeometry.h"
#pragma push_macro("W3DMPO_GLUE")
#define W3DMPO_GLUE(ARGCLASS)
#include "aabtree.h"
#pragma pop_macro("W3DMPO_GLUE")
#include "chunkio.h"
#include "aabox.h"
#include "obbox.h"
#include "sphere.h"
#include "plane.h"
#include "wwdebug.h"
#include "wwmemlog.h"
#include "w3d_file.h"
#include "vp.h"
#include "htree.h"
#include "matrix4.h"
#include "rinfo.h"
#include "camera.h"


struct Rva00925860Pivot
{
	char m_pad0[0x44];
	Matrix3D m_tm;
	char m_pad1[0x40];
};
struct Rva00925860Tree
{
	char m_pad0[0x14];
	Rva00925860Pivot *m_pivots;
};
struct MeshGeometryRetailSkinView
{
	char pad_00[0x28];
	int vertex_count;
	char pad_2c[4];
	ShareBufferClass<Vector3> *vertex[2];
	char pad_38[0x20];
	ShareBufferClass<unsigned short> *bone_link;
	ShareBufferClass<unsigned short> *bone_run;
};

void rva009371E0Inc();
extern float g_01076C24;

void MeshGeometryClass::get_deformed_vertices(Vector3 *dst_vert,const HTreeClass * htree)
{
	MeshGeometryRetailSkinView * const geometry =
		reinterpret_cast<MeshGeometryRetailSkinView *>(this);
	Rva00925860Tree *tree = (Rva00925860Tree *)htree;
	if (geometry->bone_run == 0 || geometry->bone_link == 0 || tree == 0)
		return;
	int streams = 1;
	if (geometry->vertex[1] != 0)
		streams = 2;
	Vector3 *srcV[2];
	int i;
	for (i = 0; i < streams; i++) {
		if (geometry->vertex[i] != 0)
			srcV[i] = (Vector3 *)geometry->vertex[i]->Get_Array();
		else
			srcV[i] = 0;
	}
	unsigned short *runs = (unsigned short *)geometry->bone_run->Get_Array();
	unsigned short *links = (unsigned short *)geometry->bone_link->Get_Array();
	rva009371E0Inc();
	int count = geometry->vertex_count;
	int left = count;
	while (left > 0) {
		int n = runs[1];
		runs += 2;
		left -= n;
		int b0 = links[0];
		int b1 = links[count];
		int c;
		if (streams == 2 && b1 != 0) {
			float w0 = (float)links[count * 2];
			float w1 = (float)links[count * 3];
			w0 *= g_01076C24;
			w1 *= g_01076C24;
			Matrix3D m0 = tree->m_pivots[b0].m_tm;
			Matrix3D m1 = tree->m_pivots[b1].m_tm;
			for (int r3 = 0; r3 < 3; r3++) {
				m0[r3] *= w0;
				m1[r3] *= w1;
			}
			const Vector3 *pa;
			const Vector3 *pb;
			Vector3 *po;
			po = dst_vert;
			pb = srcV[1];
			pa = srcV[0];
			c = n;
			while (c--) {
				po->X = m0[0].X * pa->X + m0[0].Y * pa->Y + m0[0].Z * pa->Z + m0[0].W + m1[0].X * pb->X + m1[0].Y * pb->Y + m1[0].Z * pb->Z + m1[0].W;
				po->Y = m0[1].X * pa->X + m0[1].Y * pa->Y + m0[1].Z * pa->Z + m0[1].W + m1[1].X * pb->X + m1[1].Y * pb->Y + m1[1].Z * pb->Z + m1[1].W;
				po->Z = m0[2].X * pa->X + m0[2].Y * pa->Y + m0[2].Z * pa->Z + m0[2].W + m1[2].X * pb->X + m1[2].Y * pb->Y + m1[2].Z * pb->Z + m1[2].W;
				++pa;
				++pb;
				++po;
			}
		} else {
			const Matrix3D &m = tree->m_pivots[b0].m_tm;
			const Vector3 *in;
			Vector3 *out;
			in = srcV[0];
			out = dst_vert;
			c = n;
			while (c--) {
				out->X = m[0].X * in->X + m[0].Y * in->Y + m[0].Z * in->Z + m[0].W;
				out->Y = m[1].X * in->X + m[1].Y * in->Y + m[1].Z * in->Z + m[1].W;
				out->Z = m[2].X * in->X + m[2].Y * in->Y + m[2].Z * in->Z + m[2].W;
				++in;
				++out;
			}
		}
		links += n;
		for (i = 0; i < streams; i++)
			srcV[i] += n;
		dst_vert += n;
	}
}
