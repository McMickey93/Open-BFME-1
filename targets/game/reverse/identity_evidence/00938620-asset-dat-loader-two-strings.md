# 0x00938620: the asset.dat loader takes two AsciiStrings by value

The matched row named the body at 0x00938620 (1057 bytes, retail ends with a
plain `ret` at +0x420) `?Load_Asset_Dat@@YA_NXZ`, a function with no
arguments. The name came with a naked `__emit` lift
(game/Libraries/Source/WWVegas/WW3D2/Load_Asset_Dat.cpp) and no evidence.
Retail disproves the empty argument list:

- The only caller, W3DDisplay::init at 0x006ED5B0 (vtable 0x0111EDD0 slot 1),
  copy-constructs two strings into the outgoing slots with the StringBase<char>
  copy constructor 0x00887B60: GlobalData+0xDC4 at +0x4FC, then GlobalData+0xDC0
  at +0x51B, calls 0x00938620 at +0x524 and pops both slots (`add esp, 8`).
- The body's unwind map (handler 0x00C5D4A0, FuncInfo 0x00E4C634) has two
  states that destroy `[ebp+4]` and `[ebp+8]`, the two incoming slots, and the
  body releases both through releaseBuffer 0x00887940 before returning.
- The body reads both slots as string headers (`cmp word ptr [eax+4], 0` on
  `[esp+0x1b0]` and `[esp+0x1ac]`) and calls StringBase<char>::concat on the
  first one.

So the signature is `bool (AsciiString, AsciiString)`, already pinned in
symbols.csv as `?Rva00938620@@YA_NVAsciiString@@0@Z` and declared that way in
W3DDisplayInit_Bfme.cpp. EA's file for the address is
Libraries/Source/WWVegas/WW3D2/assetinit.cpp (ea_evidence.csv, route wb1), but
no source names the function, so it keeps the address-derived name
`?Rva00938620@@YA_NVAsciiString@@0@Z` and retires `?Load_Asset_Dat@@YA_NXZ`.
