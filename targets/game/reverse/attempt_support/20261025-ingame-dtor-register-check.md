# InGameUI destructor: current-bank compiler controls

Target `??1InGameUI@@UAE@XZ`, RVA `0x0044AE70`, 936 bytes. Input BFME 1
revision `afb8c1a3d0`; preferred bank `attempts/0x0044ae70.cpp` (2026-10-20,
score 0.969) is preserved unchanged. Prior attempts 56543 and 57406 were read.
The primary InGameUI and secondary Snapshot vtables, retail cleanup offsets,
and RET at `0x0044B217` remain the existing identity and boundary evidence.
No new identity or layout claim is made.

A private baseline probe reproduces 936/936 bytes, 64 relocations, shape
1.000, and 29 non-relocation differences. The first is at +0x35:
retail `xor ebx,ebx`, bank `xor ebp,ebp`. Later retail keeps the movie
member address in EBP while the bank uses EBX. The remaining mismatch is
this exchanged register allocation, not a shorter body or missing cleanup.

The old 90-switch sweep at attempt 39838 used the obsolete 917-byte bank.
This pass tested all 90 combinations on the corrected 936-byte bank:
`/O2`, `/O1`, `/Ox`; `/Ob0`, `/Ob1`, `/Ob2`; default, `/G5`, `/G6`, `/G7`,
`/GB`; default frame omission or `/Oy-`. All compiled. Best results retain
29 differences and shape 1.000 under `/O2` or `/Ox` with `/Ob1` or `/Ob2`
and default frame omission. CPU tuning does not fix the swap.

Eight additional equivalent delete-expression trials are also inert:
for each of the first three singleton deletes, either capture the pointer
in a const local immediately before deleting it or add an explicit null
guard; or factor the first one / first three delete-and-null pairs through
one `template<class T> __forceinline` helper. Every trial emits the same
936-byte body with 29 differences. These transformations do not move the
register allocation. Earlier movie-helper and named-null trials need not
be repeated.

Compiler context is the bank's MSVC 7.1 `/DNDEBUG /MD /EHsc`, static STLport,
no STLport exceptions, WWLib and Common/System include directories, with
the standard build defaults. Diagnostic sources and objects stayed under
private `build/seat-ingame-20261025/` / diagnostic-tool output directories.
No diagnostic object was submitted as a normal verified build. No source
under `game/`, ledger, header, pin, or baseline was changed.

BFME 2 read-only revision `beed8a16790a6812231ac7b05e3e6893e4cb5d1b`,
`Code/GameEngine/Source/GameClient/InGameUIDtor.cpp` and its relevant header
adoption history were reviewed. Its teardown order supports the existing
semantic reconstruction; its three-base layout differs from BFME 1's
witnessed primary/secondary tables and supplies no register-allocation
repair. Donor offsets are not imported. The bank remains the best candidate;
resuming needs new compiler/source-shape evidence. Parent conversion still
blocks the six previously identified native cleanup funclets.

## AudioManager follow-up

Target `?isMusicAlreadyLoaded@AudioManager@@UBE_NXZ`, RVA `0x006AC1A0`,
456 bytes. Read the full attempt history through 57495 and the newer
`attempt_history/0x006ac1a0/55960d857e0e98d3c477e9a478a6b1975d41be823d8d1841a73641d132022abc.json`
alternative, rather than retrying the inferior preferred bank. `callees.py`
reports ten named direct targets and the two Interlocked IAT entries. The
existing vtable slot +0x138, GameAudio.cpp:274/282 callers and full retail
boundary remain the independent BFME 1 identity evidence.

A private probe reproduces 463/456 bytes, 19 relocations, normalized shape
0.972 and five structural differences. The missing entry `xor esi,esi`,
two immediate-zero stores, missing +0xDC alignment LEA and extra exit reload
are unchanged. All 90 compiler variants compile; none is exact. The sweep's
byte-difference ranking favors a worse 407-byte /Ob1 body (shape 0.730), so
that result must not replace the structurally stronger 463-byte alternative.
The flag sweep excludes /arch; a separate donor-style /O1 /G7 /arch:SSE
probe emits 273 bytes and shape 0.220, also inapplicable. No bank is replaced.

Read-only BFME 2 revision `16c3ea885a293dafc872dd5b67a59fa92b1d6407`,
`Code/GameEngineDevice/Source/MilesAudioDevice/MilesAudioIsMusicAlreadyLoaded.cpp`,
uses visible noinline ownership helpers and the same redundant iterator
self-comparisons already present in the latest BFME 1 alternative. Its
+0xB8 table, AudioEventInfo +0x49/+0xB0 fields, cursor ABI and 288-byte
body differ; no donor address, layout or name is imported. Zero Hour
`GeneralsMD/Code/GameEngine/Source/Common/Audio/GameAudio.cpp:963` supports
the broad search/file-existence behavior but lacks BFME 1's counted ownership
and flag predicate. Neither reference supplies a supported new register/PRE
repair. Diagnostics are private under `build/seat-audio-20261025/`.

## Other checked lanes

Fresh BFME 2 scan: 52,925 donor bodies, 672,372 placements. The first 60
eligible near results cover the same five previously blocked cleanup sites:
BF75F0 (callee identity/type conflict), C1F7B8 (base-destructor identity and
sanctioned DIR32 rename refusal), C23208 (InGameUI parent remains a dump),
BF9CF0 (map operator parent remains a dump), C08E90 (formatter parent remains
a dump). Reviewed their existing attempt records; unchanged blockers are not
recompiled. Current scan and packet output are retained under ignored build/.

Fresh Zero Hour match/packets serves only 0067EE40: a 29-byte donor fragment
inside the 937-byte target with 34 placements. This establishes no unique
identity or body extent. Generated packet edits were restored after inspection.

Gate-debt fallback lists 991 DIR32 exemptions. The keyed pass-test for
`?g_rva012F19E8WindowManager@@3PAVWindowManager@@A` builds BfmeConv2004.cpp:
1/1 function and two string literals pass, but DIR32 still rejects the
reference against R2Ptr012F19E8 and 66 competing records. The tool restores
its exemption. Existing active-consumer ownership must be reconciled; no
new aliases, pins, exemptions, data rows or source changes were introduced.
Previously recorded locator/active-alias refusals were not bypassed.

The first 20 exact-unique ranked results contain two eligible sites, both
already blocked: C217F4 (parent 0042CDF0 remains an unconverted 351-byte
body with 314-318-byte banks) and C61819 (native parent action exists but
its state1 temporary still uses AssetReference, conflicting with the proved
Rva009EBCE0AssetReference destructor at 0005C640). Reviewed records through
47481/55420 and identity_evidence/0005c640-registry-return-lifetime.md.
The return-view convergence spans Find_Asset and verified consumers; an
unchanged parent byte match does not settle the callee identity. Neither
placement is accepted or repinned. The remaining ranked entries are ineligible
existing source recoveries. No previous blocker has been bypassed.

No byte-exact recovery or gate-debt removal passed in this session. There
is no measured improvement to commit; these local attempt records and this
handoff are preserved for continuation, with all session claims released.
