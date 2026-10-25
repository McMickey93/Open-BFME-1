# 0x007E8B00 conditional separator reads

The saved body remains a partial. It emits the full 549-byte retail extent with 172 non-relocation byte differences and four relocation sites displaced from their retail operands. The original saved body emitted 544 bytes with 183 differing emitted bytes and five missing bytes, giving a lower bound of 188 wrong bytes. These are the probe's positional masked-byte measurements, not acceptance results. The strict scoped byte gate is red.

The new hypothesis was that the separator read at +0x1F9 must remain conditional on the byte check at +0x1F3, followed by the separate else-arm read at +0x20F. A volatile access view limited to the separator condition reproduces both reads and adds the missing relocation site. The same view limited to the else-arm load produces the same instructions. This differs from the prior whole-global volatile and const experiments. The declared separator remains a signed char. The best body adds no assembly, helper definition, pin, shared declaration, or new identity.

## Boundary, identity and ABI

The tested revision is 93c031d5ef142cd1d1a85c386da11db2da6c8af4 with the retail-1.03-unpacked baseline. The ledger still assigns ?d_007e8b00@@YAXXZ to game/gen_asm/d_007e5080.asm. The repository's dump predicate returns true. All fourteen prior verdicts and all eight pre-existing immutable saved reconstructions were inspected. After normalizing line terminators for comparison only, those reconstructions differ in score/date headers or the pValue/pTail assignment order; their raw JSON files remain untouched.

The complete decoded target has returns at +0x0B, +0x195, +0x1AE, +0x20E, +0x21F and +0x224. Its final RET is followed by eleven INT3 bytes before the next body at 0x007E8D30. Every conditional branch stays inside the extent; there is no outgoing tail jump. Raw decoding and the checked-callee inventory are in build/fesl-007e8b00/decoded-target-caller.log and build/fesl-007e8b00/checked-target.log.

The complete 317-byte caller at 0x007E8D30 pushes the constructed field pointer, the buffer size and the record pointer, calls this body at caller +0x11D, and cleans twelve stack bytes. Its inputs to this call are three four-byte stack slots in record, size, field order. It preserves the four-byte EAX result, later returns it, and its member caller interprets a negative result as failure. The target returns without stack cleanup. There is no receiver adjustment or hidden return storage. The caller's own private register convention does not carry across this call. The complete member caller at 0x007E8EF0 tests EAX and uses JGE for success; its raw decode and inventory are in build/fesl-007e8b00/decoded-member-caller.log and build/fesl-007e8b00/checked-member-caller.log. The independent differential harness calls retail through the same three-argument cdecl declaration.

Both outgoing calls reach the complete six-byte stub at 0x009F6EC6, which jumps through IAT VA 0x0135945C. The PE import table identifies that entry as MSVCR71.dll!memmove. The source uses the canonical destination, source, unsigned count declaration with a pointer result; this target ignores the result at both sites. The _memmove pin is independently consistent. Complete stub decoding and its checked inventory are in build/fesl-007e8b00/decoded-import.log and build/fesl-007e8b00/checked-import.log. The import identity and actual compiler command are in build/fesl-007e8b00/identity-abi.log. No new pin is needed.

All accesses to the class table at VA 0x011295B0 use MOVZX byte indices, including the first field byte and every subsequent field byte. The class payloads are bytes and their sum is promoted before comparison with two. Separator comparisons against buffer bytes use MOVSX for the separator at VA 0x012C37EE. The bank follows those observed widths. The landed Y4TextToValue.c donor was read directly: its signed field-table indexing differs from this target and is not type evidence for this copy. There is no STL value type, object construction, ownership cleanup, or exception-unwind state in this body.

The only direct caller names the dump through an address-qualified function-pointer view. No independent real function name or owner is established. _Rva007E8B00 remains the bank's actual emitted symbol and is retained unchanged. The oracle's direct body-RVA API returns UNTESTABLE because this is an address placeholder, which is the intended naming form. The external table and separator spellings remain the existing bank names; their future DIR32 recording is not claimed by this partial.

## Remaining differences

