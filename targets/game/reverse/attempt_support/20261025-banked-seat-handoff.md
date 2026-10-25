# Banked seat handoff, 2026-10-25

No new accepted C++ conversion or linking gain in this run. The substantive
result is the stronger 0x0060F3C0 candidate: 184 bytes, nine relocations, six scratch
register differences instead of thirteen. The independently verified callee
route and counted-reference ABI are prerequisites for finishing that body;
the superficially exact legacy constructor declaration selects the wrong twin.
See [the audio handoff](20261025-counted-audio-handoff.md) and its linked target
evidence. This evidence commit is not byte progress.

The named-tier listing returned 156 reloc-named entries before and after the
compiler trials. All had prior attempts (audit: 133 blocked, 21 partial, two
attempted). The final listing has 157 after restoring the inherited blocked
army-visual candidate. Reviewed the existing high-score banks and histories; did not repeat
unchanged donor/refusal or source-variation matrices. New independent trials
for score-screen merging, counted audio, LivingWorldSound cleanup, the Object
predicate, closed-list release and the EVA picker are recorded in re_attempts.log.
Only the audio candidate improved. Its remaining six bytes need a new legitimate
constructor-call lowering/allocation explanation. W3DView's native BFME 2 donor
compile was refused by source classification because of its existing x87
helper; no alternate compiler path bypassed that refusal.

Pre-commit refused the audio preferred-bank update under name_regression
(seven descriptive-to-placeholder findings). The preferred file is restored
unchanged. The new candidate is retained only as immutable attempt evidence;
the refusal is recorded in the log. No gate bypass or guessed-name landing.

The permitted repair fallback listed 991 items, all DIR32. Three pass tests:

* The rva0032a490 entry has no exact decorated source spelling, so the helper
  cannot select a source to verify; no baseline deletion occurred.
* TheLivingWorldManager: Bfme5RemoveEntry.cpp passed its function (108 bytes),
  source, string and constant checks, but DIR32 still refuses the canonical
  global at VA 0x012F706C because the ledger records older aliases.
* TheLivingWorldLogic: Glo012F1024Item_stringByteDispatch.cpp passed its function
  (182 bytes), source, string and constant checks, but DIR32 still refuses its
  canonical global at VA 0x012F1028 for the same ownership reason.

Both failed pass tests automatically restored their baseline lines. The next
step for those items is reconciling the DIR32 ownership check with the matched
canonical data rows, outside this seat's tool-edit limits. Do not add a second
data row or replace the canonical identity with an alias to evade the check.
Do not repeat the unchanged pass tests. No baseline, pin, generated source,
shared header or production source change is part of this evidence commit.

BFME 2 reference inspected: read-only current master
8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9. BFME 1's pinned donor pointer was
unchanged. Compiler trials used MSVC 7.1 with private experiment-store objects;
normal byte/relocation checks remain required before any bank can be rowed.
check_csv and diff whitespace checks pass. Link census preview is unknown
because prepared objects are unreadable/stale; no linked-byte gain is claimed.

Commit 07061e6716499d27f4d1c5f8d53453929ffb90dd was inherited from the previous
run with 648 exact C++ bytes previously verified in LivingWorldArmyVisual.cpp.
Publication rebased it onto 69d6af4071, resolving an append-only conflict in
docs/shape_levers.md by preserving both discoveries. The conversion source
itself was unchanged. The required scoped rebuild still passed its 648-byte
function, two strings, one float and source claims, but failed DIR32 for the
canonical TheLivingWorldManager at VA 0x012F706C. The canonical matched data
row is present (LivingWorldManager.cpp); the checker instead demands one of
the old aliases. This refusal is logged, not bypassed.

The conversion was removed from the publish batch and preserved intact at
43932c4c33 on local branch runner/codex7-0060acb0-dir32-blocked-20261025.
That commit contains the source, original evidence and successful compiler
discovery; inspect it with git show before resuming. Fix the ownership-check
prerequisite within maintainer scope, then replay and rebuild it normally.
No 648-byte gain is claimed as accepted or published in this run. After
parking it, the final batch contains only evidence and logs (+0 exact C++,
+0 linked). The preferred attempt source is restored from upstream.
