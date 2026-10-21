// cl: /DNDEBUG /MD /EHsc
// Open-BFME5: MeshGeometryClass::Intersect_OBBox, retail 0x00927920, 34 bytes,
// and MeshGeometryClass::Cast_Ray just before it, retail 0x009278F0, 34 bytes
// (pinned by MeshClass::Cast_Ray's call; it calls Cast_Ray_Recursive and
// tail-jumps to cast_ray_brute_force). This TU keeps BFME's CullTree offset,
// +0x90, where the shared meshgeometry.h still has Zero Hour's.
//
// The Zero Hour body. AABTreeClass::Intersect_OBBox is one line, so MSVC
// inlines it and the cull-tree arm becomes a direct call to
// Intersect_OBBox_Recursive with the root node read from tree+0x0C; the
// brute-force arm is a tail jump because its result is returned unchanged.

class OBBoxIntersectionTestClass;
class RayCollisionTestClass;

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2/aabtree.h
class AABTreeClass
{
public:
	struct CullNodeStruct;

	bool Cast_Ray(RayCollisionTestClass &raytest)
	{
		return Cast_Ray_Recursive(RootNode, raytest);
	}

	bool Intersect_OBBox(OBBoxIntersectionTestClass &test)
	{
		return Intersect_OBBox_Recursive(RootNode, test);
	}

private:
	bool Cast_Ray_Recursive(CullNodeStruct *node, RayCollisionTestClass &raytest);
	bool Intersect_OBBox_Recursive(CullNodeStruct *node, OBBoxIntersectionTestClass &test);

	unsigned char m_unmodelled_000[0xc];
	CullNodeStruct *RootNode;			// tree+0x0C
};

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/WWVegas/WW3D2/meshgeometry.h
class MeshGeometryClass
{
public:
	bool Cast_Ray(RayCollisionTestClass &raytest);
	bool Intersect_OBBox(OBBoxIntersectionTestClass &boxtest);

protected:
	bool cast_ray_brute_force(RayCollisionTestClass &raytest);

private:
	bool intersect_obbox_brute_force(OBBoxIntersectionTestClass &boxtest);

	unsigned char m_unmodelled_000[0x90];
	AABTreeClass *CullTree;				// this+0x90
};

// ?Cast_Ray@MeshGeometryClass@@QAE_NAAVRayCollisionTestClass@@@Z
bool MeshGeometryClass::Cast_Ray(RayCollisionTestClass &raytest)
{
	bool hit = false;

	if (CullTree)
	{
		hit = CullTree->Cast_Ray(raytest);
	}
	else
	{
		hit = cast_ray_brute_force(raytest);
	}

	return hit;
}

// ?Intersect_OBBox@MeshGeometryClass@@QAE_NAAVOBBoxIntersectionTestClass@@@Z
bool MeshGeometryClass::Intersect_OBBox(OBBoxIntersectionTestClass &boxtest)
{
	bool hit = false;

	if (CullTree)
	{
		hit = CullTree->Intersect_OBBox(boxtest);
	}
	else
	{
		hit = intersect_obbox_brute_force(boxtest);
	}

	return hit;
}
