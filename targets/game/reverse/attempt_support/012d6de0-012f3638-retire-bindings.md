# Retire two unused records after existing ownership repairs

This is one homogeneous registry-retirement batch. It changes no executable
statement, function identity, boundary, layout, ABI, name, initializer or
compiler flag. No new address record, data row or pin is introduced.

BFME 1 commit c4ca16ec8a9ed956fc2ca54f6bd5fb53c89935f1 established the
matched 24-byte CRITICAL_SECTION at VA 012D6DE0 in
game/GameEngine/Source/Common/Rva00C6DDE0CriticalSectionInit.cpp.
The target's initializer 00C6DDE0 passes its address to
InitializeCriticalSection and registers shutdown 00C71040, which calls
DeleteCriticalSection. DeviceReset_releaseResources_rva0090F050 and
BfmeConv911 use the same cell in their enter/leave guard paths. The next
matched datum is the armed bool at +24; the current build verifies the
critical section's zero initializer and the bool's initializer 1. The old
char spelling g_012D6DE0 was removed from BfmeConv911 by that ownership
repair but its registry reservation remained.

BFME 1 commit 490b8e7ca6ee578c0ed8f3c5af1657d840fbd9e1 established
the matched four-byte zero-initialized int at VA 012F3638 in
game/GameEngine/Source/Common/Gen_ctor_004b02a0.cpp. The existing 134-byte
constructor post-increments this cell, formats Flash%d and passes its string
to CreateButtonFlash and ShowButtonFlash. That repair replaced an unsupported
semantic spelling with the existing address-derived name; the obsolete
g_buttonFlashNumber registry reservation remained. No class identity is
inferred or expanded here.

Neither old identifier occurs anywhere in tracked game/ or
inputs/reference/shims/. tools/dir32_record.py retire accepts both deletions
for their existing matched owners. Provider comments document the exact
external symbols for repair_queue.py's existing keyed source locator.

BFME 2 read-only revision 16c3ea885a293dafc872dd5b67a59fa92b1d6407
was searched narrowly. Code/GameEngine/Source/GameClient/GUI/
Rva005C663CCtor.cpp and its history (0de59772f6, 039554ea91) contain an
analogous Flash%d constructor but explicitly leave its owner class unproven.
No donor source, name, address, layout or provider placement is imported;
the existing BFME 1 target evidence and ownership commits establish this
repair. No matching critical-section donor repair was found by symbol search.
The pinned donor reference remains unchanged.

Acceptance: both repair_queue.py pass-test calls report PASS and remove
their keyed DIR32 exemptions (1014 -> 1012). Provider builds verify 2/2
functions, 3/3 matched data rows and six DIR32 references. Three critical-section
consumer builds verify 8/8 functions and 39 DIR32 references. Every build has
zero body exemptions. CSV integrity, declared-unmatched checks on both
providers and whitespace checks pass. Scope logs are build/owners-*.log.

link_check.py --compile-limit 0 is run on both providers before and after;
both display 23 -> 23 linked bytes with LINKED PREVIEW UNKNOWN.
Missing or stale census objects prevent a known linked-byte improvement;
the constructor also retains its existing unresolved destructor.
The verified improvement is two fewer gate exemptions and two fewer obsolete
address records, completing the earlier ownership prerequisites. Exact C++
coverage grows by zero bytes.
