# BFME2 tooling port: Phase 0 contract

Research date: 2026-10-22. BFME1 base: `aef2f1687742cdc91db274993cd41c3d036860ad`;
BFME2 reference: `02518d74b13d6fe74cadbd374e723e374591030e`.
`B1:path:line` refers to this repository at that base; `B2:path:line` refers to
the read-only clone at `/home/thag/Projects/Open-BFME-1/build/bfme2_port/bfme2`.
References describe those revisions, not a promise about a later master.
The owner plan is `/home/thag/Projects/Open-BFME-1/build/bfme2_port/PLAN.md:1`.
This phase changes only this document; it neither publishes a measurement nor
changes a validity rule, source body, ledger, hook, or publisher configuration.

The contract is to import measurement machinery while BFME1 continues to decide
validity. **A** means reusable algorithms, serialization, integrity checks,
ranking, or synthetic tests. **B** means a BFME1 adapter is required. **C** means
excluded for now, including policy changes disguised as dependencies. A tool can
contain all three classes. “Port” below never authorizes copying its dependency
tree or replacing an existing BFME1 gate. Later-phase proposals are explicitly
proposals, not descriptions of implemented behavior.

## Component manifest and same-name comparisons

Diffs were made from BFME1 to BFME2 with `git diff --no-index`; `+/-` counts are
added/deleted lines, including comments. They establish divergence, not superiority.
The test and import inventories below complete this table.

| tool | BFME2 feature | BFME1 current equivalent | port/adapt/skip | invariants |
|---|---|---|---|---|
| `link_cycle.py` | Measured graph, canonical object identity, normalized text hashes, environment binding, data-fold shadow series (`B2:tools/link_cycle.py:1745`, `:1789`, `:2477`, `:2581`) | Existing port with ILT routing, dump conversion and one text group; +955/-187 (`B1:tools/link_cycle.py:4`, `:265`) | **A/B adapt** graph/provenance; **C skip** BFME2 folding and section assumptions | Keep BFME1 routes, row kinds, generated-node closure exclusion and import source; measure only finalized verdicts. |
| `closure_report.py` | Conditional single-address gain, complete bounded blocker sets, measured graph versus replay labels, forced-closure verification (`B2:tools/closure_report.py:31`, `:260`, `:420`, `:528`) | No same-named file; cycle already computes greatest closure (`B1:tools/link_cycle.py:677`) | **A port**, **B adapt** replay/input/row interfaces | Unique-byte union; single scores are not additive; joint-only gain stays separate; fillers/stubs/unknowns never score. |
| `cycle_artifacts.py` | Immutable measurement identity, authenticated releases, integrity validation, atomic store, freshness and rule compatibility (`B2:tools/cycle_artifacts.py:9`, `:431`, `:797`, `:922`, `:1004`) | No same-named file; existing index/queue distribution is a different format (`B1:tools/link_check.py:53`) | **A port**, **B adapt** repository, trust, rules and members | Integrity is not authorship; explicit local bundles stay unauthenticated; no implicit stale override. |
| `publish_cycle.py` | Validate/bundle/publish lifecycle; inputs at measured commit; closure and diff companions (`B2:tools/publish_cycle.py:9`, `:124`, `:220`, `:316`) | No same-named file; `publisher*.py` publishes code, not cycle releases | **A/B adapt**; publication deferred | Never rewrite a published release; BFME1 profile must not require BFME2 data-fold rules. |
| `cycle_diff.py` | Interval-union gains/losses; category partition; changed-ruler detection; candidate commits (`B2:tools/cycle_diff.py:4`, `:105`, `:743`) | No same-named file | **A port**, **B adapt** tool list/optional fold diagnostic | Renames do not gain bytes; receipts and unions must reconcile; candidate commits are not established causes. |
| `data_back_rank.py` | Rank data identity failures by address, scope bindings, quarantine ambiguity; distinguish sole self-strict gain from closure (`B2:tools/data_back_rank.py:8`, `:24`, `:76`) | No same-named file; typed relocation and verified data machinery (`B1:tools/reloc_ledger.py:1`, `B1:tools/data_rows.py:1`) | **A/B adapt** an evidence view; **C skip** BFME2 data-fold exceptions and boot dependency | Derived data ledger is not verified ownership; no guessed scope or first-candidate resolution. |
| `census_receipts.py` | Witnessed preprocessor/object proof, collected failures, version-2 census-grade sidecars (`B2:tools/census_receipts.py:81`, `:163`, `:172`) | Existing implementation; +88/-161; mutable search-root handling, `ProofFailed`, diagnostic retry (`B1:tools/census_receipts.py:27`, `:136`, `:299`) | **B retain** BFME1 implementation; selectively adapt interfaces | Do not lose external/root include-search proofs, failure reasons, or current-object guarantees. |
| `link_census.py` | Reference reachability, `retail-truth-4`, rule history/rebaseline, unreferenced-copy diagnostics (`B2:tools/link_census.py:1005`, `:1059`, `:2685`) | Existing census; +1096/-781; strict copy rule, weak/alias rejudging, truth/policy fingerprints and bounded linker (`B1:tools/link_census.py:84`, `:959`, `:1053`, `:2029`) | **B retain** BFME1 census; **C skip** imported verdict exemptions | Rule equality cannot be inferred from tool names or BFME2 comments claiming equivalence. |
| `link_check.py` | Published index/object fetch, reference graph, local variants and VP6 exclusion (`B2:tools/link_check.py:90`, `:175`, `:1088`) | Existing preview/claims/family/near queues; +1098/-2139; changed-definer proof, weak and alias schemas (`B1:tools/link_check.py:47`, `:95`) | **A/B adapt** useful diagnostics only; **C skip** replacement and VP6 | Preserve unknown verdict when definers are unproved, `alias_target`/`alias_unknown`, COMDAT selection and claim leases. |
| `link_rank.py` | U/D/L/S/A blockers, sole/shared byte ranking, near rows (`B2:tools/link_rank.py:9`, `:53`) | No same-named file; `link_check.py --next`, `next`, `near` (`B1:tools/link_check.py:54`) | **A/B adapt** only if a consumer needs the reporting API | Do not duplicate the queue or replace its ownership/freshness policy. |
| `link_debt.py` | Hard-coded address detector and staged aggregate count ratchet (`B2:tools/link_debt.py:24`, `:76`) | Existing stronger per-file address multiset, rename support, extra cast/mask cases; +29/-56 (`B1:tools/link_debt.py:25`, `:88`) | **B retain** BFME1 detector; **C skip** weaker ratchet | A removed literal cannot pay for a different added address; image bounds are target-specific. |
| `repair_queue.py` | Census fallback, gzip cycle rows, bundle/closure modes, machine-readable refusal, TU approval routing (`B2:tools/repair_queue.py:398`, `:505`, `:560`, `:568`, `:628`) | Existing debt and local-cycle parsing; +376/-36; link lane explicitly disabled for BFME1 despite existing cycle (`B1:tools/repair_queue.py:328`) | **A/B adapt** in Phase 3; **C skip** unrelated smoke/desync/boot/TU policy additions | Remove obsolete guard deliberately; do not silently fall back when explicit bundle authentication fails. |
| `publisher.py` | Pinned checker, receipted code publication, isolated builds (`B2:tools/publisher.py:2`, `:127`) | Same implementation; +3/-3, only documentation differs | **A already shared**; **B retain** local settings; **C skip** rollout | Cycle release publishing and code publishing remain distinct; no bot credentials or identity copied. |
| `publisher_gate.py` | Pinned pre-push hook, optional gitlinks/toolchains (`B2:tools/publisher_gate.py:2`, `:103`) | Byte-identical file | **A retain**, **B local** gate arguments | Do not import BFME2 gitlink topology. |
| `publisher_hook.py` | Remote-tip off/shadow/enforce mode and submission/status (`B2:tools/publisher_hook.py:43`, `:71`) | Byte-identical file, already supports both mode paths | **A retain**; **C skip** mode change | Candidate cannot choose its own publication mode. |
| `publisher_load.py` | Load simulation/benchmark of code publisher (`B2:tools/publisher_load.py:2`) | Byte-identical file | **A retain** | Simulated throughput is not verified target progress. |
| `publisher_service.py` | Service, shadow mirror, pinned fixture generation/promotion (`B2:tools/publisher_service.py:55`, `:61`, `:159`) | Byte-identical file | **A retain**, **B configure** existing service separately; **C skip** deployment | BFME1 fixture cases/gate paths, no BFME2 host state or bot configuration. |
| `place_bodies.py` | Masked whole-text search, callee filtering, ambiguity/conflict pruning; `--apply` writes pins/rows (`B2:tools/place_bodies.py:13`, `:33`, `:82`, `:194`) | No same-named file; existing `harvest.py` and `locate.py` | **A/B adapt later** discovery only; **C skip** writes | Placement is a lead; no symbols.csv writes, no fold-pin exception, no automatic landing. |
| `bfme1_sweep.py` | BFME1-to-BFME2 binary donor scan, ranked/near/packet/show and automatic land (`B2:tools/bfme1_sweep.py:2`, `:67`, `:1391`, `:1676`) | No same-named file; `source_donors.py`, `zh_sweep.py` | **A reuse algorithms later**, **B reverse direction** as proposed `bfme2_sweep.py`; **C skip** land and donor assertions | Re-prove BFME1 identities/ABI; donor pins/bytes are not target evidence. Existing A/B/C/D/S/P/L tiers are not the owner's proposed T1–T5. |
| `donor_sweep.py` | Recompile BFME1 donor at `/O1`, masked placement, resumable leads, optional pin writes (`B2:tools/donor_sweep.py:2`, `:33`, `:75`) | No same-named file; existing ZH/source donor tools | **C skip** direction, flags and pin writer; **A/B consider later** discovery | BFME1 compilation flags and proven target baseline decide; do not invert a flag assumption by renaming variables. |
| `stlport_folds.py` | Recursive full-body certificates for four fixed STLport storage families (`B2:tools/stlport_folds.py:18`, `:36`) | No same-named file; `one_identity.py` refuses multiple identities | **C skip** certificates and family sizes; **A retain as adversarial examples** | BFME2 fold proof is not BFME1 identity admission. This tool does not serve decl-only specializations. |
| `dup_defs.py` | Duplicate/divergent report, selected-copy evidence, shrink-only debt; optional identical-extra removal (`B2:tools/dup_defs.py:3`, `:68`, `:207`) | No same-named file; census/preview already judge copies | **A/B diagnostic later**; **C skip** removal and baseline adoption | Keep BFME1 truth/selection; no new debt baseline to permit previously refused code. |
| `pin_admission.py` | Pin writer/register, in-image-code test, ICF `fold-proof`, alias-row restrictions (`B2:tools/pin_admission.py:9`, `:24`, `:64`, `:830`) | No same-named file; `pin_consistency.py`, `one_identity.py`, import/label/data writers | **C skip** gate/writer; **A use tests as negative cases** | BFME1 routing, ABI views, overrides and identity policy remain authoritative. |
| `code_identity_gate.py` | Allowed code-binding sets, duplicate gate, tool-generated alternatenames/name tiers, shadow register (`B2:tools/code_identity_gate.py:9`, `:23`, `:83`) | No same-named file; `identity_guard.py`, `alias_guard.py`, pin/identity/build gates | **C skip** policy/enforcement; **A/B diagnostics only after review** | Never replace BFME1 alias judgment with BFME2's permitted-binding sets. |
| `next_work.py` | Landability bands, WorldBuilder leads, WPO annotations, claims, repair routing (`B2:tools/next_work.py:65`, `:630`, `:1144`, `:1621`) | Existing finish/carved/extent/eligibility selection; +633/-508 (`B1:tools/next_work.py:600`, `:650`, `:752`) | **B retain** picker; **A shadow comparisons later**; **C skip** wholesale replacement | Only eligibility.py decides open work; preserve finish banks, dead ends, target guards and claims. |
| `model_routing.py` + `.json` | Per-size Wilson lower-bound model routing and judge protection (`B2:tools/model_routing.py:39`, `:97`, `:154`) | Both files byte-identical | **A retain**, **B existing config** | This is model-performance routing, not the proposed bundle-failure/lane router. Do not change it to choose validity. |

