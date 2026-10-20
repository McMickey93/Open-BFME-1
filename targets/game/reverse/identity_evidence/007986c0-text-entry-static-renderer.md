# 0x007986C0 text-entry renderer (file-static of W3DGadgetTextEntryDraw's TU)

- Boundary: retail [0x007986C0, 0x00798D78), 1720 bytes, `ret` at +0x6B7
  then INT3.
- ABI: both retail callers (0x00798F30 and 0x007991A0) push seven dwords
  and clean 0x1C bytes themselves. The callee reads the window at entry+4,
  four colours, then x and y.
- Linkage: 0x00798F30 reaches the body with a direct `call 0x007986C0`, not
  through the ILT, so the body is internal to that caller's TU. The C++
  matches only when compiled that way. With external linkage MSVC 7.1 loads
  x late and gives EBX to the window, where retail keeps x in EBP from entry.
- Identity: the symbols.csv pin
  `?drawTextEntryText@@YAXPAVGameWindow@@PAVWinInstanceData@@HHHHHHHH@Z`
  carries Zero Hour's ten-argument signature, which the seven-word caller ABI
  refutes. The BFME body is a selection-range rewrite of that helper, so the
  row keeps the address-derived spelling `Rva007986C0`. The matched,
  hand-written caller W3DGadgetTextEntryDraw (0x00798F30) names that
  spelling at its call site.

pin-identity-override: ?Rva007986C0@@YAXPAVGameWindow@@HHHHHH@Z 0x007986C0 the matched hand-written W3DGadgetTextEntryDraw caller=0x00798F30 calls it directly with seven cdecl words; the ten-argument ZH drawTextEntryText pin is refuted by that ABI
