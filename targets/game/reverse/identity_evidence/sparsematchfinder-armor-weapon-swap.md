# SparseMatchFinder Armor/Weapon identity evidence

Approved header project, project lead 2026-10-16. Investigator: fleet sol-1, GPT-6.1 Sol.

Baseline: `inputs/baselines/bfme1/retail-1.03-unpacked/files/lotrbfme.exe`; image base 0x00400000.
Snapshot: `37f19b491b5753c4d0afcdc480563b58f3b98dbf`.
The lead-referenced `build/linkfleet/ds/pin_candidates_open.tsv` is absent from ds-6; all evidence below is independently re-derived from this worktree's retail image and ledgers.

## Retail flag name arrays

Both arrays are NULL-terminated little-endian VA pointer arrays. In this baseline .data raw offsets equal RVAs. These are flag names, not the separate MODEL_CONDITION strings carrying similar prefixes.

### Armor: 11 entries, RVA/file offset 0x00EA68D8, VA 0x012A68D8

| Bit | String VA | Retail text |
| --- | --- | --- |
| 0 | 0x01073AA0 | `VETERAN` |
| 1 | 0x01073A98 | `ELITE` |
| 2 | 0x010741B8 | `HERO` |
| 3 | 0x01073A84 | `PLAYER_UPGRADE` |
| 4 | 0x01073A64 | `WEAK_VERSUS_BASEDEFENSES` |
| 5 | 0x01073F80 | `ALTERNATE_FORMATION` |
| 6 | 0x01074218 | `MOUNTED` |
| 7 | 0x01073A50 | `PLAYER_UPGRADE_2` |
| 8 | 0x01073A3C | `PLAYER_UPGRADE_3` |
| 9 | 0x01073A2C | `UNBESIEGEABLE` |
| 10 | 0x01073A20 | `AS_TOWER` |
| 11 | 0x00000000 | NULL terminator |

### Weapon: 29 entries, RVA/file offset 0x00EAD6B0, VA 0x012AD6B0

| Bit | String VA | Retail text |
| --- | --- | --- |
| 0 | 0x01073AA0 | `VETERAN` |
| 1 | 0x01073A98 | `ELITE` |
| 2 | 0x010741B8 | `HERO` |
| 3 | 0x01073A84 | `PLAYER_UPGRADE` |
| 4 | 0x010A1580 | `PASSENGER_TYPE_ONE` |
| 5 | 0x010A1568 | `PASSENGER_TYPE_TWO` |
| 6 | 0x01074FE8 | `GARRISONED` |
| 7 | 0x010A1558 | `CLOSE_RANGE` |
| 8 | 0x010A154C | `RAMPAGE` |
| 9 | 0x01073464 | `CONTESTING_BUILDING` |
| 10 | 0x010A153C | `WEAPON_RIDER1` |
| 11 | 0x010A152C | `WEAPON_RIDER2` |
| 12 | 0x010A151C | `WEAPON_RIDER3` |
| 13 | 0x010A150C | `WEAPON_RIDER4` |
| 14 | 0x010A14FC | `WEAPON_RIDER5` |
| 15 | 0x010A14EC | `WEAPON_RIDER6` |
| 16 | 0x010A14DC | `WEAPON_RIDER7` |
| 17 | 0x010A14CC | `WEAPON_RIDER8` |
| 18 | 0x010A14BC | `SPECIAL_ONE` |
| 19 | 0x010A14AC | `SPECIAL_TWO` |
| 20 | 0x010A14A0 | `CONTAINED` |
| 21 | 0x01074218 | `MOUNTED` |
| 22 | 0x010733A4 | `ENRAGED` |
| 23 | 0x010A148C | `SPECIAL_UPGRADE` |
| 24 | 0x01073DEC | `WEAPONSET_TOGGLE_1` |
| 25 | 0x01073DD4 | `WEAPONSET_TOGGLE_2` |
| 26 | 0x01073DBC | `WEAPONSET_TOGGLE_3` |
| 27 | 0x01073DA4 | `WEAPONSET_HERO_MODE` |
| 28 | 0x010A1470 | `WEAPONSET_ONE_RING_MODE` |
| 29 | 0x00000000 | NULL terminator |

Thus BFME uses `ArmorSetFlags = BitFlags<11>` and `WeaponSetFlags = BitFlags<29>`, each storing one 32-bit word (sizeof 4, not 11/17/29 bytes). MSVC non-type argument spellings are `$0L@` = 11, `$0BB@` = 17 (Zero Hour), `$0BN@` = 29, and `$0LL@` = 187. The 187-bit local empty class is a compilation spelling workaround, never BFME weapon flags.

`inputs/reference/shims/sweep/GameLogic/ArmorSet.h` already has the correct 11-entry enum. The shared Zero Hour `GameLogic/WeaponSetType.h` still has 17 entries: its first four agree, its later entries do not. Fix BFME through a shadow header rather than editing pristine upstream.

## Physical routing and identity anchors

`tools/dis_retail.py` proves:

- Comparator 0x00140740/75: `cmp edx,0x1d` at +0x38, weapon; ILT 0x0000A9A2 jumps here.
- Comparator 0x001407A0/75: `cmp edx,0x0b` at +0x38, armor; ILT 0x00010B1D jumps here.
- `ThingTemplate::findWeaponTemplateSet` 0x001467E0/73 uses vector +0x2F8 / finder +0x304; calls ILT 0x00042D1B -> tree find 0x00141220, ILT 0x00013ACA -> slow 0x00144000, ILT 0x00019155 -> map subscript 0x00145100.
- `ThingTemplate::findArmorTemplateSet` 0x00146780/73 uses vector +0x310 / finder +0x31C; calls ILT 0x0000AE20 -> tree find 0x001412A0, ILT 0x0002AFA4 -> slow 0x00144300, ILT 0x00036C0A -> map subscript 0x001451E0.
- `findBestInfo` 0x00146310/63 follows the weapon route (42D1B,13ACA,19155); 0x00146360/63 follows armor (AE20,2AFA4,36C0A). The ledger presently claims both real specializations at 146310 and calls the actual armor body `?dup_00146360@@YAXXZ`.
- Slow 0x00144000 really is weapon (29-bit mask, 0xEC-byte elements, flags at element+4); slow 0x00144300 really is armor (11-bit mask, 12-byte elements, flags at element+0). The slow family is not an Armor/Weapon swap; its weapon template argument still needs 17 -> 29.

## Complete family ledger snapshot

Rows below come from narrow `rg SparseMatchFinder` filters, not a full ledger dump. Names/notes are reproduced exactly. Their presence records a claim, not proof. Sibling shims whose name lacks SparseMatchFinder are included when their TU participates.

### functions.csv

