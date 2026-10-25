# 0x00346D60 successful compiler-matching evidence

The parent is recovered as native C++ in
`game/GameEngine/Source/GameLogic/ScriptEngine/ScriptEngineSequentialScripts.cpp`.
See `../../identity_evidence/00346d60-sequential-scripts.md` for target identity,
layout, donor provenance, boundary and the existing erase provider reconciliation.

VS2003 compiler 13.10.3077; effective build defaults plus source cl flags:
/O2 /MD /EHsc /DNDEBUG /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS;
canonical local ascii_string.h and repository STLport. Every diagnostic trial
used an explicit private object path under build/script346d60. No shared
header, verifier or baseline was edited. BFME 2 donor ce1b975697 informed the
advance flag and default-team guard, while all BFME 1 offsets and calls remain
independently checked against its retail executable.

## What worked together

1. The bank rechecked frames after opaque readiness calls. Use an advance flag
   with the positive, negative and zero wait paths retail actually implements.
2. Force-inline cleanup: the default compiler decision leaves both dangling
   deletion loops out of line. But the non-null erase itself must remain opaque,
   while null-entry vector compaction stays inline. A declared address-derived
   ABI view produces the witnessed direct call, with no original type claim.
3. Negate the default-team protection guard around cleanup, then execute one
   shared continue. This lets the compiler share the EH cleanup tails. Keeping
   the old early continue duplicates destruction code and changes code size.
4. Adopt canonical AsciiString and locally expose the native StringBase string
   concat body. The complete parent remains 1950 bytes, with zero differences.

## Important negative results

Original bank 1856 B / shape .862. Force-inline alone gives 2016 B, and an early
positive-wait decrement gives 1770 B (1913 B with forced cleanup). Advance-flag
plus forced cleanup gives 2021 B, with 388 masked differences. Forcing every
STL erase out of line, then manually spelling null compaction, does not match
(1764-2033 B). Iterator-return cleanup, templates, explicit expansion, G7 and
inline-depth trials do not independently solve the body. The fully combined
correct source and canonical-header variants emit 1950 B exactly.

`erase_abi2/3` and `erase_view2/3` in scratch were INVALID private diagnostics:
an overly broad replacement moved a brace in the object-death arm and changed
control flow. Their favorable scores are not valid progress. Only *_guard
variants used the corrected whole-block replacement. The winning parent was
re-audited against native control flow and passed all normal scoped gates.

Tables preserve sizes, masked differences and structural scores. These
measurements alone do not establish identity or a recovery. The full private
provider proof is explicitly diagnostic; official add_match verification later
passed both rows with all call bindings and data/string checks.

## Validation

- Normal add_match scoped gate: 2/2 functions; 3 literals and 3 empty strings;
  7 recorded DIR32 references; source claims and body guard green.
- Native EH predecessors and all four 8-byte cleanup bodies agree; eh-proof.json.
- Science.cpp after provider repoint: 48/48 functions and its one data row pass.
- find_declared_unmatched: all defined functions already matched.
- Linking preview is unknown: this clone has no link census index. No linked
  bytes are claimed, and no census or full rebuild was run.

No credit is claimed for the 43-byte provider repoint: that body was already
verified C++. The newly recovered parent replaces a generated dump.
