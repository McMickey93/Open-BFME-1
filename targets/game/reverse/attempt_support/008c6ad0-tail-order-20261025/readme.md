# 0x008C6AD0: preserve the canonical callback and native layout investigation

## Status and next operation

This is preservation of a **non-exact** reconstruction, not a recovery or a
canonical bank update. Variant 07 emits 229 bytes for the independently bounded
233-byte retail body, with 120 non-relocation byte differences. Its measured
instruction-shape score is 0.893; that is not a byte-match fraction. Variant 08
emits the identical instruction table. No C++ exact bytes were gained.

The canonical `re_log.py partial --stash` operation is **pending native
remeasurement**. The tool recompiles both the incoming and retained candidates
through `finish_measure.measure`; it refuses banking when that compiler is
unavailable. The local 32-bit compiler cannot run in this environment. Do not
substitute the supplied shape score for that gate, edit the log by hand, or
weaken `_measure_stash`. The existing canonical bank and attempt log have been
left untouched. The unmatched addition was removed from
`game/Libraries/Source/Apt/AptActionInterpreter.cpp`; its original 5,349-byte
source and already matched 520-byte sibling remain unchanged.

The next native banking step should submit `best-whole-tu.cpp.txt` through
`tools/re_log.py record` for
`?BooleanCoerce008C6AD0@@YAPAVAptValue@@PAXH@Z`, RVA `0x008C6AD0`, size 233,
status `partial`, with submitted `--score 0.893`. Let the tool remeasure both
banks and preserve whichever actually ranks better. Cite this handoff and
record `model=gpt-6-astra-pro`, `t=60min` for this continuation, and
`blocker=codegen-order/branch-tail-order`. This operation has not been run.

## Preserved inputs

The whole-TU source is `best-whole-tu.cpp.txt`, exactly variant 07:
Git blob `6f590f236f882e4fa62d50b22b5214ed2c5a4b8c`, SHA256
`872ab57f5654deadc23c474e1307b6a73709030d396b5cfd923b3c827539f927`.
It is the simpler equivalent of 08. Patches `07-to-03.patch` through
`07-to-08.patch` reproduce the other measured variants from that same file;
there is no patch for 07 itself. `native-inputs.json` records each reconstructed
source hash, immutable GitHub payload commit and completed workflow run.
Apply a patch to a temporary copy of the best source, never cumulatively.

`probe-04-008c6ad0.txt`, `probe-05-008c6ad0.txt` and
`probe-07-008c6ad0.txt` preserve the three relevant raw comparison tables.
`probe-07-008cf1b0.txt` preserves the unchanged sibling check. The native runner
verified the artifact digests and frozen source/evidence inputs. Use the raw
comparison tables: filling retail relocations into a displaced block corrupts
the explanatory rendering and is not reliable operand evidence.
Only line endings and trailing whitespace are normalized in the preserved
probes; `native-inputs.json` records both original and preserved file hashes.

The reviewed source base was
`3d3b0681294a0de92aae10ea1a753ae22068f091`; unchanged native guards accepted
unrelated upstream advances. Run 08 used actual upstream
`adf0790854f08041700a3b401cafdefdb905a140`. The following official
`7a54fc6ed91a7803fdf555072d465023bf5b6431` appends unrelated linking verdicts;
preserve those entries when recording the native partial verdict. Compiler
inputs were the original MSVC 7.1 and the whole source's existing
`/O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc` configuration. Diagnostic objects
must not be reused as verified build receipts.

## What was established

The [identity evidence](../../identity_evidence/008c6ad0-canonical-coercion.md)
records the independently bounded body, real callee ABI and canonical data
bindings. The three direct callees are already matched. The new source calls
`AptValue::toNumber`, `AptBoolean::Create(bool)` and the cdecl
`Rva008C4A30Check(Rva8CD130Value*)` directly. It does not retain the old bank's
void-function cast, unbound zero symbol or wrong-image-base stack globals.

An explicit array local, following matched `Rva008C6800.cpp`, restores the
retail load roles: array in EAX, count in ECX, then the indexed ESI load.
Distinct zero-code `_WriteBarrier` and `_ReadWriteBarrier` tags retain all
four factory call blocks, including both false returns. This is supported
by the already matched BFME 1 tail-separation witnesses at `0x00653990` and
`0x003E5950`; the source imports no instructions or new pins.

The remaining failure is branch linearization and jump relaxation. Independent
instruction-inventory review found the same 68 non-branch instructions and
193 non-branch bytes in retail and the corrected measured variants. All have
16 conditional jumps. Retail needs two long jumps (233 bytes), 04/06/07/08
have one (229 bytes), and 05 has three (237 bytes). This does not make any of
the candidates byte-exact.

