# Queue 7: vector<AsciiString> assignment

The current 212-byte canonical ledger row at RVA 0x000DE2C0 is backed by
`AsciiStringVectorAssignmentThunk.cpp`. That file still contains a naked byte
emitter named `_bfme_AsciiStringVectorAssignment_DE2C0`; its row uses
`object-symbol=`. Its COFF therefore does **not** define the public C++ assignment
symbol that the verified callers reference. This is a provider mismatch in
addition to the competing COMDAT copies; suppressing callers alone cannot solve it.
The independent caller evidence is recorded in
`targets/game/reverse/identity_evidence/000de460.md`.

The October 19 census identifies 15 competing assignment COMDATs, all wrong.
The copy-constructor TU explicitly instantiated the entire vector class, thus
emitting assignment even though none of its 22 verified ledger rows owns it.
A specialization declaration now excludes only that unnecessary assignment
emitter. `./build.sh game/Libraries/Source/WWVegas/WWLib/AsciiStringVectorCopyConstructor.cpp`
passes 22/22 rows. COFF inspection confirms the assignment definition is absent.

Before: `link_check.py --census-only` on the copy TU reports assignment COMDAT
and selection blockers, alongside existing copy/destroy/fill helper blockers.
After: one wrong emitter removed; no overall LINKED claim. The naked owner must
be converted to a correctly exported C++ body, and the other competing emitters
must be handled while retaining their ledger-backed helper definitions.