```csv
??$_M_find@V?$BitFlags@$0BB@@@@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeapon,,0x00042D1B,5,game/GameEngine/Source/GameLogic/Object/STLWeaponTemplateSetBitFlagsFindThunk.cpp,matched,Open-BFME5 exact C++ thunk replacing MASM dump;object-symbol=??$_M_find@V?$BitFlags@$0BB@@@@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0BB@@@@Z
??$_M_find@V?$BitFlags@$0BB@@@@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0BB@@@@Z,,0x001412A0,96,game/GameEngine/Source/GameLogic/Object/STLWeaponTemplateSetBitFlagsHintedInsertUnique.cpp,matched,SparseMatchFinder Weapon map find beside the landed hinted insert; out-of-line MapHelper comparator
??$_M_find@V?$BitFlags@$0L@@@@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0L@@@@Z,,0x00141220,96,game/GameEngine/Source/GameLogic/Object/STLArmorTemplateSetBitFlagsHintedInsertUnique.cpp,matched,SparseMatchFinder ArmorT map find beside the landed hinted insert; out-of-line MapHelper comparator
??A?$map@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVWeaponTemplateSet@@ABV?$BitFlags@$0BB@@@@Z,,0x001451E0,106,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,resweep exact post-GWM-fix (exact-ambiguous)
??A?$map@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVArmorTemplateSet@@ABV?$BitFlags@$0L@@@@Z,,0x00145100,106,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,
??RMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QBE_NABV?$BitFlags@$0L@@@0@Z,,0x0000A9A2,5,game/GameEngine/Source/GameLogic/Object/SparseMatchFinderMapHelperThunks.cpp,matched,5-byte const SparseMatchFinder map helper thunk converted to focused C++ source
??RMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QBE_NABV?$BitFlags@$0BB@@@0@Z,,0x00010B1D,5,game/GameEngine/Source/GameLogic/Object/SparseMatchFinderMapHelperThunks.cpp,matched,5-byte const SparseMatchFinder weapon map helper thunk converted to focused C++ source
?_M_find@?$_Rb_tree@$$CBV?$BitFlags@$0LL@@@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0LL@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0LL@@@@Z,,0x00042D1B,5,game/GameEngine/Source/GameLogic/Object/SparseMatchFinderBitFlagsTreeFindThunk.cpp,matched,compiler-emitted symbol differs from truncated retail spelling
?_M_lower_bound@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0BB@@@@Z,,0x00140AB0,59,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,
?_M_lower_bound@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0L@@@@Z,,0x00140A60,59,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,
?call@ArmorMapHelperShim@@QBE_NABV?$BitFlags@$0L@@@0@Z,,0x00140740,75,game/GameEngine/Source/GameLogic/Object/SparseMatchFinderMapHelperThunks.cpp,matched,
?call@WeaponMapHelperShim@@QBE_NABV?$BitFlags@$0BB@@@0@Z,,0x001407A0,75,game/GameEngine/Source/GameLogic/Object/SparseMatchFinderMapHelperThunks.cpp,matched,
?clear@?$SparseMatchFinder@UModelConditionInfo@@V?$BitFlags@$0HF@@@@@QAEXXZ,,0x00078D20,51,game/GameEngine/Source/Common/UserPreferences.cpp,matched,object-symbol=?clear@?$map@VAsciiString@@V1@U?$less@VAsciiString@@@_STL@@V?$allocator@U?$pair@$$CBVAsciiString@@V1@@_STL@@@3@@_STL@@QAEXXZ;C++ alias
?clear@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QAEXXZ,,0x00078D20,51,game/GameEngine/Source/Common/UserPreferences.cpp,matched,object-symbol=?clear@?$map@VAsciiString@@V1@U?$less@VAsciiString@@@_STL@@V?$allocator@U?$pair@$$CBVAsciiString@@V1@@_STL@@@3@@_STL@@QAEXXZ;C++ alias
?clear@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QAEXXZ,,0x00078D20,51,game/GameEngine/Source/Common/UserPreferences.cpp,matched,object-symbol=?clear@?$map@VAsciiString@@V1@U?$less@VAsciiString@@@_STL@@V?$allocator@U?$pair@$$CBVAsciiString@@V1@@_STL@@@3@@_STL@@QAEXXZ;C++ alias
?countConditionIntersection@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@CAHABV?$BitFlags@$0L@@@0@Z,,0x0013F460,54,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,
?countConditionIntersection@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@CAHABV?$BitFlags@$0BB@@@0@Z,,0x0013F3E0,54,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,
?countConditionInverseIntersection@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@CAHABV?$BitFlags@$0L@@@0@Z,,0x00142160,15,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,
?dup_00146360@@YAXXZ,,0x00146360,63,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,zh-landmulti exact-multi ZH twin (rel32-all-resolve);object-symbol=?findBestInfo@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QBEPBVArmorTemplateSet@@ABV?$vector@VArmorTemplateSet@@V?$allocator@VArmorTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0L@@@@Z
?findBestInfo@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QBEPBVArmorTemplateSet@@ABV?$vector@VArmorTemplateSet@@V?$allocator@VArmorTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0L@@@@Z,,0x00146310,63,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,
?findBestInfo@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QBEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z,,0x00146310,63,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,resweep exact post-GWM-fix (exact-ambiguous)
?findBestInfoSlow@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@ABEPBVArmorTemplateSet@@ABV?$vector@VArmorTemplateSet@@V?$allocator@VArmorTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0L@@@@Z,,0x00144300,192,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,BFME ArmorSetFlags=11 bits (shadow shim ArmorSet.h)
?findBestInfoSlow@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@ABEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z,,0x00013ACA,5,game/GameEngine/Source/GameLogic/Object/SparseMatchFinderFindBestInfoSlowThunk.cpp,matched,Focused C++ thunk for weapon template best info search
?findBestInfoSlow@WeaponFindBestInfoSlowShim@@QBEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z,,0x00144000,195,game/GameEngine/Source/GameLogic/Object/SparseMatchFinderFindBestInfoSlowThunk.cpp,matched,BFME weapon matcher includes the trailing ret at +0xc0
?insert@?$map@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@_STL@@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z,,0x001444A0,31,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,
?insert@?$map@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@_STL@@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z,,0x00144450,31,game/GameEngine/Source/Common/Thing/ThingTemplate.cpp,matched,
?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$,,0x00010F1E,5,game/GameEngine/Source/GameLogic/Object/STLWeaponTemplateSetBitFlagsInsertUniqueThunk.cpp,matched,Open-BFME5 exact C++ thunk replacing MASM dump;object-symbol=?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z
?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z,,0x001429C0,629,game/GameEngine/Source/GameLogic/Object/STLWeaponTemplateSetBitFlagsHintedInsertUnique.cpp,matched,STLport hinted insert_unique for SparseMatchFinder WeaponTemplateSet MatchMap; visible noinline comparator lever (docs/shape_levers.md)
?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@_STL@@_N@2@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z,,0x00141150,167,game/GameEngine/Source/GameLogic/Object/STLWeaponTemplateSetBitFlagsHintedInsertUnique.cpp,matched,SparseMatchFinder Weapon map plain insert_unique beside the landed hinted insert; out-of-line MapHelper comparator
?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z,,0x001426A0,629,game/GameEngine/Source/GameLogic/Object/STLArmorTemplateSetBitFlagsHintedInsertUnique.cpp,matched,STLport hinted insert_unique for SparseMatchFinder ArmorTemplateSet MatchMap; retires the naked lift thunk row that borrowed this name; visible noinline comparator lever
?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@_STL@@_N@2@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z,,0x00140F90,167,game/GameEngine/Source/GameLogic/Object/STLArmorTemplateSetBitFlagsHintedInsertUnique.cpp,matched,SparseMatchFinder ArmorT map plain insert_unique beside the landed hinted insert; out-of-line MapHelper comparator
?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0LL@@@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0LL@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@2@@Z,,0x00010F1E,5,game/GameEngine/Source/GameLogic/Object/SparseMatchFinderBitFlagsTreeInsertUniqueThunk.cpp,matched,compiler-emitted symbol reconstructed from dump signature
```