## Configuration inventory: do not carry BFME2 defaults across

This list covers target, filesystem, identity, policy and deployment defaults in
the manifest and the shared interfaces it reaches. C-only defaults are listed to
prevent accidental import, not to request a new BFME1 configuration for excluded
features. Generic format constants (COFF relocation numbers, schema field names,
SHA-256, deterministic gzip) remain versioned format/algorithm definitions.
Generic tuning such as report limits is not evidence about either executable.

| BFME2 hard-coded value / location | BFME1 configuration or disposition |
|---|---|
| Checkout `ROOT` from tool location; snapshot `LINK_CYCLE_ROOT` (`B2:tools/link_cycle.py:126`), repair `REPAIR_ROOT`/cwd (`B2:tools/repair_queue.py:101`) | One explicit target context rooted in this worktree or proven snapshot; preserve stdin-hook context. No sibling-checkout fallback. |
| `Code/`, `reference/`, `vendor/`, `reverse/*` census inputs (`B2:tools/link_census.py:95`); source filters (`B2:tools/link_check.py:883`, `B2:tools/link_rank.py:89`, `B2:tools/link_debt.py:24`) | `game/`, `inputs/reference/`, `inputs/vendor/`, `targets/game/reverse/`; derive filters from BFME1 canonical generated/source classification. |
| `reference/open-bfme-1`, five-minute reference check (`B2:tools/build.py:29`); BFME1 submodule field in manifests (`B2:tools/cycle_artifacts.py:524`, `B2:tools/publish_cycle.py:186`) | Use BFME1's actual submodules/toolchain provenance; no compulsory BFME1 donor pointer in a BFME1 cycle. |
| `baselines/bfme2/workshop-vanilla-1.06/{manifest.json,files/game.dat}` (`B2:tools/build.py:72`) | `build.MANIFEST`/`build.EXE` from BFME1, currently `inputs/baselines/bfme1/retail-1.03-unpacked` (`B1:tools/build.py:31`). Workshop image is not the game byte baseline. |
| `reverse/functions.csv`, `symbols.csv`, `ghidra_functions.csv` in cycle input state, relocation recovery, load pins, measure/remeasure (`B2:tools/link_cycle.py:968`, `:2027`, `:2151`, `:2233`, `:2788`) | Adapter supplies BFME1 ledger paths; include verified-data and typed identity inputs as well, not only these three. |
| Same reverse paths repeated by replay (`B2:tools/closure_report.py:748`, `:794`) | Replay asks BFME1 context for exact input identities; it cannot substitute current ledgers for measured ones. |
| `BASE=0x400000`, `SHIFT_BASE=0x10000000`; four region starts `0x1000`, `0x75B460`, `0x7AB900`, `0x7B68D0` (`B2:tools/link_cycle.py:132`) | Base validated from target PE; shifted base is an explicit measurement setting. Retain BFME1 single group and ILT window (`B1:tools/link_cycle.py:121`). Never import BFME2 region boundaries. |
| `__except_list=0`, runtime library list, retail-generated import libs (`B2:tools/link_cycle.py:138`, `:490`, `:520`) | Preserve BFME1 absolute-symbol/import/runtime behavior; use its `imports.csv` reader (`B1:tools/link_cycle.py:254`). Any runtime change needs independent evidence. |
| `TOOL_FILES` three cycle files (`B2:tools/link_cycle.py:139`), census tool list (`B2:tools/link_census.py:99`), diff tool list (`B2:tools/cycle_diff.py:110`) | Digest complete BFME1 measurement dependencies, including adapters and dump helpers; diff uses same declared dependency set. No mismatched duplicated lists. |
| `link-cycle-2` literals (`B2:tools/link_cycle.py:2317`, `:2798`), `coff-canon-1` (`:1789`), `data-fold-1`, `ICF_SELECTIONS=(2,)`, export-only fold series (`:147`) | Explicit BFME1 measurement/rule profile; canonical algorithm version only after equivalence tests. No fold-shadow series by default. Same string cannot conceal changed semantics. |
| `retail-truth-4` and predecessor/history defaults (`B2:tools/link_census.py:2685`) | Preserve BFME1 `keep_rule`/`judge_selected`; assign an honest identity to those rules. No import of unreferenced/retail-kept/retail-first exemptions. |
| Cycle output `build/link_cycle`, snapshot/provenance/cache/receipt artifacts (`B2:tools/link_cycle.py:131`, `:1916`, `:2032`, `:2092`) | Configured BFME1 run/output roots; artifact basenames remain format definitions; preserve immutable-snapshot authority. |
| `COMMITTED_RECEIPT=reverse/link_cycle/receipt.json` (`B2:tools/cycle_artifacts.py:108`) | Configured historical receipt path, if BFME1 maintains one; absence is explicit. Do not invent a committed authoritative receipt. |
| `DEFAULT_REPO=Open-BFME/Open-BFME-2`, `DEFAULT_STORE=build/cycle_bundles`, `UPSTREAM=origin/master` (`B2:tools/cycle_artifacts.py:111`) | BFME1 release repository, worktree-local bundle store and ancestry ref; repository identity must be checked as part of trust. |
| `PUBLISHERS=({login: Ancalgonn, id: 1760627},)` with unconfirmed-placeholder comment (`B2:tools/cycle_artifacts.py:120`) | Owner-confirmed BFME1 account login **and numeric id**. No inferred authorization, copied placeholder, host identity or credentials. |
| Freshness 24 h, closure lookback 5, future skew 600 s (`B2:tools/cycle_artifacts.py:115`); lock defaults (`:873`) | Explicit freshness/store policy, initially proposed same limits; fail closed when trust/rules unknown. Review by owner; no automatic `--allow-stale`. |
| Required data-fold members, optional graph/report/diff members (`B2:tools/cycle_artifacts.py:93`); mandatory folds header/file (`B2:tools/publish_cycle.py:90`, `:160`) | Versioned BFME1 bundle profile makes graph/report available for authority without requiring ICF exceptions; decide empty diagnostic fold file versus new profile explicitly. |
| `DIAGNOSTIC_INPUTS=(reverse/data_ledger.csv, exports.csv, functions.csv)` and repeated measured-input/generator paths (`B2:tools/publish_cycle.py:91`, `:241`, `:276`) | BFME1 evidence-view paths/schema; bind functions, symbols, verified data and derived identity inputs at the measured commit. |
| Producer example `bfme-laptop/watchdog` (`B2:tools/publish_cycle.py:859`) | Required explicit producer label for the BFME1 measuring host; label is not authentication. |
| Rank `reverse/data_ledger.csv`, `functions.csv`, `data_xrefs.tsv`, `exports.csv`, `build/match`, `build/data_back_rank_objects.pkl`, base `0x400000`, xref cap 12 (`B2:tools/data_back_rank.py:117`) | BFME1 data-binding adapter and configured paths/object store. Do not assume BFME1 xrefs have that cap or that B2's derived schema is an ownership ledger. |
| Provisional relocation source `boot_image` (`B2:tools/data_back_rank.py:672`); retail sections, blank relocation section, funclets `0x75B460` (`B2:tools/boot_image.py:59`) | Exclude BFME2 boot reconstruction; a BFME1 relocation provider must state provenance. Missing provider is unavailable, not a zero-result report. |
| Link index publisher repository/tag (`B2:tools/link_check.py:90`); VP6 queue (`:1088`) | Keep BFME1 queue distribution. Do not import BFME2 release/index namespaces or VP6 exclusions. |
| Cast image high `0xEDA000`, address high `0xEDA000` (`B2:tools/link_debt.py:29`, `:46`) | BFME1 detector already uses BFME1 bounds (`B1:tools/link_debt.py:36`, `:51`); retain its stricter parser/ratchet. |
| Repair layout auto-detection, source exclusions, window `0x4000`, local cycle status and committed census paths (`B2:tools/repair_queue.py:103`) | Explicit BFME1 target context; local diagnostic cycle versus committed census versus authenticated bundle must be distinguishable. |
| `REPAIR_DIFFEXEC`, `REPAIR_BOOT`, `REPAIR_DESYNC`, `REPAIR_STATIC`, tier-C path, rotation every 3 and state path (`B2:tools/repair_queue.py:215`, `:246`, `:694`) | Retain current BFME1 debt/rotation interfaces; skip new desync/static queues in Phases 1–3. |
| `reverse/place_denylist.txt`, minimum body 20, pin/body/fold notes (`B2:tools/place_bodies.py:67`, `:84`) | Later discovery context may configure denylist/threshold; no writer or fold-pin route is ported. |
| Donor `reference/open-bfme-1`, workshop BFME1 image, donor/target ledgers/symbols, sweep output/packets (`B2:tools/bfme1_sweep.py:68`) | Later BFME2 donor configuration must invert direction and preserve the BFME1 retail target. Read-only donor revision recorded; no submodule/layout assumption. |
| Benchmark refusal and GameSpy flagging; generated prefixes, placement roots, held tiers (`B2:tools/bfme1_sweep.py:99`, `:112`); include rewriting (`:742`, `:1215`) | Do not copy donor policy statements: BFME1's actual library provenance and official source paths apply (`B1:docs/matching.md:101`). New T1–T5 mapping needs specification. |
| Donor minima 16/6, fanout 8, placement cap 4096, string minimum 3 (`B2:tools/bfme1_sweep.py:85`); donor `/O1`, directory/result cache (`B2:tools/donor_sweep.py:33`, `:75`) | Later search settings must be explicit and recorded; caps never prove uniqueness. No BFME2 compiler flag imposed on BFME1. |
| Four STLport signatures/sizes 29/11/23/39 (`B2:tools/stlport_folds.py:18`) | C: do not import BFME2 fold admission. BFME1 family work remains evidence/claim scoped. |
| `reverse/{symbols,functions}.csv`, base and fold-proof admission (`B2:tools/pin_admission.py:90`); duplicate/code-identity baselines, name tiers, filters (`B2:tools/dup_defs.py:49`, `B2:tools/code_identity_gate.py:42`, `:64`, `:74`, `:122`) | C: no replacement gate or new baseline; any future diagnostic uses existing BFME1 identity providers. |
| `build/allowed_symbols`, `reverse/name_tiers.csv`, `name_basis.csv`, base (`B2:tools/allowed_symbols.py:73`, `:731`) | C: do not import naming/rename/admission graph. Required measurement data must be provided by BFME1 instead. |
| `reverse/zh_sweep/*`, Ghidra/string/anchored/reloc inputs; `Code` fallback commands and WB lane (`B2:tools/next_work.py:82`, `:96`, `:1144`) | Keep BFME1 inputs, eligibility, finish/carved lanes and separate WorldBuilder target. Later router only adds shadow decisions. |
| Model config/log/judge paths and model cost/aliases/classes (`B2:tools/model_routing.py:39`, `B2:tools/model_routing.json:1`) | Already shared configuration; retain BFME1 values. Do not import runtime model/session selection through this tooling port. |
| Publisher master/submission/results refs, mode paths and generic defaults (`B2:tools/publisher.py:127`, `B2:tools/publisher_hook.py:43`); service shadow/settings/state (`B2:tools/publisher_service.py:55`, `:159`, `:193`) | Already present. Any deployment supplies BFME1 origin, branch, operators/keys, checker and toolchain paths, host lock, builders and gate; never copy an installed BFME2 service state. |
| BFME2 publisher fixture cases/ledger and reference toolchain examples (`B2:docs/publisher.md:69`, `:87`, `B2:tools/publisher_fixtures/bfme2/cases.json:1`, `B2:tools/publisher_fixtures/bfme2/ledger.sh:1`) | Use existing BFME1 fixtures (`B1:docs/throughput-tools.md:449`). Code publisher committer `publisher` (`B2:tools/publisher.py:152`) is not the release-authentication allowlist. |
| Shared build flag-region/override inputs and alternate compiler hashes (`B2:tools/flag_defaults.py:51`, `B2:tools/compiler_profiles.py:9`); BFME2 minimal relocation module (`B2:tools/reloc_ledger.py:1`) | C: keep BFME1 compiler and complete relocation implementation. Do not copy layout/flag maps, profile hashes, shims or the reduced relocation module. |
| Test commits, BFME1 pointer, `Code/` paths, `reverse/` ledgers and folded-data fixture (`B2:tools/tests/cycle_fixture.py:20`) | Synthetic BFME1 fixture context, no real publisher identity. Test constants do not become production configuration or evidence. |

