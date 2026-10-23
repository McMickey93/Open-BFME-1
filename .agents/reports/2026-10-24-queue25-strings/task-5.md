# Task 5: remove incorrect AsciiString::clear emitters

Queue rank 7, claim 0xFEE65C1B. AudioEventRTS::generatePlayInfo now calls StringBase<char>::clear directly. RoadType now initializes the existing string storage directly through friendship, retaining the previous zero-store behavior without exporting a clear function that merely zeroes a pointer. No shared header changed.

`callees.py` inspected 0x000B3C60/664, 0x00707090/35 and 0x007070C0/131 before editing. `./build.sh` verifies all four rows (934 bytes), including four string refs and one float constant. COFF symbol inspection confirms neither compiled object defines `?clear@AsciiString@@QAEXXZ`. An initial forceinline-only experiment passed bytes but retained the wrong emitter and was replaced.

BFME2 context: `reference/shims/asciistring_downloadmanager/ascii_string.h` forwards clear into StringBase; BFME1 native `string_base.h` independently establishes clear releases the buffer. RoadType's local old clear did not implement that identity.

`link_check.py --compile-limit 0 <both files>` after the change reports LINKED PREVIEW UNKNOWN, 0 -> 0, because the cold worktree cannot refresh selection for 22,654 current ledger objects. The census-only changed-object preview reports RoadType LINKS 166 bytes, while audio remains blocked on generateFilenamePrefix. These are diagnostic previews, not a fresh census or claimed LINKED gain.
