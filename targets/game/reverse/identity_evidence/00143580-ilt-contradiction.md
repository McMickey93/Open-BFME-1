# 0x00143580: ThingTemplate asset collector keeps its address

The 339-byte body at 0x00143580 was ledgered as
`?GetAssetList@ThingTemplate@@QBEXAAVAssetList@@PAX@Z`. Retail reaches it
through the incremental-link thunk at 0x00004B92 (`jmp 0x00143580`), which the
converted caller 0x00144DC0 calls twice (+0x6D, +0x8B).

`tools/ilt_oracle.py check '?GetAssetList@ThingTemplate@@QBEXAAVAssetList@@PAX@Z' 0x00004B92`
reports CONTRADICTED (p_false 7.18e-04, outside every window of slot 3049,
buckets 3190-3200). A search over 15 method spellings (GetAssetList,
getAssetList, GetAssets, collectAssets, ...) x 4 classes (ThingTemplate,
Thing, Object, Overridable) x 6 access/const/virtual/return forms x 5 parameter
spellings (AssetList& / AssetList*, void* / const void*) found no decoration
that fits the window, so the real name is unknown.

Nothing in the ledger proved the GetAssetList name: Zero Hour's ThingTemplate
has no such method, and the name was taken by analogy with
GenericObjectCreationNugget::GetAssetList. Per AGENTS.md an unproven identity
keeps an address-derived name, so the row becomes
`?rva00143580@ThingTemplate@@QBEXAAVAssetList@@PAX@Z` (class, access, const
and signature unchanged: the bytes, the receiver and the callers are the same),
and the thunk pin at 0x00004B92 carries that name with route=0x00143580.
