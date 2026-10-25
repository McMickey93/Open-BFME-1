# Apt helper 0x008AE3A0: bank semantics review

Target: `?aptHelper008AE3A0@@YAPAVAptValue@@PAXHH@Z`, 166 bytes.
The matched 21-byte clear/set wrappers at 0x008AE450/0x008AE470 independently
identify this three-argument cdecl helper. Retail RET at +0xA5 followed by INT3
establishes the extent. Callees were checked with `callees.py`: toInteger at
0x00898300, bfmeGo1034F at 0x008D3280, and bfmeStepCBC at 0x008D2130.

## New finding: the preferred bank is semantically wrong

The 2026-10-17 0.988 bank tests
`(~(last->m_flags.m_value >> 15) & 0x100) == 0`. That tests original **bit 23**.
Retail at +0x47 instead executes `shr edx,15; not dl; test dl,1`, testing
original **bit 15**. The two-byte distance is consequently not a valid
improvement over the older three-byte bank. Do not land or optimize that bank
without restoring the bit-15 test. The 2026-10-17 partial record's assertion
that this is only a byte-NOT residue is refuted by the actual operand semantics.

Private reproduction under `build/banked-apt-20261025/`:

* `banked.cpp`: 166 bytes, 6 relocations, 2 differences at +0x4A/+0x4D.
* `correct-bit15.cpp`: replace only the second `>>15` with `>>7` while retaining
  `&0x100`; 166 bytes, 6 relocations, 3 differences at +0x49/+0x4A/+0x4D.
  This is the earlier valid shape: `shr edx,7; not edx; test dh,1`.

`tools/probe.py` was run for both, with explicit 166-byte extent. The preferred
bank remains untouched because re_log's bank selection retains the numerically
closer candidate; this note records its semantic disqualification. Correct
source can be recovered by the one-token change above; no new reconstruction
or source-shape improvement is claimed. Earlier attempts already exhausted
byte narrowing, predicate/bitfield helpers, flags locals, and callee visibility;
those trials were not repeated.

## BFME 2 reference pass

Reviewed read-only current donor `8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9`,
`Code/Libraries/Source/Apt/AptCharacter.cpp`, the type predicates and checked
casts under `Apt/AptValue/`, and the helper's relevant history. BFME 2 predicates
use a different signed type field (bits25..31), so that layout cannot be copied
into BFME 1's witnessed low-six-bit type and bit15 validity fields. Its helper
also retains out-of-line getter calls that BFME 1 has inlined.

Compiled the clean pinned donor at
`beed8a16790a6812231ac7b05e3e6893e4cb5d1b` through bfme2_sweep compile, then
match and packets. Receipt:
`build/bfme2_sweep/trials/8d9f6b69672d4fa0a003e522a2db15e8/trial.json`.
Source SHA256 ccfe24111fd12e5cad75949dccdcea54f18487e88eb315173f01dce5b2e5888d;
MSVC 13.10.3077 `/O2 /G6 /arch:SSE /DNDEBUG /MD /EHsc`, no includes/dependencies.
Only the two already-matched wrappers placed exactly; the donor helper did
not place. This is discovery evidence, not a failed identity or relocation gate.
No game source, pin, layout name or ledger row was changed.

Remaining prerequisite: reproduce the correct bit15 predicate while preserving
retail's ESI allocation and 166-byte extent. The native donor provides no new
supported spelling beyond the already-tested local forms. Claim released.