### symbols.csv

```csv
??$_M_find@V?$BitFlags@$0BB@@@@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0BB@@@@Z,0x00042D1B,resweep callee back-solved
??$_M_find@V?$BitFlags@$0L@@@@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0L@@@@Z,0x0000AE20,pinharvest x1 (thunk)
??A?$map@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVWeaponTemplateSet@@ABV?$BitFlags@$0BB@@@@Z,0x00019155,resweep callee back-solved
??A?$map@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVArmorTemplateSet@@ABV?$BitFlags@$0L@@@@Z,0x00036C0A,pinharvest x1 (thunk)
??RMapHelper@?$SparseMatchFinder@UModelConditionInfo@@V?$BitFlags@$0HF@@@@@QBE_NABV?$BitFlags@$0HF@@@0@Z,0x0000A9A2,pinharvest x1 (thunk)
??RMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QBE_NABV?$BitFlags@$0L@@@0@Z,0x0000A9A2
??RMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QBE_NABV?$BitFlags@$0BB@@@0@Z,0x00010B1D,resweep callee back-solved
?_M_erase@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@AAEXPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@Z,0x00134D00,WeaponTemplateSet finder erase body
?_M_erase@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@AAEXPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@Z,0x000493BE,ThingTemplate armor finder erase via ILT thunk
?_M_insert@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@AAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@PAU_Rb_tree_node_base@2@0ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@0@Z,0x00022197,callee of the hinted insert_unique at 0x001429C0 (SparseMatchFinder MatchMap; ILT thunk retail calls)
?_M_insert@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@AAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@PAU_Rb_tree_node_base@2@0ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@0@Z,0x00049BA7,callee of the hinted insert_unique at 0x001426A0 (SparseMatchFinder MatchMap; ILT thunk retail calls)
?_M_lower_bound@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0BB@@@@Z,0x00005A60,resweep callee back-solved
?find@SparseBitFlagsTreeFindShim@_STL@@QBEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0LL@@@@Z,0x00141220,SparseMatchFinder tree _M_find incremental-link thunk target through a TU-local forwarding shim
?findBestInfoSlow@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@ABEPBVArmorTemplateSet@@ABV?$vector@VArmorTemplateSet@@V?$allocator@VArmorTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0L@@@@Z,0x00013ACA,pinharvest x1 (thunk)
?findBestInfoSlow@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@ABEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z,0x00013ACA,resweep callee back-solved
?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z,0x00010F1E,resweep callee back-solved
?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@_STL@@_N@2@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z,0x00015BE0,callee of the hinted insert_unique at 0x001429C0 (SparseMatchFinder MatchMap; ILT thunk retail calls)
?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z,0x0000F952
?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@_STL@@_N@2@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z,0x00043950,callee of the hinted insert_unique at 0x001426A0 (SparseMatchFinder MatchMap; ILT thunk retail calls)
```

## Each body: incoming call graph

Generated with `python3 tools/callers_of.py <rva>`; this tool resolves E8/E9 through known ILT chains. Caller names here are the current ledger spellings and can themselves be the swapped names. No reported incoming E8/E9 is not evidence of no indirect/address-taken use.

```text
0x00005a60  ?j_00005a60@@YAXXZ  (5 bytes)
  no named caller reaches it directly

```

```text
0x0000a9a2  ??RMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QBE_NABV?$BitFlags@$0L@@@0@Z  (5 bytes)
  no named caller reaches it directly

```

```text
0x0000ae20  ?j_0000ae20@@YAXXZ  (5 bytes)
  no named caller reaches it directly

```

```text
0x0000f952  ?j_0000F952@@YAXXZ  (5 bytes)
  no named caller reaches it directly

```

```text
0x00010b1d  ??RMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QBE_NABV?$BitFlags@$0BB@@@0@Z  (5 bytes)
  no named caller reaches it directly

```

```text
0x00010f1e  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0LL@@@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0LL@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@2@@Z  (5 bytes)
  no named caller reaches it directly

```

```text
0x00013aca  ?findBestInfoSlow@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@ABEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z  (5 bytes)
  no named caller reaches it directly

```

```text
0x00015be0  ?j_00015be0@@YAXXZ  (5 bytes)
  no named caller reaches it directly

```

```text
0x00019155  ?j_00019155@@YAXXZ  (5 bytes)
  no named caller reaches it directly

```

```text
0x00022197  ?j_00022197@@YAXXZ  (5 bytes)
  no named caller reaches it directly

```

```text
0x00036c0a  ?j_00036c0a@@YAXXZ  (5 bytes)
  no named caller reaches it directly

```

```text
0x00042d1b  ?_M_find@?$_Rb_tree@$$CBV?$BitFlags@$0LL@@@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0LL@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0LL@@@PBVWeaponTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0LL@@@@Z  (5 bytes)
  no named caller reaches it directly

```

```text
0x00043950  ?j_00043950@@YAXXZ  (5 bytes)
  no named caller reaches it directly

```

```text
0x000493be  ?j_000493be@@YAXXZ  (5 bytes)
  no named caller reaches it directly

```

```text
0x00049ba7  ?j_00049ba7@@YAXXZ  (5 bytes)
  no named caller reaches it directly

```

```text
0x00078d20  ?clear@?$map@VAsciiString@@V1@U?$less@VAsciiString@@@_STL@@V?$allocator@U?$pair@$$CBVAsciiString@@V1@@_STL@@@3@@_STL@@QAEXXZ  (51 bytes)
  no named caller reaches it directly

```

```text
0x00134d00  ?_M_erase@?$_Rb_tree@HU?$pair@$$CBHUGen_t_00134d00_p4pod@@@_STL@@U?$_Select1st@U?$pair@$$CBHUGen_t_00134d00_p4pod@@@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHUGen_t_00134d00_p4pod@@@_STL@@@2@@_STL@@AAEXPAU?$_Rb_tree_node@U?$pair@$$CBHUGen_t_00134d00_p4pod@@@_STL@@@2@@Z  (53 bytes)
  <- 0x001356c0  ?clear@?$_Rb_tree@HU?$pair@$$CBHUGen_t_001356c0_p12cd@@@_STL@@U?$_Select1st@U?$pair@$$CBHUGen_t_001356c0_p12cd@@@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHUGen_t_001356c0_p12cd@@@_STL@@@2@@_STL@@QAEXXZ
  <- 0x00137010  ??4?$_Rb_tree@HU?$pair@$$CBHUGen_t_00137010_p12cd@@@_STL@@U?$_Select1st@U?$pair@$$CBHUGen_t_00137010_p12cd@@@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHUGen_t_00137010_p12cd@@@_STL@@@2@@_STL@@QAEAAV01@ABV01@@Z
  <- 0x00140250  ??1?$_Rb_tree@HU?$pair@$$CBHUGen_t_00140250_p4pod@@@_STL@@U?$_Select1st@U?$pair@$$CBHUGen_t_00140250_p4pod@@@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHUGen_t_00140250_p4pod@@@_STL@@@2@@_STL@@QAE@XZ
  <- 0x001404b0  ?clear@?$_Rb_tree@HU?$pair@$$CBHUGen_t_001404b0_p12cd@@@_STL@@U?$_Select1st@U?$pair@$$CBHUGen_t_001404b0_p12cd@@@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHUGen_t_001404b0_p12cd@@@_STL@@@2@@_STL@@QAEXXZ
  <- 0x00141b40  ?clear@?$_Rb_tree@HU?$pair@$$CBHUGen_t_00141b40_p12cd@@@_STL@@U?$_Select1st@U?$pair@$$CBHUGen_t_00141b40_p12cd@@@_STL@@@2@U?$less@H@2@V?$allocator@U?$pair@$$CBHUGen_t_00141b40_p12cd@@@_STL@@@2@@_STL@@QAEXXZ
  <- 0x00146130  ?parseWeaponTemplateSet@ThingTemplate@@KAXPAVINI@@PAX1PBX@Z

```

