# pin --candidates batch 3: names the thunk table puts on the pinned body (op-1, 2026-10-16)

Approved by the project lead 2026-10-16. For each name below, `pin_consistency --candidates` showed a
functions.csv row at one body and a symbols.csv pin at an incremental-link thunk that jumps to a
different body. Retail had no identical-COMDAT folding, so only one of them can carry the name.
`tools/ilt_oracle.py` tests a decorated name against the window of the thunk slot it is called
through (link.exe external-symbol hash order; a wrong name fits with p ~ 1e-3). For every name
here it CONFIRMS the name at the pinned thunk and CONTRADICTS it at the thunk of the body the row
claimed. The two bodies are the same size and byte-equal apart from relocations.

The name moves to the pinned body, replacing a placeholder (gen-tgrid, gen-shim, ?dup_ or
address-named) row there. The previously claimed body keeps its bytes under a `?dup_<rva>` row
that aliases the same compiled COMDAT (`object-symbol=`): its own identity is unknown.

| name | old body (thunk: verdict) | pinned thunk -> body (verdict) |
|---|---|---|
| `??0?$list@PAVSuperweaponInfo@@V?$allocator@PAVSuperweaponInfo@@@_STL@@@_STL@@QAE@ABV01@@Z` | 0x76f640 (0x000296E5: CONTRADICTED) | 0x3fa67 -> 0x443d60 (CONFIRMED) |
| `??0DisplayString@@QAE@XZ` | 0xd16f0 (0x00026580: CONTRADICTED) | 0x20c25 -> 0x410000 (CONFIRMED) |
| `??4?$_Rb_tree@W4NameKeyType@@U?$pair@$$CBW4NameKeyType@@M@_STL@@U?$_Select1st@U?$pair@$$CBW4NameKeyType@@M@_STL@@@3@U?$less@W4NameKeyType@@@3@V?$allocator@U?$pair@$$CBW4NameKeyType@@M@_STL@@@3@@_STL@@QAEAAV01@ABV01@@Z` | 0x5672c0 (0x00013403: CONTRADICTED) | 0x2ca16 -> 0xd63c0 (CONFIRMED) |
| `??A?$hash_map@HW4Relationship@@U?$hash@H@_STL@@U?$equal_to@H@3@V?$allocator@U?$pair@$$CBHW4Relationship@@@_STL@@@3@@_STL@@QAEAAW4Relationship@@ABH@Z` | 0x787d80 (0x00027E30: CONTRADICTED) | 0x1219d -> 0xd6340 (CONFIRMED) |
| `??A?$map@GHU?$less@G@_STL@@V?$allocator@U?$pair@$$CBGH@_STL@@@2@@_STL@@QAEAAHABG@Z` | 0x37c560 (0x00028D0D: CONTRADICTED) | 0x302f1 -> 0x669560 (CONFIRMED) |
| `??A?$map@PBVThingTemplate@@HU?$less@PBVThingTemplate@@@_STL@@V?$allocator@U?$pair@QBVThingTemplate@@H@_STL@@@3@@_STL@@QAEAAHABQBVThingTemplate@@@Z` | 0x5d3380 (0x0002A52C: CONTRADICTED) | 0x17111 -> 0xea510 (CONFIRMED) |
| `?erase@?$_Rb_tree@VAsciiString@@U?$pair@$$CBVAsciiString@@V1@@_STL@@U?$_Select1st@U?$pair@$$CBVAsciiString@@V1@@_STL@@@3@U?$less@VAsciiString@@@3@V?$allocator@U?$pair@$$CBVAsciiString@@V1@@_STL@@@3@@_STL@@QAEIABVAsciiString@@@Z` | 0x456690 (0x0003EE37: CONTRADICTED) | 0x106fe -> 0x7e090 (CONFIRMED) |
| `?insert_unique@?$_Rb_tree@GU?$pair@$$CBGE@_STL@@U?$_Select1st@U?$pair@$$CBGE@_STL@@@2@U?$less@G@2@V?$allocator@U?$pair@$$CBGE@_STL@@@2@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBGE@_STL@@U?$_Nonconst_traits@U?$pair@$$CBGE@_STL@@@2@@2@U32@ABU?$pair@$$CBGE@2@@Z` | 0x9401f0 ((none): CONTRADICTED) | 0xde77 -> 0x668150 (CONFIRMED) |
| `?push_back@?$vector@PAVObject@@V?$allocator@PAVObject@@@_STL@@@_STL@@QAEXABQAVObject@@@Z` | 0x754670 (0x0001CCF6: CONTRADICTED) | 0x19e70 -> 0x18b910 (CONFIRMED) |
| `?push_back@?$vector@VAsciiString@@V?$allocator@VAsciiString@@@_STL@@@_STL@@QAEXABVAsciiString@@@Z` | 0x757e20 (0x00046EBB: CONTRADICTED) | 0x32317 -> 0x638c0 (CONFIRMED) |

## What landed

- All eight old bodies were renamed to `?dup_<rva>` aliases: 0x0076F640, 0x000D16F0,
  0x005672C0, 0x00787D80, 0x005D3380, 0x00456690, 0x009401F0 and 0x00757E20.
- Only `?push_back@?$vector@VAsciiString@@...` moved to its pinned body (0x000638C0,
  replacing a tgrid_100 gen-tgrid row). Its TU's compiled COMDAT byte-matches there.
- The other seven names stay pin-only. Their pinned bodies differ from what their
  TUs compile, so those TUs spell the type wrong: list<SuperweaponInfo*> at
  0x00443D60 allocates 0x0C-byte nodes, while InGameUI.cpp's compile allocates
  0x2C. Each needs its own TU re-typing.
- Skipped: 0x0037C560 (a vendored zhstl row) and 0x00754670 (two rows on one body).
