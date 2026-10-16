# Address-qualified word store at 00169FF0

A fresh tools/carve_unclaimed.py pass proves the start by a direct REL32
target and the end by RET 4 at +7..+9 followed by INT3 at +10. The complete
body loads one incoming dword, stores it at ECX+0x40, and returns while
consuming that argument. checked_callees reports no outgoing calls. There
is no boundary overlap, branch, hidden result, or receiver adjustment.

Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b,
Code/GameEngine/Source/Common/Audio/AudioEventInfoPriority.cpp, supplies
its ordinary one-member assignment at RVA 0x0041FDEE, also 10 bytes.
The donor's enum identity and +0x44 displacement are not transferred:
BFME 1 only proves the raw word at +0x40. No caller proves an original
owner or member identity, so the receiver remains Rva00169FF0 and the
operation storeWord. name_oracle has no witness for that class.

repair_queue.py dest selects TinyIndexedForwarders.cpp from its existing
0x0016A040 sibling, 80 bytes away. This preserves the repository's unit
placement rule without adding a new one-function file or putting new clean
code into the mixed naked AIStates.cpp. The brief was regenerated from the
fresh carve queue before writing the body; the derived queue itself is
not part of the source/ledger change.

The assignment emits all 10 bytes without a relocation. The strict source
gate verifies all 95 rows. link_check before and after remains LINKED
0 -> 0 because of existing unresolved forwarding providers; none are changed.
There are no new pins, globals, headers, shims, source markers, or assembly.
Raw carving, brief, donor and gate/link receipts are build/sol3_carved.csv,
build/brief_00169ff0.txt and build/*00169ff0* in ds-9.
