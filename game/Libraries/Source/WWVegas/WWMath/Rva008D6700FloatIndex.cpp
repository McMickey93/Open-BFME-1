// Retail 0x008D6700 (10 B): a __thiscall float-array accessor,
//     mov eax,[esp+4] / lea eax,[ecx+eax*4] / ret 4
// i.e. `float &operator[](int i) { return (&x)[i]; }` on some float vector.
// No call, ILT stub or table slot reaches it; it sits between the camera.cpp
// Matrix4 copy constructor and matrix3d.cpp. The earlier name
// ??A_D3DXVECTOR4@@QAEAAMH@Z came from an operator[] that only this repo's
// D3D shim gives D3DXVECTOR4 (real D3DX8 has none), so it proved nothing.
// IDENTITY IS NOT RECOVERED: the name is address-derived.
class Rva008D6700FloatArray
{
public:
	float &at(int i);

private:
	float m_x;
};

float &Rva008D6700FloatArray::at(int i)
{
	return (&m_x)[i];
}
