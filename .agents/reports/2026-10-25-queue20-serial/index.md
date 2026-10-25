# Twenty queue tasks — 2026-10-25

17 verified source repairs; three blockers with committed evidence. Each task has its own commit authored Yannick Molinghen <yannick.molinghen@ulb.be>. No subagents were used.

Contents: [Outcomes](#outcomes) · [Verification](#verification) · [Machine-readable results](results.json)

## Outcomes

“Source repair” means the source/ledger change passes its scoped byte gates. It does not claim a complete unit now links. Publication is verified separately at session completion.

| # | Queue task | Result | Change / blocker | Commit |
|---:|---|---|---|---|
| 1 | ObjectTypesTemp constructor | Source repair landed | Rehome verified constructor; remove standalone duplicate. | [3d75395d50](https://github.com/Open-BFME/Open-BFME-1/commit/3d75395d500b215ea01222c50b762bfb3f7267f9) |
| 2 | ActiveBody damage | Source repair landed | Remove obsolete unmatched damage provider. | [8498595355](https://github.com/Open-BFME/Open-BFME-1/commit/8498595355ac26a35c80d1ba5029ba09e7ad2f36) |
| 3 | Team experience callback | Blocked; evidence committed | Native ABI proved; DIR32 refuses the recorded callback name change. | [9af1220741](https://github.com/Open-BFME/Open-BFME-1/commit/9af1220741fc7b6d6d87a5263ce7471fa4366e93) |
| 4 | Force-attack getter | Source repair landed | Read witnessed field; suppress competing getter. | [a799db2660](https://github.com/Open-BFME/Open-BFME-1/commit/a799db26608d3bb13fff5ec7260372844ff5c6fd) |
| 5 | Trainability getter | Source repair landed | Read witnessed field; suppress competing getter. | [5556ba29c0](https://github.com/Open-BFME/Open-BFME-1/commit/5556ba29c0a2df841c1cf6be6ac4a34076c57b60) |
| 6 | System timer getter | Source repair landed | Preserve elapsed-time logic without emitting wrong Get copy. | [164410da4f](https://github.com/Open-BFME/Open-BFME-1/commit/164410da4f90bb9156c8215a4d3c562cc0d8f9ec) |
| 7 | ATL critical-section Init | Source repair landed | Speed-optimize header inline; retain size-optimized constructor. | [5d1bf8c0cb](https://github.com/Open-BFME/Open-BFME-1/commit/5d1bf8c0cb76db8eedddadea0c8b5cf45b24382e) |
| 8 | Packed boolean equality | Source repair landed | Rehome equality; bind canonical STLport equal. | [7b900aa1a2](https://github.com/Open-BFME/Open-BFME-1/commit/7b900aa1a2786133a42102f0fce7827abee57776) |
| 9 | Q4 heap comparator | Source repair landed | Bind native comparator; avoid wrong helper instantiation. | [55448f11d9](https://github.com/Open-BFME/Open-BFME-1/commit/55448f11d9b5ffc81b18ff1fccfbe5c012431ae2) |
| 10 | STLport spin lock | Source repair landed | Bind exchange and sleep to native providers. | [f8f8ee2753](https://github.com/Open-BFME/Open-BFME-1/commit/f8f8ee275384a994d0722640f2c0fd650b3fbf88) |
| 11 | Weapon factory | Source repair landed | Use protected native constructor contract. | [49cf4d91b7](https://github.com/Open-BFME/Open-BFME-1/commit/49cf4d91b740bd7b677974cde8d5fe13728cc9cc) |
| 12 | Triangle rendering duplicate | Blocked; evidence committed | Removal loses two native constructor EH cleanup providers; restored. | [18557fdec5](https://github.com/Open-BFME/Open-BFME-1/commit/18557fdec55e5a69146f60bea5e7782041bb8bd6) |
| 13 | Outer AI guard update | Source repair landed | Remove obsolete duplicate; retain native update. | [209c665a9b](https://github.com/Open-BFME/Open-BFME-1/commit/209c665a9b92e1b25f94d90ca950bc4bfebb1cd7) |
| 14 | AI structure repair | Source repair landed | Remove obsolete duplicate; retain native repair body. | [68447c93cb](https://github.com/Open-BFME/Open-BFME-1/commit/68447c93cb6dfdf3e0da80bc7a3a0f3de2a8fb0f) |
| 15 | Player-leave accessor | Source repair landed | Rehome exact getter with game-over caller. | [8fa104a5be](https://github.com/Open-BFME/Open-BFME-1/commit/8fa104a5bee26cac3d943c23e94d51b63bc9239d) |
| 16 | Template asset visitors | Source repair landed | Bind both wrappers to native template lookup. | [3c271f0d61](https://github.com/Open-BFME/Open-BFME-1/commit/3c271f0d61a45f219afafc3d02701f25e6e5f240) |
| 17 | Guarded asset visitor | Source repair landed | Bind guarded wrapper to native template lookup. | [73b9e30533](https://github.com/Open-BFME/Open-BFME-1/commit/73b9e305334d13c34f89dea20dd163495f518cc8) |
| 18 | Tree insertion forwarder | Source repair landed | Bind native tree insertion while preserving argument lifetime. | [b3979ab9ae](https://github.com/Open-BFME/Open-BFME-1/commit/b3979ab9aec24044669123462c75ff7fd84d2748) |
| 19 | Shrub insertion forwarder | Source repair landed | Bind native shrub insertion while preserving argument lifetime. | [120297a675](https://github.com/Open-BFME/Open-BFME-1/commit/120297a675aa57d7d1b9028490a19cf246094304) |
| 20 | Armor-upgrade constructor | Blocked; evidence committed | Shared 90B initializer is distinct from full module constructor; donor/layout evidence recorded. | This commit |

## Verification

All retained source changes passed the normal scoped build, byte, relocation, constant/string and DIR32 checks, plus normal commit hooks. Representative provider/consumer batches: ObjectTypesTemp 2/2; ActiveBody 28/28; timer 5/5; ATL 3/3 plus independent alternate-copy comparison; boolean equality 3/3; Q4 heaps 7/7; spin lock 3/3; Weapon 3/3; guard states 13/13; AI repair 35/35; player-leave accessor 4/4; tree pair 2/2; shrub pair 3/3. The reverted DX8 trial passed 122/124; restoring it passes 124/124. No near-matching source remains.

Link previews during editing reported UNKNOWN because the donor gitlink differed from the staged snapshot. Current global selection also depends on unavailable/stale census objects. No linked-byte increase is claimed; inspect a refreshed census before counting gains. Some tasks remove one competing emitter while other family providers remain. These are verified source/linking repairs, not new recovered-byte claims.

The three unresolved tasks have tracked handoffs under `targets/game/reverse/attempt_support/`: [callback](../../../targets/game/reverse/attempt_support/20261025-team-refresh-callback.md), [triangle cleanup](../../../targets/game/reverse/attempt_support/20261025-dx8-buffer-triangles-link.md), and [upgrade identity](../../../targets/game/reverse/attempt_support/20261025-armor-upgrade-identity.md).

BFME2 donor was updated from reviewed checkout47da7755f1 to official beed8a16790a6812231ac7b05e3e6893e4cb5d1b. The old checkout is retained at donor-local `refs/donor-history/20261025-before-queue20`. The task20 donor source is unchanged; its private compile and scan/match were refreshed:42B constructor, zero BFME1 placements. This is discovery evidence, not recovery. BFME1 build inputs were not redirected to the donor.

Existing untracked `.agents/reports/2026-10-24-queue25-dispatch/` and `.agents/scratch/` were preserved.
