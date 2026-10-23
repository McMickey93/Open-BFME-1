# Task 25: keep inline emptiness reads local

Queue rank 30, claim 0xF19ABB22. Moved the existing emptiness tests into TU-static helpers in the resource-image and start-game sources. The three retail reads retain the measured buffer pointer/+4 unsigned-short length check, without emitting competing external AsciiString::isNotEmpty bodies. Friendship keeps the existing storage fields private. No shared header, pin or ledger change.

`callees.py` inspected the 155-byte and 168-byte resource-image bodies plus the 163-byte start-game body. `./build.sh <both files>` passes all three rows, two string references and nine DIR32 references. Both COFF objects omit the AsciiString isNotEmpty symbol.

Before `link_check.py --census-only <both files>`: both fail wrong isNotEmpty COMDAT and selected-definition checks. After the same check: both LINKS, 321 + 163 = 484 bytes in the changed-object preview. This is not a fresh global census.

BFME2 supporting source: `Code/Libraries/Source/WWVegas/WWLib/string_base.h` declares the owning implementation and `reference/shims/asciistring_downloadmanager/ascii_string.h` provides wrapper glue. BFME1's direct field reads and complete byte checks justify keeping these particular inlined shapes local.
