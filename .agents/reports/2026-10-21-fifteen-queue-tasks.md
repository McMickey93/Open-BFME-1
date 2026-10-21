# Fifteen queue tasks — 2026-10-21

After the retry, seven tasks have source repairs, each committed separately as Yannick Molinghen and pushed to origin/master. Three remain partial linking repairs. Eight tasks have no landed repair. The retry retains one newly recovered eight-byte C++ forwarder. Census previews remain separate from whole-game link proof.

The queue was served by `tools/link_check.py next` (published census `b79ddbcd94`), with live claims, in the order below. Rank 25 became available later and was served after rank 65. The local object index is from `e9a5ae5b4c`. Census-only results are previews against that index, not current whole-game link proofs. Full current checks reported over 21,000 unavailable ledger objects, so no full-link byte gain is claimed.

| Queue rank | Task | Outcome | Commit |
| --- | --- | --- | --- |
| 20 | ScoreKeeper object-count transfer | Landed on retry | a1b87e2cbd |
| 22 | Lua Parameter integer setter | Landed, partial | c69091fd70 |
| 47 | Terrain prop draw-module accessor | Landed | 317b73d773 |
| 48 | Shroud provider forwarder | Landed on retry | 47f4f753c3 |
| 50 | OpenContain removal hook | Blocked | — |
| 52 | Vector2 Clear provider | Landed, partial | 5ec04cfdbe |
| 54 | W3D pool allocator | Blocked | — |
| 55 | Buffer destructor duplicates | Landed on retry | bf91f4be3a |
| 64 | OpenContain constructor duplicate | Landed, partial | 1091945d31 |
| 65 | Image name setter | Blocked | — |
| 25 | StringClass constructor | Blocked | — |
| 66 | Living World shared-string destructor | Blocked | — |
| 67 | Terrain tracks vtable | Blocked | — |
| 69 | Special-power lookup | Blocked | — |
| 71 | Physics motive-force provider | Blocked | — |

## Retry after the first pass

Three former blockers landed on the second attempt:

- `47f4f753c3`: the shroud forwarder uses the documented, snapshot-bound name correction in `docs/naming_evidence.md`. The correction pairs exact ledger-row hashes and records both source hashes, with independent caller/callee evidence in `targets/game/reverse/identity_evidence/008f73b0-shroud-forwarder-abi.md`. The name guard stays enabled. Both the eight-byte forwarder and the 395-byte caller byte-match; the caller TU census preview links 402 non-padding bytes.
- `bf91f4be3a`: `Buffer` scope exits retain inline `Reset` calls while imported-forceinline suppresses the incorrect destructor COMDATs. All 15 header dependents were verified: 411 bodies and two data rows pass. Their objects have exactly one native Buffer destructor provider and no imported Buffer destructor references. The false `Buffer` pin at ILT 0x0001A401 was corrected: that thunk actually reaches the four-byte attribute-handle destructor at 0x0039D550. HitReaction's two falsely named Buffer members now use the existing AttributeHandleStandIn type, with both its destructor and cleanup byte-verified. The EH tool re-derived 23 cleanup bindings across five sources. Additional pin-change dependents also passed the normal hooks.
- `a1b87e2cbd`: the ScoreKeeper transfer helper now references the existing address-scoped map provider at 0x000EA510 by its own object symbol. Its original canonical comparator symbol was attached to the refuted body at 0x005D3380, which is why additive pin matching had hidden the link mismatch. A declaration-only specialization emits no competing map body; branch-local key variables preserve the exact retail stack shape. The helper byte-matches and its own census preview now links 332 bytes. No alias or new pin was added.

The first pass stopped too early on these issues: there was a documented guard-correction path, a safe shared-header repair with only 15 dependent TUs, and a concrete wrong template-provider reference to trace. The earlier sections below preserve the first-pass findings; this retry section and the table supersede their blocked outcomes for queues 20, 48, and 55.

Queue 50 has a more precise remaining diagnosis: OpenContain::onRemoving calls ILT 0x00026530 -> 0x002231C0, while its integer-tree find symbol is assigned to the different body at 0x00195120. Resolving that provider identity requires its own repair; no unverified change was retained.

## Evidence and remaining work

### 1. Queue #20: ScoreKeeper object-count transfer

`?xferObjectCountMap@ScoreKeeper@@QAEXPAVXfer@@PAV?$map@PBVThingTemplate@@HU?$less@PBVThingTemplate@@@_STL@@V?$allocator@U?$pair@QBVThingTemplate@@H@_STL@@@3@@_STL@@@Z`

Blocked: helper independently byte-matches; default link preview still selects wrong body and is incomplete because 21691 ledger objects are unavailable (598.9s). No safe minimal source change established.

