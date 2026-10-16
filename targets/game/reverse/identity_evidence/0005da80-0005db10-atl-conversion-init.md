# 0x0005DA80 / 0x0005DB10 are ATL CW2AEX<128>::Init and CA2WEX<128>::Init

The two conversion-holder bodies ledgered under address-derived names
`?init@Rva0005DA80WideToAnsi@@QAEXPBGI@Z` (107 B) and
`?init@Rva0005DB10AnsiToWide@@QAEXPBDI@Z` (101 B) in
game/gen_small/W3AtlStringConversion.cpp are the VS2003 `atlconv.h`
template members `ATL::CW2AEX<128>::Init(LPCWSTR, UINT)` and
`ATL::CA2WEX<128>::Init(LPCSTR, UINT)`:

- The census of compiled objects shows both symbols emitted, unclaimed, by
  TUs that include the pristine VS2003 atlmfc headers:
  `?Init@?$CW2AEX@$0IA@@ATL@@AAEXPBGI@Z` by
  game/GameEngine/Source/Common/T3AtlCImageCreateFromGdiplusBitmap.cpp and
  `?Init@?$CA2WEX@$0IA@@ATL@@AAEXPBDI@Z` by
  game/GameEngine/Source/Common/Rva00060010CImageLoadAnsi.cpp. Their
  compiled section bytes equal retail at the full extents with only the
  relocation slots masked.
- The callees agree with atlconv.h: lstrlenW/WideCharToMultiByte resp.
  lstrlenA/MultiByteToWideChar, malloc for the >128-unit case, and the
  AtlThrow helpers through ILT 0x00019ACE / 0x00032AF1.
- symbols.csv already pins both real names at these addresses
  (`direct body pin: VS2003 ATL CW2AEX<128> initializer ... ILT 0x0000F62D`
  and `VS2003 atlconv.h CA2WEX conversion helper alias`), so the
  address-derived row names were a second identity on each body.
- Retail bytes, 0x0005DA80 (107 B): `53 55 8b 6c 24 0c 85 ed 8b d9 75 07 89 2b
  5d 5b c2 08 00 56 57 55 ff 15 8c 8f 35 01 ...` (NULL source stores NULL and
  returns; lstrlenW+1, byte count against 0x80, dllimport malloc, E_OUTOFMEMORY
  0x8007000E to AtlThrow, WideCharToMultiByte, zero -> AtlThrowLastWin32,
  `ret 8`). 0x0005DB10 (101 B) is the same shape with lstrlenA and
  MultiByteToWideChar, as atlconv.h lines 378 and 441 read.
- Callers: 0x0005E566 (constructor 0x0005E550) and 0x0005F6D4 (ATL's
  GetEnvironmentVariableW wrapper 0x0005F680, which inlines the CW2AEX
  constructor) call 0x0005DA80 through ILT 0x0000F62D; 0x0005E596 (constructor
  0x0005E580) and 0x00060042 (`?Load@CImage@ATL@@QAEJPBD@Z`, CImage::Load's
  CT2W temporary) call 0x0005DB10 through ILT 0x000022B1.
- The failure arms call `?AtlThrowLastWin32@ATL@@YGXXZ` (0x0005BA60, see
  0005ba60-atl-throw-last-win32.md) through ILT 0x00032AF1 and AtlThrow through
  ILT 0x00019ACE; the constructors at 0x0005E550/0x0005E580 call these bodies
  (0005e550-0005e580-atl-conversion-ctors.md).

Refuted by: a scoped build of either TU that does not reproduce the bytes,
or a different callee set.