## BFME1 invariants retained by every phase

1. `eligibility.py` is the sole open-work predicate; dumps are open, dead ends
   retire, deferrals do not, a bank survives later blocked, and released blockers
   require landed evidence (`B1:tools/eligibility.py:1`, `B1:docs/throughput-tools.md:8`).
   All new donor/router/placement consumers call it instead of reconstructing it.
2. The target is the unpacked retail 1.03 image, with its manifest, not the
   workshop mod executable (`B1:tools/build.py:31`, `B1:AGENTS.md:134`). Preserve
   `target_guard` separation from WorldBuilder (`B1:tools/target_guard.py:6`).
3. Byte verification, DIR32 content/consistency, REL32 binding, full extents,
   jump tables and TU-local data remain build/gate decisions
   (`B1:docs/matching.md:5`, `:13`, `B1:AGENTS.md:8`). A report never admits a row.
4. `add_match` keeps extent/source/replacement/tombstone checks, model attribution
   and rollback after failed verification (`B1:tools/add_match.py:745`, `:930`,
   `:1038`, `:1117`). It exposes `--no-verify`; that does **not** authorize this
   port to bypass verification. Generated claims yield only through supported
   replacements, never by editing generated files (`B1:AGENTS.md:176`).
5. `check_csv` requires tracked source, consistent ledgers and tombstones;
   run it first and keep it in queue health checks (`B1:tools/check_csv.py:108`,
   `B1:AGENTS.md:22`, `B1:docs/naming_evidence.md:60`). No ledger row reordering
   to change the COMDAT winner (`B1:AGENTS.md:39`).
