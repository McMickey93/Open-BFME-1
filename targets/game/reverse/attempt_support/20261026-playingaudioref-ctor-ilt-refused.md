# T8 handoff: PlayingAudioRef ctor/dtor repair refused by ilt_guard (2026-10-26)

Gate debt: `dir32,0x004046F6,??1Rva006967A0...` and `dir32,0x00431EDF,??0Rva006967A0...`
(both lines still baselined; reverted, nothing staged).

## Proven facts (all verified this session, then reverted)

- `MilesAudioManager` +0xad0 holds `PlayingAudioRef m_ad0[3]` (3 x 4 B, ends at
  +0xadc where `m_vectoradc` starts). Destruction goes through ILT 0x46F6 to
  `??1PlayingAudioRef` (0x00696870, matched row 7857); array construction goes
  through ILT 0x31EDF (`?j_00031edf`, row 101863) to the 9 B body at 0x006967A0.
- The 9 B body (`?m@Gen_006967a0`, gen-shim row 125380, skeleton this-zero-0)
  is the out-of-line default ctor: `PlayingAudioRef::PlayingAudioRef(void) :
  m_ptr(0) {}` outlined in a scratch TU probes EXACT (9/9 B, 0 relocs) first
  try under the allocate TU's `/O2` flags (scratch: build/ctor-shape.cpp).
- With the member type swapped to the real view, the constructor TU builds
  15/15 byte-exact with DIR32 clean; the 12 funclet `$L` pins renumber +1
  behind the type swap (bodies identical) and `eh_state_pins.py --fix`
  repoints all of them byte-verified.
- The outlined ctor in `MilesAudioManagerAllocatePlayingAudio.cpp` (end of
  file, past all funclets) lands via `add_match --replace-rva 0x006967A0`
  byte-verified, retiring the gen-shim; the TU's other rows stay green.

## Why it cannot land

`ilt_guard` refuses the new row name `??0PlayingAudioRef@@QAE@XZ` at
0x006967A0 (outside slots 40082:24251-24261). The sibling dtor at 0x00696870
is contradicted the same way and survives only through
`ilt_contradicted_baseline.txt:4781` grandfathering; that baseline is
shrink-only, so the ctor can never be added. Same refusal class as the
NamedCameraDataChunkParser EA rename (commit 7980299bf2).

## Resume path

If the oracle windows change or an exemption route opens, re-apply: member
type swap in `MilesAudioManagerConstructor.cpp` (keep 4 B layout!), outlined
ctor at end of `MilesAudioManagerAllocatePlayingAudio.cpp`, `eh_state_pins.py
--fix --source` the constructor TU, delete both baseline lines, commit with a
`Verifier-Change` trailer. Do NOT repeat the Z-first-style shape probes; the
9 B body is settled. model=muse-spark, t=90min.
