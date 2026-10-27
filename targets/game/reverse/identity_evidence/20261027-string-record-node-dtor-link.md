# String-record node deletion: bind both callers to the existing provider

Inspected BFME 1 base: ce1daafa6a59b48c3ca371de266ce299f79cbd99.
This is one shared destructor-name repair, with no new reconstructed body.

## BFME 1 target facts

| Role | RVA | Bytes | Source |
| --- | --- | --- | --- |
| first clearer | 0x003593F0 | 54 | Common/Rva00359330StringRecordClearNodes.cpp |
| sibling clearer, unchanged | 0x003595F0 | 54 | same file |
| unregister drain | 0x0035AC30 | 92 | Common/BfmeSecondZUnregister.cpp |
| complete node destructor | 0x00354A00 | 72 | ScriptEngine/Rva00354A00NodeDestructor.cpp |

Both changed callers reach ILT 0x00042A32, which routes to the existing
72-byte `??1Rva00354A00Node@@QAE@XZ` owner. Their old
`??1BfmeNodeZ@@QAE@XZ` name has no matching definition. The provider's
complete body tears down the embedded subobject at +4; the callers only
read the next-link prefix at +0 and delete the original allocation pointer.

Use the existing provider's address-derived class name in both prefix views.
Do not change the field reads, null tests, record or vector layouts, allocation
interface, calling convention, flags, public function names or ledger rows.
No complete node layout or original EA type name is claimed by these views.

## BFME 2 comparison and exclusions

Reviewed pinned donor 73898a96342963eac2826836db10649a69e3dbb8:
`Code/GameEngine/Source/Common/Rva00359330StringRecordClearNodes.cpp` and
`Code/GameEngine/Source/GameLogic/ScriptEngine/ScriptListNodeZDtor.cpp`.
The donor ledger places its clearer at 0x003B578E / 47 bytes and explicitly
credits BFME 1 donor source with /O1; the copied source comment still contains
BFME 1 addresses. It is not independent identity evidence.

BFME 2's BfmeNodeZ destructor is an 8-byte body at 0x003B3F5E: it adjusts
the receiver by four and jumps to a Script destructor. BFME 1's witnessed
callee is the different 72-byte provider above. The common record/prefix
shape therefore does not justify importing the donor's node identity, body,
flags or layout. The target ILT, existing owner and full paired byte checks
decide this repair. Donor evidence is credited for ruling out that unsafe mapping.

## Native compiler and object evidence

The initial clearer/provider baseline passes 3/3; the unchanged unregister
baseline passes 1/1. The completed family passes 4/4 through the normal native
MSVC 7.1 byte gate across all three sources. The sibling clearer remains exact.
One DIR32 reference and all four body guards pass, with no skipped reference.

For each changed object, every executable section's bytes and relocations
remain identical after normalizing only the BfmeNodeZ-to-Rva00354A00Node spelling.
The one undefined destructor name changes to the exact definition emitted
by the independently verified provider. The generated scalar deleting helper
follows the same owner rename; all other external definitions and references
are unchanged. Its two new copies are byte-and-relocation twins, 30 bytes each,
calling the existing destructor and ordinary operator delete.
Shared-helper section/relocation SHA-256:
`34d2826a32225fd565ab2b3f8ecaf8ef7cf956b4458ad0d9c6714b84ad081105`.

The related-source sweep found only BfmeSecondZUnregister.cpp still using the
old node type, so it is included in the same repair. No authored game source
retains that token. Existing pin candidates are left to their owning tools.

## Ordinary link previews and remaining scope

Index: census a0940f921b, 2026-10-27 11:50. The ordinary before/after commands
use `python3 tools/link_check.py <source>`, with both changed sources in the
final check.

Before: the clearer reports the unresolved BfmeNodeZ destructor. The unregister
drain reports that name and the separate BfmeElementZ destructor.
After: the BfmeNodeZ reference is gone from both. The unregister drain still
reports `??1BfmeElementZ@@QAE@XZ`, which is a separate identity repair.

The final preview cannot read 22,663 other new/changed ledger objects and
therefore says selection UNKNOWN. Neither source is established link-clean
by that preview; its LINKED counters remain 0 -> 0. This does not establish
a census-linked gain. Do not promote the near packet's hypothetical 107-byte
unlock to a measurement.

Accounting: +0 new C++ bytes, +0 measured LINKED/LINKING bytes, no new pins,
aliases, hatches, shared headers or debt-register retirements.

Autonomous implementation and measurements: OpenAI Codex.
