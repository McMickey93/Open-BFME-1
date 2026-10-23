# Task 14: correct the AsciiString destructor copies

Queue rank 19, claim 0xFC0A313F. Restored auto-inlining after the Palantir global initializer: the initializer still calls the native AsciiString constructor, while its late-generated destructor now inlines base cleanup. FileTransfer exposes the existing StringBase destructor body inline so its AsciiString destructor also forwards directly to releaseBuffer. Both copies now consist of exactly `e9` with a REL32 relocation to `?releaseBuffer@?$StringBase@D@@AAEXXZ`, matching the canonical five-byte destructor.

`callees.py` inspected the 27-byte initializer, 10-byte cleanup and 659-byte transfer body. `./build.sh <both files>` passes all three rows and the global's data row, including 13 DIR32 references. Two rejected static-initializer alternatives were reverted: specializing the base destructor after inclusion fails C2908; changing to the standalone shim removes the wrong destructor but makes the initializer call the base constructor instead of native AsciiString (byte mismatch at +0xb).

Before `link_check.py --census-only <both files>`: both fail AsciiString destructor COMDAT checks. After the same check: Palantir source LINKS 37 bytes; FileTransfer's destructor blocker disappears, with GetArtPreviewFromMap/GetPicPreviewFromMap/GetPreviewFromMap remaining selected-definition blockers. Changed-object preview 0 -> 37 bytes; not a fresh global census.

BFME2 supporting examples: `Code/GameEngine/Source/Common/AsciiStringFoldDeleters.cpp` and `RvaAsciiStringTripleDtors.cpp` use shared string headers and destructor code generation to forward to the owning cleanup worker. Their addresses and byte shapes differ; BFME1 verification supplies the proof here.
