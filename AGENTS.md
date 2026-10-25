## Instruction freshness

Before continuing work, reread `AGENTS.md` if 24 hours have elapsed
since the last read. Reread it immediately whenever a user message
or commit message reports an edit to `AGENTS.md`.

# Contributing

Many agents push to `origin/master` all day. Keep each change small, verified
and easy to rebase. `docs/matching.md` covers byte matching and
`docs/structural.md` manual reverse engineering.

## Verifier upgrade

Live checks: jump tables, bytes past a row's extent, TU-local data, `gen-alias`
only on a retail twin, unrecorded globals resolved by retail address.
`hatch_counters.py` counts escape hatches. Pause bulk renames. Pushes stay
direct. Lanes and plan:
`targets/game/reverse/analysis/verifier_upgrade_plan.md`.

## Setup

- `git pull --rebase origin master`. Once per host:
  `python3 -m pip install -r tools/requirements.txt`.
- On Windows use `.\build.cmd` (same arguments as `./build.sh`) and
  `tools\fleet\launch_fleet.cmd`; run other scripts as `bash tools/<name>.sh`, never
  directly from PowerShell or cmd. Python is `py -3` in PowerShell.
- `python3 tools/check_csv.py` must pass before other work.

## Work selection

An explicit request or assigned lane overrides the queue. WorldBuilder work
uses `python3 tools/worldbuilder.py next` and `docs/worldbuilder.md`, with its
own ledger and verification.

1. **Linking first.** `tools/link_check.py next` claims the name
   alone blocking the most unlinked bytes; `near` lists files linking once
   calls use the pinned row's name (never `/alternatename`). Fix it minimally:
   keep the retail-proven copy, remove a wrong definition nothing
   verified needs, define one datum (`tools/add_data_match.py`), or map an
   import to retail's. Gate, push with its `Claim-Lease:` trailer and
   `link_check.py <file>` before/after in the
   message, then `claims.py release --landed <sha>`. STLport, string and
   `The*` names have one owner each (`next --family F`).
   Never reorder `functions.csv` rows for COMDAT selection.
   **Sweep BFME 2 linking repairs before rediscovering shared fixes.** For the
   selected blocker or family, inspect the BFME 2 reference's shared headers,
   providers and consumers, global ownership, import bindings and COMDAT
   repairs, not just its reconstructed function bodies. Consult its relevant
   commits and verification evidence; prioritize supported repairs that unblock
   the most BFME 1 bytes. A same-name or link-clean BFME 2 provider is a lead,
   not proof. Reconcile BFME 1 layouts, ABI, paths and thunk-versus-body
   identity before adapting the repair. Verify affected BFME 1 bytes and check
   providers and consumers together; an unchanged caller body alone does not
   prove that the selected provider is correct or the unit links. If the census
   index or current dependencies are unavailable, report the preview as unknown
   rather than claiming linked bytes. Record donor evidence and ruled-out
   adaptations, sweep related units after a supported fix, and batch compatible
   repairs. Revisit recorded blockers when their dependencies or donor evidence
   change instead of repeating unchanged scans.
2. **Run the reference lanes before dump or structural reconstruction.** They are
   separate from the default picker; a zero result in one is no reason to skip
   the others. Follow the BFME 2 and Zero Hour reference pass below before
   choosing a new reconstruction target.
3. `python3 tools/next_work.py` is the byte-matching default and explains its
   tiers. Its `finish` tier serves a banked attempt scoring 0.90+: start from
   that stash, even after a later `blocked`.
4. Most remaining work is anonymous `?d_` bodies; the brief's evidence pack
   is the lead. A proven identity gets its real name, evidence cited. An
   unproven one gets an opaque name that keeps the address
   (`RvaXXXXXXXX::method`, `?dup_XXXXXXXX`). Never ship a plausible
   guessed name: no gate can see it. `docs/carving.md` and
   `tools/carve_unclaimed.py` serve bodies found by boundary evidence.
