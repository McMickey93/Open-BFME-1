# grabSinglePlayerInfo: equivalent-branch weighting retry

Target: `?grabSinglePlayerInfo@@YAXXZ`, RVA `0x004E8320`, 1036 bytes.
Matched initSinglePlayer/initReplaySinglePlayer callers route through ILT
`0x000077C5`. RET is at +0x3F3; six switch-table entries occupy +0x3F4..+0x40B;
INT3 begins at +0x40C. Identity and the larger-than-queue extent are unchanged.

The preferred tracked bank emits 1036 bytes, 54 COFF relocations, and 20 masked
byte differences. The remaining differences are counter scheduling/registers
(+0x266..+0x285), units-lost load/receiver lifetime (+0x2BF..+0x2C8), and the
color destination register (+0x2D3/+0x2DD). Calls resolve. The six linear-probe
relocation warnings are jump-table entries, not six displaced calls.

New hypothesis: equivalent branches merged by MSVC can retain different
allocation weights. BFME 2 revision `8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9`,
`docs/recipes.md` and `reverse/attempt_support/damage507d84-recovery-20261022/`
provide this compiler technique only; no BFME 2 grabSinglePlayerInfo body exists
in its Code or function ledger. BFME 1 identity/layout remain supported by the
previous target records, not by this donor technique.

Reproduced baseline, then tested 28 whole-region duplicates and all 63 nonempty
subsets of six load/store sites under four side-effect-free predicates (252
additional trials). Each branch executes the same original operation once.
No result improved 20 differences. Most altered code size or scheduling; the
best subset variants remained identical to the bank. Do not repeat this if/else
weighting matrix under these inputs. The attached generator records the exact
transformations; original bank and production sources were preserved.

Compiler: MSVC 7.1, repository normal optimization settings plus the bank's
`/DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB`, stringbaseascii
shim and WWLib include directories. All experiments used experiment_store's
private hashed object paths, never shared verification objects. No normal byte
gate was claimed: every candidate still fails a byte comparison.

Next prerequisite: a distinct supported explanation for native scalar/receiver
lifetimes or instruction scheduling. Existing counter lifetime, ABI, helper
visibility, flags and statement-order histories remain applicable. Keep the
0.9807 bank; there is no improved source to land from this retry.
