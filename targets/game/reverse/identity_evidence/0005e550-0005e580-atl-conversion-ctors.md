# 0x0005E550 / 0x0005E580 are ATL CW2AEX<128> / CA2WEX<128> constructors

The two 33-byte bodies ledgered under address-derived names in
game/gen_small/W3AtlConversionHolderCtors.cpp are the VS2003 atlconv.h
one-argument constructors:

- `0x0005E550` `??0Rva0005DA80WideToAnsi@@QAE@PBG@Z` is
  `??0?$CW2AEX@$0IA@@ATL@@QAE@PBG@Z`, `CW2AEX<128>::CW2AEX(LPCWSTR)`
  (`inputs/toolchains/vs2003/Program Files/Microsoft Visual Studio .NET 2003/Vc7/atlmfc/include/atlconv.h` line 417: `m_psz( m_szBuffer ) { Init( psz, _AtlGetConversionACP() ); }`).
- `0x0005E580` `??0Rva0005DB10AnsiToWide@@QAE@PBD@Z` is
  `??0?$CA2WEX@$0IA@@ATL@@QAE@PBD@Z`, `CA2WEX<128>::CA2WEX(LPCSTR)`
  (atlconv.h line 354, same shape).

Evidence:
- Retail bytes (identical apart from the call): `56 8b f1 8d 46 04 89 06 ff 15
  c0 64 2a 01 8b 4c 24 08 50 51 8b ce e8 .. .. .. .. 8b c6 5e c2 04 00`:
  m_psz = &m_szBuffer (this+4), `call [0x012A64C0]` = the inline
  _AtlGetConversionACP() through `?g_pfnGetThreadACP@ATL@@3P6GIXZA` (pinned at
  0x012A64C0 in symbols.csv and dir32_addresses.csv), then Init(psz, acp) and
  return this.
- The calls land on ILT 0x0000F62D -> 0x0005DA80 and ILT 0x000022B1 ->
  0x0005DB10, pinned in symbols.csv as `?Init@?$CW2AEX@$0IA@@ATL@@AAEXPBGI@Z` and
  `?Init@?$CA2WEX@$0IA@@ATL@@AAEXPBDI@Z`; the 0x80-byte buffer at this+4 is
  the <128> template argument.
- No retail `call` reaches either body (only the ILT thunks 0x0003B4FD and
  0x0004A3C2 name them): they are emitted COMDAT copies; the retail callers
  (0x0005F680 ATL::GetEnvironmentVariableW wrapper, 0x00060010
  CImage::Load(LPCSTR)) inline the constructor and call Init directly.
- Emitters: T3AtlCImageCreateFromGdiplusBitmap.cpp (CW2AEX) and
  Rva00060010CImageLoadAnsi.cpp (both) include the pristine `<atlimage.h>` and
  define these symbols; the scoped gate reproduces retail's bytes.

Refuted by: a scoped build that does not reproduce the bytes, or a different
Init callee or ACP slot.
