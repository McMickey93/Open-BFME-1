# Task 12: use the canonical StringBase length getter

Queue rank 16, claim 0xFDD2B830. The INI parser now explicitly calls the already included StringBase<char>::getLength. The obfuscator exposes its inherited StringBase getter rather than declaring a separate AsciiString getter. No shared header changed.

`callees.py 0x004776E0 512` and `callees.py 0x0007FBF0 254` establish these length reads are inline, with no new callee or pin required. `./build.sh <both files>` passes all three rows, including the 25-byte cleanup. Both COFF objects omit `?getLength@AsciiString@@QBEHXZ`. `eh_state_pins.py --source .../obfuscate_AsciiString_Thunk.cpp --fix` proves the cleanup identity and updates its compiler label.

Before `link_check.py --census-only <both files>`: both fail the AsciiString getLength COMDAT check. After the same check: both sources LINKS, 0 -> 766 bytes in the changed-object preview; no AsciiString getLength blocker remains. The tool previews changed objects against the Oct 19 census; a fresh census is required to measure global LINKED progress.

BFME2 supporting source: `Code/Libraries/Source/WWVegas/WWLib/string_base.h` owns getLength; `reference/shims/asciistring_downloadmanager/ascii_string.h` only forwards the AsciiString wrapper. BFME1 byte checks remain the proof.
