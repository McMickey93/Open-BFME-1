# RVA 0x009124C0: VectorClass<Vector2>::Clear, from the class vftable

Baseline: BFME 1 retail 1.03 unpacked, SHA256
`1fbdc0ced8f283732c094c4f0804ce8dc1e3e3675b720bcab066c94fed964e75`.

The matched `??0?$VectorClass@VVector2@@@@QAE@HPBVVector2@@@Z` body at
0x00913500 stores its vftable pointer with `mov dword ptr [esi], 0x0113ACC4`.
That is an absolute VA; subtracting the 0x00400000 image base gives vftable
RVA 0x00D3ACC4. The table's first entries are

| slot | stored VA | RVA | declaration |
| --- | --- | --- | --- |
| 0 | 0x00D13A80 | 0x00913A80 | `~VectorClass` |
| 1 | 0x00D13670 | 0x00913670 | `operator ==` |
| 2 | 0x00D136F0 | 0x009136F0 | `Resize` |
| 3 | 0x00D124C0 | 0x009124C0 | `Clear` |
| 4 | 0x00D135B0 | 0x009135B0 | `ID(T const &)` |

Slot 2 is the ledger-pinned `?Resize@?$VectorClass@VVector2@@@@UAE_NHPBVVector2@@@Z`
at 0x009136F0, and slot 4 is the ledger-pinned
`?ID@?$VectorClass@VVector2@@@@UAEHABVVector2@@@Z` at 0x009135B0. The
declaration order in `WWLib/vector.h` (destructor, `operator ==`, `Resize`,
`Clear`, `ID`) therefore makes slot 3 the Vector2 `Clear` body at 0x009124C0.

The 39-byte body at 0x009124C0 is the clear-and-free shape and its only
relocation is a call to `??_V@YAXPAX@Z` at 0x00881EF0 (operator delete[]),
exactly matching pointgr.obj's emitted
`?Clear@?$VectorClass@VVector2@@@@UAEXXZ` (digest e18f898361b9). The
byte-identical 39-byte emitter with digest 82149c5f7f25, produced by
render2d.cpp because that TU is built without always.h's array operators,
calls `??3@YAXPAX@Z` at 0x00881EB0 instead and is not the retail-selected
copy.

This retires the address-derived `?dup_009124c0@@YAXXZ` row, whose
object-symbol was `?Clear@?$VectorClass@E@@UAEXXZ` (a byte-identical
unsigned-char instantiation used only as an emitter), and names the retail
body with its real Vector2 identity.
