# Next ten queue tasks — 2026-10-22

Ten additional names, excluding the first batch, were selected from the ranked linking queue and claimed before investigation. All ten were attempted sequentially. Three tasks produced source progress, each in its own pushed commit authored by Yannick Molinghen <yannick.molinghen@ulb.be>. Seven produced no new source change; their measured findings were recorded with `tools/re_log.py` and collected with this report.

| # | Task | Brief result | Landed this batch? | Commit |
|---|---|---|---|---|
| 1 | RefHandle cleanup | Suppressing the competing destructor changes two verified EH actions; restored both sources. | No — blocked | — |
| 2 | StringClass constructor | Multibyte mode fixes the standalone constructor but changes its matching caller; no safe TU-local repair. | No — blocked | — |
| 3 | OpenContain removal | Current provider and caller pass their byte gates; saved selection is stale. | No — blocked | — |
| 4 | OpenContain constructor | Competing constructor was already removed upstream; current owner and caller pass. | No — already fixed | — |
| 5 | Image name setter | Removing the obsolete emitter loses a matched placement-delete helper; restored baseline also has an existing comparator relocation failure. | No — blocked | — |
| 6 | Living-world shared-string cleanup | Removed a competing destructor emission while preserving the exact 307-byte update. | Yes — source progress | [0a4cb4954e](https://github.com/Open-BFME/Open-BFME-1/commit/0a4cb4954e603a7689a1d01833efea23fce90270) |
| 7 | Terrain-track vtable | Adopted RefCountClass to restore the missing Delete_This vtable slot; all three constructor/destructor rows remain exact. | Yes — source progress | [4c4394701f](https://github.com/Open-BFME/Open-BFME-1/commit/4c4394701fe097317de11c540074976372fa1bb2) |
| 8 | Special-power finder | Current 96-byte provider passes its byte gate; queued callers only declare it. Wrong copies are in the stale census. | No — blocked | — |
| 9 | Physics motive force | Call targets an unconverted 990-byte native provider, not the 39-byte donor wrapper; identity repair remains blocked. | No — blocked | — |
| 10 | Battle-plan object accessor | Read the witnessed object slot directly, removing the competing accessor while retaining the exact 292-byte update. | Yes — source progress | [b3c5355698](https://github.com/Open-BFME/Open-BFME-1/commit/b3c535569812ca277114ee290b233dce0b94152e) |

## Verification and limits

- `tools/check_csv.py` passed before work. Each of the three source fixes passed its scoped `./build.sh` gate and normal commit/push hooks, without bypasses or baseline additions. The retained task changes cover five verified rows across four translation units: living-world update 307 bytes; terrain-track constructor/destructors 169/109/30 bytes; battle-plan update 292 bytes. The battle-plan gate also verified its five jump-table entries.
- The terrain-track retail table at VA `0x011212A4` has `RefCountClass::Delete_This` before its deleting destructor. Using the existing canonical header restores the emitted table from four to eight bytes without changing the matched body bytes. No shared header was edited.
- Before/after `link_check.py --census-only` previews change living-world update from blocked to `LINKS` (307 bytes), and battle-plan update from blocked to `LINKS` (292 bytes). Terrain-track destructor previews link, but the saved constructor selection remains stale. These previews use the saved `e9a5ae5b4c` index; queue ranking used `2615147aca`. They are not a confirmed current whole-program LINKED gain. The current-check limitation from the first batch (18,056 stale or missing ledger objects and `LINKED PREVIEW UNKNOWN`) remains unresolved.
- No new matched-byte coverage is claimed: these are linker/provider and vtable repairs to already verified bodies. All unsuccessful reconstruction attempts were restored; unrelated `.agents/scratch/` work was preserved.
- The restored MapUtil baseline has a pre-existing AsciiString comparator relocation failure at two call sites. Removing its obsolete map-preview definition additionally drops a matched placement-delete emitter. Neither failure was hidden by changing pins or baselines.
- The adjacent Open-BFME-2 source still has the short, unmatched physics wrapper; it does not supply the native 990-byte BFME 1 provider needed for task 9. No identity or address was imported without BFME 1 evidence.

## Follow-up evidence

The seven unlanded outcomes are in `targets/game/reverse/re_attempts.log`. Task 1 needs handle-cleanup/EH identity reconciliation; task 2 needs compatible ANSI/multibyte constructor emission; task 5 needs the comparator and placement-delete ownership repaired together; task 9 is blocked on `0x0029AC40`. Tasks 3, 4 and 8 need current link-census evidence before further source changes are justified.