5. Named `__emit` lifts are dumps too; `python3 tools/lift_lane.py` lists them.
   Names are often wrong; follow the brief's EXTENT and IDENTITY CHECK
   lines. Write the real body in the TU its `// readable body of` comment
   names, land it with `add_match --replace-existing` at the proven extent,
   delete the naked function.
6. When `next_work.py` is dry, `python3 tools/list_naked_candidates.py game`
   serves `game/gen_asm/` dumps with proven boundaries.
7. Replacing generator-written C++ scores +0; take it last. Only
   `gen-tgrid`/`gen-shim` rows have source to write.
8. **EA renames.** `python3 tools/ea_queue.py next` serves one rename to EA's
   own name and every file it touches.
9. **Names.** `python3 tools/name_lane.py next --model <your model>` serves one
   file's placeholder names. A name lands only when another vendor's model
   proposes it; never rename placeholders by hand.

`tools/eligibility.py` alone decides whether a body is open work; never
re-derive it.

## Reference-source sweeps

Use `inputs/reference/open-bfme-2` as a source and evidence reference, not a
replacement for BFME 1's own build inputs. Initialize it with
`git submodule update --init inputs/reference/open-bfme-2`.
Initialize cross-repository references without recursion. Do not initialize a
nested reference back to BFME 1 or BFME 2. Initialize other required build
dependencies explicitly. Zero Hour is already available in BFME 1's own
`inputs/reference/CnC_Generals_Zero_Hour/`; do not obtain a second copy through
BFME 2.

1. **Sweep BFME 2 before rediscovering shared fixes.** Compare the current BFME 1
   target or blocker family with BFME 2's `Code/`, `reverse/functions.csv`,
   shared headers, linking repairs and dependency reconciliations. Use narrow
   `rg` searches for supported names, callers, strings and class families;
   inspect relevant donor commits and their verification evidence. Consult
   BFME 2's `docs/recipes.md` and pertinent `reverse/attempt_support/` records.
   `python3 tools/bfme2_sweep.py linking --limit 20` ranks blocker-provider
   packets; `sources --limit 20` inventories corresponding source units. Run
   `scan` after donor/target images, ledgers or reviewed donor sources change;
   it caches relocation-aware binary placements. `ranked` serves exact-unique
   leads; `near` serves approximate ones; `show --rva 0xRVA` explains a target;
   `packets` writes work packets. These commands recheck eligibility and shared
   claims; `--offline` means inspection only. Stale input hashes require a new
   scan. Ambiguous, truncated and conflicting-string matches never qualify as
   unique recoveries. No search result establishes identity or verifies a row.
2. For Zero Hour, use `GeneralsMD/`, not `Generals/`. Run
   `python3 tools/zh_sweep.py compile` when the object cache is missing or its
   source, headers, toolchain or flags changed (`--force` for changed inputs),
   then `python3 tools/zh_sweep.py match` and
   `python3 tools/zh_sweep.py packets`. Inspect the resulting evidence before
   selecting a new dump or structural target; an empty exact-match result does
   not exhaust near matches or adaptable reference source.
3. Try a supported donor repair directly, then adapt it locally. Preserve
   BFME 1 layouts, addresses, ABI, behavior and compiler context. A BFME 2 name,
   placement or linking result is a lead, not BFME 1 proof. Claim the BFME 1
   target, port into its proper `game/` unit, and pass BFME 1's identity,
   boundary, relocation, byte and linking checks. Never edit the donor tree or
   redirect BFME 1's build to BFME 2's toolchain or nested references.
4. Record the donor revision, paths and evidence reviewed, whether a repair is
   inherited, applicable, blocked or inapplicable, and the concrete reason in
   the attempt evidence. Reuse that record while its inputs remain unchanged;
   revisit it when donor evidence or dependencies change. Do not repeatedly
   scan an unchanged donor tree. After a supported repair succeeds, sweep
   related BFME 1 units for the same cause, batch compatible fixes and refresh
   the affected blockers.

**Translate the donor layout explicitly.** Paths in BFME 2 sources, ledgers,
flags and handoffs are relative to BFME 2's root, not this checkout:

