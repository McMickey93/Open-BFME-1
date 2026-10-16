# 0x0005BA60 is ATL::AtlThrowLastWin32

The 26-byte body at `0x0005BA60`, ledgered as the address-derived
`?Rva0005BA60ThrowLastWin32@@YGXXZ` in
game/gen_small/W3AtlConversionSupport.cpp, is the VS2003 atlexcept.h inline
`ATL::AtlThrowLastWin32()`, compiler symbol `?AtlThrowLastWin32@ATL@@YGXXZ`
(`inputs/toolchains/vs2003/Program Files/Microsoft Visual Studio .NET 2003/Vc7/atlmfc/include/atlexcept.h` line 79: `DWORD dwError = ::GetLastError(); AtlThrow( HRESULT_FROM_WIN32( dwError ) );`).

- Retail bytes: `ff 15 b4 8d 35 01 85 c0 7e 0a 25 ff ff 00 00 0d 00 00 07 80 50 e8 54 e0 fb ff`
  = `call [GetLastError]`, the inline HRESULT_FROM_WIN32 (`x <= 0 ? x :
  (x & 0xFFFF) | 0x80070000`), and a tail call into ILT 0x00019ACE, which jumps
  to 0x0005BA40, pinned in symbols.csv as `?AtlThrow@ATL@@YGXJ@Z` (VS2003
  atlexcept.h). The body has no epilogue: AtlThrow is __declspec(noreturn).
- Callers: retail reaches it only through ILT 0x00032AF1 (`e9` to 0x0005BA60),
  from 0x0005DADF inside 0x0005DA80 (CW2AEX<128>::Init) and 0x0005DB6A inside
  0x0005DB10 (CA2WEX<128>::Init), exactly the two atlconv.h Init failure arms
  that call AtlThrowLastWin32 when the conversion API returns 0.
- Emitters: T3AtlCImageCreateFromGdiplusBitmap.cpp and
  Rva00060010CImageLoadAnsi.cpp include the pristine `<atlimage.h>` and their
  objects define `?AtlThrowLastWin32@ATL@@YGXXZ`; the scoped gate reproduces
  retail's 26 bytes from that definition with every relocation resolved.

Refuted by: a scoped build that does not reproduce the bytes, or a caller
other than the two ATL Init bodies.
