# Retired pinharvest pins that contradict a byte-verified row (pin_consistency --candidates, batch 1)

Each name below had exactly two resolver candidates: its own byte-verified
functions.csv row and one `pinharvest x1` symbols.csv pin (a harvest proposal,
not evidence). The pin's thunk chain lands on a body that other byte-verified
functions.csv rows already own, and that body is not the same function as the
name's row (pin_consistency: size-disagreement or divergent-bodies). Retail was
linked without identical-COMDAT folding, so one of the two is wrong; the row is
byte-verified under the name at a real source, the pin proves nothing.

Callers were checked the way the gate's pin-deletion check does
(`tools/delta_sources.py --staged --pins --selectors`): every source whose
retail call sites reached a deleted pin was rebuilt with ./build.sh. Ten pins
whose deletion broke a byte-matched caller were KEPT (listed as undecided in
op-3's pin_candidates_open.tsv); the 58 below rebuilt green, and link_check on
the 35 affected sources is unchanged (LINKED 5,557 -> 5,557).

| name | retired pin | pin body | name's row | row source | other owner of pin body |
|---|---|---|---|---|---|
| `??0AIMoveToState@@QAE@PAVStateMachine@@@Z` | 0x0000C6E9 | 0x5bf5d0 | 0x173430 | game/GameEngine/Source/GameLogic/AI/AIMoveToStateCtorThunk.cpp | `??0?$CategoryModuleTemplateBase@$02@FXParticleSystem@@QAE@ABV01@@Z` |
| `??0ActiveBodyModuleData@@QAE@XZ` | 0x00001780 | 0x2cf5a0 | 0x20f7c0 | game/GameEngine/Source/GameLogic/Object/Body/ActiveBodyModuleDataCtor.cpp | `??0SupplyCenterDockUpdateModuleData@@QAE@XZ` |
| `??0AutoDepositUpdateModuleData@@QAE@XZ` | 0x00001780 | 0x2cf5a0 | 0x123e90 | game/GameEngine/Source/GameLogic/Object/Update/AutoDepositUpdateModuleDataCtorThunk.cpp | `??0SupplyCenterDockUpdateModuleData@@QAE@XZ` |
| `??0BaikonurLaunchPowerModuleData@@QAE@XZ` | 0x0001ABF9 | 0x2d99b0 | 0x212c10 | game/GameEngine/Source/GameLogic/Object/SpecialPower/BaikonurLaunchPowerModuleDataConstructor.cpp | `??0UnpauseSpecialPowerUpgradeModuleData@@QAE@XZ` |
| `??0BeaconClientUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0001D3AE | 0x24f860 | 0x6030c0 | game/GameEngine/Source/GameClient/Drawable/Update/BeaconClientUpdateConstructor.cpp | `??0GrantUpgradeCreate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0CreateCrateDie@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0001D3AE | 0x24f860 | 0x253e70 | game/GameEngine/Source/GameLogic/Object/Die/CreateCrateDie.cpp | `??0GrantUpgradeCreate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0CreateCrateDieModuleData@@QAE@XZ` | 0x0000497B | 0x203440 | 0x1298d0 | game/GameEngine/Source/GameLogic/Object/Die/CreateCrateDieModuleDataCtorThunk.cpp | `??0Rva00203440@@QAE@XZ` |
| `??0CreateObjectDie@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0001D3AE | 0x24f860 | 0x254680 | game/GameEngine/Source/GameLogic/Object/Die/CreateObjectDie.cpp | `??0GrantUpgradeCreate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0CrushDie@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0001D3AE | 0x24f860 | 0x254b90 | game/GameEngine/Source/GameLogic/Object/Die/CrushDie.cpp | `??0GrantUpgradeCreate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0DefectorSpecialPowerModuleData@@QAE@XZ` | 0x0001ABF9 | 0x2d99b0 | 0x25a110 | game/GameEngine/Source/GameLogic/Object/SpecialPower/DefectorSpecialPowerModuleData_ctor.cpp | `??0UnpauseSpecialPowerUpgradeModuleData@@QAE@XZ` |
| `??0DestroyDie@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0001D3AE | 0x24f860 | 0x254f80 | game/GameEngine/Source/GameLogic/Object/Die/DestroyDie.cpp | `??0GrantUpgradeCreate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0DetailedArchivedDirectoryInfo@@QAE@ABV0@@Z` | 0x009CA8F0 | 0x9ca8f0 | 0x9d0db0 | game/GameEngine/Source/Common/System/DetailedArchivedDirectoryInfoCopyConstructorThunk.cpp | `??0ArchivedDirectoryInfo@@QAE@ABV0@@Z` |
| `??0ExperienceScalarUpgradeModuleData@@QAE@XZ` | 0x00010C80 | 0x2c52e0 | 0x2d5180 | game/GameEngine/Source/GameLogic/Object/Upgrade/ExperienceScalarUpgradeModuleData.cpp | `??0SiegeAIUpdateModuleData@@QAE@XZ` |
| `??0FXListDie@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x00008878 | 0x2aaf30 | 0x255360 | game/GameEngine/Source/GameLogic/Object/Die/FXListDieConstructor.cpp | `??0SpecialEnemySenseUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0FireWeaponCollide@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x00008878 | 0x2aaf30 | 0x216430 | game/GameEngine/Source/GameLogic/Object/Collide/FireWeaponCollideCtorThunk.cpp | `??0SpecialEnemySenseUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0FireWeaponUpdateModuleData@@QAE@XZ` | 0x000118E7 | 0x2cef40 | 0x292cb0 | game/GameEngine/Source/GameLogic/Object/Update/FireWeaponUpdate.cpp | `??0RepairDockUpdateModuleData@@QAE@XZ` |
| `??0FireWeaponWhenDeadBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x00008878 | 0x2aaf30 | 0x1fbc70 | game/GameEngine/Source/GameLogic/Object/Behavior/FireWeaponWhenDeadBehavior_ctor_Thunk.cpp | `??0SpecialEnemySenseUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0InactiveBody@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x00008878 | 0x2aaf30 | 0x213bf0 | game/GameEngine/Source/GameLogic/Object/Body/InactiveBodyCtorThunk.cpp | `??0SpecialEnemySenseUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0InstantDeathBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0001D3AE | 0x24f860 | 0x200ba0 | game/GameEngine/Source/GameLogic/Object/Behavior/InstantDeathBehaviorCtorThunk.cpp | `??0GrantUpgradeCreate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0KeepObjectDie@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0001D3AE | 0x24f860 | 0x255870 | game/GameEngine/Source/GameLogic/Object/Die/KeepObjectDie.cpp | `??0GrantUpgradeCreate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0MessageStream@@QAE@XZ` | 0x000132B4 | 0x6735d0 | 0x8a600 | game/GameEngine/Source/Common/MessageStream_ctor.cpp | `??0NetCommandMsg@@QAE@XZ` |
| `??0ModelConditionUpgradeModuleData@@QAE@XZ` | 0x00010C80 | 0x2c52e0 | 0x2d6a20 | game/GameEngine/Source/GameLogic/Object/Upgrade/ModelConditionUpgradeModuleDataCtorThunk.cpp | `??0SiegeAIUpdateModuleData@@QAE@XZ` |
| `??0NetDisconnectKeepAliveCommandMsg@@QAE@XZ` | 0x000132B4 | 0x6735d0 | 0x673bd0 | game/GameEngine/Source/GameNetwork/NetCommandMsg_ctors.cpp | `??0NetCommandMsg@@QAE@XZ` |
| `??0OCLUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0000EF5C | 0x202f40 | 0x298960 | game/GameEngine/Source/GameLogic/Object/Update/OCLUpdateConstruction.cpp | `??0PropagandaTowerBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0OCLUpdateModuleData@@QAE@XZ` | 0x00001780 | 0x2cf5a0 | 0x298920 | game/GameEngine/Source/GameLogic/Object/Update/OCLUpdateConstruction.cpp | `??0SupplyCenterDockUpdateModuleData@@QAE@XZ` |
| `??0ObjectCreationUpgradeModuleData@@QAE@XZ` | 0x00010C80 | 0x2c52e0 | 0x2d75b0 | game/GameEngine/Source/GameLogic/Object/Upgrade/ObjectCreationUpgradeModuleDataConstructor.cpp | `??0SiegeAIUpdateModuleData@@QAE@XZ` |
| `??0ParkingPlaceBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0000CDD8 | 0x20ae30 | 0x1f59f0 | game/GameEngine/Source/GameLogic/Object/Behavior/ParkingPlaceBehaviorCtorThunk.cpp | `??0SpawnBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0PhysicsBehaviorModuleData@@QAE@XZ` | 0x00007FF4 | 0x2827e0 | 0x29a090 | game/GameEngine/Source/GameLogic/Object/Update/PhysicsBehaviorModuleDataCtorThunk.cpp | `??0AutoPickUpUpdateModuleData@@QAE@XZ` |
| `??0ProductionUpdateModuleData@@QAE@XZ` | 0x0000E9F8 | 0x291950 | 0x29fb70 | game/GameEngine/Source/GameLogic/Object/Update/ProductionUpdateModuleDataCtor.cpp | `??0HitReactionBehaviorModuleData@@QAE@XZ` |
| `??0RAMFile@@QAE@XZ` | 0x009E6990 | 0x9e6990 | 0x9d1980 | game/GameEngine/Source/Common/System/File.cpp | `??0RawFileClass@@QAE@XZ` |
| `??0RadiusDecalUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0000EF5C | 0x202f40 | 0x2a0640 | game/GameEngine/Source/GameLogic/Object/Update/RadiusDecalUpdateCtorThunk.cpp | `??0PropagandaTowerBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0RiderChangeContainModuleData@@QAE@XZ` | 0x00014619 | 0x26b1d0 | 0x268120 | game/GameEngine/Source/GameLogic/Object/Contain/RiderChangeContainModuleData_ctor_Thunk.cpp | `??0SplitHordeSpecialPowerModuleData@@QAE@XZ` |
| `??0SlavedUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x00001CDA | 0x25a1b0 | 0x2a4260 | game/GameEngine/Source/GameLogic/Object/Update/SlavedUpdateCtorThunk.cpp | `??0DeflectSpecialPower@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0SlowDeathBehaviorModuleData@@QAE@XZ` | 0x000186FB | 0x2d6a20 | 0x2093f0 | game/GameEngine/Source/GameLogic/Object/Behavior/SlowDeathBehaviorModuleData_ctor_Thunk.cpp | `??0ModelConditionUpgradeModuleData@@QAE@XZ` |
| `??0SpawnBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x00034711 | 0x2af1e0 | 0x20ae30 | game/GameEngine/Source/GameLogic/Object/Behavior/SpawnBehaviorCtorThunk.cpp | `??0StructureToppleUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0SpecialPowerCompletionDie@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x00008878 | 0x2aaf30 | 0x255e30 | game/GameEngine/Source/GameLogic/Object/Die/SpecialPowerCompletionDie.cpp | `??0SpecialEnemySenseUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0SpyVisionUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x00004D36 | 0x2062c0 | 0x1ee950 | game/GameEngine/Source/GameLogic/Object/Update/SpyVisionUpdateCtor.cpp | `??0SiegeDockingBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0SquishCollide@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0001D3AE | 0x24f860 | 0x216ba0 | game/GameEngine/Source/GameLogic/Object/Collide/SquishCollideConstructor.cpp | `??0GrantUpgradeCreate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0SubObjectsUpgradeModuleData@@QAE@XZ` | 0x0001ABF9 | 0x2d99b0 | 0x12b6c0 | game/GameEngine/Source/GameLogic/Object/Upgrade/SubObjectsUpgradeModuleDataCtorThunk.cpp | `??0UnpauseSpecialPowerUpgradeModuleData@@QAE@XZ` |
| `??0SupplyCenterDockUpdateModuleData@@QAE@XZ` | 0x000118E7 | 0x2cef40 | 0x2cf5a0 | game/GameEngine/Source/GameLogic/Object/Update/DockUpdate/SupplyCenterDockUpdateModuleDataConstructorThunk.cpp | `??0RepairDockUpdateModuleData@@QAE@XZ` |
| `??0ToppleUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x00006780 | 0x603790 | 0x2b1060 | game/GameEngine/Source/GameLogic/Object/Update/ToppleUpdateConstructors.cpp | `??0LaserUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0UnpauseSpecialPowerUpgradeModuleData@@QAE@XZ` | 0x00010C80 | 0x2c52e0 | 0x2d99b0 | game/GameEngine/Source/GameLogic/Object/Upgrade/UnpauseSpecialPowerUpgradeModuleData.cpp | `??0SiegeAIUpdateModuleData@@QAE@XZ` |
| `??0UpgradeDie@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0001D3AE | 0x24f860 | 0x2560e0 | game/GameEngine/Source/GameLogic/Object/Die/UpgradeDie.cpp | `??0GrantUpgradeCreate@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0UpgradeDieModuleData@@QAE@XZ` | 0x0000497B | 0x203440 | 0x1256a0 | game/GameEngine/Source/GameLogic/Object/Die/UpgradeDieModuleDataCtorThunk.cpp | `??0Rva00203440@@QAE@XZ` |
| `??0W3DLaserDrawModuleData@@QAE@XZ` | 0x0001BE41 | 0x1fe190 | 0x757960 | game/GameEngineDevice/Source/W3DDevice/GameClient/Drawable/Draw/W3DLaserDrawModuleDataConstructor.cpp | `??0HordeUpdateModuleData@@QAE@XZ` |
| `??0W3DSupplyDraw@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x0001F659 | 0x1f1470 | 0x77db70 | game/GameEngineDevice/Source/W3DDevice/GameClient/Drawable/Draw/W3DSupplyDrawConstructors.cpp | `??0BezierProjectileBehavior@@QAE@PAVThing@@PBVModuleData@@@Z` |
| `??0W3DSupplyDrawModuleData@@QAE@XZ` | 0x0001235A | 0x2bc190 | 0x77dd50 | game/GameEngineDevice/Source/W3DDevice/GameClient/Drawable/Draw/W3DSupplyDrawConstructors.cpp | `??0FirestormDynamicGeometryInfoUpdateModuleData@@QAE@XZ` |
| `??0W3DTankDrawModuleData@@QAE@XZ` | 0x00018322 | 0x299e10 | 0x77ea70 | game/GameEngineDevice/Source/W3DDevice/GameClient/Drawable/Draw/W3DTankDrawModuleDataCtor.cpp | `??0PartTheHeavensUpdateModuleData@@QAE@XZ` |
| `??0WorkerAIUpdateModuleData@@QAE@XZ` | 0x00024BFE | 0x1efd50 | 0x11bf80 | game/GameEngine/Source/GameLogic/Object/Update/AIUpdate/WorkerAIUpdateModuleDataCtorThunk.cpp | `??0BezierProjectileBehaviorModuleData@@QAE@XZ` |
| `??1RAMFile@@MAE@XZ` | 0x00029555 | 0x5d4390 | 0x9d19a0 | game/GameEngine/Source/Common/System/RAMFileDestructorThunk.cpp | `??1SmudgeManager@@UAE@XZ` |
| `?Overlap_Test@CollisionMath@@SA?AW4OverlapType@1@ABVFrustumClass@@ABVAABoxClass@@@Z` | 0x008DB060 | 0x8db060 | 0x8db380 | game/Libraries/Source/WWVegas/WWMath/colmathfrustum.cpp | `?Overlap_Test@CollisionMath@@SA?AW4OverlapType@1@ABVFrustumClass@@ABVSphereClass@@@Z` |
| `?Remove_All@?$SList@VTagBlockIndex@@@@UAEXXZ` | 0x0000B9CE | 0x6731a0 | 0x9edd30 | game/GameEngine/Source/Common/SListTagBlockIndexRemoveAllThunk.cpp | `?reset@NetCommandList@@QAEXXZ` |
| `?Replace_VertexMaterial@MeshModelClass@@QAEXPAVVertexMaterialClass@@0@Z` | 0x00924C30 | 0x924c30 | 0x94f450 | game/Libraries/Source/WWVegas/WW3D2/MeshModelReplaceTexture.cpp | `?Get_User_Text@MeshGeometryClass@@QAEPBDXZ` |
| `?close@File@@UAEXXZ` | 0x000309CC | 0x722190 | 0x9cb880 | game/GameEngine/Source/Common/System/File.cpp | `?ReleaseResources@W3DSmudgeManager@@UAEXXZ` |
| `?getGridResolution@WaterRenderObjClass@@QAEXPAM00@Z` | 0x0001125C | 0x7a2290 | 0x79fbd0 | game/GameEngineDevice/Source/W3DDevice/GameClient/Water/W3DWater.cpp | `?setGridResolution@WaterRenderObjClass@@QAEXMMM@Z` |
| `?getHeightAboveTerrainOrWater@Thing@@QBEMXZ` | 0x00001C30 | 0x131b00 | 0x1324a0 | game/GameEngine/Source/Common/Thing/Thing.cpp | `?getHeightAboveTerrain@Thing@@QBEMXZ` |
| `?setGridChangeAttenuationFactors@WaterRenderObjClass@@QAEXMMMM@Z` | 0x000088F0 | 0x7a0b00 | 0x79faf0 | game/GameEngineDevice/Source/W3DDevice/GameClient/Water/W3DWater.cpp | `?setGridTransform@WaterRenderObjClass@@QAEXMMMM@Z` |
| `??0StealthUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` | 0x00006780 | 0x603790 | 0x2acb70 | game/GameEngine/Source/GameLogic/Object/Update/StealthUpdate_ctor_Thunk.cpp | `??0LaserUpdate@@QAE@PAVThing@@PBVModuleData@@@Z` |