```text
0x0013f3e0  ?countConditionIntersection@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@CAHABV?$BitFlags@$0BB@@@0@Z  (54 bytes)
  no named caller reaches it directly

```

```text
0x0013f460  ?countConditionIntersection@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@CAHABV?$BitFlags@$0L@@@0@Z  (54 bytes)
  no named caller reaches it directly

```

```text
0x00140740  ?call@ArmorMapHelperShim@@QBE_NABV?$BitFlags@$0L@@@0@Z  (75 bytes)
  <- 0x00140a60  ?_M_lower_bound@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0L@@@@Z
  <- 0x00140ea0  ?_M_insert@?$_Rb_tree@HU?$pair@$$CBHURva001363B0Value@@@_STL@@U?$_Select1st@U?$pair@$$CBHURva001363B0Value@@@_STL@@@2@URva00140EA0Compare@@V?$allocator@U?$pair@$$CBHURva001363B0Value@@@_STL@@@2@@_STL@@AAE?AU?$_Rb_tree_iterator@U?$pair@$$CBHURva001363B0Value@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBHURva001363B0Value@@@_STL@@@2@@2@PAU_Rb_tree_node_base@2@0ABU?$pair@$$CBHURva001363B0Value@@@2@0@Z
  <- 0x00140f90  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@_STL@@_N@2@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z
  <- 0x00141220  ??$_M_find@V?$BitFlags@$0L@@@@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0L@@@@Z
  <- 0x001426a0  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z
  <- 0x00145100  ??A?$map@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVArmorTemplateSet@@ABV?$BitFlags@$0L@@@@Z

```

```text
0x001407a0  ?call@WeaponMapHelperShim@@QBE_NABV?$BitFlags@$0BB@@@0@Z  (75 bytes)
  <- 0x00140ab0  ?_M_lower_bound@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0BB@@@@Z
  <- 0x00141060  ?_M_insert@?$_Rb_tree@HU?$pair@$$CBHURva00136490Value@@@_STL@@U?$_Select1st@U?$pair@$$CBHURva00136490Value@@@_STL@@@2@URva00141060Compare@@V?$allocator@U?$pair@$$CBHURva00136490Value@@@_STL@@@2@@_STL@@AAE?AU?$_Rb_tree_iterator@U?$pair@$$CBHURva00136490Value@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBHURva00136490Value@@@_STL@@@2@@2@PAU_Rb_tree_node_base@2@0ABU?$pair@$$CBHURva00136490Value@@@2@0@Z
  <- 0x00141150  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@_STL@@_N@2@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z
  <- 0x001412a0  ??$_M_find@V?$BitFlags@$0BB@@@@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0BB@@@@Z
  <- 0x001429c0  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z
  <- 0x001451e0  ??A?$map@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVWeaponTemplateSet@@ABV?$BitFlags@$0BB@@@@Z

```

```text
0x00140a60  ?_M_lower_bound@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0L@@@@Z  (59 bytes)
  <- 0x001421d0  Gen_setmd_001421d0
  <- 0x00144480  Gen_setmd_00144480
  <- 0x00145100  ??A?$map@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVArmorTemplateSet@@ABV?$BitFlags@$0L@@@@Z

```

```text
0x00140ab0  ?_M_lower_bound@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0BB@@@@Z  (59 bytes)
  <- 0x00142230  Gen_setmd_00142230
  <- 0x001444d0  Gen_setmd_001444d0
  <- 0x001451e0  ??A?$map@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVWeaponTemplateSet@@ABV?$BitFlags@$0BB@@@@Z

```

```text
0x00140f90  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@_STL@@_N@2@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z  (167 bytes)
  <- 0x001426a0  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z

```

```text
0x00141150  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@_STL@@_N@2@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z  (167 bytes)
  <- 0x001429c0  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z

```

```text
0x00141220  ??$_M_find@V?$BitFlags@$0L@@@@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0L@@@@Z  (96 bytes)
  <- 0x00142ce0  Gen_setmd_00142ce0
  <- 0x00144150  Gen_setmd_00144150
  <- 0x00146310  ?findBestInfo@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QBEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z
  <- 0x001467e0  ?findWeaponTemplateSet@ThingTemplate@@QBEPBVWeaponTemplateSet@@ABV?$BitFlags@$0BB@@@@Z

```

```text
0x001412a0  ??$_M_find@V?$BitFlags@$0BB@@@@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0BB@@@@Z  (96 bytes)
  <- 0x00142d00  Gen_setmd_00142d00
  <- 0x001443f0  Gen_setmd_001443f0
  <- 0x00146360  ?dup_00146360@@YAXXZ
  <- 0x00146780  ?findArmorTemplateSet@ThingTemplate@@QBEPBVArmorTemplateSet@@ABV?$BitFlags@$0L@@@@Z

```

```text
0x00142160  ?countConditionInverseIntersection@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@CAHABV?$BitFlags@$0L@@@0@Z  (15 bytes)
  no named caller reaches it directly

```

```text
0x001426a0  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z  (629 bytes)
  <- 0x00144450  ?insert@?$map@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@_STL@@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z
  <- 0x00145100  ??A?$map@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVArmorTemplateSet@@ABV?$BitFlags@$0L@@@@Z

```

```text
0x001429c0  ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BB@@@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z  (629 bytes)
  <- 0x001444a0  ?insert@?$map@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@_STL@@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z
  <- 0x001451e0  ??A?$map@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVWeaponTemplateSet@@ABV?$BitFlags@$0BB@@@@Z

```

```text
0x00144000  ?findBestInfoSlow@WeaponFindBestInfoSlowShim@@QBEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z  (195 bytes)
  <- 0x00146310  ?findBestInfo@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QBEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z
  <- 0x001467e0  ?findWeaponTemplateSet@ThingTemplate@@QBEPBVWeaponTemplateSet@@ABV?$BitFlags@$0BB@@@@Z

```

```text
0x00144300  ?findBestInfoSlow@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@ABEPBVArmorTemplateSet@@ABV?$vector@VArmorTemplateSet@@V?$allocator@VArmorTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0L@@@@Z  (192 bytes)
  <- 0x00146360  ?dup_00146360@@YAXXZ
  <- 0x00146780  ?findArmorTemplateSet@ThingTemplate@@QBEPBVArmorTemplateSet@@ABV?$BitFlags@$0L@@@@Z

```

