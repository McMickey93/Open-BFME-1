# 0x007AE850-0x007B13E0 are W3DShadowTextureManager's; the Geometry names are over-claims

Approved by the project lead 2026-10-16.

Eleven bodies in this range carry both a W3DShadowGeometryManager-family name
(W3DVolumetricShadow.cpp) and a W3DShadowTextureManager-family name
(W3DProjectedShadow.cpp). Retail was linked without identical-COMDAT folding,
and none of these bodies has a byte-twin anywhere in the image, so each has one
identity.

- freeAllTextures 0x007AEEA0 is called by ~W3DShadowTextureManager 0x007B0FF0,
  by ??_GW3DShadowTextureManager 0x007B13E0 and by the matched
  ~W3DProjectedShadowManager 0x007B4E40. Zero Hour's projected-shadow manager
  owns the texture manager, so this cluster is W3DShadowTextureManager (with its
  iterator and MissingTextureClass).
- No byte-matched caller lands on any of these bodies under a Geometry name.
  The two Geometry spellings that do occur at call sites (Free_All_Geoms,
  Get_Geom) land elsewhere through pins (0x0007BB670 / 0x007B9B00).

Retired Geometry-named rows: Get_Current_Geom 0x007AE850, Free_All_Geoms
0x007AEEA0, Peek_Geom 0x007AEF40, Get_Geom 0x007AEF70, Add_Geom 0x007AEFA0,
Is_Missing 0x007AF050, ~W3DShadowGeometryManager 0x007B0FF0,
??_GMissingGeomClass 0x007B1100, ~MissingGeomClass 0x007B1130,
Register_Missing 0x007B1190, ??_GW3DShadowGeometryManager 0x007B13E0.

Still open (not changed here):
- The ICF-alias pins `?Free_All_Geoms@W3DShadowGeometryManager@@QAEXXZ` ->
  ILT 0x00002365 and `?Get_Geom@...` -> ILT 0x0001275B land on bodies the
  ledger names HAnimManagerClass::Free_All_Anims 0x007BB670 /
  HAnimManagerClass::Get_Anim 0x007B9B00. ~W3DVolumetricShadowManager 0x007BDE90
  and BfmeVolumetricShadowManager::addShadow 0x007BF240 also call those bodies.
  So either BFME's shadow geometry manager is an HAnimManagerClass-shaped copy
  whose rows are mislabelled, or the callers' Geometry spellings are wrong. That
  is unresolved.
- dir32_addresses.csv records ??_7MissingGeomClass@@6B@ and
  ??_7MissingTextureClass@@6B@ at the same VA 0x01128460.
- 0x007AF300 AABoxClass::Translate vs Coord3D::add: no evidence either way.
