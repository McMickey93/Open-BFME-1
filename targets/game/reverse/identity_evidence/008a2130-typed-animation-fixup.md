# 0x008A2130: typed loaded-animation fixup

## Scope and status

The whole-TU donor-context reconstruction has passed native qualification:
all 1,092 bytes of `0x008A2130`, including its switch table, and the existing
56-byte wrapper at `0x008A2580` verify through the normal relocation-aware
byte gates. Unmodified `add_match.py` admitted the C++ body in place of its
generated assembly row. The exact native-qualified commit
`bb30874d1638178f4ff0ec79daa299e5c3d8e109` is published on official master.
Its `tools/progress.py origin/master` receipt measures **+1,092 C++ exact
bytes**, with the same decrease in ASM-only exact bytes.

Candidate 00 left one non-relocation byte in an assignment self-comparison.
Candidate 01 exchanged only that comparison's written operands, plus a
header comment, and matched completely. The measured compiler effect and
qualification evidence appear below. Fresh-base qualification retained the
same source and admitted bytes. This record makes no fresh link-census
coverage claim.

The whole-file destination is
`game/Libraries/Source/Apt/BfmeFixup008A2580.cpp`. EA file evidence associates
both bodies with `AptAnimation.cpp`, but that canonical source/header does
not exist in this checkout; the existing wrapper is the concrete source
owner. A nearest-neighbor suggestion of `BfmeConv1996` is not ownership
evidence.

Both bodies were claimed for this recovery under
`github:mcmickey93:bfme1:cpp-loop-3`, lease
`e8bda153fad7486f8632b608a4b28259`, claim commit
`97d5073aecf605094b3a53d2b2a0b18a91735c82`. The whole-TU qualification also
verified the wrapper after its void-symbol/fastcall cast was replaced by
the actual typed member call. Its relative-pointer adjustment, flag clear
and inverse adjustment were retained.

## Independently established extent and ABI

The executable body is 1,050 bytes (`0x41A`), including the three-byte `ret 12`
starting at `+0x417`. The earlier 1,047-byte assignment stopped before that
instruction and is not the body extent. Two alignment bytes `8B FF` occupy
`+0x41A..+0x41B`. Ten DWORD jump-table entries occupy `+0x41C..+0x443`;
`INT3` starts at `+0x444`. The full ledger/probe extent is therefore 1,092
bytes, including the compiler-generated table. All table targets and direct
branches land on internal instruction boundaries.

The wrapper and helper together prove an ECX receiver and three stack
arguments: base pointer, constant/chunk pointer, and load context. The helper
ends in `ret 12`. The existing address-qualified declaration is retained:
`void BfmeFixup2580::helper(void *, BfmeFixupChunk2580 *, void *)`.
The wrapper's `BfmeFixupChunk2580::m_rel` remains at `+0x1C` and the owner's
flag remains at `+0x30`.

## Prior work and the new hypothesis

The original partial body covered only pointer fixups. The complete prior
pass, logged at `re_attempts.log:54375`, added dispatch, callbacks and owning
string/handle cleanup. Its best bank emitted 1,056/1,092 bytes, with 785
non-relocation differences, 29 relocations and measured quality 0.2152;
the first difference was saved-register/base-load order at `+0x17`.
The earlier no-Wine deferral did not test another implementation.

The BFME 2 homolog at `0x006E5050` is matched over its full 2,172-byte extent
in `Code/Libraries/Source/Apt/AptAnimation.cpp`, at verified donor revision
`beed8a16790a6812231ac7b05e3e6893e4cb5d1b`. It supplies a typed character
union, import/export/action records, and a macro that repeats its field
expression in the null check and relocation store. These contexts were not
tried in the old raw-Word bank.

Two BFME 1 observations independently motivate that transformation:

- Nested fields reload their address chain after the null test, for example
  `+0xCB -> +0xD2`, `+0x18C -> +0x194` and `+0x2B1 -> +0x2B8`. The old
  `fixPointer(Word &, Word)` binds the field address once. The repeated-lvalue
  `RVA008A2130_OFFSET` spelling follows the observed reevaluation.
