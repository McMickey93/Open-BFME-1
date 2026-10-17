# 0x00415BC0: Anim2DTemplate::getName

Retail `0x00415BC0` (32 bytes) returns a copy of the AsciiString at `this+8`
(`push ecx; push esi; ... add ecx,8; call 0x00887B60` StringBase<char> copy
ctor; `ret 4`). The ledger carried it as `dup_415bc0`, a `dup-of` placeholder of
the byte-identical `Rva000EE6D0StringAccessor::getString`, so it had no identity
of its own and `?getName@Anim2DTemplate@@QBE?AVAsciiString@@XZ` had no
definition at link time.

Evidence (`tools/callers_of.py 0x00415BC0`, ILT `0x00012E72` = `jmp 0x00415BC0`):

- `0x005BB330` `Anim2DCollection::findTemplate` (matched,
  Anim2DCollectionTemplates.cpp) calls ILT `0x00012E72` where its C++ calls
  `animTemplate->getName()`.
- `0x005BB150` `Anim2DTemplate::parseImageSequence` (matched,
  Anim2DTemplate_parseImageSequence_Thunk.cpp) calls ILT `0x00012E72` twice
  where its C++ calls `animTemplate->getName().str()`.
- The other callers are `Anim2DTemplate::parseNumImages`,
  `Anim2DTemplate::storeImage` and `Drawable::xfer` (ZH xfers the icon's
  Anim2D template name), all Anim2DTemplate users.
- `symbols.csv` already pins the name at the ILT `0x00012E72`.
- Layout: template vptr +0, `m_nextTemplate` +4 (findTemplate walks +4),
  `m_name` +8 (ZH Anim2DTemplate field order).

Retail has no identical-COMDAT folding, so this copy is the Anim2DTemplate
accessor and the six other 32-byte copies keep their own identities.