6. `link_census.keep_rule`, `judge_selected`, alias judgment, common/weak
   external handling and `link_check` changed-definer checks remain BFME1's
   rules (`B1:tools/link_census.py:959`, `:1397`, `:2029`,
   `B1:tools/link_check.py:47`). An unknown result is not LINKS.
7. Only current objects count. Preserve ledger-payload identity, truth/policy
   fingerprints, source/header/search-directory receipts and start/end currency
   checks (`B1:tools/link_census.py:105`, `:1053`, `:2290`, `:2449`,
   `B1:tools/census_receipts.py:27`). Preserve canonical module identity and
   linker timeout/retry (`B1:tools/link_census.py:71`, `:84`).
8. Pins remain additive resolver candidates, not identity proof; validate them
   with `pin_consistency` before/after. Routes, ABI views and verified overrides
   have existing specific rules (`B1:tools/build.py:1535`,
   `B1:tools/pin_consistency.py:29`). `one_identity` and its shrink-only count
   forbid an invented second real identity (`B1:tools/one_identity.py:1`,
   `B1:tools/identity_guard.py:80`). No ICF pin exception imported.
9. Aliases must reach the same proven body; unknown aliases do not resolve a
   caller for LINKED (`B1:tools/alias_guard.py:12`). Data ownership is byte-verified
   through `add_data_match`/`data_rows`; gate-read sole writers remain in force
   (`B1:tools/add_data_match.py:2`, `B1:AGENTS.md:191`).
10. Baselines only shrink; removing debt requires re-verification. No copied
    BFME2 baseline or count can make a refusal disappear (`B1:.githooks/pre-commit:322`,
    `:419`, `:439`, `:449`, `B1:tools/identity_guard.py:10`). Preserve the
    per-file address multiset ratchet (`B1:tools/link_debt.py:88`).
11. Generated, assembly, alias and filler bytes never become authored credit.
    Preserve progress provenance and unique interval unions; banked attempts are
    evidence, not progress (`B1:tools/progress.py:90`, `:105`,
    `B1:tools/link_cycle.py:14`, `:234`, `:667`). Source closure must not count a
    dependency on generated/assembly code as recovered source closure.
12. Claim/family leases, official source placement, callee ABI evidence and
    honest naming survive new queues (`B1:AGENTS.md:30`, `:67`, `:71`, `:154`).
    Existing hooks and explicit-path staging stay enabled; Phase 0 does not push.

## Same concepts, different semantics

| concept | concrete difference and port consequence |
|---|---|
| RVA versus VA | Both function ledgers use `target_rva`; BFME2 pin admission rejects VA-valued code pins (`B2:tools/pin_admission.py:9`, `:93`); BFME1 add_match calls its input RVA (`B1:tools/add_match.py:749`). Directly reading both configured PE headers verified `ImageBase=0x400000`. BFME2's Image reader exposes VAs (`B2:tools/reloc_ledger.py:34`), its derived data ledger stores RVAs (`B2:tools/data_ledger.py:16`), and BFME1 verified data rows explicitly carry `address_kind` (`B1:tools/data_rows.py:55`, `:80`). Use tagged conversions at adapters, never a blanket subtract-base heuristic. |
| Call route versus body identity | BFME1 retail has ILT routing; its resolver builds thunk/body candidates and checks `route=` separately for identity (`B1:tools/build.py:1535`, `B1:tools/link_census.py:185`). BFME2 census has a different `route_claims`/validation path (`B2:tools/link_census.py:178`). Porting BFME2 pin/alias code would drop BFME1's route proof and candidate-list behavior. |
| Alias | BFME2 `allowed_symbols` can propose `/alternatename` bindings to owners, and identity gate checks those sets (`B2:tools/allowed_symbols.py:692`, `B2:tools/code_identity_gate.py:15`). BFME1 follows aliases/thunks and charges wrong or unknown identity to declaring/calling units (`B1:tools/alias_guard.py:12`, `B1:tools/link_census.py:2029`). Preserve those blockers, not just “alias target is defined.” |
| COMDAT selection versus ICF | Multiple copies of the **same** COMDAT name are selection; multiple **names** at one folded address are ICF. BFME1 has no retail ICF (`B1:tools/one_identity.py:1`). BFME2's fold certificates and data-fold shadow rules are target-specific (`B2:tools/pin_admission.py:24`, `B2:tools/link_cycle.py:77`). Do not admit new BFME1 identities because bytes coincide. |
| Copy losers | At this base BFME1 charges any retail-proven wrong copy (`B1:tools/link_census.py:959`). BFME2 `retail-truth-4` can excuse discarded wrong copies if another copy is proven, excuse some unknown copies when the first is proven, and ignore unreferenced unaddressed names (`B2:tools/link_census.py:1005`). Its documentation calls these BFME1 rules, but the checked BFME1 implementation differs. This is an explicit non-port, not a path adaptation. |
| Data identity | BFME2 `data_ledger.csv` is derived, sizes are upper bounds, owner can be provisional, and `name@source` indicates local scope (`B2:tools/data_ledger.py:13`). `data_rows.csv` is separately verified. BFME1 has verified data rows plus the full typed relocation ledger and DIR32 address evidence (`B1:tools/data_rows.py:55`, `B1:tools/reloc_ledger.py:1`). Adapter must provide evidence/scope without promoting a derived canonical name or size into ownership proof. |
| Generated sources | BFME1 cycle distinguishes generated and asm kinds and forbids closure through their source units (`B1:tools/link_cycle.py:14`, `:234`). BFME2 excludes particular gen-note kinds but has different path/row classification (`B2:tools/link_cycle.py:249`, `B2:tools/data_back_rank.py:137`). Reuse BFME1 canonical classification; do not translate `Code/` alone and accidentally credit a dump. |
| Census versus cycle status | Census is one row per source and LINKED; cycle is one row per ledger body with placement/self/closed verdicts. BFME2 rank validates a distinct cycle header (`B2:tools/data_back_rank.py:132`); BFME1 currently disables its repair link parser behind `BFME1` (`B1:tools/repair_queue.py:328`). No extension may parse one format as the other or sum source bytes as unique closure gain. |
| Reproducibility versus instance identity | BFME2 core/canonical core identify reproducible content, while tag includes commit, measured end and receipt-byte digest (`B2:tools/link_cycle.py:2112`, `B2:tools/cycle_artifacts.py:9`). A repeat measurement can share a core but must retain its own measurement identity. |
| Freshness and authority | Local mtime/ancestry selection exists in BFME2 ordinary repair mode (`B2:tools/repair_queue.py:425`); bundle mode separately authenticates and refuses rather than silently falling back (`:560`). Router must consume reason codes and choose another lane explicitly. A local diagnostic or replay is not an authoritative publication. |