```text
0x00144450  ?insert@?$map@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@_STL@@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z  (31 bytes)
  no named caller reaches it directly

```

```text
0x001444a0  ?insert@?$map@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@_STL@@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@2@@Z  (31 bytes)
  no named caller reaches it directly

```

```text
0x00145100  ??A?$map@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVArmorTemplateSet@@ABV?$BitFlags@$0L@@@@Z  (106 bytes)
  <- 0x00146310  ?findBestInfo@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QBEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z
  <- 0x001467e0  ?findWeaponTemplateSet@ThingTemplate@@QBEPBVWeaponTemplateSet@@ABV?$BitFlags@$0BB@@@@Z

```

```text
0x001451e0  ??A?$map@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BB@@@PBVWeaponTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVWeaponTemplateSet@@ABV?$BitFlags@$0BB@@@@Z  (106 bytes)
  <- 0x00146360  ?dup_00146360@@YAXXZ
  <- 0x00146780  ?findArmorTemplateSet@ThingTemplate@@QBEPBVArmorTemplateSet@@ABV?$BitFlags@$0L@@@@Z

```

```text
0x00146310  ?findBestInfo@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QBEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z  (63 bytes)
  no named caller reaches it directly

```

```text
0x00146360  ?dup_00146360@@YAXXZ  (63 bytes)
  no named caller reaches it directly

```


## Correction map and limits

This is a per-address map, not a global text swap. `Weapon/29` means
`SparseMatchFinder<WeaponTemplateSet, BitFlags<29>>`; `Armor/11` means
`SparseMatchFinder<ArmorTemplateSet, BitFlags<11>>`. The full old names are
preserved in the inventory above. The retail bodies/extents are unchanged.

| RVA / current family claim | Retail identity / required action |
| --- | --- |
| 0x00140740 ArmorMapHelperShim / 75 | Weapon/29 MapHelper; 29-bit loop |
| 0x001407A0 WeaponMapHelperShim / 75 | Armor/11 MapHelper; 11-bit loop |
| 0x0000A9A2 Armor/11 MapHelper / 5 | Weapon comparator ILT, route=0x00140740; ModelConditionInfo/117 pin here is also false identity evidence |
| 0x00010B1D Weapon/17 MapHelper / 5 | Armor comparator ILT, route=0x001407A0 |
| 0x00140A60 Armor lower_bound / 59 | Weapon/29; comparator route A9A2 -> 140740 |
| 0x00140AB0 Weapon lower_bound / 59 | Armor/11; comparator route 10B1D -> 1407A0 |
| 0x00140F90 Armor plain insert_unique / 167 | Weapon/29; comparator A9A2 -> 140740 |
| 0x00141150 Weapon plain insert_unique / 167 | Armor/11; comparator 10B1D -> 1407A0 |
| 0x00141220 Armor tree find / 96 | Weapon/29; matched findWeaponTemplateSet caller, comparator A9A2 |
| 0x001412A0 Weapon tree find / 96 | Armor/11; matched findArmorTemplateSet caller, comparator 10B1D |
| 0x001426A0 Armor hinted insert_unique / 629 | Weapon/29; comparator A9A2; node insert via 49BA7 -> 140EA0 |
| 0x001429C0 Weapon hinted insert_unique / 629 | Armor/11; comparator 10B1D; node insert via 22197 -> 141060 |
| 0x00144450 Armor map insert / 31 | Weapon/29; forwards to hinted insert via F952 -> 1426A0 |
| 0x001444A0 Weapon map insert / 31 | Armor/11; forwards to hinted insert via 10F1E -> 1429C0 |
| 0x00145100 Armor map subscript / 106 | Weapon/29; matched findWeaponTemplateSet caller |
| 0x001451E0 Weapon map subscript / 106 | Armor/11; matched findArmorTemplateSet caller |
| 0x00146310 Armor AND Weapon findBestInfo / 63 | Weapon/29 only; retire wrong Armor overclaim; route 42D1B,13ACA,19155 |
| 0x00146360 dup, object-symbol Armor findBestInfo / 63 | Armor/11; route AE20,2AFA4,36C0A; the actual Armor body |
| 0x00144000 Weapon slow-search shim / 195 | Weapon/29; correct owner, fix argument; mask 0x1FFFFFFF at +0x6B, element stride 0xEC |
| 0x00144300 Armor slow search / 192 | Armor/11; correct owner, mask 0x7FF at +0x4B, element stride 12 |
| 0x00013ACA BOTH Armor and Weapon slow-search pins / 5 | Weapon/29 ILT only, route=0x00144000; Armor pin is false; real armor route is 2AFA4 -> 144300 |
| 0x00042D1B TWO Weapon tree-find rows / 5 | Weapon/29 ILT route=0x00141220; 17 and 187 argument claims need retirement/consolidation |
| 0x0000AE20 Armor tree-find pin / 5 | Armor/11, correct owner, route=0x001412A0 |
| 0x00019155 Weapon subscript pin / 5 | Weapon/29, correct owner, route=0x00145100 |
| 0x00036C0A Armor subscript pin / 5 | Armor/11, correct owner, route=0x001451E0 |
| 0x00049BA7 Armor node insert pin / 5 | Weapon/29 view, route=0x00140EA0; reached body already has an address-derived tree identity, so do not add a second real body name |
| 0x00022197 Weapon node insert pin / 5 | Armor/11 view, route=0x00141060; same one-identity constraint |
| 0x00043950 Armor plain insert pin / 5 | Weapon/29, route=0x00140F90 |
| 0x00015BE0 Weapon plain insert pin / 5 | Armor/11, route=0x00141150 |
| 0x0000F952 Armor hinted insert pin / 5 | Weapon/29, route=0x001426A0 |
| 0x00010F1E TWO Weapon hinted-insert rows / 5 | Armor/11 ILT route=0x001429C0; consolidate 17/187 claims |
| 0x00005A60 Weapon lower_bound pin / 5 | Armor/11, route=0x00140AB0 |
| 0x00134D00 Weapon erase pin / 53 | Current graph includes parseWeaponTemplateSet 146130; retain weapon owner, change argument only if independently verified; body already carries generated tree identity, so typed pin must be ABI view rather than a new real owner |
| 0x000493BE Armor erase pin / 5 | route=0x00134D50; no new Armor/Weapon swap inferred solely from adjacent specialization; existing generated target has a real row |
| 0x0013F3E0 Weapon intersection / 54; 0x0013F460 Armor intersection / 54 | Byte twins with no named incoming E8/E9 in this graph; counts do not distinguish them. Do not swap by adjacency. Weapon argument still needs 17 -> 29 after independent attribution |
| 0x00142160 Armor inverse intersection / 15 | Calls 46C3B -> BitFlags<11>::countInverseIntersection at 140900; keep Armor/11 |
| 0x00078D20 three SparseMatchFinder clear rows / 51 | Overclaims sharing the AsciiString map clear body from UserPreferences.cpp; do not generate replacement Armor/Weapon real names here |
| 0x00141220 SparseBitFlagsTreeFindShim pin | Compilation shim points at the physical weapon find; retire or admit only as verified ABI view of the single canonical row |

