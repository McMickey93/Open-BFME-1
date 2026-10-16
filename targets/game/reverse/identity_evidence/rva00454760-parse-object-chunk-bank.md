# 0x00454760 ParseObjectDataChunk bank: registry view name

The earlier bank called the template-registry view `ThingNameRegistry`, a
stand-in with no retail evidence, and reached its methods through
`/alternatename` to `?j_0002323b` / `?j_00028560`. The same ILT slots are
pinned in symbols.csv as `Rva0088B70ThingRegistry::acceptsThingTemplateName`
(0x0002323B) and `Rva0088B70ThingRegistry::findTemplate` (0x00028560) by the
matched object reader 0x00088B70 (game/GameEngine/Source/Common/MapObject.cpp),
so the bank now uses that address-derived view, which links without
alternatename. The owner (ThingFactory) is not renamed here.