| Block | Retail offset | Best 07 offset |
|---|---:|---:|
| Shared numeric conversion | `+0x8A` | `+0xB7` |
| Common false factory | `+0xA0` | `+0x86` |
| Coercion type-5 test | `+0xAC` | `+0x92` |
| Coercion type-6/type-7 tests | `+0xC7 / +0xCC` | `+0xAD / +0xB2` |
| Separate default false factory | `+0xD1` | `+0xD9` |
| Shared true factory | `+0xDD` | `+0xCD` |

The first unmasked difference in 07 is the branch displacement at `+0x3C`.
There are 11 relocations, with eight sites displaced by the block ordering.
The original sibling at `0x008CF1B0` was exact modulo relocations in every
native experiment. No admission or complete relocation-aware gate was run.

## Measured experiment record

| Variant | Isolated source question | Result |
|---|---|---|
| 03 | Distinct barriers before false factory calls | 229/233; 121 differences; first `+0x1C`; four factory blocks retained, numeric at `+0xB7`; array/count register roles wrong |
| 04 | After-call tags and canonical array-local order | 229/233; 120 differences; first `+0x3C`; prefix fixed, numeric at `+0xB2`, type-7 test after true |
| 05 | Explicit flat labels in retail block order | 237/233; 116 differences; coercion moved first and common false last |
| 06 | Cached type plus one inline-helper entry barrier | Complete raw instruction table identical to 04 |
| 07 | Single numeric label inside structured negative guard; early false returns retained | 229/233; 120 differences; both coercion type tests together; table equals 03 except the corrected three array/count instructions |
| 08 | Coercion made the explicit `else` arm of 07 | Complete raw instruction table identical to 07 |

The pre-existing nine if/switch/ternary/Boolean-output trials were not repeated
unchanged. Initial scratch variants 00-02 were not compiled in this continuation.
The prepared 02 combined a validity bitfield with a native member helper; it
must not be described as measured evidence.
They were prepared before the first native run, but the independently matched
distinct-barrier witnesses supplied a more specific explanation for the known
merged false tails, so native work began with 03. Trial 04 then established
that the retained raw-shift validity spelling already gives the correct
non-branch prefix. Compiling 01/02 unchanged would combine that unrelated
representation change with the unresolved inlining/block-origin question.
Their omission is prioritization, not evidence that either spelling fails.

## Reassessment and future work

The callee contracts, data identities and body extent were checked separately
from compiler shape. The corrected native instruction inventory supports the
current types and stack roles. No shared header or source owner was guessed,
no flag sweep was performed, and no sibling behavior was altered. The
post-call tags, helper-entry boundary, flat labels, structured numeric label
and explicit-else context now have concrete measured outcomes.

A more specific untested combination remains: 05's separate positive
`isType(6)`/`isType(7)` jumps to coercion, together with 07's separate tagged
early false returns for fallback and predicate. Variant 05 instead used
common-false gotos; 07 instead used the combined negative type guard. Old log
54855 lists nine source forms but reports merged false tails for all its
if-chain forms, and the preserved old banks have no differing barrier tags.
It does not establish that this exact combination was tested. The
`docs/shape_levers.md` witness at `0x0068D730` (129-byte bounded string append)
shows split early-return guards changing shared-block placement. Its guards
return instead of jumping to a coercion arm, so it motivates this precise
future diagnostic without guaranteeing a result. No such trial was run here.

An isolated forced-inline member helper remains an untested source-context
idea. Existing Apt members establish the class/layout context, but there is
no matched evidence that changing a free forced-inline helper into an otherwise
identical member moves this numeric block. The W3D `0x007334B0` witness concerns
extracting an interleaved search/mutation operation and is not direct support
for that one-variable change. It is therefore a weak future hypothesis, not
an assertion that all conceivable C++ spellings are exhausted. Reassess it
against new evidence before restarting a source-shape sweep.
In particular, no matched Apt or scoped BFME 2 witness found in this review
either proves or rules out a member-helper block-origin effect. The measured
helper-entry barrier in 06 rules out only that exact cached-type/barrier
transformation; it does not test a member receiver context. An isolated
member-only trial retaining 04's verified flags, array load and false-tail tags
would be distinct, but should be motivated by new evidence before another run.

BFME 2 revision `beed8a16790a6812231ac7b05e3e6893e4cb5d1b` materially informed
the null 08 test through `docs/recipes.md:646-652` and the matched
`MilesAudioManager::shouldPlayLocally` body at `0x00053BA1`. That witness also
has cleanup and EDI shrink-wrapping absent here. Preserve the
`[BFME 2 donor]` attribution on this investigation's commit; it is evidence
provenance, not a donor identity claim for the BFME 1 callback.