- BFME 2 `Code/<path>` normally maps to BFME 1 `game/<path>`; confirm the
  official BFME 1 unit and exact filename case rather than blindly copying or
  overwriting an existing source.
- BFME 2 `reverse/` evidence corresponds to BFME 1
  `targets/game/reverse/`; addresses, symbol pins and ledger rows are specific
  to each executable and must be established independently.
- BFME 2 `reference/open-bfme-1/inputs/reference/`, `inputs/vendor/` and
  `inputs/toolchains/` under that nested BFME 1 prefix refer to this repo's own
  corresponding `inputs/` trees. Older donor paths may use `reference/`,
  `vendor/`, `build/toolchains/` or `Code/` instead. Resolve the actual paths at
  the reviewed revisions; never initialize BFME 2's BFME 1 reference to satisfy
  those stale paths.
- Rewrite each donor `// cl:` include path and relevant quoted include against
  the intended BFME 1 header. BFME 2 `reference/shims/` has no automatic
  one-to-one mapping to BFME 1 `inputs/reference/shims/`: check definitions,
  layouts and include order, using a justified local adaptation when needed.
  Preserve or deliberately reconcile compiler flags, defines and STLport
  selection; do not import BFME 2 compiler overrides by accident.

BFME 2's `tools/bfme1_sweep.py` and `tools/build.py` contain forward mappings.
BFME 1's `bfme2_trial.py` resolves known nested-input paths and explicit include
maps; unknown or missing paths fail rather than silently selecting headers.
Before judging a donor trial, verify every rewritten include directory exists
and inspect dependency output or compiler include tracing to confirm the actual
headers used. MSVC can ignore missing include directories and still compile
against unintended headers. Record the donor-to-local mapping and build context;
invalidate affected cached trials when mapped source, headers, flags or the
compiler change. A path/setup failure is not evidence the donor body is wrong.

An explicit assigned lane still takes precedence. Linking remains first; use
this donor pass within linking work as well as before new reconstruction.

## Prefer coverage-first reference sweeps

Prefer reference-source sweeps first whenever compatible reference units exist;
optimize for verified unique bytes per effort by batching compatible units,
especially library families whose dependencies already exist. Escalate before
abandoning a reference for dump reconstruction:

1. Direct reuse or small evidence-backed repair (constants, declarations,
   offsets, helper selection, compiler settings) that preserves the verified body
   and semantics.
2. Moderate repair of control flow, data access, calls, layouts or compiler
   shape while identity and relationship stay well supported. Make evidence-backed
   adaptations; preserve the reference function's established purpose and
   semantics while reconciling target-specific differences.
3. Substantial reconstruction from the reference while retail evidence supports
   identity, ABI, behavior, call relationships and data usage; the reference
   stays the semantic and structural guide.
4. Byte-true reconstruction of the `game/gen_asm/` body as real C++, only once the
   reference paths are exhausted or no longer applicable.

Use compiler variants from matched siblings, with caching and isolated trials;
preserve provenance, dependencies and compiler settings; continue through viable
independent candidates; commit successful imports with their ledger updates
coherently. Do not force a weak reference: once evidence no longer supports the
same identity or semantics, or reasonable repairs stop progressing, move on.
Re-run sweeps as dependencies, identities, compiler configurations and sibling
matches land.

## Compile BFME 2 donors beyond byte matches

A lack of byte-identical BFME 2 retail bodies does not exhaust reusable donor
source. Before treating BFME 2 references as exhausted, compile plausible clean
C++ donor TUs with BFME 1's toolchain and settings (flags from matched siblings),
adapting paths as above, and compare the emitted bodies with the BFME 1 retail
target. Prioritize supported identities and siblings of successful transfers;
exclude dumps and retired or refuted candidates unless new evidence addresses
the earlier finding. Use `python3 tools/bfme2_sweep.py compile Code/path/File.cpp` for a private
compile; `--map MAP.json` supplies explicit donor include-prefix to BFME 1
root-relative directory mappings. It records compiler arguments, include traces
and stable dependency hashes without touching shared objects. A failed compile
keeps its diagnostics. Run `match build/bfme2_sweep/trials/ID/trial.json` to
place the compiled COFF bodies in BFME 1 retail, then `packets --matches
build/bfme2_sweep/trials/ID/match.json` for current eligibility/claim context.
COFF relocation masking is discovery only; full relocation verification follows.
Never claim the external donor path as BFME 1 source. Port supported bodies into
an allowed `game/` TU, preserving the donor revision, flags and dependencies,
and pass BFME 1's scoped build and normal byte and identity gates. A placement
proves neither identity nor recovery.

