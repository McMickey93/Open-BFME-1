# Readonly float references: two gate-debt repairs

Input revision: `d6c4b40659`. No function identity, boundary, ABI, layout or
global ownership changes. The existing opaque names remain opaque.

## BFME 1 evidence

`BfmeA1269::bfmeGet1269`, RVA `0x005FAE40`, retains its 133-byte extent
through `RET 0x14` at `+0x82`. Its three FMUL operands read VA `0x0107533C`.
The existing matched `?g_rva0107533C@@3MB` data row independently establishes
the four readonly bytes `00 00 00 3f` as `0.5f`. The virtual call at `+0x1e`,
its five argument words, and the `TheWritableGlobalData` access are unchanged.

`parseFontDefaultSettings`, RVA `0x00477320`, retains 480 bytes through RET
at `0x004774FF`, with INT3 at `0x00477500`. The existing INI block registry
at `0x012B591C` and FieldParse table at `0x010F76AC` establish its identity.
The two comparisons read VA `0x01075350`; the existing matched
`?g_rva01075350@@3MB` data row establishes readonly `00 00 00 00` as `0.0f`.
Its calls, strings, exception lifetimes and ref-counted assignments are
unchanged.

Both sources formerly referenced external constant names that conflict with
older DIR32 names. They now express those proven values directly: a local
readonly volatile half constant in the arithmetic body, and plain zero
literals in the parser. No registry entry, pin, data row, alias or baseline
exemption is added.

## Compiler trials and acceptance

Private trials were compiled by `tools/probe.py` under
`build/gate-debt-1269/`; diagnostic objects were not used as verified builds.

| Trial | Size | Non-relocation differences |
| --- | ---: | ---: |
| Arithmetic: plain `0.5f` literal | 133 | 14; FMUL order reverses |
| Arithmetic: scale in three float locals | 137 | 55 |
| Arithmetic: literal with `/Op` | 143 | 58 |
| Arithmetic: local static const volatile half | 133 | 0 |
| Parser: local static const volatile zero | 484 | 312; compare reverses |
| Parser: local static const zero | 480 | 0 |
| Parser: plain `0.0f` literals, selected | 480 | 0 |

The arithmetic TU uses default MSVC 7.1 `/O2 /GR- /EHsc-`, no includes or
overrides. The parser retains its existing `/O2 /Ob1 /DNDEBUG /DWIN32
/D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB` controls and
`inputs/reference/shims/asciistring_downloadmanager` header context.

Normal scoped builds pass both bodies. The arithmetic gate verifies three
local readonly loads and four remaining DIR32 references; the parser gate
verifies two float literals, its diagnostic string and seven remaining DIR32
references. Both have zero baselined body findings.

The keyed `repair_queue.py pass-test` for `?g_rva0107533C@@3MB` passes on the
arithmetic TU. The zero-constant keyed test selects `Drawable.cpp`, whose
remaining name mention is a comment; the parser is separately verified so
that success on the already-repaired consumer is insufficient by itself.
That test passes all 100 Drawable rows and its existing data row. Both keyed
exemptions are removed, reducing the repair queue from 1014 to 1012. Existing
data providers remain unchanged. These are gate-debt reductions, with no new
authored C++ bytes or claimed linked-byte gain.

The read-only BFME 2 revision
`8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9` was searched for the existing
names and parser unit. No corresponding donor identity was established;
these repairs rely on BFME 1 instructions and existing data evidence.

## Other reviewed debt, retained

The AIGuardRetaliateMachine vtable exemption remains necessary: its scoped
test still emits the conflicting vtable name at VA `0x01096420`.

The scalar codec entries `0x009A91D0` and `0x009A92D0` individually pass
their provider tests, but the installer at `0x009B0D60` still fails against
obsolete same-identifier no-argument DIR32 records. Both exemptions were
restored. The sanctioned retirement requires the old bare identifier to be
absent, which these signature-only corrections cannot establish. No bypass
or record change was attempted. All three installer-unit byte rows and its
data row otherwise pass. Their claims were released.

The subsequent shell-hook test at RVA `0x0051E0F0` still fails: the consumer
references `?TheShellHookNames@@3PAPADA`, while the recorded DIR32 identity
at VA `0x012B3DC0` is `?TheShellHookNames@@3PAPBDA`. The provider's mutable
pointer table and the recorded const-pointer type require independent owner
reconciliation. The test restored its exemption; no naming or data-pin
workaround was attempted.

Three further readonly-constant debts cannot reach the sanctioned pass-test.
`repair_queue.py pass-test` reports `no source spells ...; nothing left to
verify` for `?g_real3f400000@@3MB`, `?g_real3f0ccccd@@3MB`, and
`?g_bfmeRva0109A028@@3MB`. The source locator searches the full decorated
name, whereas AudioManagerInit.cpp and AIFollowWaypointPathState_onEnter.cpp
spell the bare C++ names. Existing matched data rows establish the audio
values 0.75f and 0.55f; the waypoint body's tracked evidence establishes its
150.0f operand. Literal repair remains an untested lead, not a verified
improvement. The refusals were recorded through `re_log.py`; no source,
tool, pin, data row or exemption was changed, and both claims were released.
