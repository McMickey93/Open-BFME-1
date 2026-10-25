# BfmeObjEQT::bfmeRunEQT call-setup reassessment

Target: RVA `0x001DD8F0`, 264 bytes. The matched BfmeConv1946 caller and
ILT `0x00013E71` establish the existing opaque identity. Retail returns at
`+0xFB` and `+0x105`, followed by INT3 at `+0x108`, establish the extent.
The preferred bank remains `attempts/0x001dd8f0.cpp`; it emits 264 bytes,
nine aligned relocations and six non-relocation differences at the final
obstacle call. Retail loads the owner into EDX and receiver into ECX before
the pushes; the bank uses ECX for the owner and loads the receiver later.

The earlier native Coord3D lifetime, guard-scope corrections, visible
Pathfinder/Geometry implementations and receiver-local trials were reviewed
before these experiments. They were not repeated.

New trials used private sources under `build/banked-eqt-20261025/` and
`tools/probe.py`, preserving MSVC 7.1 defaults plus the bank's `/DNDEBUG /MD
/EHsc /Igame/Libraries/Source/WWVegas/WWMath` overrides and BFME 1 coord3d.h.
A typed AI prefix with its target-proven Pathfinder pointer at
offset `0x0C`, used at both accesses or just the last, still emits 264 bytes
with the same six differences. An inline owner accessor emits 265 bytes
with 74 differences. No tested variant improves the bank.

BFME 2 revision `8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9`,
`Code/GameEngine/Source/Common/Rva0026163A.cpp`, supplies a related 151-byte
coordinate overload, not this target's object overload. Its nested AI guard,
Pathfinder local and boolean result are supported donor structure. Donor
commit `8c4dab19bc829292cf9e9a936296313621f277ee` and later canonical Coord3D
adoption were reviewed. Donor AI offset `0x10` and geometry offset `0xA8`
cannot replace target offsets `0x0C` and `0xAC`.

The required private compile used pinned donor revision
`beed8a16790a6812231ac7b05e3e6893e4cb5d1b` with BFME 1's toolchain;
receipt `build/bfme2_sweep/trials/5ef4366bc59c4bda9a95588a3068cd5b/trial.json`
records `/O2 /GR- /EHsc- /DNDEBUG /MD /EHsc` and source SHA256
`b90fe5f325a819e75ff4a8f1fef6608bbe45e72ecca26b7c9a5c1942183c0643`.
Include tracing confirms the pinned donor's `Code/Libraries/Include/Lib/Coord3D.h`
was used in this private discovery compile; no BFME 1 build input was redirected.
Its match has one near placement and no exact placement. Adapting only the
nested guard/local/bool structure into the bank's BFME 1 header context,
with either pointer arithmetic or the typed AI view, produces 264 bytes
with 40 differences starting in the prologue. This does not improve the
target's final call setup. Donor behavior is a related-overload lead, not
target identity or layout proof.

The six-byte call-setup mismatch remains. Preserve the stronger bank and
resume only with a new compiler-context or scheduling explanation. No
production source, pin, name, header or ledger row changed. Claim released.