## Donor repair and landing tools

`python3 tools/bfme2_sweep.py globals game/path/File.cpp` proposes typed global
reference repairs from BFME 1's matched data ledger; `--apply` claims affected
rows, verifies providers and consumers, and restores its edit on failed byte
verification. It never creates vtable aliases or imports donor addresses.
`rehome --home game/path/Home.cpp --split game/path/Split.cpp` verifies whether
the home object reproduces every split row; `--apply --model MODEL` repoints
through `add_match.py`. Inspect an emptied split unit before deleting it; the
helper never deletes files. Use `link_check.py` for the current linking verdict;
missing census evidence remains unknown, even after a byte check passes.

`naming --source game/path/File.cpp [--donor-source Code/path/File.cpp]` prints
naming evidence for review, never votes or automatic renames. Keep these hints
out of independent blind-voting sessions.

After adapting a donor into `game/` and recording independent BFME 1 identity
and boundary evidence, `land --source game/path/File.cpp --name SYMBOL --rva
0xRVA --size BYTES --evidence targets/game/reverse/identity_evidence/NOTE.md
--model MODEL [--replace-existing]` claims the row and invokes normal
`add_match.py` verification. No sweep command commits or pushes. Use `--help`
on each subcommand for its options; global and rehome application is explicit.

## Investigate shared deltas first

When multiple failures suggest the same layout, offset, callee, compiler, ABI or
wrapper difference, test that shared explanation before retrying each body.
Apply a shared fix only where target evidence supports it; similar symptoms alone
do not establish a common cause. Do not repeat
attempts blocked on the same unresolved dependency: continue with independent
candidates and resweep affected units once it is resolved.

## BFME 2 reference freshness

Use the `inputs/reference/open-bfme-2` submodule for donor discovery and shared
reconstruction, linking and naming evidence. On initialization, and before BFME 1
work when the last successful check is missing or over 72 hours old, fetch
official `Open-BFME/Open-BFME-2` `master`, compare commit IDs, and preserve dirty
or unpublished submodule work.

Initialize cross-repository references without recursion. Do not initialize a
nested reference back to BFME 1 or BFME 2. Initialize other required build
dependencies explicitly.

For a routine update:

1. Record the previous verified pointer and checkout revision; update only a
   clean checkout to official upstream HEAD. Retain enough history to compare
   old and new donor inputs at the same BFME 1 revision.
2. Check changed donor paths, source flags and mapped include directories using
   the layout rules above. Inspect include traces where headers changed;
   compilation alone does not prove the intended headers were used. BFME 2 is
   a donor reference, not BFME 1's build dependency: verify affected donor compile
   trials and BFME 1 units, and run the full byte gate when shared build inputs
   change or the normal hooks require it. Compare failures against the previous
   inputs under the same conditions, repair update regressions and report
   pre-existing failures separately. Never weaken verification or silently
   substitute headers.
3. Refresh donor sweeps and compile trials affected by changed sources, headers,
   ledgers or settings. Record the donor revision with cached results; discard
   or regenerate results whose inputs no longer agree. Do not repeat an
   unchanged broad scan for each transfer.
4. Include the verified submodule pointer and required repairs in the next
   commit batch: advancing a local checkout does not update other contributors.

Record the successful check time and verified donor revision in ignored
`build/bfme2-last-check.txt` only after verification, or when upstream is already
at the verified pointer. Do not fetch per transfer. If an update is blocked,
keep the last verified inputs and report the exact blocker and attempted repair;
do not mark it successful or suspend future freshness checks indefinitely.