Retail saves EBX at +0x12, ESI and EDI at +0x29, and EBP at +0x157. It preserves pValue in EBX and counts iLength in EBP. The candidate preserves pValue in EBP and counts iLength in EBX, forcing the extra EBP save at +0x29. This shifts the first scan, its stack offsets, relocation operands and branch displacements. The class loop rejoins at the same aligned offset +0xB0 after different padding. The counter loop uses different padding at +0x15E/+0x15F and the mapped SIB at +0x161 reverses addition operands. The resulting restore order differs at the capacity failure, no-change return, and final-byte branches. The separator's two conditional reads now match the retail instruction positions. No missing callee or unresolved ABI explains this remaining byte failure.

Every remaining positional difference is retained in build/fesl-007e8b00/separator-guard-volatile-diffs.json. Its emitted-byte ranges are +0x029..+0x04C, +0x051..+0x067, +0x069..+0x06F, +0x072..+0x085, +0x08A..+0x08F, +0x091, +0x096..+0x09A, +0x09F..+0x0AE, +0x0EC, +0x0F1, +0x0F6, +0x102, +0x116, +0x11D, +0x126, +0x133, +0x13C, +0x14F, +0x156..+0x160, +0x163, +0x167, +0x169, +0x18E..+0x190, +0x19F, +0x1A1, +0x1A8..+0x1AA, +0x1CB, +0x1D0, +0x1D4, +0x1E2, +0x1E9, +0x202..+0x20C and +0x214..+0x21D. There are no missing bytes. The complete raw instruction comparison and value-register mapping are in build/fesl-007e8b00/candidate-difference-map.log. Mapping registers is diagnostic only and does not waive a gate difference.

## Measured experiments

Each named source and its unedited probe output is retained under build/fesl-007e8b00 as NAME.cpp and NAME.log. The baseline source is copied to pristine-bank.cpp. The following lower bound counts differing emitted bytes plus any missing or extra bytes. A result with displaced relocations remains unsuitable for acceptance even where a mask removes its address bytes.

| Experiment | Emitted bytes | Wrong, missing or extra bytes |
|---|---:|---:|
| baseline | 544 | 188 |
| visible-caller-external-crt | 544 | 188 |
| visible-caller-static-crt | 544 | 188 |
| unsigned-char-mode | 528 | 465 |
| unsigned-field-pointer | 544 | 188 |
| scan-span | 544 | 188 |
| scan-span-return | 528 | 402 |
| overlay-first-byte | 544 | 188 |
| compare-while | 544 | 188 |
| compare-do | 530 | 484 |
| search-while-fixed | 488 | 469 |
| tail-duplicate-return | 544 | 188 |
| tail-zero-early-return | 544 | 188 |
| scan-out-pTail | 461 | 494 |
| scan-out-pValue-fixed | 460 | 495 |
| separator-guard-volatile | 549 | 172 |
| separator-store-volatile | 549 | 172 |
| tail-inline-joined | 466 | 491 |
| tail-inline-per-exit | 928 | 862 |
| tail-zero-store-volatile | 549 | 172 |
| tail-separator-store-volatile | 549 | 172 |
| tail-both-stores-volatile | 549 | 172 |
| debug-symbols | 549 | 172 |
| prepared-best | 549 | 172 |

Actual caller visibility with proper C CRT linkage does not change the bank's instructions. C++ CRT prototypes without C linkage introduce two non-retail calls and are rejected separately. A local scan-span aggregate leaves the bank unchanged; returning that span delays the EBP save to the scan join but drops the retail predecessor copies. Output-parameter scans merge code and move the early failure branches. The uncorrected pValue output trial is a C compile failure because the bank's pValue has register storage; its raw diagnostics are in build/fesl-007e8b00/invalid-trial-diagnostics.log. The first search-while transformation mistakenly changed an inner break into a scan exit and is excluded as invalid; the corrected source is the measured search-while-fixed trial.

The class-loop while form, duplicate returns, volatile final-byte stores and optimized /Zi metadata do not change their respective starting bodies. The do-loop and outer search-loop forms change the retail control structure. Expanding the complete tail once per scan exit retains repeated tails rather than merging to retail. A whole-TU /J control removes the retail separator's signed promotion and is rejected for that reason; changing only the field pointer to unsigned leaves the bank unchanged. The optimized compiler listing is retained in build/fesl-007e8b00/debug-symbols.cod. Prior declaration-order, pointer-order, counter-width and ordinary processor-flag experiments were not repeated. The loop/branch and register/copy/SIB generators returned no applicable choices for these source forms; their raw outputs are in build/fesl-007e8b00/structural-choices.log and build/fesl-007e8b00/remaining-family-choices.log.

