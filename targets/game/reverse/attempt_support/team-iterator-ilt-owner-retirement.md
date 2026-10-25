# Team iterator ILT ownership debt

A gate-debt repair completes an existing address identity; no executable body,
source name, type, ABI, pin, address or layout changes. The generated thunk is
still generated and no conversion credit is claimed.

## Independent BFME 1 evidence

At VA `0x00422A70` retail bytes are `E9 BB 5F 0A 00`, a complete five-byte
ILT jump to VA `0x004C8A30` (RVA `0x000C8A30`). The existing matched row is
`?j_00022a70@@YAXXZ`, RVA `0x00022A70`, size 5,
`game/gen_small/thunks_016.cpp`, with notes `gen-thunk;target=FUN_004c8a30`.
The boundary and route are byte-established. This address identity makes no
claim about the actual target's function signature or semantic class name.

The old record `?TheBfmeOwner_000CBB80@@3PADA` at VA `0x00422A70` has no active
source references, including its bare identifier. `dir32_record.py retire`
accepts the existing ILT owner and removes only that obsolete record. There
is no new data pin or alias.

Existing consumers spell `j_00022a70`, use it as a function address and retain
their current call declarations. A two-line comment in
`game/GameEngine/Source/GameLogic/ScriptEngine/ScriptActions_doTeamGiveNearestTeamUpgrade002FE270.cpp`
spells the exact decorated ILT identity and route so the repair queue can find
the consumer for its keyed test. Existing independent target evidence at
`targets/game/reverse/identity_evidence/002fe270-helper-visibility.md`
describes the iterator use and the target's `mov eax,[ecx+0x14]; ret` body;
this repair does not extend those layout or naming claims.

## Acceptance and measurements

- `repair_queue.py pass-test LINE` passes the edited consumer's normal scoped
  byte gate: 2/2 matched rows, one literal and four DIR32 references verified,
  zero body-guard findings. Only that exact exception is removed.
- Other direct pointer consumers and the existing five-byte thunk are checked
  together with a scoped `./build.sh` invocation:
  `ScriptConditionsEvaluatePlayerHasNumUnitsLoadedWithObject.cpp`,
  `ScriptConditionsRva0032C7F0.cpp`,
  `ScriptConditionsEvaluateUnitHasToggledWeapon.cpp`, and
  `row:0x00022A70:5:?j_00022a70@@YAXXZ`: 4/4 matched rows, twelve DIR32
  references verified, zero body-guard findings.
- No newly defined function exists (`find_declared_unmatched.py` passes).
- Record size 17,303 -> 17,302; baseline debts 1,002 -> 1,001.
  Exact C++ and linked-byte deltas remain zero. This completes an existing
  canonical-owner prerequisite; it does not establish whole-unit linking.

BFME 1 parent `98463eaba5`; source flags, headers, compiler and donor pointer
are unchanged. Read-only BFME 2 master was consulted for the corresponding
Team/ScriptActions family, but supplies no ownership proof for this BFME 1
ILT address. No donor source, identity, layout or linker directive is adopted.

The same retirement approach for non-generated GameSpy callback bodies is
blocked by disagreement between the retirement guard and consumer DIR32
verification. Those attempts were fully reverted and are separately preserved
in `peer-callback-owner-retirement.md` and the append-only attempt log.