**Claim a body first:** `python3 tools/claims.py claim 0xRVA` (if held, take
another; claims expire after 4 h). After pushing, `claims.py release --landed`
frees what landed; `release 0xRVA` frees a banked, blocked or abandoned body.

**Before writing a body**, run `python3 tools/callees.py <rva> <size>` and use
the callee names it prints. A link failure against a real retail body usually
means a callee is named wrong, not a missing pin; never pin on a seat's say-so.
For a callee with no signature it prints `inferred ABI:`; declare it that way
before blaming your body.

**Small dependency repairs travel with the body.** If the scoped gate fails only
on an unresolved callee the body really calls, prove that callee's identity and
ABI independently, add one pin, run `tools/pin_consistency.py --check` and
rerun the gate, all in the same commit; use an address-derived name if its
meaning is unproven. Switch bodies when the evidence is ambiguous or the repair
spreads.

A staged source defining any function the ledger lacks is
refused. First run `python3 tools/find_declared_unmatched.py
<file>`: row the body, or mark a known unpinned one
`// ?<Class::method> present-unmatched`.

**Stay with one substantive target.** Before experimenting, read its banked
source, relevant attempt log entries, handoffs and prior compiler evidence.
Finish or revert each body or homogeneous trivial batch before the next.
After about 60 minutes without
meaningful progress, reassess; this is a review point, not an automatic stopping
time. Continue while testing a new evidence-backed hypothesis; identity,
layout, dependency and compiler discoveries count as progress. Bank and switch
when viable hypotheses are exhausted or a concrete prerequisite blocks further
work. Before declaring a function blocked, reassess independent explanations:
control flow, variable lifetime, types/layout, callee visibility and compiler
settings. Exhausting one family of source variations is insufficient. Do not
repeat disproven trials or leave a non-matching reconstruction in `game/`.

A persistent mismatch may reflect a compiler quirk or unexpected instruction
ordering. Compare the specific assembly difference, consult
`docs/shape_levers.md` and relevant BFME 2 recipes, then systematically test
justified equivalent C++ variants with isolated output paths. Preserve the
flags, minimal source transformation, generated-code effect, useful failed
trials and evidence for the next agent; distinguish observations from hypotheses.

**Isolate compiler experiments.** Keep diagnostic sources and objects in unique,
untracked `build/` paths. Any direct compiler helper call must use an explicit
private output path, never the shared `build/match/` object or dependency receipt.
Use the normal build command for verification; a diagnostic object must not be
reused as a verified cached build.

**Preserve successful compiler discoveries too.** When a recovery establishes a
reusable compiler-matching technique, add or refine a concise entry in
`docs/shape_levers.md`: the original assembly mismatch, minimal successful source
transformation, observed code-generation effect, compiler version/flags and
relevant translation-unit context. Cite the verified source or tracked evidence
and supporting commit when available. Distinguish the measured effect from its
hypothesized cause; do not claim broader applicability without testing it.

**Reconcile classes, not just bodies.** Private per-unit views of one class can
produce incompatible COMDATs and unresolved members even when individual bodies
byte-match. Prefer an existing evidenced canonical header over another private
view. For a shared repair, use `tools/class_contract.py` to establish BFME 1's
ABI from evidence and `python3 tools/header_adopt_lane.py order` to plan header
adoption. Reconcile the affected providers and consumers, verify each unit, and
check linking separately; compiling one caller does not prove the shared repair.
A BFME 2 header is a lead, not proof of BFME 1 layout.

## Work the file

Work the other queued bodies `next_work.py` lists in the same file together:
siblings share layout, offsets and callee pins. A shared header
edit costs a full gate: edit every dependent body and pay once.

## Batch homogeneous trivial recoveries

Atomic does not mean one function per commit. When bodies use one established
recovery pattern and form one coherent, reviewable change (tiny getters/setters,
thunks, wrappers, or reference transfers differing only by verified RVA or
offset), recover, ledger, verify and commit them as one batch, roughly 5-20
entries (a guideline, not a quota or hard limit). Similar instruction shapes do
not establish identity, types, calling convention or layout: verify each member
against its own evidence. Keep substantive reconstruction, or work needing
distinct identity, compiler, ABI/layout or reconstruction reasoning, in separate
commits. Verify the whole batch before committing. If a member fails, determine
whether that undermines the shared pattern; continue with the remaining members
only if their evidence and verification still hold, otherwise reassess the batch.

