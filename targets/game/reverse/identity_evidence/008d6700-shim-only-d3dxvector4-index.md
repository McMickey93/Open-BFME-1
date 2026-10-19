# 0x008D6700: not `_D3DXVECTOR4::operator[]`

The 10-byte body at 0x008D6700 was matched as `??A_D3DXVECTOR4@@QAEAAMH@Z`
from game/Libraries/Source/WWVegas/WW3D2/sortingrenderer.cpp. That name does
not hold up, so the row is re-homed as the address-derived
`?at@Rva008D6700FloatArray@@QAEAAMH@Z`.

## Facts

- Retail bytes: `8B 44 24 04 8D 04 81 C2 04 00`
  (`mov eax,[esp+4]; lea eax,[ecx+eax*4]; ret 4`), a __thiscall
  `float &(int)` index accessor on any float vector.
- No `E8` call in retail .text reaches 0x008D6700 (full rel32 scan), and
  nothing else references it.
- The DirectX 8 `D3DXVECTOR4` has no `operator[]`, only `operator FLOAT*`.
  The one that produced the old name is
  `inputs/reference/shims/d3d8_shim_validated.h:658`, this repo's shim.
  The row matched only because sortingrenderer.cpp's unmatched upstream
  `SortingRendererClass::Insert_Triangles` copy (a second strong definition of
  the matched 0x0093B340 body, link queue #1) wrote `transformed_vec[2]` and so
  emitted the shim inline out of line.
- The address sits between `??0Matrix4@@QAE@ABV0@@Z` (0x008D6680, camera.cpp)
  and `?Set@Matrix3D@@...` (0x008D6710, matrix3d.cpp), in the WWMath range, and
  nowhere near the sorting renderer (0x00938A70..0x0093BDF7).

The owner of the body is unknown, so the replacement name keeps the address.
