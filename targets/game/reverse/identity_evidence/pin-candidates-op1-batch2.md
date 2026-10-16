# pin --candidates drain, batch 2 (op-1, 2026-10-16)

Approved by the project lead 2026-10-16. 67 symbols.csv pins removed. Each pinned a name whose
functions.csv row sits at a different body (pin_consistency --candidates). For every one, no
relocation in any byte-matched row lands on the pinned body under that name. That was computed
from the census objects (orch build/match) by resolving every REL32/DIR32 site that names the
symbol against the retail image. So the pin was never the candidate a caller needed.

Verification: ./build.sh over the 371 matched sources whose objects mention any of the 67 names:
12,037/12,037 rows matched after the removal. pin_consistency --check OK.

| symbol | removed pin | pin body | row body | kind |
|---|---|---|---|---|
| `??$_Construct@GG@_STL@@YAXPAGABG@Z` | 0x3b3e5 | 0x00665240 | 0xcb1b0 | size-disagreement |
| `??$_Construct@VPlayerTemplate@@V1@@_STL@@YAXPAVPlayerTemplate@@ABV1@@Z` | 0x24321 | 0x00024321 | 0xe3b70 | no-boundary |
| `??$__uninitialized_copy@PBUParticleSysBoneInfo@@PAU1@@_STL@@YAPAUParticleSysBoneInfo@@PBU1@0PAU1@ABU__false_type@0@@Z` | 0x32a6 | 0x003AA480 | 0xa7aa0 | divergent-bodies |
| `??$swap@V?$_STLP_alloc_proxy@PAU?$_List_node@V?$basic_string@DV?$char_traits@D@_STL@@V?$allocator@D@2@@_STL@@@_STL@@U12@V?$allocator@U?$_List_node@V?$basic_string@DV?$char_traits@D@_STL@@V?$allocator@D@2@@_STL@@@_STL@@@2@@_STL@@@_STL@@YAXAAV?$_STLP_alloc_proxy@PAU?$_List_node@V?$basic_string@DV?$char_traits@D@_STL@@V?$allocator@D@2@@_STL@@@_STL@@U12@V?$allocator@U?$_List_node@V?$basic_string@DV?$char_traits@D@_STL@@V?$allocator@D@2@@_STL@@@_STL@@@2@@0@0@Z` | 0x21927 | 0x005C4D00 | 0x37df30 | size-disagreement |
| `??0?$VectorClass@U_ENUM_VALUE@EnumParameterClass@@@@QAE@HPBU_ENUM_VALUE@EnumParameterClass@@@Z` | 0x187af | 0x0013A580 | 0x93dbb0 | divergent-bodies |
| `??0?$VectorClass@VProxyClass@@@@QAE@HPBVProxyClass@@@Z` | 0x933d30 | 0x00933D30 | 0x13a580 | size-disagreement |
| `??0?$list@PAVFXNugget@@V?$allocator@PAVFXNugget@@@_STL@@@_STL@@QAE@ABV01@@Z` | 0x2f333 | 0x0035B550 | 0x887b60 | size-disagreement |
| `??0?$list@VAsciiString@@V?$allocator@VAsciiString@@@_STL@@@_STL@@QAE@ABV?$allocator@VAsciiString@@@1@@Z` | 0x8dcd | 0x004C4500 | 0x1a93a0 | size-disagreement |
| `??0?$list@VQueuedDownload@@V?$allocator@VQueuedDownload@@@_STL@@@_STL@@QAE@ABV?$allocator@VQueuedDownload@@@1@@Z` | 0x8dcd | 0x004C4500 | 0x1a93a0 | size-disagreement |
| `??0?$pair@$$CBVAsciiString@@VArchivedFileInfo@@@_STL@@QAE@ABU01@@Z` | 0x1005f | 0x0075EA00 | 0x9cf180 | size-disagreement |
| `??0AnimationSteeringUpdateModuleData@@QAE@XZ` | 0x1feb0 | 0x001FABC0 | 0xa71c0 | size-disagreement |
| `??0CreateObjectDieModuleData@@QAE@XZ` | 0x10b2c | 0x0028DC60 | 0x2547e0 | size-disagreement |
| `??0DemoTrapUpdateModuleData@@QAE@XZ` | 0x2bff8 | 0x00122ED0 | 0x28c9e0 | size-disagreement |
| `??0FXListDieModuleData@@QAE@XZ` | 0x25ebe | 0x002136E0 | 0x1234f0 | size-disagreement |
| `??0FireWeaponWhenDamagedBehaviorModuleData@@QAE@XZ` | 0x3025b | 0x00204ED0 | 0x12a100 | size-disagreement |
| `??0FireWeaponWhenDeadBehaviorModuleData@@QAE@XZ` | 0x25ebe | 0x002136E0 | 0x12a1c0 | size-disagreement |
| `??0FlammableUpdateModuleData@@QAE@XZ` | 0x4a250 | 0x001F6C70 | 0x294b20 | size-disagreement |
| `??0GameSpyPeerMessageQueueInterface@@QAE@XZ` | 0xa1b9 | 0x0064D650 | 0x642c50 | size-disagreement |
| `??0LightningDrawModuleTemplate@FXParticleSystem@@QAE@ABV01@@Z` | 0x19614 | 0x005DA340 | 0x5d9170 | size-disagreement |
| `??0LightningEmissionModuleTemplate@FXParticleSystem@@QAE@ABV01@@Z` | 0x19f88 | 0x005DC6E0 | 0x5d6ba0 | divergent-bodies |
| `??0ModelConditionSoundSelectorClientBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x2874 | 0x00113DA0 | 0x124a10 | size-disagreement |
| `??0OrthoEmissionVelocityModuleTemplate@FXParticleSystem@@QAE@ABV01@@Z` | 0x21cb0 | 0x005DB730 | 0x5d7000 | size-disagreement |
| `??0PointDefenseLaserUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | 0xef5c | 0x00202F40 | 0x286f80 | divergent-bodies |
| `??0PointEmissionVolumeModuleTemplate@FXParticleSystem@@QAE@ABV01@@Z` | 0x391a3 | 0x005DBEE0 | 0x5d5930 | size-disagreement |
| `??0QuadDrawModuleTemplate@FXParticleSystem@@QAE@ABV01@@Z` | 0x2218d | 0x005DA060 | 0x5d8a40 | size-disagreement |
| `??0RadarUpgradeModuleData@@QAE@XZ` | 0x10c80 | 0x002C52E0 | 0x129c10 | size-disagreement |
| `??0RailedTransportDockUpdateModuleData@@QAE@XZ` | 0x2c9d0 | 0x00295500 | 0x2ce760 | size-disagreement |
| `??0SmartBombTargetHomingUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | 0xef5c | 0x00202F40 | 0x286f80 | divergent-bodies |
| `??0SpecialPowerCompletionDieModuleData@@QAE@XZ` | 0x497b | 0x00203440 | 0x123620 | size-disagreement |
| `??0SphereEmissionVolumeModuleTemplate@FXParticleSystem@@QAE@ABV01@@Z` | 0x1eda3 | 0x005DC3B0 | 0x5d62c0 | size-disagreement |
| `??0StatusBitsUpgradeModuleData@@QAE@XZ` | 0x28ab | 0x002B65B0 | 0x129c10 | size-disagreement |
| `??0StreakDrawModuleTemplate@FXParticleSystem@@QAE@ABV01@@Z` | 0xf56a | 0x005D9F10 | 0x5d8790 | size-disagreement |
| `??0TechBuildingBehaviorModuleData@@QAE@XZ` | 0x2ea73 | 0x002029B0 | 0x8a430 | size-disagreement |
| `??0TensileFormationUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x13750 | 0x00213990 | 0x252f50 | size-disagreement |
| `??0ToppleUpdateModuleData@@QAE@XZ` | 0x10b2c | 0x0028DC60 | 0x2b13a0 | size-disagreement |
| `??0TransitionDamageFX@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x2450 | 0x0022EE70 | 0x252f50 | size-disagreement |
| `??0UpgradeSoundSelectorClientBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x2874 | 0x00113DA0 | 0x121f60 | size-disagreement |
| `??1?$_Rb_tree@IU?$pair@$$CBI_N@_STL@@U?$_Select1st@U?$pair@$$CBI_N@_STL@@@2@U?$less@I@2@V?$allocator@U?$pair@$$CBI_N@_STL@@@2@@_STL@@QAE@XZ` | 0x1481c | 0x000E3D80 | 0x887940 | size-disagreement |
| `??1?$pair@$$CBHVGameSpyGroupRoom@@@_STL@@QAE@XZ` | 0x21274 | 0x004EA1B0 | 0x631920 | size-disagreement |
| `??1Gen_00491580@@UAE@XZ` | 0x492370 | 0x00492370 | 0x491620 | size-disagreement |
| `??1Gen_00491880@@UAE@XZ` | 0x4923a0 | 0x004923A0 | 0x491940 | size-disagreement |
| `??4StringClass@@QAEABV0@ABV0@@Z` | 0x7a63 | 0x000DE2C0 | 0x13b600 | size-disagreement |
| `??8@YA_NABVAsciiString@@0@Z` | 0x15898 | 0x006451D0 | 0x5a8140 | size-disagreement |
| `??_GBroadcastStealthUpdate@@UAEPAXI@Z` | 0x18156 | 0x00289B00 | 0x289bb0 | size-disagreement |
| `??_GCreateCrateDie@@UAEPAXI@Z` | 0x4142a | 0x00253D30 | 0x253f60 | size-disagreement |
| `??_GDecalMeshClass@@UAEPAXI@Z` | 0x1762a | 0x000FCA80 | 0xfc6f0 | divergent-bodies |
| `?Resize@?$SimpleVecClass@PAV?$MultiListClass@VDX8FVFCategoryContainer@@@@@@UAE_NH@Z` | 0x38ece | 0x0079FF40 | 0x78c820 | size-disagreement |
| `?Resize@?$SimpleVecClass@PAVBSPClass@@@@UAE_NH@Z` | 0x38ece | 0x0079FF40 | 0x78c820 | size-disagreement |
| `?Resize@?$SimpleVecClass@PAVDynamicMeshClass@@@@UAE_NH@Z` | 0x38ece | 0x0079FF40 | 0x78c820 | size-disagreement |
| `?TEST_KINDOFMASK_ANY@@YA_NABV?$BitFlags@$0HE@@@0@Z` | 0x497d3 | 0x00132A20 | 0x132ab0 | size-disagreement |
| `?_M_erase@?$_Rb_tree@W4NameKeyType@@U?$pair@$$CBW4NameKeyType@@VObjectCreationList@@@_STL@@U?$_Select1st@U?$pair@$$CBW4NameKeyType@@VObjectCreationList@@@_STL@@@3@U?$less@W4NameKeyType@@@3@V?$allocator@U?$pair@$$CBW4NameKeyType@@VObjectCreationList@@@_STL@@@3@@_STL@@AAEXPAU?$_Rb_tree_node@U?$pair@$$CBW4NameKeyType@@VObjectCreationList@@@_STL@@@2@@Z` | 0xe363 | 0x00129270 | 0x78c70 | divergent-bodies |
| `?_M_insert_overflow@?$vector@UDetonatorInfo@MinefieldBehavior@@V?$allocator@UDetonatorInfo@MinefieldBehavior@@@_STL@@@_STL@@IAEXPAUDetonatorInfo@MinefieldBehavior@@ABU34@ABU__false_type@2@I_N@Z` | 0xae93 | 0x0075A330 | 0x573f40 | divergent-bodies |
| `?_M_insert_overflow@?$vector@VArmorTemplateSet@@V?$allocator@VArmorTemplateSet@@@_STL@@@_STL@@IAEXPAVArmorTemplateSet@@ABV3@ABU__false_type@2@I_N@Z` | 0xe868 | 0x002109B0 | 0x144170 | divergent-bodies |
| `?_M_open@_Filebuf_base@_STL@@QAE_NPBDH@Z` | 0x84a144 | 0x0084A144 | 0x84a120 | no-boundary |
| `?anyIntersectionWith@?$BitFlags@$0HE@@@QBE_NABV1@@Z` | 0x3873 | 0x00421830 | 0x786bd0 | size-disagreement |
| `?concat@AsciiString@@QAEXPBD@Z` | 0x6db6 | 0x00090140 | 0x61c30 | size-disagreement |
| `?countIntersection@?$BitFlags@$0HF@@@QBEHABV1@@Z` | 0x497d3 | 0x00132A20 | 0x786bd0 | size-disagreement |
| `?countInverseIntersection@?$BitFlags@$0BB@@@QBEHABV1@@Z` | 0x3873 | 0x00421830 | 0x786bd0 | size-disagreement |
| `?countInverseIntersection@?$BitFlags@$0HF@@@QBEHABV1@@Z` | 0x497d3 | 0x00132A20 | 0x421830 | size-disagreement |
| `?dup_006963a0@@YAXXZ` | 0xa963a0 | 0x00A963A0 | 0x6963a0 | no-boundary |
| `?freeBlock@MemoryPool@@QAEXPAX@Z` | 0x3873 | 0x00421830 | 0x786bd0 | size-disagreement |
| `?getName@DataChunkTableOfContents@@QAE?AVAsciiString@@I@Z` | 0x2ecd | 0x00068550 | 0x102d90 | size-disagreement |
| `?loadPostProcess@TeamRelationMap@@MAEXXZ` | 0xf3c50 | 0x000F3C50 | 0xf2230 | size-disagreement |
| `?pop_front@?$deque@VPSRequest@@V?$allocator@VPSRequest@@@_STL@@@_STL@@QAEXXZ` | 0x2d77c | 0x006486F0 | 0x656b60 | divergent-bodies |
| `?winGetPosition@GameWindow@@QAEHPAH0@Z` | 0x179bd | 0x000C9D10 | 0x478140 | size-disagreement |
| `_errormessage` | 0xd96d50 | 0x00D96D50 | 0x996d50 | non-text-pin |
| `??0StructureToppleUpdateModuleData@@QAE@XZ` | 0x287c7 | 0x00285F10 | 0x12bf50 | size-disagreement |