## Convert, verify, commit, push

1. Make the smallest source and ledger change for one function or homogeneous
   trivial batch, following the rule above.
2. `./build.sh <file-or-symbol>`. Poll any returned process or session ID;
   never launch a duplicate build.
3. Stage explicit paths only (never `git add .`); check every new ledger source
   is tracked.
4. Commit normally; never bypass hooks (`--no-verify`). A commit that stages a
   header or shim runs the full gate (40-60 minutes): poll it; never relaunch it
   or pipe it through anything that hides its exit code.
   Baselines may only shrink; never add a line to one to go green.
5. Accumulate verified commits and push them together when practical,
   especially banked attempts, blocker notes and homogeneous linking repairs.
   Keep substantive reconstructions as separate atomic commits. Then
   `git pull --rebase origin master`, `git push`, and pull again; on rejection,
   rebase, recheck the ledger, retry.
6. `python3 tools/progress.py origin/master` shows what your session added.

Never bare `git stash pop` (worktrees share one stash); park work in a patch
or temp branch.

**Integrate pull requests through local verification.** Never use GitHub's merge
button to land a PR: it bypasses the local byte gates. Fetch the PR branch,
cherry-pick the applicable commits onto current `master` (preserving authorship),
resolve conflicts, verify affected sources with the normal build and hooks, then
publish through the procedure above. Report the landed SHAs on the PR when
posting that follow-up is authorized. A prior PR check does not replace local
verification after integration.

## Verdicts and near misses

Use MASM or inline asm only for a proven codegen blocker (compiler machinery,
x87 shape, SEH). A `__declspec(naked)`/`__emit` lift is
not a conversion; hooks refuse it. Ghidra boundaries, xrefs and vtables
are identity evidence; decompiled C is not byte-match proof.

Record outcomes with
`python3 tools/re_log.py record <symbol> <rva> <size> <status> <evidence>`, never
by hand (`add_match.py --model` records `landed`; fleet: `BFME_MODEL`): cite the
boundary, `t=<minutes>`, `model=`, `blocker=<family>` (`tools/blockers.py`) for
a `partial` or long `blocked`, and `blocked-on=0x<rva>` for unlanded blockers.

Bank a near miss for the next agent:
`partial '<what is wrong>' --stash <your .cpp> --score <0..1>`; with no body,
record `blocked`. For 0.9+, run `tools/probe.py` and read
`docs/shape_levers.md` first.

**Preserve substantial failed work.** Before retrying any function, read its
attempt-log entries and linked evidence, regardless of how you selected it.
For substantive attempts ending `blocked` or `partial`, commit a concise handoff
under `targets/game/reverse/attempt_support/` and cite its tracked path in the
`re_log.py` evidence. Include hypotheses tested and ruled out, the exact remaining
mismatch or prerequisite, the best candidate and useful diagnostic diffs, and
relevant input revisions/compiler settings. Preserve better existing banks;
retain only artifacts needed to resume (diagnostic source as patches or
`.cpp.txt`). A simple blocker needs only a concise log entry.

## File placement

- The game baseline is `inputs/baselines/bfme1/retail-1.03-unpacked` (since
  2026-09-27); its
  `no_ground_truth` addresses are retired. Mods build from the workshop exe.
- Game source lives under `game/` at its official BFME path, MASM dumps in
  `game/masm_dumps/`, and scratch in untracked `build/`. Banked attempts
  (`targets/game/reverse/attempts/`) are evidence, never progress.
- Progress is `matched` rows in `targets/game/reverse/functions.csv` backed by
  real source and byte verification.
- Prefer TU-scoped shims to editing a shared header, but never redeclare a type
  a header already covers: `#include` it. `tools/adopt_header.py --fix-staged`
  does the swap; see `docs/header_adoption.md`.
