# 0x0069C470: `__uninitialized_copy<const Rva0069C300Element *, Rva0069C300Element *>`

Old row: `?dup_0069c470@@YAXXZ`, a gen-alias of the HideShowSubObjInfo
`__uninitialized_copy` object in HideShowSubObjInfoUninitializedCopyBody.cpp.
New name: `??$__uninitialized_copy@PBURva0069C300Element@@PAU1@@_STL@@YAPAURva0069C300Element@@PBU1@0PAU1@ABU__false_type@0@@Z`.

The two 45-byte bodies are the same template shape but call different element
constructs, and retail was linked without identical-COMDAT folding:

- 0x0069C470 calls ILT 0x0004A818, which jumps to 0x0069C300, the matched
  `_Construct<Rva0069C300Element>` (Rva006A8120IndexedEntryApply.cpp,
  006a8120-element-contracts.md).
- 0x003AA480 calls ILT 0x00033FF0, which jumps to the 8-byte construct at
  0x003A9110, the callee the HideShowSubObjInfo allocate-and-copy body uses.

One object symbol cannot produce both call targets, so 0x0069C470 is
instantiated beside its element's construct. tools/probe.py: EXACT, 45 bytes.
