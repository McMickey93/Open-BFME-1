// cl: /O2 /DNDEBUG /MD /EHsc
//
// Retail 0x001E0CE0, 14 bytes: a __thiscall getter returning dword element i
// of an array at this+0xA4 (mov eax,[esp+4] / mov eax,[ecx+eax*4+0xA4] /
// ret 4). It sits among GameEngine's tiny getters and nothing calls it directly.
//
// It used to carry two over-claimed identities.
// MeshMatDescClass::Peek_Single_Material really is 0x0092EFE0, its byte-twin
// in the WW3D2 meshmatdesc inline group (after Get_Single_Material
// 0x0092EFC0, which reads Material[] at +0xA4, and before
// Has_Material_Array). VolumeTextureLoadTaskClass::Get_Locked_Volume_Slice_Pitch
// has no evidence here. IDENTITY IS NOT RECOVERED: the name is
// address-derived. Evidence:
// targets/game/reverse/identity_evidence/001e0ce0-0092efe0-peek-single-material.md

class Rva001E0CE0IndexedField
{
public:
	int get(int index) const;

private:
	char m_lead[0xA4];
	int m_values[1];
};

int Rva001E0CE0IndexedField::get(int index) const
{
	return m_values[index];
}