## Decl-only explicit-specialization pattern

At the reference revision, `rg -l 'bfme link decl-only' Code` finds **1,053 files**.
For example, `B2:Code/Libraries/Source/assetmanager/AssetManagerImplCtor.cpp:35`
declares `_STLP_alloc_proxy`, `_Vector_base`, `vector` and allocator member
specializations inside `_STL`, without bodies. The comments immediately after
the block explicitly describe suppressing this TU's non-retail COMDAT, using
the kept copy and avoiding `__imp_` (`:47`). A smaller example is
`B2:Code/GameEngine/Source/GameLogic/System/ArmySummaryLoad.cpp:111`; its
following comment explains the declaration-only vector destructor (`:115`).

A search of `tools/**/*.py` and `tools/**/*.sh` for `decl.only`, `decl-only`
and `explicit.speciali` found no marker consumer/generator. This is a bounded
negative result, not a claim about every historical or untracked script.
`dup_defs.py --candidates` serves identical extra definitions and its optional
remover recognizes simple ordinary member definitions (`B2:tools/dup_defs.py:153`,
`:207`); it does not serve these template specializations. `stlport_folds.py`
proves emitted-body folds (`B2:tools/stlport_folds.py:36`), not suppression.
`link_rank`/`link_check` report COMDAT blockers but do not prescribe this edit.
Any future family queue may present this as a repair hypothesis only after
BFME1 provider/consumer and selected-copy checks, followed by the normal gate.

## Proposed module boundary and Phases 1–3

These are implementation requirements for subsequent phases, not added files:

- `tools/link_cycle_context.py`: one small BFME1 context/config module used by
  measurement, bundle and queue consumers. Expose roots, target PE identity,
  ledger/evidence paths, import/ILT providers, source-kind classification,
  current-object proof, complete measurement dependency digests, explicit rule
  tuple and release trust configuration. Delegate to existing BFME1 owners;
  it must contain no substitute eligibility or pin-validity predicate.
- Keep CLI filenames `link_cycle.py`, `closure_report.py`, `cycle_artifacts.py`,
  `publish_cycle.py`, `cycle_diff.py`, `data_back_rank.py`, `repair_queue.py`.
  Keep graph/interval/report code pure where practical; inject context at I/O
  boundaries. Do not split algorithms merely to mirror BFME2's module graph.
- Existing `build`, `link_census`, `census_receipts`, `data_rows`, `reloc_ledger`,
  `alias_guard`, `pin_consistency`, `one_identity`, `eligibility`, `progress`
  remain owners. `publisher*.py` is not part of the new dependency substrate.

**Phase 1A:** Add the BFME1 context and honest rule identity first, then port
read-only finalized graph serialization, receipt graph digest, normalized text
hashing, environment and object/canonical provenance. Preserve ILT/dump/import
logic; bind functions/symbols/data inputs, tool dependencies, target hash and
objects at start/end. BFME2 currently hashes only functions/symbols/Ghidra in
cycle `inputs` (`B2:tools/link_cycle.py:2027`); blindly copying it does not meet
the owner's stronger data-ledger contract. Rule/profile changes must invalidate
compatibility rather than silently relabel old receipts.

**Phase 1B:** Port closure analysis after graph emission. Consume the measured
graph, verify digest/rows/credit, preserve replay labels for legacy diagnostics,
and compare forced closures with BFME1's actual closure semantics. Required
synthetic coverage: chains, cycles, diamonds, two roots, overlapping rows,
duplicate addresses, unplaced rows, generated/assembly dependencies,
fillers/stubs and unknown targets. Graph writing must not rerun or mutate
verdicts (`B2:tools/tests/test_closure_report.py:295`). Preserve complete blocker
sets up to the cap, explicit overflow, and single-versus-joint gain limits.

**Phase 2:** Port authenticated immutable bundles and publish companion, with a
BFME1 member/profile decision before wiring rank generation. The owner's
authoritative bundle requires receipt, compressed status, graph, roots,
blockers, data-back JSON and manifest; BFME2 additionally requires data-fold
CSV and rank text while treating graph/roots as optional
(`B2:tools/cycle_artifacts.py:93`). Version that distinction explicitly.
Rank input uses the measured BFME1 evidence view. Bind commit, target, rules,
tools, ledgers and objects; validate sizes, hashes, receipt repetitions,
graph/report/rank associations and freshness. Configure publisher identity
before remote use. Local-unpublished bundles are available for tests and
inspection, never authoritative router inputs. Phase 0 authorizes no remote publication; subsequent execution must also
respect the owner plan’s publication boundary.

**Phase 3:** Extend BFME1 repair queue with local cycle/census selection,
`link --bundle` and `link --closure --bundle`, retaining existing plain behavior
and explicit source labels. Remove the obsolete “BFME1 has no link cycle” guard
with tests. Keep failure reasons distinct: corrupt → tooling seat;
unavailable/empty/stale → another lane; incompatible rules → tooling seat/owner;
unauthenticated → refuse; no closure report → ordinary link queue. An explicit
failed bundle read does not quietly become a local-file read. Route only from
authenticated publications; never auto-add `--allow-stale`. Do not replace
`next_work` or conflate this lane router with model routing. Owner plan schedules
adversarial review R1 after this phase; placement, donors, COMDAT families and
picker promotion remain later work.

## Open questions for the owner

1. Which BFME1 release repository and publisher login **plus numeric id** are
   authorized, and does that repository enforce immutable releases? BFME2's
   allowlist explicitly remains marked unconfirmed (`B2:tools/cycle_artifacts.py:120`).
2. What BFME1 measurement/rule identifier and compatibility policy should be
   frozen? BFME1 currently also says `link-cycle-2` despite its different target
   semantics, and lacks BFME2's shadow/canonical tuple
   (`B1:tools/link_cycle.py:1717`, `B2:tools/cycle_artifacts.py:347`). The
   shared string alone must never authorize cross-target receipt consumption.
