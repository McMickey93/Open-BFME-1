# pin --candidates batch 4: names the thunk table puts on the pinned body (op-1, 2026-10-16)

Approved by the project lead 2026-10-16. Same method as pin-candidates-op1-batch3-oracle.md: each
name has a functions.csv row at one body and a symbols.csv pin at an incremental-link thunk that
jumps to another. tools/ilt_oracle.py CONFIRMS the name at the pinned thunk and CONTRADICTS it at
the thunk of the body the row claimed. Retail had no identical-COMDAT folding.
The claimed body keeps its bytes as a `?dup_<rva>` alias (object-symbol= the same COMDAT, identity
unknown). The name moves to the pinned body only where the TU's compiled COMDAT byte-matches
there; otherwise it stays pin-only.

| name | claimed body (thunk: verdict) | pinned thunk -> body (verdict) |
|---|---|---|
| `??$_Construct@VAsciiString@@V1@@_STL@@YAXPAVAsciiString@@ABV1@@Z` | 0x756d90 (0x4725d: CONTRADICTED) | 0x7554 -> 0x620b0 (CONFIRMED) |
| `??$uninitialized_fill_n@PAUICoord2D@@IU1@@_STL@@YAPAUICoord2D@@PAU1@IABU1@@Z` | 0x33a580 (0x2ecf3: CONTRADICTED) | 0x278b3 -> 0x4501e0 (CONFIRMED) |
| `??0?$list@VPeerResponse@@V?$allocator@VPeerResponse@@@_STL@@@_STL@@QAE@ABV?$allocator@VPeerResponse@@@1@@Z` | 0x1a93a0 (0x1f5d2: CONTRADICTED) | 0x39022 -> 0x4fd8a0 (CONFIRMED) |
| `??1AutoAbilityBehaviorModuleData@@UAE@XZ` | 0x1edca0 (0x10a2d: CONTRADICTED) | 0x3c51 -> 0x1ed890 (CONFIRMED) |
| `??1HordeTransportContain@@UAE@XZ` | 0x24c530 (0xa862: CONTRADICTED) | 0x37e6b -> 0x22cc80 (CONFIRMED) |
| `??1RespawnBodyModuleData@@UAE@XZ` | 0x211d40 (0x3b372: CONTRADICTED) | 0x1be1e -> 0x212bb0 (CONFIRMED) |
| `??A?$map@HIU?$less@H@_STL@@V?$allocator@U?$pair@$$CBHI@_STL@@@2@@_STL@@QAEAAIABH@Z` | 0x6473a0 (0x1aa50: CONTRADICTED) | 0x3dd2a -> 0xa56d0 (CONFIRMED) |
| `??R?$less@VAsciiString@@@_STL@@QBE_NABVAsciiString@@0@Z` | 0x6455d0 (0x1c01c: CONTRADICTED) | 0x43d42 -> 0x62fa0 (CONFIRMED) |
| `?_M_insert_overflow@?$vector@VAsciiString@@V?$allocator@VAsciiString@@@_STL@@@_STL@@IAEXPAVAsciiString@@ABV3@ABU__false_type@2@I_N@Z` | 0x757c70 (0x112c0: CONTRADICTED) | 0x3827b -> 0x63700 (CONFIRMED) |
| `?_M_insert_overflow@?$vector@VProductionPrerequisite@@V?$allocator@VProductionPrerequisite@@@_STL@@@_STL@@IAEXPAVProductionPrerequisite@@ABV3@ABU__false_type@2@I_N@Z` | 0x787e80 (0x41f1f: CONTRADICTED) | 0x1aeb0 -> 0x146940 (CONFIRMED) |
| `?_M_insert_overflow@?$vector@W4ObjectID@@V?$allocator@W4ObjectID@@@_STL@@@_STL@@IAEXPAW4ObjectID@@ABW43@ABU__false_type@2@I_N@Z` | 0x36b490 (0x33dac: CONTRADICTED) | 0x10b8b -> 0x1523d0 (CONFIRMED) |
| `?addMoneyEarned@ScoreKeeper@@QAEXH@Z` | 0xc85f0 (0x2b2a1: CONTRADICTED) | 0x3a45e -> 0xe8b20 (CONFIRMED) |
| `?draw@Drawable@@QAEXPAVView@@@Z` | 0x786bd0 (0x3291b: CONTRADICTED) | 0x3873 -> 0x421830 (CONFIRMED) |
| `?getStdGuardRange@AIGuardRetaliateMachine@@SAMPBVObject@@@Z` | 0x189b30 (0x1cfbc: CONTRADICTED) | 0x8da5 -> 0x15e770 (CONFIRMED) |
| `?insert_unique@?$_Rb_tree@VAsciiString@@U?$pair@$$CBVAsciiString@@V?$list@PAVSuperweaponInfo@@V?$allocator@PAVSuperweaponInfo@@@_STL@@@_STL@@@_STL@@U?$_Select1st@U?$pair@$$CBVAsciiString@@V?$list@PAVSuperweaponInfo@@V?$allocator@PAVSuperweaponInfo@@@_STL@@@_STL@@@_STL@@@3@U?$less@VAsciiString@@@3@V?$allocator@U?$pair@$$CBVAsciiString@@V?$list@PAVSuperweaponInfo@@V?$allocator@PAVSuperweaponInfo@@@_STL@@@_STL@@@_STL@@@3@@_STL@@QAE?AU?$_Rb_tree_iterator@U?$pair@$$CBVAsciiString@@V?$list@PAVSuperweaponInfo@@V?$allocator@PAVSuperweaponInfo@@@_STL@@@_STL@@@_STL@@U?$_Nonconst_traits@U?$pair@$$CBVAsciiString@@V?$list@PAVSuperweaponInfo@@V?$allocator@PAVSuperweaponInfo@@@_STL@@@_STL@@@_STL@@@2@@2@U32@ABU?$pair@$$CBVAsciiString@@V?$list@PAVSuperweaponInfo@@V?$allocator@PAVSuperweaponInfo@@@_STL@@@_STL@@@2@@Z` | 0x64cbd0 (0x3afee: CONTRADICTED) | 0x14376 -> 0x44aa20 (CONFIRMED) |
| `?setIsLogicalAudio@AudioEventRTS@@QAEX_N@Z` | 0xb2330 (0x2c5cf: CONTRADICTED) | 0x8206 -> 0xb2350 (CONFIRMED) |
| `?winSetNextInLayout@GameWindow@@QAEXPAV1@@Z` | 0x1bd6a0 (0x4097b: CONTRADICTED) | 0x35cf6 -> 0x478df0 (CONFIRMED) |
| `?winSetPrevInLayout@GameWindow@@QAEXPAV1@@Z` | 0x478dd0 (0x1a046: CONTRADICTED) | 0x15fb4 -> 0x478e00 (CONFIRMED) |

## What landed

- Nine claimed bodies became `?dup_<rva>` aliases: 0x001EDCA0, 0x0024C530,
  0x00211D40, 0x006473A0, 0x006455D0, 0x00757C70, 0x000C85F0, 0x001BD6A0
  and 0x00478DD0. No move to a pinned body byte-matched (each TU
  compiles a differently shaped body), so those names stay pin-only.
- Not changed:
  - The ProductionPrerequisite `_M_insert_overflow` row at 0x00787E80: the thunk
    alias for 0x00041F1F in RvaShard2TailThunks.cpp binds that name there
    (alias_guard).
  - `?setIsLogicalAudio@AudioEventRTS@@QAEX_N@Z` (0x000B2330): eleven byte-matched
    callers spell it at that body. The oracle contradicts it there (and
    setUninterruptable too) and confirms it at 0x00008206 -> 0x000B2350. The
    callers and 0x000B2330 both need their real identity first.
  - Rows sitting at thunk addresses (0x00033DAC, 0x0003291B), bodies carrying
    several rows (0x0033A580, 0x001A93A0, 0x00189B30, 0x0064CBD0), and a
    LadderDefs.cpp body that failed to verify (0x00756D90).