- Cases 5 and 9 have distinct call blocks at `+0x205` and `+0x275`, including
  different argument-register preparation. The old bank merged them into a
  single `case 5: case 9:` block. The donor keeps them separate, and this
  candidate does the same using separate union members at the same `+8`.

The candidate follows the donor's typed field/loop context while retaining
BFME 1's real callees, callback cells and existing owning temporary cleanup.
Donor assertions and case 12 are omitted: BFME 1's table has exactly ten
entries covering types 1-10. Original source names for the views are not
proven, so their names retain the target RVA. This is material donor use and
is credited by the landed commit's `[BFME 2 donor]` title prefix.

## Field and stride audit

| View | BFME 1 offsets or stride |
|---|---|
| Existing owner | character count/table `+0x0C/+0x10`, import count/table `+0x20/+0x24`, export count/table `+0x28/+0x2C`, flag `+0x30` |
| Character header | type `+0`, parent pointer `+4`, discriminated payload begins `+8` |
| Case 1 | callback result at `+0x18` |
| Case 2 | relocated pointers at `+0x34/+0x38` |
| Case 3 | relocated pointers at `+8/+0x10` |
| Case 4 | pointers `+0x24/+0x28/+0x30`; condition count `+0x34`, condition table `+0x38`, trailing pointer `+0x3C` |
| Action condition | stride 8, stream pointer at `+4` |
| Cases 5/9 | existing `Rva008D32B0` receiver at character `+8`; its canonical 12-byte prefix is reused |
| Cases 6/7 | callback result at `+8` |
| Case 10 | count/table `+0x30/+0x34`; record stride `0x38`, glyph pointer at record `+0x34` |
| Export | stride 8: pointer at `+0`, index at `+4` |
| Import | stride 16: pointers at `+0/+4`, unmodelled word at `+8`, owning four-byte handle at `+0x0C` |

These are data-format views of accessed fields. They do not assert a complete
animation class identity or extra runtime ownership. The import's first
pointer is passed to the existing string setter, supporting its string type;
other field roles carried from the donor remain structural inferences.
No canonical AptAnimation/record/RefHandle header exists under `game/` for
this view. No shared header is edited or replaced.

## Canonical direct callees

`tools/callees.py 0x008A2130 1092` finds seven distinct named targets.
Their contracts were checked against the full target paths and matched
providers, rather than accepting the inventory's ABI heuristic alone.

| Target RVA | Existing binding and contract |
|---|---|
| `0x00894D80` | `Rva00894D80Accessor::increment(unsigned *)`, cdecl, one pointer, DWORD result |
| `0x00894D90` | `Rva00894D90Accessor::decrement(unsigned *)`, cdecl, one pointer, DWORD result |
| `0x00895320` | `bfmeDropA(void *)`, cdecl, one pointer |
| `0x0089E680` | `BfmeStrVKI::bfmeSetVKI(const char *)`, thiscall, `ret 4`; existing nothrow declaration retained |
| `0x00895A00` | `Rva00893030Manager::rva00895A00(BfmeStrVKI *)`, thiscall returning owning `RefHandle008958D0`; hidden result pointer plus key, `ret 8` |
| `0x008D32B0` | `Rva008D32B0::relocate(unsigned, int, void *)`, thiscall, `ret 12`, reached separately by cases 5 and 9 |
| `0x008CC560 -> 0x008CBDF0` | existing generated thunk identity, full parser target is cdecl with four DWORD arguments and plain `ret`; caller ignores return |

The existing thunk symbol is declared through its generated linker identity
with the independently established typed signature. No routing pin or guessed
semantic name is introduced. The counted handle and string cleanup retain the
prior bank's direct canonical accessors and free-slot use.

## Existing data and indirect-call contracts

The callback-cell symbols remain the existing generic pointer declarations,
preserving their canonical decorated names and owning TU. Only the local
call-site views carry the proven argument/result contracts:

| VA / symbol | Observed caller contract |
|---|---|
| `0x01337898`, `g_bfmeSlot24VB` | cdecl, context plus index, EAX word stored in character `+0x18` |
| `0x0133787C`, `g_bfmeSlot17VB` | cdecl, context/index/name pointer, EAX word stored at `+8` |
| `0x0133788C`, `g_bfmeSlot21VB` | cdecl, context plus index, EAX word stored at `+8` |

