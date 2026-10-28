# ILT-confirmed real-name candidates for address-named matched bodies

Input revision: origin/master at 7d4f5f19 (2026-10-28). Not applied: AGENTS.md
pauses bulk renames and routes placeholder names through the name lane.

Method (tools only, reproducible): for every matched row whose source is not
generated and whose name carries an address token (Rva/Gen/Open2Rec/hex), take
the 5-byte ILT thunks that jump to its body, collect the real-looking names
pinned at those ILTs in symbols.csv, and keep a candidate only when
`python3 tools/ilt_oracle.py check NAME 0xBODY` reports CONFIRMED. A fit is
consistent with retail, not proof (the oracle's own caveat): each still needs
the usual identity evidence (layout, callers, vtable) before it lands, ideally
through `add_match.py --correct-identity ... --identity-evidence`.

One was landed as a worked example: 0x004F1120 -> ??0PlayerInfo@@QAE@ABV0@@Z
(commit 7d4f5f19, identity_evidence/004f1120-playerinfo-copy-ctor.md).

| body | size | current name | ILT-confirmed candidate | source |
|---|---:|---|---|---|
| 0x723a50 | 80 | `??0BfmeA1137@@QAE@XZ` | `??0W3DSnowManager@@QAE@XZ` | BfmeConv1137.cpp |
| 0x10db80 | 189 | `??0Gen_0010DB80@@QAE@ABV0@@Z` | `??0SaveGameInfo@@QAE@ABV0@@Z` | BfmeNineMemberCopyWL.cpp |
| 0x14b6b0 | 140 | `??0Gen_0014B790@@QAE@XZ` | `??0AISideInfo@@QAE@XZ` | BfmeConv1651.cpp |
| 0x33a640 | 104 | `??0Gen_0033A640@@QAE@ABV0@@Z` | `??0NamedReveal@@QAE@ABU0@@Z` | BfmeThreeStringCopyVZ.cpp |
| 0x4f1280 | 138 | `??0Open2Rec4F1280@@QAE@XZ` | `??0PlayerInfo@@QAE@XZ` | Open2Rec4F1280.cpp |
| 0x7b620 | 19 | `??0Rva0007B620@@QAE@XZ` | `??0FunctorNotSet@@QAE@XZ` | S1IndirectSlotCalls.cpp |
| 0xed2d0 | 79 | `??0Rva000ED2D0@@QAE@XZ` | `??0DamageInfoInput@@QAE@XZ` | Rva000ED2D0Ctor.cpp |
| 0x29bcc0 | 66 | `??0Rva0029BCC0@@QAE@XZ` | `??0ProductionEntry@@QAE@XZ` | Rva0029BCC0Ctor.cpp |
| 0x3fd790 | 34 | `??0Rva003FD790@@QAE@XZ` | `??0Path@@QAE@XZ` | R3ScalarFieldConstructors3.cpp |
| 0x410000 | 23 | `??0Rva00410000@@QAE@XZ` | `??0DisplayString@@QAE@XZ` | R2ZeroingConstructors.cpp |
| 0x428e10 | 69 | `??0Rva00428E10@@QAE@XZ` | `??0LightPulseFXNugget@@QAE@XZ` | Rva00428E10Ctor.cpp |
| 0x9f7a0 | 103 | `??1Gen_0009F7A0@@UAE@XZ` | `??1SkirmishPreferences@@UAE@XZ` | Bfme5ListMemberDtors.cpp |
| 0xe54b0 | 165 | `??1Gen_000E54B0@@QAE@XZ` | `??1ProductionPrerequisite@@QAE@XZ` | Bfme5TwoVectorDtors.cpp |
| 0xf8a40 | 156 | `??1Gen_000F8A40@@UAE@XZ` | `??1TunnelTracker@@UAE@XZ` | Bfme5ThreeMemberDtor.cpp |
| 0x4f10b0 | 89 | `??1Gen_004F10B0@@QAE@XZ` | `??1PlayerInfo@@QAE@XZ` | Bfme7NarrowStringChainDestructors.cpp |
| 0x77dd80 | 85 | `??1Gen_0077DD80@@UAE@XZ` | `??1W3DSupplyDrawModuleData@@UAE@XZ` | Bfme5ChainedDestructors.cpp |
| 0xe27a0 | 702 | `??1PlayerTemplate000E27A0@@QAE@XZ` | `??1PlayerTemplate@@QAE@XZ` | PlayerTemplateDestructor000E27A0.cpp |
| 0x113e60 | 7 | `??1Rva0002B8C8TailBase@@UAE@XZ` | `??1DrawableModule@@MAE@XZ` | Rva0002B8C8TailBaseDestructor.cpp |
| 0x659e0 | 14 | `??1Rva000659E0MultiTailDtor@@UAE@XZ` | `??1CRCParameterCheck@@UAE@XZ` | MultiVptrTailJumpDestructors.cpp |
| 0x72490 | 77 | `??1Rva00072490@@QAE@XZ` | `??1GameSlot@@QAE@XZ` | R4TwoMemberDestructors.cpp |
| 0x86320 | 11 | `??1Rva00086320TailDtor@@UAE@XZ` | `??1LANPreferences@@UAE@XZ` | VptrTailJumpDestructors.cpp |
| 0x8f840 | 14 | `??1Rva0008F840MultiTailDtor@@UAE@XZ` | `??1Bucket@@UAE@XZ` | MultiVptrTailJumpDestructors.cpp |
| 0xaafd0 | 11 | `??1Rva000AAFD0TailDtor@@UAE@XZ` | `??1IgnorePreferences@@UAE@XZ` | VptrTailJumpDestructors.cpp |
| 0xe9a40 | 150 | `??1Rva000E9A40@@UAE@XZ` | `??1ScoreKeeper@@UAE@XZ` | Rva000E9A40Destructor.cpp |
| 0x105350 | 11 | `??1Rva00105350TailDtor@@UAE@XZ` | `??1FunctionLexicon@@UAE@XZ` | VptrTailJumpDestructors.cpp |
| 0x129560 | 76 | `??1Rva00129560@@QAE@XZ` | `??1SymbioticStructuresBodyModuleData@@UAE@XZ` | BigPairMemberDtors.cpp |
| 0x12acd0 | 67 | `??1Rva0012ACD0@@QAE@XZ` | `??1FireWeaponWhenDamagedBehaviorModuleData@@UAE@XZ` | BigTwoMemberDtors.cpp |
| 0x16ac60 | 11 | `??1Rva0016AC60TailDtor@@UAE@XZ` | `??1AttackFireWhileChargingMachine@@UAE@XZ` | VptrTailJumpDestructors.cpp |
| 0x16b5a0 | 11 | `??1Rva0016B5A0TailDtor@@UAE@XZ` | `??1BackAwayAndCowerStateMachine@@UAE@XZ` | VptrTailJumpDestructors.cpp |
| 0x1780a0 | 94 | `??1Rva001780A0@@UAE@XZ` | `??1AIAttackMeleeEngageState@@UAE@XZ` | R4OwnedPointerDestructors.cpp |
| 0x179550 | 94 | `??1Rva00179550@@UAE@XZ` | `??1AIFollowPathAsTeamState@@UAE@XZ` | R4OwnedPointerDestructors.cpp |
| 0x17d7a0 | 106 | `??1Rva0017D7A0@@UAE@XZ` | `??1AIDockState@@MAE@XZ` | Q4OwnedPtrDtors.cpp |
| 0x17e160 | 106 | `??1Rva0017E160@@UAE@XZ` | `??1AIGuardRetaliateState@@MAE@XZ` | Q4OwnedPtrDtors.cpp |
| 0x1d6d80 | 95 | `??1Rva001D6D80@@QAE@XZ` | `??1AttackNugget@@UAE@XZ` | Rva001D6D80Dtor.cpp |
| 0x1f7790 | 32 | `??1Rva001F7790NestedDtor@@UAE@XZ` | `??1ClickReactionBehavior@@MAE@XZ` | NestedInlineDestructors.cpp |
| 0x1feb50 | 178 | `??1Rva001FEB50@@UAE@XZ` | `??1GettingBuiltBehavior@@MAE@XZ` | Rva001FEB50Destructor.cpp |
| 0x20d090 | 32 | `??1Rva0020D090NestedDtor@@UAE@XZ` | `??1SpawnUnitBehavior@@MAE@XZ` | NestedInlineDestructors.cpp |
| 0x20f8e0 | 178 | `??1Rva0020F8E0Owner@@UAE@XZ` | `??1ActiveBody@@UAE@XZ` | Rva0020F8E0Destructor.cpp |
| 0x212bb0 | 76 | `??1Rva00212BB0@@QAE@XZ` | `??1RespawnBodyModuleData@@UAE@XZ` | BigPairMemberDtors.cpp |
| 0x212d30 | 35 | `??1Rva00212D30FlatDtor@@UAE@XZ` | `??1DetachableRiderBody@@MAE@XZ` | FlatMultiVptrDestructors.cpp |
| 0x215a70 | 32 | `??1Rva00215A70NestedDtor@@UAE@XZ` | `??1AODCrushCollide@@MAE@XZ` | NestedInlineDestructors.cpp |
| 0x215df0 | 67 | `??1Rva00215DF0@@QAE@XZ` | `??1AODCrushCollideModuleData@@UAE@XZ` | BigTwoMemberDtors.cpp |
| 0x24fb30 | 67 | `??1Rva0024FB30@@QAE@XZ` | `??1GrantUpgradeCreateModuleData@@UAE@XZ` | BigTwoMemberDtors.cpp |
| 0x250df0 | 67 | `??1Rva00250DF0@@QAE@XZ` | `??1EvacuateDamageModuleData@@UAE@XZ` | BigTwoMemberDtors.cpp |
| 0x2545e0 | 25 | `??1Rva002545E0NestedDtor@@UAE@XZ` | `??1CreateObjectDie@@MAE@XZ` | NestedInlineDestructors.cpp |
| 0x255320 | 25 | `??1Rva00255320NestedDtor@@UAE@XZ` | `??1FXListDie@@MAE@XZ` | NestedInlineDestructors.cpp |
| 0x256890 | 96 | `??1Rva00256890Module@@UAE@XZ` | `??1ObjectGuardingHelper@@MAE@XZ` | Rva00256890ModuleDestructor.cpp |
| 0x259320 | 79 | `??1Rva00259320@@QAE@XZ` | `??1CloudBreakSpecialPowerModuleData@@UAE@XZ` | Q4PairSubobjectDtors.cpp |
| 0x25a390 | 46 | `??1Rva0025A390FlatDtor@@UAE@XZ` | `??1DeflectSpecialPower@@MAE@XZ` | FlatMultiVptrDestructors.cpp |
| 0x26b8e0 | 79 | `??1Rva0026B8E0@@QAE@XZ` | `??1TaintSpecialPowerModuleData@@UAE@XZ` | Q4PairSubobjectDtors.cpp |
| 0x26c550 | 42 | `??1Rva0026C550FlatDtor@@UAE@XZ` | `??1ToggleMountedSpecialAbilityUpdate@@MAE@XZ` | FlatMultiVptrDestructors.cpp |
| 0x2bf7d0 | 94 | `??1Rva002BF7D0@@UAE@XZ` | `??1GiantBirdAttackMoveToState@@UAE@XZ` | R4OwnedPointerDestructors.cpp |
| 0x2d2210 | 32 | `??1Rva002D2210NestedDtor@@UAE@XZ` | `??1SupplyCenterProductionExitUpdate@@MAE@XZ` | NestedInlineDestructors.cpp |
| 0x2d3080 | 141 | `??1Rva002D3080@@UAE@XZ` | `??1AudioLoopUpgrade@@UAE@XZ` | Rva002D3080Destructor.cpp |
| 0x428b50 | 79 | `??1Rva00428B50@@QAE@XZ` | `??1SoundFXNugget@@UAE@XZ` | Q4PairSubobjectDtors.cpp |
| 0x4297d0 | 79 | `??1Rva004297D0@@QAE@XZ` | `??1LaserFXNugget@@UAE@XZ` | Q4PairSubobjectDtors.cpp |
| 0x5a3b20 | 120 | `??1Rva005A3B20@@UAE@XZ` | `??1Keyboard@@UAE@XZ` | Rva005A3B20Destructor.cpp |
| 0x5dd6e0 | 66 | `??1Rva005DD6E0@@UAE@XZ` | `??1PointEmissionVolumeModule@FXParticleSystem@@UAE@XZ` | V3MiDtorsWithListNodeWave2.cpp |
| 0x5dd740 | 66 | `??1Rva005DD740@@UAE@XZ` | `??1LineEmissionVolumeModule@FXParticleSystem@@UAE@XZ` | V3MiDtorsWithListNodeWave2.cpp |
| 0x5dd7a0 | 66 | `??1Rva005DD7A0@@UAE@XZ` | `??1BoxEmissionVolumeModule@FXParticleSystem@@UAE@XZ` | V3MiDtorsWithListNodeWave2.cpp |
| 0x5dd800 | 66 | `??1Rva005DD800@@UAE@XZ` | `??1SphereEmissionVolumeModule@FXParticleSystem@@UAE@XZ` | V3MiDtorsWithListNodeWave2.cpp |
| 0x5dd860 | 66 | `??1Rva005DD860@@UAE@XZ` | `??1CylinderEmissionVolumeModule@FXParticleSystem@@UAE@XZ` | V3MiDtorsWithListNodeWave2.cpp |
| 0x5dd940 | 66 | `??1Rva005DD940@@UAE@XZ` | `??1OrthoEmissionVelocityModule@FXParticleSystem@@UAE@XZ` | V3MiDtorsWithListNodeWave2.cpp |
| 0x5dd9a0 | 66 | `??1Rva005DD9A0@@UAE@XZ` | `??1SphericalEmissionVelocityModule@FXParticleSystem@@UAE@XZ` | V3MiDtorsWithListNodeWave2.cpp |
| 0x5dda00 | 66 | `??1Rva005DDA00@@UAE@XZ` | `??1HemisphericalEmissionVelocityModule@FXParticleSystem@@UAE@XZ` | V3MiDtorsWithListNodeWave2.cpp |
| 0x5dda60 | 66 | `??1Rva005DDA60@@UAE@XZ` | `??1CylindricalEmissionVelocityModule@FXParticleSystem@@UAE@XZ` | V3MiDtorsWithListNodeWave2.cpp |
| 0x5ddac0 | 66 | `??1Rva005DDAC0@@UAE@XZ` | `??1OutwardEmissionVelocityModule@FXParticleSystem@@UAE@XZ` | V3MiDtorsWithListNodeWave2.cpp |
| 0x6609d0 | 197 | `??1Rva006609D0@@UAE@XZ` | `??1Pinger@@UAE@XZ` | Rva006609D0Destructor.cpp |
| 0x6bdb50 | 114 | `??1Rva006BDB50@@UAE@XZ` | `??1W3DGhostObjectManager@@UAE@XZ` | Rva006BDB50Destructor.cpp |
| 0x5b37c0 | 95 | `??1S4Dtor005B37C0@@UAE@XZ` | `??1HotKeyManager@@UAE@XZ` | S4TwoMemberDestructors.cpp |
| 0xa8490 | 81 | `??4Rva000A8490@@QAEAAV0@ABV0@@Z` | `??4TerrainType@@QAEAAV0@ABV0@@Z` | Rva000A8490Assign.cpp |
| 0x14a470 | 162 | `??4Rva0014A470@@QAEAAV0@ABV0@@Z` | `??4AISideInfo@@QAEAAV0@ABV0@@Z` | Rva0014A470Assign.cpp |
| 0x458450 | 93 | `??4Rva00458450@@QAEXABV0@@Z` | `??4RadiusDecalTemplate@@QAEXABV0@@Z` | Rva00458450Assign.cpp |
| 0x630d60 | 105 | `??4Rva00630D60@@QAEAAV0@ABV0@@Z` | `??4PlayerInfo@@QAEAAV0@ABV0@@Z` | Rva00630D60Assign.cpp |
| 0x59abc0 | 952 | `?PushButtonImageDrawThree@Rva0059ABC0@@YAXPAVGameWindow@@H@Z` | `?PushButtonImageDrawThree@@YAXPAVGameWindow@@H@Z` | PushButtonImageDrawThreeRva0059ABC0.cpp |
| 0x2b6630 | 1 | `?Rva002B6630NoOp@@YAXXZ` | `??1DozerDockPointInfo@DozerAIUpdate@@QAE@XZ` | Rva002B6630NoOp.cpp |
| 0x5091b0 | 21 | `?Rva005091B0@@YAXH@Z` | `?PopulateQMLadderListBox@@YAXPAVGameWindow@@@Z` | Q1GlobalGuardedForwarders.cpp |
| 0x7b7580 | 46 | `?Rva007B7580@@YAXXZ` | `?Reset@W3DShadowManager@@QAEXXZ` | S3GuardedGlobalTriples.cpp |
| 0x45c1b0 | 14 | `?apply@Rva0045C1B0@@QAEXXZ` | `??1View@@UAE@XZ` | Rva0045C1B0Init.cpp |
| 0x155da0 | 576 | `?attack00155DA0@AIGroupGroupAttackObjectPrivateShim@@QAEX_NPAVObject@@HW4CommandSourceType@@@Z` | `?groupAttackObjectPrivate@AIGroup@@AAEX_NPAVObject@@HW4CommandSourceType@@@Z` | AIGroupGroupAttackObjectPrivate.cpp |
| 0xe8b20 | 30 | `?bfmeAddCount@Gen_000E8AF0@@QAEXH@Z` | `?addMoneyEarned@ScoreKeeper@@QAEXH@Z` | Bfme5TinyTwenty.cpp |
| 0xed960 | 85 | `?bfmeApplyXG@Gen_000ED960@@QAEXVAsciiString@@@Z` | `?setAttackPriorityName@Team@@QAEXVAsciiString@@@Z` | BfmeLabelSetterXG.cpp |
| 0x1b98b0 | 113 | `?bfmeClear@Gen_001B98B0@@QAEXXZ` | `?clear@LocomotorSet@@QAEXXZ` | Bfme5CountedClears.cpp |
| 0x1efce0 | 41 | `?bfmeCost@Gen_001EFCE0@@QBEHXZ` | `?calcSleepTime@BezierProjectileBehavior@@ABE?AW4UpdateSleepTime@@XZ` | Bfme5FortyThree.cpp |
| 0x35b680 | 93 | `?bfmeCreate@Gen_0035B680@@QAEPAVBfmeCreated_0035B680@@XZ` | `?duplicate@Script@@QBEPAV1@XZ` | Bfme5MakeAndReturn.cpp |
| 0xa1d80 | 38 | `?bfmeGo1024F@BfmeF1024@@QAEDXZ` | `?isGoalObjectDestroyed@StateMachine@@QBE_NXZ` | BfmeConv1024.cpp |
| 0xd2480 | 51 | `?bfmeHasBit@Gen_000D2480@@QBE_NPBVBfmeThingEL@@@Z` | `?hasUpgradeInProduction@Player@@QAE_NPBVUpgradeTemplate@@@Z` | Bfme5SixtyFour.cpp |
| 0x723ac0 | 117 | `?bfmeReleaseResources@BfmeA1137Release@@QAEXXZ` | `?ReleaseResources@W3DSnowManager@@QAEXXZ` | BfmeConv1137Release.cpp |
| 0x433690 | 65 | `?bfmeRun@Gen_00433690@@QAEXPAX00000@Z` | `?drawOpenRect@Display@@QAEXMMMMMH@Z` | Bfme5VirtualForwarders.cpp |
| 0x793c70 | 65 | `?bfmeRun@Gen_00793C70@@QAEXPAX00000@Z` | `?drawRectClock@Display@@QAEXMMMMMH@Z` | Bfme5VirtualForwarders.cpp |
| 0x450270 | 75 | `?bfmeSet@Gen00450270@@QAEXVAsciiString@@@Z` | `?setFilename@Image@@QAEXVAsciiString@@@Z` | Bfme7NarrowSetterHeads.cpp |
| 0x4c3150 | 26 | `?bfmeValue@Gen_004C3150@@QBEHE@Z` | `?getMessageColor@InGameUI@@QAEH_N@Z` | Bfme5TinyEleven.cpp |
| 0x26ee60 | 15 | `?clear@Rva0026EE60@@QAEXXZ` | `?clearWaypointQueue@AIUpdateInterface@@QAEXXZ` | R1MemberValueReads.cpp |
| 0x5b5440 | 39 | `?clearFlags@Rva005B5440@@QAEXXZ` | `?resetModes@LookAtTranslator@@QAEXXZ` | Rva005B5440ClearFlags.cpp |
| 0x489b30 | 32 | `?copyString@Rva00489B30@@QAE?AVBfmeSharedString@@XZ` | `?getName@TransitionGroup@@QAE?AVAsciiString@@XZ` | NetworkStringGetterIdentities.cpp |
| 0x1a6f90 | 32 | `?copyStringAt54@Rva001A6F90Host@@QAE?AV?$BFMERetailStringBase@D@@XZ` | `?getPathLabel2@Waypoint@@QBE?AVAsciiString@@XZ` | RvaStringAccessor.cpp |
| 0x1a6fc0 | 32 | `?copyStringAt58@Rva001A6FC0Host@@QAE?AV?$BFMERetailStringBase@D@@XZ` | `?getPathLabel3@Waypoint@@QBE?AVAsciiString@@XZ` | RvaStringAccessor.cpp |
| 0x45ab10 | 241 | `?d_0045ab10@@YAXXZ` | `??0WeatherSetting@@QAE@XZ` | Snow.cpp |
| 0x4dd2b0 | 2116 | `?d_004dd2b0@@YAXXZ` | `?HandlePersistentStorageResponses@@YAXXZ` | PopupPlayerInfo_responses.cpp |
| 0x7b77e0 | 12 | `?d_007b77e0@@YAXXZ` | `?removeShadow@W3DShadowManager@@QAEXPAVShadow@@@Z` | VirtualSlot5CallThunk.cpp |
| 0x421830 | 674 | `?draw@DrawTransform00421830@@QAEXPAX@Z` | `?draw@Drawable@@QAEXPAVView@@@Z` | DrawTransform00421830.cpp |
| 0x86840 | 111 | `?dup_00086840@@YAXXZ` | `?getPreferredColor@LANPreferences@@QAEHXZ` | promoted__getPreferredColor_CustomMatchPreferences_QAEHXZ_000AC2A0.cpp |
| 0x868d0 | 160 | `?dup_000868d0@@YAXXZ` | `?getPreferredFaction@LANPreferences@@QAEHXZ` | UserPreferences.cpp |
| 0x90140 | 259 | `?dup_00090140@@YAXXZ` | `?nameToLowercaseKey@NameKeyGenerator@@QAE?AW4NameKeyType@@PBD@Z` | NameKeyGeneratorNameToLowercaseKeyIndexed.cpp |
| 0xa14b0 | 16 | `?dup_000a14b0@@YAXXZ` | `?getGoalObject@StateMachine@@QBEPBVObject@@XZ` | StateMachine_getGoalObject.cpp |
| 0xb32c0 | 32 | `?dup_000b32c0@@YAXXZ` | `?getAttackFilename@AudioEventRTS@@QBE?AVAsciiString@@XZ` | CDManager.cpp |
| 0xb32f0 | 32 | `?dup_000b32f0@@YAXXZ` | `?getDecayFilename@AudioEventRTS@@QBE?AVAsciiString@@XZ` | NetCommandMsg_text.cpp |
| 0x18b520 | 38 | `?dup_0018b520@@YAXXZ` | `?isOnSquad@Squad@@QBE_NPBVObject@@@Z` | Squad_isOnSquad.cpp |
| 0x18b620 | 62 | `?dup_0018b620@@YAXXZ` | `?removeObject@Squad@@QAEXPAVObject@@@Z` | Squad.cpp |
| 0x1a6f60 | 32 | `?dup_001a6f60@@YAXXZ` | `?getPathLabel1@Waypoint@@QBE?AVAsciiString@@XZ` | TerrainRoads.cpp |
| 0x1fad80 | 25 | `?dup_001fad80@@YAXXZ` | `??1EnragedBehavior@@UAE@XZ` | AutoAbilityBehaviorDestructorThunk.cpp |
| 0x250660 | 25 | `?dup_00250660@@YAXXZ` | `??1BoneFXDamage@@MAE@XZ` | TensileFormationUpdateCtorThunk.cpp |
| 0x283330 | 76 | `?dup_00283330@@YAXXZ` | `??0BannerCarrierUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | BannerCarrierUpdateRawCtor.cpp |
| 0x292550 | 25 | `?dup_00292550@@YAXXZ` | `??1FireSpreadUpdate@@MAE@XZ` | AutoAbilityBehaviorDestructorThunk.cpp |
| 0x2a16f0 | 25 | `?dup_002a16f0@@YAXXZ` | `??1RespawnUpdate@@UAE@XZ` | AutoAbilityBehaviorDestructorThunk.cpp |
| 0x2d3770 | 32 | `?dup_002d3770@@YAXXZ` | `??1BaseUpgrade@@MAE@XZ` | DynamicPortalBehaviourDestructorThunk.cpp |
| 0x2d6650 | 32 | `?dup_002d6650@@YAXXZ` | `??1ModelConditionUpgrade@@MAE@XZ` | DynamicPortalBehaviourDestructorThunk.cpp |
| 0x569680 | 63 | `?dup_00569680@@YAXXZ` | `?destroyQuitMenu@@YAXXZ` | HideSaveLoadMenu.cpp |
| 0x569d50 | 32 | `?dup_00569d50@@YAXXZ` | `?getPristineMapName@GameState@@QAE?AVAsciiString@@XZ` | NetCommandMsg_text.cpp |
| 0x624b90 | 13 | `?dup_00624b90@@YAXXZ` | `??0IPEnumeration@@QAE@XZ` | IPEnumeration.cpp |
| 0x74ac50 | 32 | `?dup_0074ac50@@YAXXZ` | `?getTexture@TerrainType@@QAE?AVAsciiString@@XZ` | LANGameInfo.cpp |
| 0x410f10 | 91 | `?ensure@Rva00410F10Owner@@QAEPAVRva00410F10Allocation@@XZ` | `?getIconInfo@Drawable@@QAEPAVDrawableIconInfo@@XZ` | Rva00410F10Ensure.cpp |
| 0x683d0 | 278 | `?ensureUniqueBody000683D0@Dict@@AAEPAUDictPair@1@H_NPAU21@@Z` | `?ensureUnique@Dict@@AAEPAUDictPair@1@H_NPAU21@@Z` | Dict.cpp |
| 0x105360 | 5 | `?forwardSlot1@AddressThunk00105360@@QAEXXZ` | `?reset@FunctionLexicon@@UAEXXZ` | VirtualDispatchSlot4.cpp |
| 0x49d2b0 | 27 | `?get@Rva0049D2B0@@QAEXPAPAX0@Z` | `?getForegroundMarkerPos@ControlBar@@QAEXPAH0@Z` | Rva0049D2B0GetFields.cpp |
| 0x49d2e0 | 27 | `?get@Rva0049D2E0@@QAEXPAPAX0@Z` | `?getBackgroundMarkerPos@ControlBar@@QAEXPAH0@Z` | Rva0049D2E0GetFields.cpp |
| 0x93f40 | 32 | `?getString@Rva00093F40StringAccessor@@UAE?AVAsciiString@@XZ` | `?getFilename@INI@@QBE?AVAsciiString@@XZ` | DisplayStringGetTextThunk.cpp |
| 0x1568a0 | 77 | `?groupGuardPosition@Open2Group1568A0@@QAEXPBUCoord3D@@W4GuardMode@1@W4CommandSourceType@1@@Z` | `?groupGuardObject@AIGroup@@QAEXPAVObject@@W4GuardMode@@W4CommandSourceType@@@Z` | Open2Twins001.cpp |
| 0x1a0de0 | 3 | `?identity@Rva001A0DE0Owner@@QAEPAV1@XZ` | `??0Vector2@@QAE@XZ` | Rva0019TinyCarvedBatch.cpp |
| 0xa5640 | 8 | `?invoke@Rva000A5640@@QAEXXZ` | `??1PSResponse@@QAE@XZ` | MemberOffsetTailThunks.cpp |
| 0x351230 | 8 | `?invoke@Rva00351230@@QAEXXZ` | `??1Parameter@@QAE@XZ` | MemberOffsetTailThunks.cpp |
| 0x436950 | 8 | `?invoke@Rva00436950@@QAEXXZ` | `??1NoString@@QAE@XZ` | MemberOffsetTailThunks.cpp |
| 0x602c30 | 8 | `?invoke@Rva00602C30@@QAEXXZ` | `?reset@TerrainVisual@@UAEXXZ` | MemberOffsetTailThunks.cpp |
| 0x6c8d80 | 11 | `?invoke@Rva006C8D80@@QAEXXZ` | `?removeTerrainBib@BaseHeightMapRenderObjClass@@QAEXW4ObjectID@@@Z` | IndirectMemberTailThunks.cpp |
| 0x33c340 | 209 | `?lookupNamedItemA@BFMEScriptEngineFlagLookup@@QAEPAVBfmeNamedItem0033c340@@VAsciiString@@PAV3@@Z` | `?findGroup@ScriptEngine@@IAEPAVScriptGroup@@VAsciiString@@PAV3@@Z` | ScriptEngineLookupNamedItem.cpp |
| 0x33c450 | 209 | `?lookupNamedItemB@BFMEScriptEngineFlagLookup@@QAEPAVBfmeNamedItem0033c340@@VAsciiString@@PAV3@@Z` | `?findScript@ScriptEngine@@IAEPAVScript@@VAsciiString@@PAV3@@Z` | ScriptEngineLookupNamedItem.cpp |
| 0x7aaf10 | 115 | `?moveAllToInactive@Rva007AAF10Owner@@QAEXXZ` | `?reset@WaterTracksRenderSystem@@QAEXXZ` | Rva007AAF10RelinkNodes.cpp |
| 0x49c5d0 | 14 | `?push@Rva0049C5D0List@@QAEXPAPAV1@@Z` | `?friend_addToList@CommandSet@@QAEXPAPAV1@@Z` | Rva0049C5D0List.cpp |
| 0x1e8670 | 138 | `?rebuildScatterTargets@Rva001E8670Weapon@@QAEXXZ` | `?rebuildScatterTargets@Weapon@@IAEXXZ` | Rva001E8670RebuildScatterTargets.cpp |
| 0xfc6e0 | 3 | `?self@Rva000FC6E0Self@@QAEPAV1@XZ` | `??0Matrix3D@@QAE@XZ` | Rva000FC6E0ThisGetter.cpp |
| 0x26fe90 | 13 | `?set@Rva0026FE90DwordSlot@@QAEXH@Z` | `?setPathExtraDistance@AIUpdateInterface@@QAEXM@Z` | DispDwordFieldSetters.cpp |
| 0x478d80 | 22 | `?set@Rva00478D80@@QAEHPAX@Z` | `?winSetOwner@GameWindow@@QAEHPAV1@@Z` | Rva00478D80Set.cpp |
| 0x354220 | 215 | `?setConditionType@Rva00354220Condition@@QAEXW4ConditionType@1@@Z` | `?setActionType@ScriptAction@@QAEXW4ScriptActionType@1@@Z` | Rva00354220ConditionSetType.cpp |
| 0xad8c0 | 169 | `?store@Open2Option0AD8C0@@QAEXH@Z` | `?setPreferredColor@CustomMatchPreferences@@QAEXH@Z` | Open2Twins003.cpp |
| 0xec8c0 | 21 | `?subtractField@Rva000EC8C0SubtractField@@QAEXXZ` | `?decreaseAIPriorityForFailure@TeamPrototype@@QBEXXZ` | Rva000EC8C0SubtractField.cpp |
| 0x4329d0 | 1632 | `?update@ClientUpdate004329D0@@QAEXXZ` | `?update@GameClient@@UAEXXZ` | ClientUpdate004329D0.cpp |
| 0x1077d0 | 175 | `?update@Rva001077D0Radar@@QAEXXZ` | `?update@Radar@@UAEXXZ` | Rva001077D0RadarUpdate.cpp |
| 0x65e30 | 41 | `Gen_f265_b7a8aa_00065e30` | `?__copy_trivial@_STL@@YAPAXPBX0PAX@Z` | GameAudio.cpp |
| 0x161d90 | 32 | `dup_161d90` | `?getBuildingName@BuildListInfo@@QBE?AVAsciiString@@XZ` | DisplayStringGetTextThunk.cpp |
| 0x161dc0 | 32 | `dup_161dc0` | `?getTemplateName@BuildListInfo@@QBE?AVAsciiString@@XZ` | ControlBarObserver.cpp |
| 0x1c2e20 | 32 | `dup_1c2e20` | `?getName@AttackPriorityInfo@@QBE?AVAsciiString@@XZ` | DisplayStringGetTextThunk.cpp |
| 0x2029f0 | 164 | `dup_2029f0` | `??0PoisonedBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` | PoisonedBehaviorCtorModuleFactory.cpp |
| 0x288c50 | 374 | `dup_288c50` | `??0BoneFXUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | BoneFXUpdateCtorModuleFactoryBody.cpp |
| 0xa7660 | 32 | `dup_a7660` | `?getName@TerrainType@@QAE?AVAsciiString@@XZ` | DisplayStringGetTextThunk.cpp |
| 0xc2d40 | 32 | `dup_c2d40` | `?getName@TerrainRoadType@@QAE?AVAsciiString@@XZ` | DisplayStringGetTextThunk.cpp |
| 0xf9c30 | 32 | `dup_f9c30` | `?getName@Image@@QBE?AVAsciiString@@XZ` | DisplayStringGetTextThunk.cpp |
