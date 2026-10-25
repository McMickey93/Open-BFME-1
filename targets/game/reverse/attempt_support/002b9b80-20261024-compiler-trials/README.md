# Dozer aiDoCommand: correct receivers still block C++ replacement

RVA 0x002B9B80, 330 bytes. Existing MASM remains unchanged and byte-exact.
See identity_evidence/002b9b80-masm-codegen-blocker.md for identity, boundary,
relocations and prior trials. The historical 329/330-byte agreement is INVALID:
its resume idle call receives the complete object instead of the secondary
AICommandInterface at complete+0x20. Do not land that historical source.

The attached flags_00.cpp.txt fixes the receiver and emits 330 bytes / 7 calls,
but has 40 non-relocation byte differences: register assignment and the
prologue's push/move schedule. This session did not improve that correct body.

## New measurements

Compiler MSVC 13.10.3077, repository default flags plus each source's cl line;
private objects, no game source changes. Results JSON records sizes and masked
byte differences, not relocation proof or a claim of semantic equivalence.
Sources accompanying tables are representative trials, not landed code.

- flags: O1/Os shrink to 279 B, G7 gives 328 B, Og- gives 487 B;
  normal O2/G6, Ob1, Ot, Oa/Ow and exception-mode variants retain 330/40.
- CPU scheduling G3/G4/G5, Oi-, Op, GF/Gy/GT, Og, Ob1 with Ow and Ob2
  with Oa also retain 330/40; Og- changes the structure without improvement.
- Equivalent integer forms of complete+0x20 and four shared forceinline
  receiver/task/object accessors (15 combinations) all retain 330/40.
- A raw-secondary-entry class avoids implicit this adjustment but changes
  lifetime allocation: 331 B, 216 differences. Moving the complete receiver
  after model-condition clearing or repeating the rebase did not fix it.
- Named paired receiver PODs and parameter references emitted 338-341 B.
- Returns versus breaks, command/task temporaries and qualified versus
  unqualified idle calls retain 330/40. Short-circuit otherObj && isKindOf
  instead of the original bool assignment gives 330/51.
- Forceinline idle wrappers taking the complete object retain 330/40.
  Pointer/reference interface wrappers, member-pointer invocation and local
  interface variables grow to 337 or 348 B; they do not solve allocation.
- Valid non-null contracts on this/parms do not improve these results.
- Explicit primary field views for object/task/machine accesses give
  329-342 B or the same 330/40; no exact body.

Remaining hypothesis space must address allocation with BOTH correct idle
receivers. More arithmetic spelling changes and the listed flags have no
support as useful next steps. This does not prove C++ recovery impossible.

BFME 2 donor reviewed: Code/GameEngine/Source/GameLogic/Object/Update/AIUpdate/
DozerAIUpdateCtor.cpp, aiDoCommand implementation, plus docs/recipes.md.
Both repair and resume use inherited aiIdle; the donor supports the receiver
correction but not BFME 1's exact register schedule. Existing createMachines
at 0x002B7B20 is already recovered; it is not a new dependency landing.

Reviewed donor revision: 47da7755f19649ecee722513c2ce672dce22fb3a

## Complete experiment log

`trial_logs.json` preserves every private C++ variant in this session (185 trials), its source patch against `flags_00.cpp.txt`, available compiler diagnostics, object hash, relocation list and exact non-relocation difference offsets. Missing logs are explicitly null; they are not invented. Object files remain private build outputs. Patches plus the baseline reconstruct each source. These are compile/byte comparisons, not runtime equivalence tests.

Source specimens use `.cpp.txt` because they are attempt evidence, not game translation units. `base_original_source` in the log preserves the exact baseline text used to construct all source patches and hashes.