3. For the BFME1 bundle profile, should data-fold CSV be an explicitly empty
   diagnostic member, or should a new profile remove it? Should graph/roots be
   mandatory for authoritative use, with replay/diagnostic bundles kept separate?
4. Which BFME1 derived data-binding view will feed data-back ranking, and where
   will its schema, TU-local scope, provenance and content hashes live? It must
   not replace verified `data_rows` or the typed relocation ledger.
5. Are the proposed 24-hour age, 600-second skew and five-release closure
   lookback appropriate for BFME1? What is the expected publication cadence and
   where should a historical committed receipt live, if anywhere?
6. Which measuring host, producer label and full toolchain/object evidence set
   will define the first authoritative BFME1 cycle? Which dependency changes
   require a rule bump versus a tool-digest warning?
7. For later donor work, what exactly are T1–T5, and what approved read-only
   BFME2 snapshot/provenance path should replace the BFME1 donor assumption?
   The donor's benchmark/ICF statements must not be copied as BFME1 facts.
8. Should a later COMDAT family queue explicitly serve decl-only hypotheses,
   or only rank blockers? No such marker-serving tool was found in the frozen
   BFME2 tooling tree; family ownership and BFME1 verification are still needed.

## Research validation

`python3 tools/check_csv.py` passed before inspection: 173,041 function rows,
91,151 symbol rows and 1,707 data rows. Read the plan, both contributing guides,
both matching/structural guides, BFME1 naming/header/throughput documentation,
and BFME2 naming/publisher/agent-tool documentation. Inspected source and test
code without running reference tools, compiling either game or modifying the
reference clone. No whole function/export/Ghidra ledger was loaded for this
research. Test entries below are inventories and acceptance leads, not claims
that the tests were executed or that a port already passes them.

## Transitive import manifest

An AST walk of normal and function-local imports reaches **70 local modules**,
including the 26 entry modules above. The following table records every edge.
`dependency@N` cites the import at `B2:tools/<module>.py:N`; “none” means no
local Python import, not no subprocess or filesystem dependency. Third-party
imports in this closure are `capstone` and `pefile` (for example
`B2:tools/link_cycle.py:728`, `:953`, `B2:tools/boot_image.py:52`).
Standard-library imports are not ports. The BFME2 module must **not** be imported
just to obtain a helper if that activates C policy through this graph.
“Main” refers to the classifications in the component table. For other modules,
A means extract/reuse only a pure helper if needed; B means use the existing
BFME1 module/API or an explicit adapter; C means do not import in this port.
The comparison column records existence and literal diff, not semantic parity.

| module (`tools/*.py`) | class / disposition | direct local imports, with import line | BFME1 comparison (+/-) |
|---|---|---|---|
| `allowed_symbols` | C / exclude | `build@69`, `link_census@70`, `pin_admission@71`, `rename@800` | absent |
| `audit_ret_arity` | B / BFME1 owner or adapter | none | +17/-90 |
| `bfme1_sweep` | Main | `build@62`, `ledger_io@63`, `claims@64`, `wb_context@65`, `drift_classify@430`, `pe_imports@602`, `pe_imports@630`, `pe_imports@1154` | absent |
| `boot_image` | C / exclude | `build@57`, `link_cycle@925`, `boot_relayout@1215` | +272/-368 |
| `boot_relayout` | C / exclude | `boot_image@53`, `link_cycle@677`, `link_cycle@902` | absent |
| `boundary_validator` | B / BFME1 owner or adapter | `audit_ret_arity@26` | +31/-26 |
| `build` | B / BFME1 owner or adapter | `flag_defaults@19`, `compiler_profiles@20`, `ledger_io@21`, `stlport_folds@22`, `coffar@23`, `gen_case_shims@24`, `portable_lock@25`, `eh_verify@2367`, `eh_verify@2373`, `eh_verify@2388`, `pin_admission@2513`, `pe_imports@3693`, `pe_imports@3815`, `data_rows@3896`, `check_module_registry@3983`, `data_rows@4050`, `pin_consistency@4075`, `check_module_registry@4078`, `data_rows@4121` | +2383/-2249 |
| `census_receipts` | Main | `build@24` | +88/-161 |
| `check_module_registry` | B / BFME1 owner or adapter | `build@44` | absent |
| `claims` | B / BFME1 owner or adapter | `portable_lock@762` | +833/-332 |
| `closure_report` | Main | `link_cycle@784` | absent |
| `code_identity_gate` | Main | `allowed_symbols@39`, `dup_defs@40` | absent |
| `coffar` | A / helper only | none | +14/-34 |
| `compiler_profiles` | C / exclude | `build@65` | absent |
| `cycle_artifacts` | Main | `link_cycle@377` | absent |
| `cycle_diff` | Main | none | absent |
| `data_back_rank` | Main | `build@643`, `boot_image@672`, `cycle_artifacts@986` | absent |
| `data_rows` | B / BFME1 owner or adapter | `build@110`, `build@242`, `reloc_ledger@243` | +235/-94 |
| `donor_sweep` | Main | `build@31` | absent |
| `drift_classify` | B / BFME1 owner or adapter | `build@38`, `locate@39` | +58/-9 |
| `dup_defs` | Main | `allowed_symbols@45`, `build@46`, `link_census@47` | absent |
| `eh_verify` | B / BFME1 owner or adapter | `build@49` | absent |
| `flag_defaults` | C / exclude | `build@317`, `build@407` | absent |
| `gaps` | B / BFME1 owner or adapter | `build@12` | +10/-5 |
| `gen_case_shims` | A / helper only | none | +1/-1 |
| `harvest` | B / BFME1 owner or adapter | `build@22` | +9/-6 |
| `hatch_counters` | B / BFME1 owner or adapter | `retail_inventory@497` | +396/-64 |
| `judges` | B / BFME1 owner or adapter | none | identical |
| `landability` | C / exclude | none | absent |
| `ledger_io` | A / helper only | none | +61/-53 |
| `link_census` | Main | `build@83`, `data_rows@111`, `data_rows@121`, `data_rows@138`, `data_rows@143`, `link_check@1214`, `progress@1798`, `census_receipts@1888`, `link_check@2020`, `link_debt@2259`, `link_check@2300`, `link_check@2372`, `progress@2389`, `progress@2402`, `census_receipts@2430`, `link_debt@2624` | +1096/-781 |
| `link_check` | Main | `build@86`, `link_census@87`, `progress@110`, `link_debt@563`, `link_debt@1060` | +1098/-2139 |
| `link_cycle` | Main | `build@128`, `link_census@129` | +955/-187 |
| `link_debt` | Main | none | +29/-56 |
| `link_rank` | Main | `link_census@50`, `link_check@57`, `link_check@83`, `link_check@135` | absent |
| `list_naked_candidates` | B / BFME1 owner or adapter | `build@18`, `claims@19`, `re_log@20`, `yield_model@21` | +143/-78 |
| `locate` | B / BFME1 owner or adapter | `build@28`, `harvest@29`, `ledger_io@30`, `portable_lock@31` | +41/-20 |
| `model_routing` | Main | `judges@157` | identical |
| `name_agreement` | C / exclude | `claims@74` | absent |
| `name_dependents` | C / exclude | `build@77`, `build@107`, `data_rows@108`, `build@197`, `build@225`, `build@244` | absent |
| `name_evidence` | C / exclude | `name_metric@122`, `rename@123`, `build@769` | absent |
| `name_metric` | C / exclude | none | absent |
| `next_work` | Main | `boundary_validator@65`, `claims@66`, `landability@67`, `re_log@68`, `wb_context@69`, `yield_model@70`, `wpo_detect@73`, `build@145`, `build@248`, `build@287`, `build@783`, `build@802`, `wb_gold@1159`, `similar@1270`, `build@1588`, `repair_queue@1621` | +633/-508 |
| `pe_features` | A / helper only | none | absent |
| `pe_imports` | A / helper only | none | absent |
| `pin_admission` | Main | `build@88`, `eh_verify@555`, `hatch_counters@836`, `pin_consistency@837` | absent |
| `pin_consistency` | B / BFME1 owner or adapter | `build@90`, `pe_imports@91`, `progress@92` | +63/-1493 |
| `place_bodies` | Main | `build@60`, `harvest@61` | absent |
| `portable_lock` | A / helper only | none | identical |
| `progress` | B / BFME1 owner or adapter | `build@37`, `gaps@38`, `list_naked_candidates@39` | +164/-192 |
| `publish_cycle` | Main | `cycle_artifacts@86`, `data_back_rank@87`, `cycle_diff@104`, `closure_report@316` | absent |
| `publisher` | Main | none | +3/-3 |
| `publisher_gate` | Main | none | identical |
| `publisher_hook` | Main | `publisher@90` | identical |
| `publisher_load` | Main | `publisher@44` | identical |
| `publisher_service` | Main | `publisher@52`, `publisher_hook@53` | identical |
| `re_log` | B / BFME1 owner or adapter | `ledger_io@38` | +240/-522 |
| `reloc_ledger` | B / BFME1 owner or adapter | `build@22` | +10/-2089 |
| `rename` | C / exclude | `ledger_io@180`, `name_agreement@181`, `name_metric@182`, `name_evidence@1216`, `name_dependents@1578`, `name_dependents@2449`, `build@2751`, `claims@3130`, `claims@3263`, `claims@3277`, `portable_lock@3319` | absent |
| `repair_queue` | Main | `cycle_artifacts@540`, `closure_report@572`, `tu_map@631` | +376/-36 |
| `retail_body` | C / exclude | `pe_features@79`, `wb_data@308`, `build@483` | absent |
| `retail_inventory` | C / exclude | none | identical |
| `similar` | B / BFME1 owner or adapter | none | identical |
| `stlport_folds` | Main | none | absent |
| `tu_map` | B / BFME1 owner or adapter | none | +541/-42 |
| `wb_context` | C / exclude | `wb_gold@274` | absent |
| `wb_data` | C / exclude | none | absent |
| `wb_gold` | C / exclude | none | absent |
| `wpo_detect` | C / exclude | `retail_body@41` | absent |
| `yield_model` | B / BFME1 owner or adapter | none | identical |

