# Queue tasks — 2026-10-22

Fifteen tasks were taken from the repository linking queues: the first open ranked name and fourteen `serve` packets from `link_check.py near`. Each was claimed before its attempt. Work was sequential; unrelated `.agents/scratch/` files were preserved.

Five task commits contain byte-verified source progress: three complete local repair packets and two partial repairs. Ten task commits preserve measured blockers without changing their already matching game bodies. Every task has its own commit authored by Yannick Molinghen <yannick.molinghen@ulb.be>.

| # | Task | Brief result | Outcome | Commit |
|---|---|---|---|---|
| 1 | ExperienceLevel assignment | Current assignment owner matches; saved selection verdict is stale. | Blocked — report only | This commit |
| 2 | Game-browser array request | Constructor repaired; callback retirement guard still blocks. | Partial — pushed | [238903d1d4](https://github.com/Open-BFME/Open-BFME-1/commit/238903d1d4) |
| 3 | Game-browser host slot | Constructor and complete cleanup call the verified providers. | Landed | [e6ae210bb9](https://github.com/Open-BFME/Open-BFME-1/commit/e6ae210bb97b7d46d1c6662b500f570658087640) |
| 4 | Texture-handle table forwarders | Two return adapters change hidden-result forwarding. | Blocked — report only | [2f060dcd88](https://github.com/Open-BFME/Open-BFME-1/commit/2f060dcd88415c57e20f7dc8f9999ec724223070) |
| 5 | Two-handle buffer constructor | Buffer construction and handle cleanup bind to their providers. | Landed | [cae794d585](https://github.com/Open-BFME/Open-BFME-1/commit/cae794d585679961b45092c71a2a7ef22af05f60) |
| 6 | Static EAStringC array | Constructor identity recovered; array lifetime providers repaired. | Landed | [402f934de1](https://github.com/Open-BFME/Open-BFME-1/commit/402f934de13c935710fdd88fe9123e08705da251) |
| 7 | Skirmish profile forwarder | Three calls repaired; saved census still flags levelBar selection. | Partial — pushed | [2483354a03](https://github.com/Open-BFME/Open-BFME-1/commit/2483354a03644ae1449c8aa851316d8f9a750510) |
| 8 | BfmeHolderCU wrapper | Destructor forwarding adds six bytes; class reconciliation needed. | Blocked — report only | [e5427bbb89](https://github.com/Open-BFME/Open-BFME-1/commit/e5427bbb8938bec46e4c535fe1ee08be5821adb0) |
| 9 | BeaconClientUpdate wrapper | Destructor forwarding adds six bytes; class reconciliation needed. | Blocked — report only | [bbfd482f07](https://github.com/Open-BFME/Open-BFME-1/commit/bbfd482f07eda1aed49e2db9a6bb7e7288bfbb38) |
| 10 | AIBackAwayAndCowerState wrapper | Destructor forwarding adds six bytes; class reconciliation needed. | Blocked — report only | [3729f2a8b4](https://github.com/Open-BFME/Open-BFME-1/commit/3729f2a8b4ab13a2565651d9671cb9515762f222) |
| 11 | AIFollowPathAsTeamState wrapper | Destructor forwarding adds six bytes; class reconciliation needed. | Blocked — report only | [c06a81effc](https://github.com/Open-BFME/Open-BFME-1/commit/c06a81effc083884c198ab9c37942892220ef249) |
| 12 | ObjectGuardingHelper wrapper | Destructor forwarding adds six bytes; class reconciliation needed. | Blocked — report only | [b55429256c](https://github.com/Open-BFME/Open-BFME-1/commit/b55429256cd776f50e69c01ee3766c7c822168c5) |
| 13 | DelayedWorldTextEventModule wrapper | Destructor forwarding adds six bytes; class reconciliation needed. | Blocked — report only | [b80799b4de](https://github.com/Open-BFME/Open-BFME-1/commit/b80799b4deb018ce2f566721ebe8eb24a44764f4) |
| 14 | ActiveBody wrapper | Destructor forwarding adds six bytes; class reconciliation needed. | Blocked — report only | [ecddd5cac9](https://github.com/Open-BFME/Open-BFME-1/commit/ecddd5cac9bdbd3f10b4264a64152cd803b82dd3) |
| 15 | CreateCrateDie wrapper | Destructor forwarding adds six bytes; class reconciliation needed. | Blocked — report only | [b90a03a041](https://github.com/Open-BFME/Open-BFME-1/commit/b90a03a0414479509782c371e1e556e4e31fa616) |

## Verification and limits

- `tools/check_csv.py` passed before work. Normal commit and push hooks ran; no hook was bypassed and no baseline was expanded.
- Every source repair passed `./build.sh` against retail, including its call targets and DIR32 checks. The EAStringC repair verified all eleven rows in its three affected translation units and passed `pin_consistency.py --check`. The separately checked levelBar provider also passes its current byte gate.
- The saved-census previews succeed for host-slot registration (286 bytes), the buffer constructor (71 bytes), and the EAStringC array initializer/cleanup (62 bytes). These are saved-census predictions, not a confirmed current LINKED gain.
- A normal current `link_check.py --compile-limit 0` check reports `LINKED PREVIEW UNKNOWN`: 18,056 new/changed ledger objects cannot be read in this checkout. No current LINKED-byte increase is claimed.
- Task 2 retains one callback blocker: `dir32_record.py retire` refuses the corrected callback signature because its unchanged bare identifier remains in the callback provider and caller. The refusal was recorded as required; it was not bypassed.
- Task 4 independently failed both direct result-copy and member-pointer return adapters. The original 43-byte twins were restored.
- Each of tasks 8–15 independently compiled a native inline complete-destructor forwarding attempt (36 bytes versus retail 30). A second `novtable` attempt emitted no deleting-wrapper symbol. These tasks need proven class/provider identity reconciliation; all original game bodies remain. For CreateCrateDie the probe uses its ledger object-symbol (`??_GGen_dtor_00253f60@@UAEPAXI@Z`), preserving the authenticated row identity. The per-boundary verdicts are in `targets/game/reverse/re_attempts.log`, written with `re_log.py`.
- Task 1's current ExperienceLevel copy/assignment provider passes both byte checks; its sole saved provider is nevertheless marked wrong by the old selection census. No unsupported code change was made. A fresh current census is required to settle selection.

## BFME 2 evidence reused

The BFME 2 inline/imported-provider pattern avoids emitting a competing local inline constructor in task 5. Its native EAStringC default constructor in `Code/Libraries/Source/Apt/AptValue/AptValueUrlEncode.cpp` supplies the same empty-singleton/refcount pattern used in task 6. BFME 1 identity is independently tied to its paired native destructor and static array lifetime; BFME 2 addresses and folding assumptions were not imported. The exact constructor proof is in `targets/game/reverse/identity_evidence/2026-10-22-00891b40-eastring-default-constructor.md`.