The complete installed routes for slots 21/24 reach the same matched hash
lookup through ILT `0x0003291B -> 0x00786BD0`; slot 21 adds a null-owner guard.
One existing wrapper's `MemoryPool::freeBlock` label is misleading and is not
inherited here. Slot 17's installed target is a complete return-zero stub.
The evidence supports opaque word/pointer returns, not invented callback
service names or an unrelated wrapper repair.

The existing manager cell remains `g_rva00893030Manager` at VA `0x013377D4`.
The string release cell remains `g_rva01337A30AllocPair` at VA `0x01337A30`,
a pointer to the established two-slot allocation/free table; only its `+4`
free slot is used. All five cells already have canonical matched data rows.

## First measured native result and table audit

Workflow `40190138970`, job `121159185159`, compiled candidate 00 with the
project's original MSVC 7.1 toolchain and normal settings, retaining the
source directives `/DNDEBUG /MD /EHsc`. Its immutable fork payload was
`2c4bb620e2c39962b2e48e6957b6083dac1b7c45`; its actual official base was
`3b375d6e2844dbceda9f4e2fd50e88bf77f0703c`. The source blob was
`b303fd8e828166f77839d2a59d3c2f81f071058c` (SHA-256
`9a64be13dfad564e8e7c55fdda2bc6e4fc1fc7920f919023aee4d997c4005667`).
The downloaded artifact `12597639301` was verified against SHA-256
`acc7d80b62b35f6b21ecfc47597fcdcebd12f2001fa872264f3d7af373f8b1e3`.
It contains the raw primary comparison `046-probe-0x008A2130.log`, raw
wrapper comparison `048-probe-0x008A2580.log`, immutable inputs and objects.

The primary measures 1,092/1,092 bytes with 30 relocations. The only
non-relocation difference is `EF` versus `FD` at `+0x36D`, the ModRM byte
in `cmp ebp, edi` versus `cmp edi, ebp` at `+0x36C`. Every other
non-relocation byte matches, including `ret 12` at `+0x417` and `8B FF`
alignment at `+0x41A`. The existing wrapper measures 56/56 bytes, exact
modulo relocation slots.

The probe's ten relocation-layout warnings and extent warning are caused
by decoding the switch table as instructions. They do not establish an
extra executable tail or ten wrong code operands. An independent read of
the retained COFF symbol/relocation table confirms that its dispatch DIR32
at `+0xAA` targets the local table at `+0x41C`. Each of the ten table
DWORDs has a DIR32 relocation to a defined local label in this same
function's section. Resolving that label plus its object addend gives
exactly the retail target below, and every target is a decoded instruction
boundary within the executable `+0x000..+0x419` range:

| Case | Table slot | Target offset | Target RVA |
|---|---|---|---|
| 1 | `+0x41C` | `+0x0AE` | `0x008A21DE` |
| 2 | `+0x420` | `+0x0CB` | `0x008A21FB` |
| 3 | `+0x424` | `+0x0F5` | `0x008A2225` |
| 4 | `+0x428` | `+0x11F` | `0x008A224F` |
| 5 | `+0x42C` | `+0x205` | `0x008A2335` |
| 6 | `+0x430` | `+0x21C` | `0x008A234C` |
| 7 | `+0x434` | `+0x25B` | `0x008A238B` |
| 8 | `+0x438` | `+0x2DE` | `0x008A240E` |
| 9 | `+0x43C` | `+0x275` | `0x008A23A5` |
| 10 | `+0x440` | `+0x289` | `0x008A23B9` |

Retail `INT3` padding begins at `+0x444`. The diagnostic private object and
the separately built native match object contain identical primary bytes
and relocation lists. Normal admission and publication subsequently used
the ordinary build and byte gates. The ignored audit receipt is
`build/008a2130-canonical/00-native-table-analysis.json`.

## Candidate 01: one operand-order correction

