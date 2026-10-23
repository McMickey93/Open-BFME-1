# Task 10: remove AsciiString::concat glue emitters

Queue rank 14, claim 0xF036DAE0. Moved each TU's existing concat glue into a TU-static helper. The call still reaches StringBase<char>::concat(const char*,int), as independently decoded by `callees.py 0x000B3730 272` and `callees.py 0x004DE8E0 519`; it no longer emits an incompatible external AsciiString::concat body. No shared header changed.

`./build.sh <both files>` passes all six rows, including four cleanup funclets, seven string references and twelve DIR32 references. COFF inspection finds no AsciiString concat symbol in either object. The sole writer `eh_state_pins.py --source .../PopupReplay_saveReplay_Thunk.cpp --fix --model gpt-6.1-sol` repins the four renumbered compiler labels after proving unique cleanup states and byte matches.

Before `link_check.py --census-only <both files>`: both fail concat COMDAT checks as well as unrelated selected callees. After the same check: concat blockers disappear; audio remains blocked by generateFilenamePrefix and replay by reallySaveReplay, so 0 -> 0 LINKED bytes. This is a changed-object preview against the Oct 19 census, not a fresh global link census.

BFME2 context: `reference/shims/asciistring_downloadmanager/ascii_string.h` delegates concat into StringBase, confirming the architectural distinction between wrapper glue and storage implementation.
