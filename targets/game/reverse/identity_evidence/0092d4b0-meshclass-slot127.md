# 0x0092D4B0 is MeshClass vtable slot 127; its name stays address-derived

Retail 0x0092D4B0 (419 B, `ret 8`) is referenced only from MeshClass's
vtable at 0x0113C58C, the slot after `Recolor0092DF50@MeshClass` (slot 126,
0x0092DF50) and `Replace_Texture@MeshClass` (slot 125). It is therefore a
MeshClass virtual taking `(int, const char *)`, landed as
`?rva0092D4B0@MeshClass@@UAEXHPBD@Z`.

The banked attempt `attempts/0x0092d4b0.cpp` spelled it
`?apply@Rva0092D4B0@@QAEXHPBD@Z` and its 0x00929900 callee `setTexture`;
neither name had evidence. The callee keeps its ledger name
`?bfmeSetVGT@BfmeMeshVGT@@QAEXPAPAVBfmeTexVGS@@HH@Z` (0x00929900), and the
method takes the MeshClass owner the vtable proves with an address-derived
method token, since no caller or string names the slot.
