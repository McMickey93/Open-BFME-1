# Render helper byte-global binding prerequisite

The existing matched RTS3DScene helper at RVA 00713780 retains its identity,
2,491-byte extent, ABI, class views and compiler settings. Its recorded
identity evidence is the complete RET 16 at +09B8 and the matched callers
through ILT 00017238, which pass four stack words. No semantic name is inferred.

Independent BFME 1 retail instructions establish the shared data accesses:

| Helper offset | Instruction | Existing recorded symbol |
| --- | --- | --- |
| +088D | MOV BYTE [01341220],1 | g_00710e10 |
| +089A | MOV BYTE [012D6E04],AL | g_00710e20 |
| +08A1 | MOV BYTE [01341220],0 | g_00710e10 |
| +08A8 | MOV BYTE [012D6E04],60 | g_00710e20 |

The matched 10-byte setters at RVA 00710E10 and 00710E20 each load AL from
[ESP+4], store AL at the respective address, and RET without popping the
argument. Their unsigned-char cdecl declarations and public data definitions
already exist in Gen_00710e10_SetGlobal.cpp and Gen_00710e20_SetGlobal.cpp.
The DIR32 ledger independently records both addresses. ShaderClass::Apply
at RVA 00911020 reads these existing byte globals: the first selects whether
the second overrides the alpha reference. These target relationships support
the binding; similar spellings or instruction shapes alone are not the basis.

Replace the helper's private bool and unsigned-char extern bindings with the
existing unsigned-char declarations. Its flag writes remain exactly 1 and 0.
No new symbol, global definition, data row, pin, alias, header or layout is
introduced. The whole helper continues to byte-match, including all four
stores and their relocations.

The existing g_00710e20 definition was uninitialized despite retail's initial
byte 60 at VA 012D6E04. Set that definition to 0x60 in the same repair; leaving
it zero would bind a correct caller to an incorrect provider. The retail PE
.data raw extent contains this byte (offset 031E04, raw size 049000).
Conversely, VA 01341220 lies at .data offset 09C220, beyond that raw extent,
so its initial value is loader-zero, as its existing matched data row says.
Reading past a section's raw extent as file data would give a false value.

The existing data_rows.verify_row checker, called read-only with an in-memory
description and compile=False, verifies g_00710e20 as one byte equal to retail,
zero relocations, sizeof 1 under its actual /DNDEBUG /MD /EHsc settings and
allocation extent 1. No data ledger entry or gate allowance is written.

Donor review: read-only BFME 2 master
8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9 was searched in Code/,
reverse/functions.csv, reverse/attempt_support/ and docs/recipes.md for the
helper address and both existing global names. The only related result is
LightEnvironmentClass_Set_Output_Ambient.cpp, itself derived from this BFME 1
helper; it contains no corresponding helper or global repair. No donor source,
name, layout or compiler discovery contributes. The pinned reference is unchanged.

Acceptance: the scoped helper build passes 1/1 bodies, 10 DIR32 references,
four float constants and zero body exemptions. Both repair_queue.py pass-test
commands pass and remove only the two retired binding exemptions: gate debt
1020 -> 1018. Both setter units pass 1/1; the flag's existing data row passes.
The only other source using these globals is shader.cpp, which passes all
22 matched bodies, five data rows, 68 DIR32 references, 57 string references,
84 jump-table entries and its checked tail. check_csv.py and both changed
sources' find_declared_unmatched.py checks pass. Authored C++ coverage stays +0.

Link preview before: the helper's two retired globals are unresolved,
LINKED 0 -> 0 bytes. After: neither global is unresolved, but LINKED PREVIEW
UNKNOWN, LINKED 0 -> 0 bytes. Census 2026-10-24 11:02 at 32774ab033 lacks
22,643 current objects here, so selection and linked-byte improvement remain
UNKNOWN. No census rebuild is run.