- Never load `functions.csv`, `ghidra_functions.csv` or `exports.csv` whole; use
  `rg` or narrow filters.
- Preserve others' work; revert only your own attempt. No fallback paths:
  they hide mismatches.

## Preserve donor provenance

In evidence records, distinguish facts established from BFME 1 target evidence,
facts carried from donor source, and structural inferences. Record the basis for
identity and layout claims separately when their evidence differs. Exact bytes
alone do not establish a donor name or layout as a BFME 1 fact: preserve the
uncertainty until independent target evidence resolves it.

## Names and identity

**Sweep BFME 2 for naming evidence.** Before replacing placeholders in a
shared subsystem, consult the reference's corresponding declarations,
implementations, naming evidence and relevant commits. Prefer the same name
where BFME 1 evidence establishes the same identity or member role; retain
better-established EA names and BFME 1 naming conventions. Map by witnessed
class, behavior and relationships, not equal RVAs, offsets or filenames: shared
classes can have shifted fields or different meanings. Record the donor revision,
path, proposed mapping and BFME 1 evidence. Verify affected bytes and relocations;
an unchanged byte match does not prove a name is correct.

Use the existing evidence/header-adoption checks or naming lane to land names;
BFME 2 spelling alone is not an exemption. An agent-inferred BFME 2 name is a
hint, not an original EA name or an independent vendor vote. Keep donor name
suggestions out of blind-voting sessions; do not manufacture agreement by asking
both vendors to copy them. If evidence or the normal lane cannot establish a
name, keep the placeholder and record the lead. Batch compatible verified renames
rather than pushing each separately.

- A wrong name compiles to the same bytes. A matched caller naming the symbol
  is the strongest evidence.
- Ask before you invent a member, type or file name:
  `tools/name_oracle.py --class <C> --offset <N>`, and `docs/naming_evidence.md`
  for the rules. An address-derived name is honest; drop the address only for a
  name the evidence supports.
- `symbols.csv` pins are candidates: the resolver keeps the first address that
  reproduces retail, so a wrong pin still matches. Run
  `tools/pin_consistency.py --symbol <name>` before pinning and `--check` after.
  A `pinharvest` row proposes a name and proves nothing. A pin at an address
  that is only called through (an import thunk, a jump stub) needs a
  `route=<target>` note.
- Retail was linked without identical-COMDAT folding, so each body has exactly
  one identity. A second real name on an address is an over-claim to retire;
  `python3 tools/one_identity.py` shows the evidence.
- `?j_XXXXXXXX@@YAXXZ` is a 5-byte ILT thunk claimed by address;
  `?dup_XXXXXXXX@@YAXXZ` is a real body whose identity is unknown or disputed.
  Re-home a mis-anchored row to whichever fits its size. Never infer a
  funclet's `parent=` from adjacency.
- Read shipped `GlobalData` values with `tools/ini_value.py <Key>` before
  quoting them: `ini.big` and `_patch222.big` override compiled defaults.

## Generated and vendored claims

`gen-*` rows (`game/gen_small/`, `game/gen_asm/`) are byte-true placeholders,
not progress. Recover the identity in
clean C++ at the proper `game/` path and repoint the row with
`tools/add_match.py <real-name> <rva> <size> <source> --replace-rva <rva>`
(`--replace-existing` when the name is unchanged). Never edit files under
`game/gen_asm/` or `game/gen_small/`. After landing a batch, check your own
rows: one body per address.

`vendored=<lib>-<ver>` rows carry the upstream's real identities, and the header
comment names the exact release. Library sources live at their official BFME
paths; pristine C TUs compile against `inputs/reference/shims/gamespy/`, never a
real Platform SDK.

## Gate-read files

Sole writers: `dir32_addresses.csv` `dir32_record.py`; `$L` labels
`eh_state_pins.py --fix`; names `name_lane.py`/`ilt_repair.py`; `__imp_` pins
`import_binding.py`; data rows `add_data_match.py`. Record a refusal as
`blocked "false-reject <check>"`; never redo it another way.
