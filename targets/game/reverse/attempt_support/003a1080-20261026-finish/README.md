# Finish-lane retry: RVA 0x003A1080

## Result and boundary

No recovery or linking credit is claimed. The preferred bank remains unchanged
at `targets/game/reverse/attempts/0x003a1080.cpp`. It emits 119 bytes with one
relocation and five non-relocation differences, for measured quality 0.9580.
The complete retail decode ends with `ret 0x18` at +0x74 and `int3` at +0x77:
the body is `[0x003A1080, 0x003A10F7)`, not the 114-byte extent in an older log.

The remaining window is exactly five bytes:

| Offset | Retail | Preferred bank |
| --- | --- | --- |
| +0x54 | `3B C3` / `cmp eax,ebx` | `89 5E 3C` / `mov [esi+0x3c],ebx` |
| +0x56 | `89 5E 3C` / `mov [esi+0x3c],ebx` | comparison starts at +0x57: `3B C3` |

Both streams realign at +0x59. The single call relocation is aligned at +0x40;
its masking in these diagnostics is not callee-binding acceptance.

## Inputs and identity limits

- BFME 1 revision: `c8b77ca733696220efbdf5d6bcc47fa594c284ad`.
- Model: `gpt-6.1-sol`; assigned finish lane R, budget 30 minutes.
- Target: this checkout's `retail-1.03-unpacked` game baseline.
- Compiler: repository MSVC 7.1 `cl.exe` through Wine in OrbStack machine
  `bfme2-build`, with `BUILD_POOL=1`, `BFME_OBJSTORE=off`, and Wine prefix
  `/home/mehmet/.wine-bfme2-orbstack`.
- Base compiler options from `compiler_command`: `-nologo -c -O2 -GR- -EHsc-`.
  Explicit flag alternatives are preserved in `choices.json`.
- Before experimentation, all 16 prior verdicts and the preferred bank were
  reviewed. Existing register/store/barrier trials are not new discoveries.
- Retail proves six stack arguments, an unused first argument, the count clamp,
  the subobject address +0x10, and the witnessed field writes. The lexical
  `BfmeThingJG::bfmeSetupJG` identity is inherited, not newly established.
  `callers_of.py` finds no named direct caller. No rename was attempted.
- The existing matched `bfmeDropJG` body in
  `game/GameEngine/Source/Common/BfmeTwoHundredSixteen.cpp` independently reads
  and clears a pointer at +0x40. Pointer-field trials test that limited layout
  fact; they do not prove the rest of the class or its original name.

## Finite trials and dependency audit

`measurements.csv` records 259 trial entries across five bounded official
`shape_search.py` runs, including repeated baselines. All searches retained
the starting five-byte residue as their best result:

| Group | Entries | Hypothesis |
| --- | ---: | --- |
| store | 64 | Selective volatile qualifiers, comparison local/parameter, field reread |
| type | 72 | Bool/byte stores, pointer +0x40, signed/unsigned +0x3c |
| flag | 11 | Processor, optimization, aliasing, FP and inlining options |
| control | 80 | Duplicated if/else arms, switch lowering, comma expression |
| inline | 32 | Forced-inline reset boundary with bool/char input and selective qualifiers |

The choices are explicit and finite in `choices.json`. Groups other than
`inline` start from the unchanged preferred bank. Apply `inline-reset.patch`
to a scratch copy of that bank before replaying the inline group. Reconstruct
the trial streams with `tools/shape_search.py`; use target size 119 and the
bank's existing decorated symbol. Quality and masked shape are not admission.

Removing only the volatile qualifier at +0x3c worsens the result to 14 differing
bytes by delaying that store. An early comparison local does not recover the
desired compare/store ordering in any tested qualifier combination. The inline
reset overload is a diagnostic transformation, not a newly recovered method.

The inherited bank's `BfmeSubJG::bfmeStartJG(int,int,float)` has no pin. The
complete call target is ILT `0x0002A1B2`, which routes to the already matched
300-byte `ParabolicEase::setEaseTimes(float,float,float)` at `0x00094970`.
`native-ease.patch` gives the scratch caller its actual existing dependency
and float parameter declarations without adding a pin. It still emits 119
bytes with the same five differences. Its diagnostic decorated symbol is
`?bfmeSetupJG@BfmeThingJG@@QAEXHHMMH_N@Z`; this is not a landed identity.

`visible-ease.patch` additionally exposes the actual current BFME 1 provider
source `game/GameEngine/Source/Common/ParabolicEaseSetEaseTimesBFME.cpp`.
Its absolute scratch include must be changed to the current checkout when
replayed elsewhere. The provider independently emits exactly 300 bytes with
17 relocation operands, modulo relocation slots. The caller still has the
same five differing bytes. This rules out this tested provider-visibility
explanation; neither object is a strict byte/link receipt. Raw probe output
for the bank, typed caller and visible provider/caller is retained here.

The experiment cache declined reuse for unavailable include-directory
inventories and, for the explicit `.cpp` include, unknown search roots. These
were fresh diagnostic compiles with private output objects, not accepted
dependency-cache or normal-build receipts. No shared object was substituted.

## Reference and publication boundaries

A narrow BFME 2 inspection at `90e8324a3553517c3a351a3233b71bcc7371f6a0`
found no `BfmeThingJG` or `bfmeSetupJG` source/ledger/support counterpart. That
does not exhaust unnamed or structurally related donor source, and no donor
identity or source was imported. The initially unpopulated donor checkout was
initialized non-recursively at the parent-pinned revision
`3252f8ecf0ebd738896f2aea4780279ed29538b8`. An unbounded history fetch was
stopped and replaced by a shallow/blob-filtered fetch. The donor pointer was
not advanced and no successful donor-freshness verification was recorded.

The source-file collision check against live claims passed before claiming
`0x003A1080`. No production source, preferred bank, symbol pin or function
ledger was changed. No `add_match` or production byte gate was invoked for
this still-nonmatching candidate. Exactly one blocked verdict is recorded.

`link_check.py game/GameEngine/Source/Common/BfmeTwoHundredSixteen.cpp` cannot
give a preview because this worktree has no `build/link_census/link_index.pkl`.
Current linking is therefore unknown, not proven by the provider's masked
match. No new body was admitted, so this retry contributes zero matched and
zero newly credited linked bytes. No link-cycle receipt is claimed.

Reopen on independently supported source/lifetime or compiler-scheduling
evidence predicting the early comparison and delayed `setne`, not another
unbounded spelling sweep. The unresolved lexical identity and inherited
callee declaration also need reconciliation before eventual admission.