The C-only tail includes BFME2 flag/profile data, allowed-symbol/pin/rename
policy, landability selection, retail-inventory reconstruction and WB/WPO/boot
workflows. It is reachable through imports but is not required to port the pure
graph/report algorithms. In particular, BFME2 `build` imports `stlport_folds`
and later `pin_admission`; BFME1 `build` must stay the provider. BFME2
`B2:tools/reloc_ledger.py:1` explicitly says it is a reduced BFME1 copy: never overwrite
the full BFME1 module with it.

Subprocess/resource dependencies also require review: snapshot export and
Wine/MSVC (`B2:tools/link_cycle.py:1898`, `:1978`), measured-commit rank generation
(`B2:tools/publish_cycle.py:276`), GitHub CLI (`B2:tools/cycle_artifacts.py:178`),
pinned fixture-generator dynamic load (`B2:tools/publisher_service.py:61`),
pre-push hook (`B2:tools/publisher_gate.py:103`), and same-name helper CLIs printed
by donor/queue tools (`B2:tools/bfme1_sweep.py:1285`, `B2:tools/next_work.py:94`).
They do not justify copying an executor, gate, fixture configuration or model.

## Tests and fixture manifest

This is a static association inventory: same-name test families, direct module
imports, and literal module-loader filenames. A test can exercise more than one
entry tool. Each test filename below is relative to `tools/tests/` and cites
line 1 in the indicated repository; detailed acceptance anchors follow.
“No identified direct test” is a coverage gap, not a passing result.

| tool / family | BFME2 tests (`B2:tools/tests/<name>:1`) | BFME1 tests (`B1:tools/tests/<name>:1`) |
|---|---|---|
| `link_cycle` | `test_boot_image.py`, `test_boot_relayout.py`, `test_closure_report.py`, `test_cycle_artifacts.py`, `test_cycle_diff.py`, `test_link_cycle.py`, `test_progress_v2.py`, `test_readme_progress.py`, `test_repair_queue.py` | `test_boot_image.py`, `test_link_cycle.py`, `test_progress_v2.py` |
| `closure_report` | `test_closure_report.py`, `test_cycle_artifacts.py`, `test_repair_queue.py` | no identified direct test |
| `cycle_artifacts` | `test_closure_report.py`, `test_cycle_artifacts.py`, `test_data_back_rank.py`, `test_repair_queue.py` | no identified direct test |
| `publish_cycle` | `test_closure_report.py`, `test_cycle_artifacts.py` | no identified direct test |
| `cycle_diff` | `test_cycle_artifacts.py`, `test_cycle_diff.py` | no identified direct test |
| `data_back_rank` | `test_cycle_artifacts.py`, `test_data_back_rank.py`, `test_link_cycle.py` | no identified direct test |
| `census_receipts` | `test_build_include_inventory.py`, `test_census_receipts.py`, `test_link_census_currency.py` | `test_census_parent_receipts.py`, `test_census_receipts.py`, `test_link_census_currency.py` |
| `link_census` | `test_census_rebaseline.py`, `test_census_rules_reporting.py`, `test_link_census.py`, `test_link_census_currency.py`, `test_link_census_data_sources.py`, `test_link_census_history.py`, `test_link_census_unreferenced.py`, `test_link_census_unreferenced_diagnostic.py`, `test_link_check.py`, `test_link_check_common.py`, `test_link_check_fetch_index.py` | `test_alias_guard.py`, `test_data_scaffold.py`, `test_frozen_prediction_index.py`, `test_image_check.py`, `test_link_census.py`, `test_link_census_currency.py`, `test_link_census_data_sources.py`, `test_link_census_link_timeout.py`, `test_link_census_module_identity.py`, `test_link_census_truth_fingerprint.py`, `test_link_check.py`, `test_link_check_common.py`, `test_name_lane_imports.py`, `test_process_pool_context.py`, `test_weak_fallback_truth.py` |
| `link_check` | `test_hook_argmax.py`, `test_hook_fail_closed.py`, `test_hook_link_admission.py`, `test_link_census.py`, `test_link_census_unreferenced.py`, `test_link_census_unreferenced_diagnostic.py`, `test_link_check.py`, `test_link_check_common.py`, `test_link_check_decoder_policy.py`, `test_link_check_fetch_index.py`, `test_link_check_new_variants.py` | `test_alias_guard.py`, `test_frozen_prediction_index.py`, `test_link_census.py`, `test_link_check.py`, `test_link_check_common.py`, `test_link_check_final_review.py`, `test_link_check_r5_review.py`, `test_link_check_r6_review.py`, `test_weak_fallback_truth.py` |
| `link_rank` | `test_link_census_unreferenced_diagnostic.py`, `test_link_check.py`, `test_link_check_new_variants.py` | no identified direct test |
| `link_debt` | `test_hook_argmax.py`, `test_hook_fail_closed.py`, `test_link_census_currency.py`, `test_link_debt.py` | `test_header_dependents.py`, `test_hook_holes.py`, `test_link_debt.py`, `test_name_regression.py`, `test_pre_commit_large_commit.py`, `test_target_hooks.py` |
| `repair_queue` | `test_re_log_verdicts_at.py`, `test_repair_queue.py`, `test_tu_structure.py` | `test_hook_holes.py`, `test_repair_queue.py` |
| `place_bodies` | `test_place_bodies.py` | no identified direct test |
| `bfme1_sweep` | `test_bfme1_sweep.py`, `test_claims_review_fixes.py`, `test_ledger_terminators.py`, `test_wb_queue_hooks.py` | no identified direct test |
| `donor_sweep` | no identified direct test | no identified direct test |
| `stlport_folds` | `test_stlport_folds.py` | no identified direct test |
| `dup_defs` | `test_code_identity.py` | no identified direct test |
| `pin_admission` | `test_gate_exploits.py`, `test_hook_argmax.py`, `test_hook_fail_closed.py`, `test_pin_admission_add.py`, `test_pin_admission_fold.py`, `test_pin_admission_renames.py`, `test_weak_dtor_defaults.py` | no identified direct test |
| `code_identity_gate` | `test_code_identity.py`, `test_code_identity_lib_sources.py`, `test_hook_argmax.py`, `test_hook_fail_closed.py` | no identified direct test |
| `next_work` | `test_boundary_validator.py`, `test_claims.py`, `test_claims_review_fixes.py`, `test_dump_predicate.py`, `test_next_work.py`, `test_next_work_packet_lane.py`, `test_next_work_wb_tier.py`, `test_next_work_wpo.py`, `test_re_log_verdicts_at.py`, `test_reloc_names.py`, `test_repair_queue.py`, `test_similar.py` | `test_boundary_validator.py`, `test_carve_unclaimed.py`, `test_dump_predicate.py`, `test_named_inventory_extent.py`, `test_next_work.py`, `test_next_work_dump_extents.py`, `test_next_work_finish.py`, `test_re_log_pruning.py`, `test_reloc_names.py`, `test_repair_queue.py`, `test_retired_guard.py`, `test_similar.py`, `test_target_guard.py` |
| `model_routing` | `test_model_routing.py` | `test_model_routing.py` |
| `publisher` | `test_publisher.py`, `test_publisher_fixtures.py`, `test_publisher_service.py` | `test_harvest_transactions.py`, `test_publisher.py`, `test_publisher_fixtures.py`, `test_publisher_service.py` |
| `publisher_gate` | `test_publisher_service.py` | `test_publisher_service.py` |
| `publisher_hook` | `test_publisher_service.py` | `test_publisher_service.py` |
| `publisher_load` | `test_publisher.py` | `test_publisher.py` |
| `publisher_service` | `test_publisher_service.py` | `test_publisher_service.py` |