## Verification and reopening

One independently executed differential run passed 28,580 cases. It compared return values and all 512 bytes of each test buffer against relocated retail instructions using the actual class-table bytes and the runtime CRT memmove. The matrix includes empty and repeated fields, append syntax, whitespace and control-byte endings, high-bit field bytes, growth and shrinkage, negative and small capacities, ten separator values, and null guards. It is a case-limited behavioral check, not a byte-match certificate or a concurrency claim. The generator, generated C harness, compile command receipt and raw result are retained in build/fesl-007e8b00/runtime_compare.py, build/fesl-007e8b00/runtime-harness.c, build/fesl-007e8b00/runtime-receipt.json and build/fesl-007e8b00/runtime-result.log. The candidate was linked from its separately compiled probe object.

The scoped byte gate fails this candidate, with raw output in build/fesl-007e8b00/scoped-byte-gate.log. The initial CSV check and full pin-consistency check pass in build/fesl-007e8b00/check_csv-initial.log and build/fesl-007e8b00/pin-consistency.log. The source-level naming comparison uses the repository name_regression.regressions core because this revision's CLI accepts Git revisions rather than source-path pairs; the rejected CLI invocation is also preserved. The class gate passes without a private class declaration. No full gate is required for an unlanded bank with no shared-header change.

Reopening requires a new, evidence-based source structure that changes the pValue/iLength interference while preserving the three-stack-argument ABI, unsigned class reads, early guards and predecessor pointer copies. The current experiments establish a remaining register/save-schedule mismatch, not a proof that assembly is necessary. Keep the improved conditional separator reads when testing that next hypothesis. No source recovery, ledger conversion, identity correction or new pin is claimed here.

The preferred bank was re-probed after tools/re_log.py recorded exactly one partial row. It retains the measured body and the strict byte failure in build/fesl-007e8b00/banked-probe.log and build/fesl-007e8b00/banked-byte-gate.log. The final CSV check passes in build/fesl-007e8b00/check_csv-final.log. Both newly retained archive hashes were verified against their complete source bytes; the old archive equals the pristine bank and the new archive equals the preferred bank. The final audit and measured completion time are in build/fesl-007e8b00/final-audit.log and build/fesl-007e8b00/completion-receipt.json. The attempt log changed by exactly one added row. The repository recorder emits CRLF; the whitespace check passes when CR is recognized as part of the line terminator, as recorded in build/fesl-007e8b00/diff-check-crlf.log. No compiler, linker, runtime harness or PDB helper remained in the checkout at the final process check in build/fesl-007e8b00/background-final.log.

## Donor resolution (2026-10-24)

The reopening condition above is met by the BFME 2 FESL clean-room unit
`Code/GameEngine/Source/GameNetwork/Rva007E8D30FeslSetField.cpp` at donor
revision `ce1b975697c2f20e514174e3875f8820d1dba612`, whose `Rva007E8B00`
body is recorded at donor RVA `0x00655B90` (549 bytes). Its linked donor body
is exact against the BFME 1 target outside the relocation fields, and the donor
source compiled with `/O2 /G6 /GS /MD` and the BFME 1 data names
`g_Va011295B0` (class table) and `g_Va012C37EE` (separator) emits the full
549-byte BFME 1 body with 11 relocation sites and no differences outside them.

The donor's equivalent clear paths and volatile separator read are the
structure this file asked for: retail's late EBP save and the EBX value
pointer appear without another register or flag experiment. The landed TU is
`game/GameEngine/Source/GameNetwork/Rva007E8B00FeslSetField.cpp`; the
address-derived symbol `?Rva007E8B00@@YAHPAEHPBD@Z` is retained because the
only caller names the dump through an address-qualified function-pointer view
and the donor name is likewise address-derived. The 544-byte bank is
superseded, not amended.
