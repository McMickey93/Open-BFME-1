# W3DModelDraw constructor bank: particle-list element size

This corrects a checker pairing in the partial reconstruction of RVA `0x00773360`, not a production identity or a proven byte match. `ParticleSystemID` remains `typedef int ParticleSystemID;` and remains the type of `Rva00773360ParticleEntry::m_id`. The address-derived struct represents the containing list payload, not a renamed integer ID.

Independent retail evidence from the baseline executable:

- Constructor RVA `0x007733B5` pushes `0x1C` before calling `_STL::__node_alloc::_M_allocate` at `0x0082E540`. It zeros owner `+0x48`, initializes both node links to the returned node, then stores that sentinel at owner `+0x48` (`0x007733BC` through `0x007733C9`).
- Destructor RVA `0x0077B2F2` pushes `0x1C` and then the node before calling `_M_deallocate` at `0x0082E5F0`. The preceding list cleanup uses the same owner list at `+0x48`.
- The existing byte-verified `W3DModelDraw::updateSubObjectsFromShroud` at `0x00762500` traverses the list at `+0x48` and consumes the first payload dword as a particle-system ID. Its source is `game/GameEngineDevice/Source/W3DDevice/GameClient/Drawable/Draw/W3DModelDraw_updateSubObjectsFromShroud.cpp`. That reader supports the ID field, but its `list<ParticleSystemID>` view alone cannot prove the full allocation size.

The STLport node has two four-byte links, so the observed 28-byte allocation leaves a 20-byte payload. A four-byte `ParticleSystemID` alone would require a 12-byte node. The revised bank therefore keeps the ID and models the remaining 16 bytes as unclaimed storage, under an address-derived containing-record name. No gameplay identity is asserted for that record.

The exact UTF-8 snapshots, including line endings, are:

- Before: `b083ef245f835ecd2d68e7457996d71c21f24d95aff4bac0875edfc57a2296d7`
- After (staged bank): `13f9c6070f9ce88959042b4b886b904bfa791ad4e620120bde993c16baa326ed`

The supported `name_corrections.json` entry is limited to these hashes and the `ParticleSystemID` / `Rva00773360ParticleEntry` pairing. It does not waive byte, relocation, header-adoption, or production verification requirements. The saved constructor remains a non-exact partial.