The 5-byte thunk rows and their reached bodies are distinct extents; moving a
canonical name from the thunk onto the body must not leave two REAL identities
for one retail body. Existing opaque/generated tree owners need ABI views where
appropriate. `add_match.py --replace-rva` presently requires exactly one row at
the old address, so the duplicated 42D1B,10F1E,146310 and 78D20 claims also need
an explicit retirement sequence, not a blind bulk replacement.

## Blocking identity-oracle conflict (stop before implementation)

Both the loop/name-table/caller evidence and template counts above are strong,
but the straightforward canonical decorations do **not** pass the required
ILT oracle. These exact read-only commands returned:

```text
python3 tools/ilt_oracle.py check '??RMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BN@@@@@QBE_NABV?$BitFlags@$0BN@@@0@Z' 0x00140740
CONTRADICTED  p_false=4.57e-04  (outside every window of the target's slots 7865:7057-7063)
python3 tools/ilt_oracle.py check '??RMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QBE_NABV?$BitFlags@$0L@@@0@Z' 0x001407A0
CONTRADICTED  p_false=3.26e-04  (outside every window of the target's slots 12856:9722-9726)
```

Checking the same names at their respective ILT entries 0x0000A9A2 and
0x00010B1D produces the same conflict. The *old* Armor/11 name at A9A2 and
Weapon/17 at 10B1D are also CONTRADICTED in those same windows. The corrected
candidate names for the map/find/insert/slow-search pins were likewise tested;
the complete results follow. This does not prove the frozen windows are wrong:
canonical decoration/class spelling remains an alternative explanation. No
ILT windows or baseline exemptions have been changed.

The project lead must settle the canonical decoration versus the neighboring
frozen ILT anchors before implementation can satisfy the required check. The
current `tools/ilt_guard.py` exempts verified ABI-view pins but still checks the
canonical functions.csv identity; an ABI view alone cannot make a contradicted
canonical row admissible. Do not create an override or extend a baseline to
force this project green.

`tools/callees.py` was run for both 75-byte comparator extents: neither has a
direct call. Initial `tools/check_csv.py` and `tools/pin_consistency.py --check`
passed (83 multi-pinned symbols; 0 new/stale; 329 retail-derived routes; CRT and
DIR32 checks passed). No implementation, shared header, pin or function ledger
changes have been made at this stop.

### Additional corrected-pin candidate oracle results

```text
0x42d1b ??$_M_find@V?$BitFlags@$0BN@@@@?$_Rb_tree@$$CBV?$BitFlags@$0BN@@@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BN@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0BN@@@@Z
CONTRADICTED  p_false=1.17e-03  (outside every window of the target's slots 53918:31704-31721)
0xae20 ??$_M_find@V?$BitFlags@$0L@@@@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@1@ABV?$BitFlags@$0L@@@@Z
CONTRADICTED  p_false=9.13e-04  (outside every window of the target's slots 8095:7180-7193)
0x19155 ??A?$map@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BN@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVWeaponTemplateSet@@ABV?$BitFlags@$0BN@@@@Z
CONTRADICTED  p_false=3.26e-04  (outside every window of the target's slots 19728:13460-13464)
0x36c0a ??A?$map@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@_STL@@@_STL@@QAEAAPBVArmorTemplateSet@@ABV?$BitFlags@$0L@@@@Z
CONTRADICTED  p_false=1.96e-04  (outside every window of the target's slots 44033:26410-26412)
0xa9a2 ??RMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BN@@@@@QBE_NABV?$BitFlags@$0BN@@@0@Z
CONTRADICTED  p_false=4.57e-04  (outside every window of the target's slots 7865:7057-7063)
0x10b1d ??RMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QBE_NABV?$BitFlags@$0L@@@0@Z
CONTRADICTED  p_false=3.26e-04  (outside every window of the target's slots 12856:9722-9726)
0x22197 ?_M_insert@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@AAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@PAU_Rb_tree_node_base@2@0ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@0@Z
CONTRADICTED  p_false=1.30e-04  (outside every window of the target's slots 27114:17336-17337)
0x49ba7 ?_M_insert@?$_Rb_tree@$$CBV?$BitFlags@$0BN@@@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BN@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@AAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@PAU_Rb_tree_node_base@2@0ABU?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@2@0@Z
CONTRADICTED  p_false=3.91e-04  (outside every window of the target's slots 59578:36793-36798)
0x5a60 ?_M_lower_bound@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@ABEPAU?$_Rb_tree_node@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@ABV?$BitFlags@$0L@@@@Z
CONTRADICTED  p_false=5.22e-04  (outside every window of the target's slots 3807:4074-4081)
0x13aca ?findBestInfoSlow@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BN@@@@@ABEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BN@@@@Z
CONTRADICTED  p_false=7.83e-04  (outside every window of the target's slots 15297:11057-11068)
0x13aca ?findBestInfoSlow@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BN@@@@@ABEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BN@@@@Z
CONTRADICTED  p_false=7.83e-04  (outside every window of the target's slots 15297:11057-11068)
0x10f1e ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z
CONTRADICTED  p_false=2.61e-04  (outside every window of the target's slots 13061:9835-9838)
0x15be0 ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0L@@@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@_STL@@@2@@_STL@@_N@2@ABU?$pair@$$CBV?$BitFlags@$0L@@@PBVArmorTemplateSet@@@2@@Z
CONTRADICTED  p_false=2.61e-04  (outside every window of the target's slots 16991:11972-11975)
0xf952 ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BN@@@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BN@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@2@@2@U32@ABU?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@2@@Z
CONTRADICTED  p_false=5.87e-04  (outside every window of the target's slots 11945:9215-9223)
0x43950 ?insert_unique@?$_Rb_tree@$$CBV?$BitFlags@$0BN@@@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@U?$_Select1st@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@3@UMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BN@@@@@V?$allocator@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@3@@_STL@@QAE?AU?$pair@U?$_Rb_tree_iterator@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@_STL@@@2@@_STL@@_N@2@ABU?$pair@$$CBV?$BitFlags@$0BN@@@PBVWeaponTemplateSet@@@2@@Z
CONTRADICTED  p_false=3.26e-04  (outside every window of the target's slots 54543:32067-32071)
```

## Initial LINKED check

`python3 tools/link_check.py` was run once over all ten family TUs, before any
implementation edits. Exit 1 reports existing blockers (not a tool crash).
All source/header/ledger inputs remain unchanged at the stop, so no post-edit
run or implementation delta is claimed. Observed total: 5 LINKED bytes; gains
0, losses 0. Full diagnostic output remains in `build/sparsematch/link_before.txt`.

