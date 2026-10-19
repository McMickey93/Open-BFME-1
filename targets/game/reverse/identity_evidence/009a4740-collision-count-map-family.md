# 0x009A4740 and its map: one `map<Rva009A2FE0Sub *, unsigned>` instantiation

0x009A4740 (750 B, a gen-dump until now) walks the collision data's two
bucket tables. It counts every node's two sub-object pointers in a local
`map<Rva009A2FE0Sub *, unsigned>`. The tree helpers it reaches were spread
over unrelated names. Retail was linked without identical-COMDAT folding,
so each helper body is exactly one instantiation. Every caller of every
helper below belongs to this family, so all of them are the count map that
game/Libraries/Source/collisionmanager/Rva009A4740CollisionDataCount.cpp
instantiates. That TU compiles each one byte-equal to retail.

| RVA | size | role | old claim(s) |
|---|---|---|---|
| 0x009A46C0 | 115 | `map::operator[]` | `map<unsigned, Image*>::operator[]` (Image.cpp) |
| 0x009A46A0 | 31 | `map::insert(iterator, const value&)` | `map<unsigned, Image*>::insert` (Image.cpp) |
| 0x009A4350 | 592 | `_Rb_tree::insert_unique(iterator, const value&)` | `_Rb_tree<unsigned, pair<const unsigned, Image*>>::insert_unique` (Image.cpp) |
| 0x009A41E0 | 145 | `_Rb_tree::insert_unique(const value&)` | `_Rb_tree<unsigned, pair<const unsigned, State*>>::insert_unique` (StateMachine.cpp) and `_Rb_tree<const ThingTemplate*, ...>::insert_unique` (InGameUI.cpp) |
| 0x009A4130 | 176 | `_Rb_tree::_M_insert` | address-named `Rva009A4130Target` tree (RvaTreeMInsert009A4130.cpp) |
| 0x009A3520 | 23 | `_Construct<pair>` for the 8-byte node value | address-named `Rva009A4130` pair (RvaTreeMInsert009A4130.cpp) |
| 0x009A34A0 | 53 | `_Rb_tree::_M_erase` | gen-tgrid placeholder |
| 0x009A4010 | 124 | `_Rb_tree::~_Rb_tree` | gen-tgrid placeholder |

## Callers (full rel32 scan of retail .text, `E8` and `E9`)

- 0x009A46C0: 0x009A4822, 0x009A4866, 0x009A4981 and 0x009A49C4, all
  inside 0x009A4740. No ILT reaches it.
- 0x009A4350: 0x009A4712 (inside 0x009A46C0) and 0x009A46B4 (inside the
  uncalled 31-byte `map::insert` at 0x009A46A0, adjacent).
- 0x009A46A0: no caller in retail .text. It forwards to 0x009A4350 and sits
  between 0x009A4350 and 0x009A46C0.
- 0x009A41E0: 0x009A437A, 0x009A4441, 0x009A448D and 0x009A4589, all
  inside 0x009A4350.
- 0x009A4130: ten sites, 0x009A4246..0x009A455C, all inside 0x009A41E0
  and 0x009A4350.
- 0x009A3520: 0x009A4130 and the 0x18-byte node factory 0x009A3930.
  0x009A3930 allocates the tree node and constructs the pair at +0x10, and
  its source still reaches 0x009A3520 through the address pin
  `?gen009A3520@@YAXPAX0@Z`.
- 0x009A34A0: 0x009A4740 and the two 51-byte `clear` placeholders at
  0x009A3800 and 0x009A3FB0.
- 0x009A4010: 0x009A4A16 (inside 0x009A4740) and the ILT 0x009A4280.

## The Image map lives elsewhere

Matched `ImageCollection::addImage` (0x005D3410, Image.cpp) does
`m_imageMap[key] = image` through ILT 0x0002A52C, which jumps to
0x005D3380. symbols.csv pins the Image `operator[]` name at 0x0002A52C
("REL32 pin from ImageCollection::addImage @0x5D3410"). The Image map's
helpers are therefore not the ones next to the collision code. Nothing in
the State or ThingTemplate code reaches 0x009A41E0 either.

## Cross-check

Open-BFME-2 matched the same walk at its 0x0075A1A0. After relocations are
explained, its bytes are identical to BFME1's 0x009A4740, and it uses the
same pointer-keyed count map.

The key and value spelling stays address-derived: no string, vtable or
helper names the sub-object type.

## Pin identity overrides

Each line cites a matched hand-written caller in this TU whose compiled
REL32 at the call site names the symbol. The old stand-in pins at these
bodies name the Image, State and ThingTemplate trees, which never reach
them.

pin-identity-override: ??$_Construct@U?$pair@QAURva009A2FE0Sub@@I@_STL@@U12@@_STL@@YAXPAU?$pair@QAURva009A2FE0Sub@@I@0@ABU10@@Z 0x009A3520 the count-map _M_insert caller=0x009A4130 calls it for the node value
pin-identity-override: ?_M_insert@?$_Rb_tree@PAURva009A2FE0Sub@@U?$pair@QAURva009A2FE0Sub@@I@_STL@@U?$_Select1st@U?$pair@QAURva009A2FE0Sub@@I@_STL@@@3@U?$less@PAURva009A2FE0Sub@@@3@V?$allocator@U?$pair@QAURva009A2FE0Sub@@I@_STL@@@3@@_STL@@AAE?AU?$_Rb_tree_iterator@U?$pair@QAURva009A2FE0Sub@@I@_STL@@U?$_Nonconst_traits@U?$pair@QAURva009A2FE0Sub@@I@_STL@@@2@@2@PAU_Rb_tree_node_base@2@0ABU?$pair@QAURva009A2FE0Sub@@I@2@0@Z 0x009A4130 the count-map insert_unique caller=0x009A41E0 inserts through it
pin-identity-override: ?insert_unique@?$_Rb_tree@PAURva009A2FE0Sub@@U?$pair@QAURva009A2FE0Sub@@I@_STL@@U?$_Select1st@U?$pair@QAURva009A2FE0Sub@@I@_STL@@@3@U?$less@PAURva009A2FE0Sub@@@3@V?$allocator@U?$pair@QAURva009A2FE0Sub@@I@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@QAURva009A2FE0Sub@@I@_STL@@U?$_Nonconst_traits@U?$pair@QAURva009A2FE0Sub@@I@_STL@@@2@@_STL@@_N@2@ABU?$pair@QAURva009A2FE0Sub@@I@2@@Z 0x009A41E0 the count-map hinted insert_unique caller=0x009A4350 falls back to it
pin-identity-override: ?insert_unique@?$_Rb_tree@PAURva009A2FE0Sub@@U?$pair@QAURva009A2FE0Sub@@I@_STL@@U?$_Select1st@U?$pair@QAURva009A2FE0Sub@@I@_STL@@@3@U?$less@PAURva009A2FE0Sub@@@3@V?$allocator@U?$pair@QAURva009A2FE0Sub@@I@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@QAURva009A2FE0Sub@@I@_STL@@U?$_Nonconst_traits@U?$pair@QAURva009A2FE0Sub@@I@_STL@@@2@@2@U32@ABU?$pair@QAURva009A2FE0Sub@@I@2@@Z 0x009A4350 the count-map operator[] caller=0x009A46C0 inserts through it
