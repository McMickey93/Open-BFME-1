# 0x001E0CE0 vs 0x0092EFE0: MeshMatDescClass::Peek_Single_Material

Approved by the project lead 2026-10-16.

Both bodies are 14 bytes: `mov eax,[esp+4] / mov eax,[ecx+eax*4+0xA4] / ret 4`.
Retail had no identical-COMDAT folding, so one name has one body.

- 0x0092EFE0 (?dup_0092efe0, matinfo.cpp, object-symbol already
  `?Peek_Single_Material@MeshMatDescClass@@QBEPAVVertexMaterialClass@@H@Z`) sits
  between matched `MeshMatDescClass::Get_Single_Material` 0x0092EFC0, which
  reads `Material[pass]` at this+0xA4 and adds a reference, and
  `MeshMatDescClass::Has_Material_Array` 0x0092EFF0. That is Zero Hour
  meshmatdesc.h's inline definition order (Get_Single_Material, then
  Peek_Single_Material `return Material[pass];`), emitted together in the WW3D2
  region. It is Peek_Single_Material.
- 0x001E0CE0 lies among GameEngine's tiny getters, far from WW3D2. Nothing calls
  it directly, and no matched caller lands on it under either name it carried
  (`Peek_Single_Material` from dx8renderer.cpp,
  `?Get_Locked_Volume_Slice_Pitch@VolumeTextureLoadTaskClass@@AAEII@Z` from
  textureloader.cpp, which no evidence placed). Both names are retired there
  and the body keeps an address-derived name
  (`?get@Rva001E0CE0IndexedField@@QBEHH@Z`).