Queue files: game/GameEngine/Source/Common/RTS/ScoreKeeperXfer.cpp.

### 2. Queue #22: Lua Parameter integer setter

`?friend_setInt@Parameter@@QAEXH@Z`

Replaced competing Parameter::friend_setInt with existing local +8 setter pattern. Callback byte-matches; selected Condition constructor remains. Full current preview is UNKNOWN because 21688 objects are unavailable.

Queue files: game/GameEngine/Source/GameLogic/ScriptEngine/LuaEvaluateCondition.cpp.

### 3. Queue #47: Terrain prop draw-module accessor

`?getDrawModuleInfo@ThingTemplate@@QBEABVModuleInfo@@XZ`

Replaced conflicting ThingTemplate::getDrawModuleInfo emitter with a static local layout accessor. Caller byte-matches; census preview LINKS 397 bytes. No current full-link claim.

Queue files: game/GameEngineDevice/Source/W3DDevice/GameClient/W3DTerrainVisualAddProp.cpp.

### 4. Queue #48: Shroud provider forwarder

`?rva008F73B0@ShroudManager@@QAEXPAVCDEProvider@@0@Z`

Blocked by pre-commit name_regression: generated m -> rva008F73B0 classified as descriptive regression; wrapper and caller both byte-matched, then reverted per gate refusal rule.

Queue files: game/GameEngineDevice/Source/W3DDevice/GameLogic/W3DGhostObjectManagerDoXfer.cpp.

### 5. Queue #50: OpenContain removal hook

`?onRemoving@OpenContain@@UAEXPAVObject@@@Z`

Blocked: OpenContain::onRemoving independently byte-matches 525 bytes; Garrison caller census still flags selected provider. No source change justified by standalone evidence.

Queue files: game/GameEngine/Source/GameLogic/Object/Contain/GarrisonContain_onRemoving.cpp.

### 6. Queue #52: Vector2 Clear provider

`?Clear@?$VectorClass@VVector2@@@@UAEXXZ`

Removed wrong scalar-delete Vector2 Clear emitter from render2d.cpp with a declaration-only specialization. All 14 ledger bodies byte-match; COFF lists Clear as undefined external. Census-only retains old selected-definition facts; full link gain unproven.

Queue files: game/Libraries/Source/WWVegas/WW3D2/PointGroupClassShutdown.cpp.

### 7. Queue #54: W3D pool allocator

`?allocateFromW3DMemPool@@YAPAXPAXH@Z`

Blocked: two-argument allocateFromW3DMemPool provider in unclaimed GameMemory.cpp is pinned to scalar operator new 0x00881F30. NullPrototypeClass W3DMPO glue references it. A verified allocator/ABI repair is required; replacing or redirecting it from the caller would hide the mismatch.

Queue files: game/Libraries/Source/WWVegas/WW3D2/nullrobj.cpp.

### 8. Queue #55: Buffer destructor duplicates

`??1Buffer@@QAE@XZ`

Blocked; tried BFME2 BFME_BUFFER_DTOR_OUT_OF_LINE in both INI emitters. Fails six ini.cpp rows and GetWideString: retail calls Reset at 0x009E1E60 but out-of-line destructor resolves to ILT 0x0001A401. Both edits reverted.

Queue files: game/Libraries/Source/WWVegas/WWLib/buff.cpp.

### 9. Queue #64: OpenContain constructor duplicate

`??0OpenContain@@QAE@PAVThing@@PBVModuleData@@@Z`

Removed unclaimed Zero Hour constructor from OpenContain.cpp. All 18 ledger bodies byte-match; COFF has no constructor definition. Existing constructor provider remains flagged wrong; no full link gain.

Queue files: game/GameEngine/Source/GameLogic/Object/Contain/GarrisonContainCtor.cpp, game/GameEngine/Source/GameLogic/Object/Contain/OpenContainConstructorThunk.cpp.

### 10. Queue #65: Image name setter

`?setName@Image@@QAEXVAsciiString@@@Z`

Blocked: wrong competing Image::setName comes from MapUtil.cpp using inline upstream Image.h; its retail owner is INIMappedImage.cpp. Requires shared Image header/caller repair; census also flags ImageCollection::addImage. No minimal safe local emitter removal established.

Queue files: game/GameEngine/Source/Common/INI/INIMappedImage.cpp.

### 11. Queue #25: StringClass constructor

`??0StringClass@@QAE@PBD_N@Z`

Blocked: MissingTexture emitter uses the correct MBCS constructor; DX8 callback uses non-MBCS inline constructor and emits a wrong shared COMDAT. Tried /D_MBCS on DX8ErrorTranslator.cpp; callback no longer byte-matches because retail inlines strlen while shared constructor uses _mbslen. Reverted. BFME2 solves this with header switches not present here; needs separated inline/native constructor support.