A tests to preserve: graph fixed points, interval unions, deterministic bundle
bytes, tamper rejection, atomic installs, reason codes, ranking and refusal
behavior. B tests need BFME1 paths/row kinds/receipt/rule providers and synthetic
trust identities. C tests remain research evidence: do not change a BFME1
refusal to pass a BFME2 fold/alias fixture.

- Closure: `B2:tools/tests/test_closure_report.py:59` (two roots), `:97` (bounded
  complete sets), `:114` (nonadditivity), `:145` (reference closure equivalence),
  `:209` (graph binding), `:295` (nonmutating emission), `:351` (determinism).
- Bundles/publish companion: `B2:tools/tests/test_cycle_artifacts.py:298`
  (refusals), `:414` (reruns), `:480` (forged freshness), `:560` (publisher),
  `:763` (authentication), `:852` (mutable), `:1046` (concurrent reader),
  `:1126` (age/rules), `:1172` (reason codes), `:1373` (full rule tuple).
- Queue: `B2:tools/tests/test_repair_queue.py:221` (census fallback), `:586`
  (no implicit fallback), `:620` (local labelling), `:634` (conditional gain),
  `:676` (last closure-ready bundle). Add BFME1 enablement and router tests.
- Placement: `B2:tools/tests/test_place_bodies.py:18` only tests admissible symbol
  spellings. Add single/multiple hits, conflicting callees, scope/eligibility,
  changed objects, and proof that discovery cannot mutate source or ledgers.
- Preserve BFME1 regression suites, especially `B1:tools/tests/test_link_check_r6_review.py:23`,
  `B1:tools/tests/test_link_census_truth_fingerprint.py:1`,
  `B1:tools/tests/test_build_link_census_roots.py:1`,
  `B1:tools/tests/test_census_parent_receipts.py:1`,
  `B1:tools/tests/test_next_work_finish.py:1` and
  `B1:tools/tests/test_next_work_dump_extents.py:1`. BFME2 tests supplement them.

Shared fixture dependencies: `B2:tools/tests/cycle_fixture.py:17` imports
cycle_artifacts/link_cycle and later supplies closure fixtures;
`B2:tools/tests/test_gate_exploits.py:25` writes synthetic COFF.
`B2:tools/tests/test_code_identity.py:304` uses that COFF helper;
`B2:tools/tests/test_code_identity_lib_sources.py:1` covers archive-member
scope. Publisher fixture generator and target cases are separately listed in
the configuration inventory. Test-local fixture modules are not production
modules and must not import BFME2 target policy into BFME1.

Shared-library same-name test families (`B2:tools/tests/<name>:1`); shared
libraries with no same-name test family are listed explicitly:

- `allowed_symbols` (C): no same-name family.
- `audit_ret_arity` (B): no same-name family.
- `boot_image` (C): `test_boot_image.py`.
- `boot_relayout` (C): `test_boot_relayout.py`.
- `boundary_validator` (B): `test_boundary_validator.py`.
- `build` (B): `test_build_case_resolve.py`, `test_build_include_inventory.py`, `test_build_inventory_case.py`, `test_build_lib_thin.py`, `test_build_object_paths.py`, `test_build_parallel_refs.py`.
- `check_module_registry` (B): `test_check_module_registry.py`.
- `claims` (B): `test_claims.py`, `test_claims_review_fixes.py`.
- `coffar` (A): no same-name family.
- `compiler_profiles` (C): `test_compiler_profiles.py`.
- `data_rows` (B): `test_data_rows.py`, `test_data_rows_empty_ledger.py`, `test_data_rows_hooks.py`, `test_data_rows_parallel.py`.
- `drift_classify` (B): no same-name family.
- `eh_verify` (B): `test_eh_verify.py`.
- `flag_defaults` (C): `test_flag_defaults.py`.
- `gaps` (B): no same-name family.
- `gen_case_shims` (A): no same-name family.
- `harvest` (B): no same-name family.
- `hatch_counters` (B): `test_hatch_counters.py`.
- `judges` (B): `test_judges.py`.
- `landability` (C): `test_landability.py`.
- `ledger_io` (A): no same-name family.
- `list_naked_candidates` (B): `test_list_naked_candidates.py`.
- `locate` (B): no same-name family.
- `name_agreement` (C): no same-name family.
- `name_dependents` (C): `test_name_dependents.py`.
- `name_evidence` (C): `test_name_evidence.py`.
- `name_metric` (C): `test_name_metric.py`.
- `pe_features` (A): no same-name family.
- `pe_imports` (A): `test_pe_imports.py`.
- `pin_consistency` (B): `test_pin_consistency.py`.
- `portable_lock` (A): no same-name family.
- `progress` (B): `test_progress.py`, `test_progress_site.py`, `test_progress_v2.py`.
- `re_log` (B): `test_re_log_blocked_on.py`, `test_re_log_partial.py`, `test_re_log_verdicts_at.py`.
- `reloc_ledger` (B): no same-name family.
- `rename` (C): `test_rename.py`, `test_rename_class_member.py`, `test_rename_file_global.py`, `test_rename_files.py`, `test_rename_fixes.py`, `test_rename_iniblock.py`, `test_rename_journal_fsync.py`, `test_rename_pid_probe.py`.
- `retail_body` (C): no same-name family.
- `retail_inventory` (C): `test_retail_inventory.py`.
- `similar` (B): `test_similar.py`.
- `tu_map` (B): no same-name family.
- `wb_context` (C): `test_wb_context.py`.
- `wb_data` (C): no same-name family.
- `wb_gold` (C): no same-name family.
- `wpo_detect` (C): `test_wpo_detect.py`.
- `yield_model` (B): no same-name family.