```text
game/GameEngine/Source/Common/Thing/ThingTemplate.cpp: does not link  LINKED 0 -> 0 bytes (census 2026-10-15 11:39 at 04f6b0ea9e; file's own bytes 5,612)
game/GameEngine/Source/Common/UserPreferences.cpp: does not link  LINKED 0 -> 0 bytes (census 2026-10-15 11:39 at 04f6b0ea9e; file's own bytes 7,251)
game/GameEngine/Source/GameLogic/Object/STLArmorTemplateSetBitFlagsHintedInsertUnique.cpp: does not link  LINKED 0 -> 0 bytes (census 2026-10-15 11:39 at 04f6b0ea9e; file's own bytes 892)
game/GameEngine/Source/GameLogic/Object/STLWeaponTemplateSetBitFlagsFindThunk.cpp: does not link  LINKED 0 -> 0 bytes (census 2026-10-15 11:39 at 04f6b0ea9e; file's own bytes 5)
game/GameEngine/Source/GameLogic/Object/STLWeaponTemplateSetBitFlagsHintedInsertUnique.cpp: does not link  LINKED 0 -> 0 bytes (census 2026-10-15 11:39 at 04f6b0ea9e; file's own bytes 892)
game/GameEngine/Source/GameLogic/Object/STLWeaponTemplateSetBitFlagsInsertUniqueThunk.cpp: LINKS  LINKED 0 -> 0 bytes (census 2026-10-15 11:39 at 04f6b0ea9e; file's own bytes 0)
game/GameEngine/Source/GameLogic/Object/SparseMatchFinderBitFlagsTreeFindThunk.cpp: LINKS  LINKED 5 -> 5 bytes (census 2026-10-15 11:39 at 04f6b0ea9e; file's own bytes 5)
game/GameEngine/Source/GameLogic/Object/SparseMatchFinderBitFlagsTreeInsertUniqueThunk.cpp: LINKS  LINKED 0 -> 0 bytes (census 2026-10-15 11:39 at 04f6b0ea9e; file's own bytes 0)
game/GameEngine/Source/GameLogic/Object/SparseMatchFinderFindBestInfoSlowThunk.cpp: does not link  LINKED 0 -> 0 bytes (census 2026-10-15 11:39 at 04f6b0ea9e; file's own bytes 200)
game/GameEngine/Source/GameLogic/Object/SparseMatchFinderMapHelperThunks.cpp: does not link  LINKED 0 -> 0 bytes (census 2026-10-15 11:39 at 04f6b0ea9e; file's own bytes 160)
link_check: 3 of 10 link cleanly; LINKED 5 -> 5 bytes (170.4s)
```

## Source-derived spelling follow-up, sol-1, 2026-10-16

This follow-up is approved by the project lead 2026-10-16. The existing
research commit `9a2f1e31ce` rebased to `a8ba23b6f0` on fresh master
`24db0885ad`. `check_csv.py` passed before further research. This section
supersedes the earlier suggestion that the lead must choose among unconstrained
spelling variants: the source justifies only the two candidates below. No
free-text spelling search, access/const permutation, hash-guided name fitting,
window regeneration, pin change, or implementation edit is authorized here.

### Derivation and exclusions (written before oracle testing)

All paths below start at
`inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/`:

- `Common/SparseMatchFinder.h:46-47` declares the global
  `template<class MATCHABLE, class BITSET> class SparseMatchFinder`.
  Lines 75-93 declare its nested **struct** `MapHelper`, whose public member is
  exactly `bool operator()(const BITSET& a, const BITSET& b) const`.
  The outer `private:` restricts visibility of the type; it does not make
  the struct's operator a private member. Its member decoration is therefore
  public, const, thiscall, bool, two const references (`QBE_N...0@Z`).
- `GameLogic/WeaponSet.h:124,170` declares global **class**
  `WeaponTemplateSet` and explicitly spells the finder as
  `SparseMatchFinder<WeaponTemplateSet, WeaponSetFlags>`.
  `GameLogic/WeaponSetFlags.h:35` makes `WeaponSetFlags` an ordinary typedef
  of `BitFlags<WEAPONSET_COUNT>`. There is no distinct `WeaponSetFlags` class
  to substitute into a decorated name.
- `GameLogic/ArmorSet.h:62,65,101` likewise spells
  `typedef BitFlags<ARMORSET_COUNT> ArmorSetFlags`, global **class**
  `ArmorTemplateSet`, and
  `SparseMatchFinder<ArmorTemplateSet, ArmorSetFlags>`.
- `Common/BitFlags.h:51-55` declares the global
  `template<size_t NUMBITS> class BitFlags` with a `std::bitset<NUMBITS>`
  member. Retail name arrays and comparator loop limits above prove the only
  BFME adjustments used here: Weapon=29, Armor=11. On this x86 ABI each has
  one 32-bit storage word; storage size is not the template argument.
- Generals' `Common/SparseMatchFinder.h` has `HashMapHelper` and an active
  `hash_map`, but **no MapHelper**. Zero Hour adds `MapHelper` and uses
  `std::map<const BITSET, const MATCHABLE*, MapHelper>`. Retail's ordered
  lexicographic loop agrees with Zero Hour's comparator; Generals supplies
  no alternative name for that same comparator.
- No inspected source puts these types into a namespace, reverses the
  template arguments, makes template-set types structs, turns flag typedefs
  into classes, removes const/reference qualifiers, or changes calling
  convention. None of those variants is a principled candidate.

Before any new oracle call, MSVC 7.1 compiled a scratch probe under
`build/sparsematch/source_spelling.cpp`. It copies the whole Zero Hour
`struct MapHelper` verbatim, retains the upstream class/template categories
and the real flag typedef spellings, supplies 29/11 from retail, and explicitly
instantiates the two source-spelled finders. Other matcher members are omitted;
`BitFlags::size/test` are declarations only because this probe checks symbol
spelling, not codegen. The resulting COFF externals are **exactly** W29 and
A11 below, including template backreferences. Thus the ordinary typedefs do
not create additional candidate spellings. Compilation passed; the first
COFF-reading helper invocation mistakenly treated symbol dictionaries as
strings, was corrected without recompilation, and made no oracle calls.

### Frozen candidate list

One independently derived candidate per comparator; two distinct candidate
spellings total. Both coincide with candidates already contradicted in the
initial report; compiler reproduction is new spelling evidence, not a new
name variant. Only these two are tested as possible replacements:

- **W29**, `0x00140740`: WeaponTemplateSetFinder from WeaponSet.h, WeaponSetFlags expanded to retail BitFlags<29>.
  `??RMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BN@@@@@QBE_NABV?$BitFlags@$0BN@@@0@Z`
- **A11**, `0x001407A0`: ArmorTemplateSetFinder from ArmorSet.h, ArmorSetFlags expanded to retail BitFlags<11>.
  `??RMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QBE_NABV?$BitFlags@$0L@@@0@Z`

### Frozen existing-sibling controls

The following 14 distinct `(existing spelling, RVA)` pairs were
selected **before testing** by narrow `rg SparseMatchFinder` ledger filters.
They exhaust the existing direct SparseMatchFinder members and MapHelper
operators in functions.csv/symbols.csv; identical pairs across ledgers are
counted once. STL map/tree methods, shim classes, object-symbol note aliases,
and transformed hypothetical names are excluded. These controls can establish
an already-confirmed sibling convention; they are not replacement candidates
and no control result will trigger generation of another spelling. Every
control spelling and its result will be recorded here, including failures.

- **S01**, `0x0000A9A2`, functions.csv:
  `??RMapHelper@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QBE_NABV?$BitFlags@$0L@@@0@Z`
- **S02**, `0x00010B1D`, functions.csv:
  `??RMapHelper@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QBE_NABV?$BitFlags@$0BB@@@0@Z`
- **S03**, `0x00078D20`, functions.csv:
  `?clear@?$SparseMatchFinder@UModelConditionInfo@@V?$BitFlags@$0HF@@@@@QAEXXZ`
- **S04**, `0x00078D20`, functions.csv:
  `?clear@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QAEXXZ`
- **S05**, `0x00078D20`, functions.csv:
  `?clear@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QAEXXZ`