The actual register lifetimes explain the single difference. At `+0x363`,
`mov ebp,eax` retains the returned/source handle address; at `+0x368`,
`lea edi,[ebx+ecx+0x0C]` forms the destination handle address. The following
comparison is the inline assignment's self-assignment check. Candidate 00
spells it `if (this != &other)`, producing destination-first `cmp edi,ebp`.
Candidate 01's only code change spells that condition as
`if (&other != this)`, targeting the retail source-first `cmp ebp,edi`.
Both pointer expressions are free of side effects, and exchanging equality
operands preserves the condition.
The assignment, reference counts, cleanup, EH lifetimes, ten-case dispatch,
wrapper, and compiler settings are unchanged. Its header comment is also
made timeless: native qualification must verify both complete bodies.
Native 01 confirms that effect: comparing the retained 00 and qualified 01
objects gives exactly one raw byte change, `FD -> EF` at `+0x36D`, with
identical relocation lists. The wrapper's raw bytes and relocations are
unchanged.

Candidate 00 remains preserved in ignored
`build/008a2130-canonical/00-donor-typed.cpp`, with its original evidence and
wrapper source beside it. Candidate 01 is retained as
`build/008a2130-canonical/01-source-first-compare.cpp`. The normal admission
tool removed its `present-unmatched` marker; that removal is the only
source difference between the immutable 01 input and qualified source.
No ledger or pin was edited by hand.

## Measured native qualification

The isolated 00 -> 01 effect was verified in workflow `40190782271`, job
`121161143406`, on reviewed official base
`3b375d6e2844dbceda9f4e2fd50e88bf77f0703c`. Artifact `12597726406` was
verified against SHA-256
`90b3f323a271356df5af8a04fba4ff3f9734b2ea72576e34c639f66849461e1a`.
Its complete immutable inputs, output files and raw commit identity passed
hash verification.

The frozen source was blob `a979126d294dfb0481667acb411e1746d1425765`,
SHA-256 `4e5b94c8e90cbabb2209817451b2c3f7030ddc176af34decc4201fab73d8d8de`.
Normal admission removed only the 78-byte standalone `present-unmatched`
marker, producing blob `f14613ed3b1c573442cb671b0c666487f6916a8a`, SHA-256
`dc12d7543f545916d0e3145c48b09a437554ea5818eca99713d22b9a999bea98`.
These same input and output bytes were retained in the fresh-base reruns.

Both probes were exact. Unmodified `add_match.py` replaced the generated
`d_008a2130` row with the typed helper, verified the normal build and cleared
the old bank. The ordinary scoped build, normal commit hook and full
pre-push gate all passed. The byte gate verified 2/2 functions and all five
DIR32 data references. Body guard reported zero findings and eleven local
table entries: the dispatch reference plus ten targets. Full pre-push
checked three outgoing verification selectors. No callee/data pin or
baseline exception was added.

The decisive logs are `050-verified-add-match-0x008A2130.log`,
`051-ordinary-scoped-build.log`, `081-normal-pre-push.log` and
`083-session-progress.log`. Exact C++ coverage increased from 7,596,632 to
7,597,724 bytes against that base, converting existing ASM-only coverage
into real C++ while total exact coverage stayed unchanged.

## Final qualification and publication

Workflow `40194846615` qualified the unchanged input on reviewed official
base `afb8c1a3d04f38ded951b89e483b72f2f4a3f3bb`, using immutable fork payload
`98f120fc28aa9f3c369c1cc13a985d000ab3b5d4`. Artifact `12599039336` was
verified against SHA-256
`dac2dffca098f4b90d36449a9ca6bf7c6d643138443af9a3b3f38bcb1ce7b835`.
The input and output file hashes, raw commit identity, normal commit gate
and full pre-push receipt all passed. Both complete bodies remained exact,
and the progress receipt again measured **+1,092 C++ exact bytes** against
that base.

The exact qualified commit was published to official master and confirmed
by an ordinary fetch, with no code or history rewritten:

| Receipt | Value |
|---|---|
| Landed commit | `bb30874d1638178f4ff0ec79daa299e5c3d8e109` |
| Parent | `afb8c1a3d04f38ded951b89e483b72f2f4a3f3bb` |
| Tree | `b7be338ee42d3c75ea09881c72b0fab8668b1977` |
| Admitted source blob | `f14613ed3b1c573442cb671b0c666487f6916a8a` |

The landed source has the same SHA-256 recorded above for the qualified
01 output. This follow-up changes only the evidence and the concise
compiler note in `docs/shape_levers.md`.
