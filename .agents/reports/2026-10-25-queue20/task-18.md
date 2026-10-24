# Task 18: pointer-vector overflow

Queue rank 32, census e9a5ae5b4c. Rva003C5820AppendMatch.cpp emitted a competing non-retail j_000100d7 vector overflow helper.

Repair: use the CRT and STL settings of the matched pointer-vector siblings: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB and _STLP_NO_EXCEPTIONS. The source previously had no compiler directive. /MD restores retail's imported CRT call shape; disabling STL exceptions matches the existing provider context. Keep the native helper body visible so empty-tag lifetime/codegen remains correct.

Verification: caller source passes 2/2 rows, retaining the 83-byte appendMatch and 181-byte lookup; Rva003C56F0PointerInsert.cpp, Rva003C5890VectorAppend.cpp and Rva003C58E0SortedInsert.cpp pass their scoped builds. compile_function independently verifies the emitted queue-named overflow helper at BFME1 0x003C54A0 for 265 bytes with zero unresolved relocations. The existing generator row is unchanged; no new conversion is claimed. Global linking remains unknown pending current census evidence.

Ruled out: early specialization and late extern-template suppression both force an extra caller stack slot and a longer function, failing the caller's existing extent. The extent is correct; it must not be enlarged to accept that trial. _STLP_NO_EXCEPTIONS alone preserves the caller but leaves direct-versus-imported CRT call differences in the helper. Adding the sibling CRT settings closes those differences. All unsuccessful changes were reverted.

BFME2 evidence: sibling revision f301d686c70c3e5fa0b51b342a2745f495b8a0b1, docs/recipes.md Linking section and e9d93338e0 explain losing STL COMDATs and declaration placement. The declaration-only adaptation is inapplicable here because it changes caller bytes; BFME1 matched siblings supply the successful compiler context. No BFME2 addresses, type layouts or flags were imported.
