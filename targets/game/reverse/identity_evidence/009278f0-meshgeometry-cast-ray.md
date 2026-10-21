# 0x009278F0 is MeshGeometryClass::Cast_Ray

- The 34-byte body (ret 4 at +0x1A, tail jmp at +0x1D, INT3 after) reads
  `this+0x90` (BFME's CullTree), and when it is non-null calls
  `AABTreeClass::Cast_Ray_Recursive` (0x0096B080, matched) on the tree's root
  node at +0x0C; otherwise it tail-jumps to
  `MeshGeometryClass::cast_ray_brute_force` (0x00926CB0, matched). This is
  Zero Hour's `MeshGeometryClass::Cast_Ray` with `AABTreeClass::Cast_Ray`
  inlined, the same shape as the matched `Intersect_OBBox` at 0x00927920.
- symbols.csv already pins `?Cast_Ray@MeshGeometryClass@@QAE_NAAVRayCollisionTestClass@@@Z`
  at 0x009278F0 as the retail call target of `MeshClass::Cast_Ray`.
- Open-BFME-2's matched `MeshGeometryClass::Cast_Ray` is byte-identical
  (unique masked placement in the 2026-10-21 BFME2->BFME1 sweep).
- The row was claimed as `?bfmeGo911B@BfmeThing911B@@QAEXPAX@Z`, a
  placeholder with no other user.