Queue files: game/GameEngineDevice/Source/W3DDevice/GameClient/Shadow/MissingTextureClassCtorThunk.cpp, game/Libraries/Source/WWVegas/WW3D2/DX8ErrorTranslator.cpp.

### 12. Queue #66: Living World shared-string destructor

`??1BfmeSharedString@@QAE@XZ`

Blocked: all five BfmeSharedString destructor copies are wrong against pin 0x00887940 (canonical StringBase<char>::releaseBuffer). Local partial types differ; a declaration-only change would introduce calls to an unresolved/wrongly selected public destructor. Broader identity/ABI consolidation needed.

Queue files: game/GameEngine/Source/Common/Rva00363050LivingWorldEntryUpdate.cpp.

### 13. Queue #67: Terrain tracks vtable

`??_7TerrainTracksRenderObjClass@@6B@`

Blocked: ctor references full retail TerrainTracks vtable, while dtor partial class emits only destructor slots. Dtor itself census-previews LINKS 138 bytes but ctor remains blocked by wrong table. Full table/ABI reconstruction needed, not a guessed local vtable.

Queue files: game/GameEngineDevice/Source/W3DDevice/GameClient/TerrainTracksRenderObjClassCtor.cpp, game/GameEngineDevice/Source/W3DDevice/GameClient/TerrainTracksRenderObjClassDtor.cpp.

### 14. Queue #69: Special-power lookup

`?findSpecialPowerTemplate@SpecialPowerStore@@QAEPBVSpecialPowerTemplate@@VAsciiString@@@Z`

Blocked: callers already use canonical findSpecialPowerTemplate. Shared upstream inline wrapper has seven competing emitter TUs (InGameUI/INI/ScriptActions/SpecialPower/ScriptConditions). Needs coordinated header and all dependent verification; no safe caller-only repair.

Queue files: game/GameEngine/Source/Common/RTS/Rva000C5EF0ActionManager.cpp, game/GameEngine/Source/GameLogic/ScriptEngine/ObjectDoSpecialPower.cpp.

### 15. Queue #71: Physics motive-force provider

`?applyMotiveForce@PhysicsBehavior@@QAEXPBUCoord3D@@@Z`

Blocked: retail 0x0029AC40 is a 990-byte BFME body, not the short ZH applyMotiveForce wrapper. BFME2 still carries the short ZH version as present-unmatched. PhysicsUpdate.cpp exports that wrong unclaimed provider; a full body recovery is required.

Queue files: game/GameEngine/Source/GameLogic/Object/Object_rva001C7CF0.cpp.

## BFME-2 findings

- `Code/GameEngine/Source/Common/RTS/ScoreKeeper.cpp` confirms the transfer structure but does not resolve the linking-provider dispute.
- `Code/GameEngine/Source/GameLogic/Object/PartitionManagerShroudThunks.cpp` supplies the analogous shroud forwarder; BFME-1 uses an implementation pointer at +0x0c rather than +0x10. The recovered eight-byte BFME-1 wrapper and its caller both byte-matched. The first attempt was reverted after the name guard refusal; the retry landed through the documented exact-snapshot correction process.
- BFME-2 WWLib `ini.cpp` uses `BFME_BUFFER_DTOR_OUT_OF_LINE`. Porting that switch breaks seven BFME-1 matched rows across two files: retail calls `Buffer::Reset`, while declaration-only destruction resolves to a different pinned entry. Both edits were reverted.
- BFME-2 uses separate native/inline `StringClass` header switches. BFME-1 lacks those switches. Enabling MBCS for the DX8 callback fixes one constructor context but breaks the callback itself; reverted.
- BFME-2 still carries the short Zero Hour `applyMotiveForce` body as present-unmatched; it is not an already recovered equivalent of BFME-1's 990-byte body.

## Validation

- Initial and final CSV integrity checks pass. Final restoration check: all 209 bodies across WWLib ini.cpp, INIClassGetWideString.cpp, and DX8ErrorTranslator.cpp byte-match.
- Scoped byte checks and normal commit/pre-push hooks for every retained source change: Lua callback (1 body), terrain addProp (1), render2d (14), OpenContain (18).
- The initial shroud wrapper attempt was reverted after name_regression refused it; the retry passed that guard with tracked independent evidence and a snapshot-bound correction, then landed.
- Actual object-symbol inspection confirms render2d references Clear externally and OpenContain.cpp does not define the removed constructor.
- Every attempted source edit that failed byte verification or a guard was reverted. Outcomes were appended with `tools/re_log.py record`.
- GitHub port-22 SSH began resetting connections; subsequent Git operations used ssh.github.com:443 with HostKeyAlias=github.com to retain host-key verification.
- Pre-existing untracked `.agents/scratch/` was preserved.