- **S06**, `0x0013F460`, functions.csv:
  `?countConditionIntersection@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@CAHABV?$BitFlags@$0L@@@0@Z`
- **S07**, `0x0013F3E0`, functions.csv:
  `?countConditionIntersection@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@CAHABV?$BitFlags@$0BB@@@0@Z`
- **S08**, `0x00142160`, functions.csv:
  `?countConditionInverseIntersection@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@CAHABV?$BitFlags@$0L@@@0@Z`
- **S09**, `0x00146310`, functions.csv:
  `?findBestInfo@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@QBEPBVArmorTemplateSet@@ABV?$vector@VArmorTemplateSet@@V?$allocator@VArmorTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0L@@@@Z`
- **S10**, `0x00146310`, functions.csv:
  `?findBestInfo@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@QBEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z`
- **S11**, `0x00144300`, functions.csv:
  `?findBestInfoSlow@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@ABEPBVArmorTemplateSet@@ABV?$vector@VArmorTemplateSet@@V?$allocator@VArmorTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0L@@@@Z`
- **S12**, `0x00013ACA`, functions.csv:
  `?findBestInfoSlow@?$SparseMatchFinder@VWeaponTemplateSet@@V?$BitFlags@$0BB@@@@@ABEPBVWeaponTemplateSet@@ABV?$vector@VWeaponTemplateSet@@V?$allocator@VWeaponTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0BB@@@@Z`
- **S13**, `0x0000A9A2`, symbols.csv:
  `??RMapHelper@?$SparseMatchFinder@UModelConditionInfo@@V?$BitFlags@$0HF@@@@@QBE_NABV?$BitFlags@$0HF@@@0@Z`
- **S14**, `0x00013ACA`, symbols.csv:
  `?findBestInfoSlow@?$SparseMatchFinder@VArmorTemplateSet@@V?$BitFlags@$0L@@@@@ABEPBVArmorTemplateSet@@ABV?$vector@VArmorTemplateSet@@V?$allocator@VArmorTemplateSet@@@_STL@@@_STL@@ABV?$BitFlags@$0L@@@@Z`

This freezes the session budget at two candidate checks plus 14 fixed sibling-control checks. No oracle calls have yet been made in this follow-up.

### Results of the frozen test plan

The checks below use `ilt_oracle.Oracle.check(name, rva)`, the same exact-name
check as `python3 tools/ilt_oracle.py check NAME RVA`. No repair command or
name enumeration was used. The frozen windows and oracle code are unchanged.
Each test ID maps to its full exact spelling above; different RVAs using the
same spelling remain separate visible checks. Bucket endpoints are the oracle's
B_LO/B_HI results, not new candidate-generation inputs.

| Test | RVA | Result | p_false | Bucket endpoints | Explanation |
| --- | --- | --- | --- | --- | --- |
| W29 | 0x00140740 | CONTRADICTED | 4.57e-04 | 28627/28627 | outside every window of the target's slots 7865:7057-7063 |
| A11 | 0x001407A0 | CONTRADICTED | 3.26e-04 | 23801/23801 | outside every window of the target's slots 12856:9722-9726 |
| S01 | 0x0000A9A2 | CONTRADICTED | 4.57e-04 | 23801/23801 | outside every window of the target's slots 7865:7057-7063 |
| S02 | 0x00010B1D | CONTRADICTED | 3.26e-04 | 19766/19766 | outside every window of the target's slots 12856:9722-9726 |
| S03 | 0x00078D20 | CONTRADICTED | 4.57e-04 | 15650/15650 | outside every window of the target's slots 20024:13613-13619 |
| S04 | 0x00078D20 | CONTRADICTED | 4.57e-04 | 24320/24320 | outside every window of the target's slots 20024:13613-13619 |
| S05 | 0x00078D20 | CONTRADICTED | 4.57e-04 | 12235/12235 | outside every window of the target's slots 20024:13613-13619 |
| S06 | 0x0013F460 | CONTRADICTED | 5.87e-04 | 14780/14780 | outside every window of the target's slots 7018:6585-6593 |
| S07 | 0x0013F3E0 | CONTRADICTED | 9.13e-04 | 13484/13484 | outside every window of the target's slots 26614:17043-17056 |
| S08 | 0x00142160 | CONTRADICTED | 1.04e-03 | 31694/31694 | outside every window of the target's slots 21347:14292-14307 |
| S09 | 0x00146310 | CONTRADICTED | 6.52e-04 | 20766/20766 | outside every window of the target's slots 31886:19879-19888 |
| S10 | 0x00146310 | CONTRADICTED | 6.52e-04 | 25663/25663 | outside every window of the target's slots 31886:19879-19888 |
| S11 | 0x00144300 | CONTRADICTED | 3.91e-04 | 12701/12701 | outside every window of the target's slots 34387:21220-21225 |
| S12 | 0x00013ACA | CONTRADICTED | 7.83e-04 | 24663/24663 | outside every window of the target's slots 15297:11057-11068 |
| S13 | 0x0000A9A2 | CONTRADICTED | 4.57e-04 | 10846/10846 | outside every window of the target's slots 7865:7057-7063 |
| S14 | 0x00013ACA | CONTRADICTED | 7.83e-04 | 12701/12701 | outside every window of the target's slots 15297:11057-11068 |

candidates: CONFIRMED 0, CONTRADICTED 2, UNTESTABLE 0.

controls: CONFIRMED 0, CONTRADICTED 14, UNTESTABLE 0.

**Stop decision:** Neither source-derived comparator candidate confirms. No
additional spelling can be derived from the inspected source. The requested
condition of exactly one confirming principled candidate for each slot is not
met; implementation must not proceed. This session changes only this evidence
file. This result does not identify a faulty window or prove a different
BFME spelling; it leaves that conflict unresolved for the project lead.

No confirmed direct sibling was found among all 14 fixed controls. Their
inherited decorations are claims only; none provides a positive spelling
convention on which to base an extra comparator candidate. The compiler probe
independently verifies the source spelling but does not resolve retail's ILT
conflict.

### Verification and scope

Only this evidence document differs from the rebased starting commit. No game
source, header, function row, pin, tombstone, baseline or oracle window is
changed. Function rows changed: **0**; matched-byte delta: **0**; LINKED delta:
**+0 / -0** by unchanged source/header/ledger inputs. The earlier measured
family total was **5 -> 5 LINKED bytes** across ten TUs; it has not been
remeasured in this evidence-only follow-up, and no fresh link success is
claimed. No body was started, so no body claim or reconstruction is left open.

Research reproducibility hashes at test time:

- `tools/ilt_oracle.py`: SHA-256 `8dcb5d04407dd7535868ec8b59fb18c4f9cc941141c518af1bd671496ef619a3`
- `targets/game/reverse/ilt_windows.tsv`: SHA-256 `bdc6bde88b0e1c140350a7fc825f73cdf33f163f925b110ac340c2ee48fe3765`
- `build/sparsematch/source_spelling.cpp`: SHA-256 `07d9665610f58a99642c4005ba2b44e645f537e7a958195c1854a3159d7635eb`
- `build/sparsematch/principled_test_plan.json`: SHA-256 `bdcae57f02f0428609b82fd2fdf3a3db37cddf460046729af0ea489769bb8fe2`
