# 0x000C5C90: an ActionManager.cpp helper beside canCaptureBuilding

The 90-byte body at 0x000C5C90 was ledgered as
`?bfmeCanSeeVNI@@YGDPAVBfmeObjVNI@@0PAX@Z` in its own TU (BfmeConv1513.cpp).
It calls the file-static `isObjectShroudedForAction` (0x000C3F80), so that
TU could not link (link queue rank 355, 90 B).

- It cannot have been compiled outside ActionManager.cpp. Its call at
  0x000C5CB0 passes only the command source on the stack, with the two
  objects already in EDI/ESI. That is the register ABI the compiler gives
  the static `isObjectShroudedForAction` within its own TU (matched
  0x000C3F80, ActionManager.cpp).
- Placement: it follows the matched `ActionManager::canCaptureBuilding`
  0x000C5AE0 (337 B) inside ActionManager.cpp's range (0x000C3F80..0x000C6930
  rows).
- Body: null checks, the +0x344 bit 0 veto canCaptureBuilding also uses,
  the shroud test, `Object::getRelationship` == ENEMIES, the +0x90 bit 6
  veto, then `!(+0x1A4 bit 5)`. `ret 0Ch`, ECX never read.
- Open-BFME-2's matched 0x0041C96C (88 B, "two Object pointers and command
  source with unused ECX; dead/shroud/enemy checks") sits right after its
  canCaptureBuilding twin, in its ActionManager unit beside the static
  `isObjectShroudedForAction`.
- No rel32 call, ILT jump or DIR32 pointer reaches it or its ILT 0x000424D8
  in retail. Its real name is unproven, so it stays address-derived:
  `rva000C5C90`.
