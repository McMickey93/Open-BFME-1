# 0x001DDCB0 is SimpleObjectIterator::insert(Object*, Real)

- ILT 0x0002CAE8 is `jmp 0x001DDCB0` (bytes `e9 c3 11 1b 00`), and symbols.csv
  pins `?insert@SimpleObjectIterator@@QAEXPAVObject@@M@Z` to that ILT.
- Matched callers reach it through that ILT with the iterator in ecx and an
  (Object*, Real) pair:
  - AIGroup::groupTightenToPosition 0x00155720 +0xB6
  - AIGroupGroupAttackObjectPrivateShim::attack00155DA0 0x00155DA0 +0xB9
    (Zero Hour's `iter->insert((*i), dx * dx + dy * dy)`).
- The body is Zero Hour's insert: build a 16-byte Clump with `new`
  (vtable, next, obj, numeric), push it at the front of the list at this+0x04,
  store obj and numeric, `++m_clumpCount` at this+0x0C, `ret 8`.
- Retail was linked without ICF, so this one address has one identity. The
  row's earlier placeholder `Bfme5PushList::bfmePushFront(void*, void*)` was
  the same bytes under an unproven name. The float numeric is copied as a
  dword, which is why the source stores its bits as a word.
