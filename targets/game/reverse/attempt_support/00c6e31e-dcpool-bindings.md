# DC pool initializer binding prerequisite

The existing 25-byte initializer at RVA 00C6E31E keeps its identity, ABI,
extent and /O1 /Oi /MD settings. CRT initializer slot 00EA5518 establishes
the entry independently. Retail has MOV EDI,0134FB38 at +3, four STOSD
(including one after the callback push), PUSH 010715CA at +0x0B, and RET
at +0x18. These operands establish the object and cleanup relationship.

The recorded TheDcPool object at VA 0134FB38 is already referenced by
Win32DcCache.cpp and Rva00C715CAForwarder.cpp. The former declares four
LONG slots; its matched acquire body at RVA 0005C080 iterates four slots
with InterlockedExchange before CreateCompatibleDC. The 10-byte cleanup
wrapper at RVA 00C715CA loads the same address into ECX and tail-jumps to
CDCCache::~CDCCache at RVA 009F6855. That 29-byte destructor checks four
slots and calls DeleteDC for non-null entries. These are BFME 1 target
facts; this repair neither establishes a new name nor guesses a layout.

The initializer now references TheDcPool through a forward declaration
and clears exactly four 32-bit words. Its callback now references the
existing matched rva00C715CAForward provider instead of the undefined
Rva00C715CARelease spelling. No object definition, data row, pin, alias,
shared header or class definition is added. The other initializer in the
same TU is unchanged and is verified together with the repaired row.

Donor review: read-only BFME 2 master
8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9 was searched in Code/,
reverse/functions.csv, reverse/attempt_support/ and docs/recipes.md for
DcPool, CDCCache and TheDcPool. No corresponding provider, recipe or
matching source was found. No donor source, name, ABI or setting contributes.
The pinned donor pointer was not changed.

Related BFME 1 review found the recorded legacy bfmeThePoolCJD binding
in BfmeConv612.cpp and g_bfmeSrc1044 binding. These already have separate
DIR32 records; changing them would require independent provider/ABI work.
TheDcPool remains externally declared: this repair is an initializer and
cleanup binding prerequisite, not an assertion that the global is defined
or that the complete pool family links.

Acceptance: scoped initializer build and repair_queue.py pass-test both
pass 2/2 rows with four DIR32 references and zero body exemptions. The
pass-test removes only the retired private storage binding exemption; gate
debt shrinks 1021 -> 1020. Cleanup wrapper passes 1/1, Win32DcCache.cpp
passes 2/2, and CDCCacheDestructor.cpp passes 1/1. No authored C++
coverage is added.

Link preview before: two unresolved names (Rva00C715CARelease and the
private storage global), LINKED 0 -> 0 bytes. After: the callback resolves
to its verified provider; only TheDcPool remains unresolved, LINKED 0 -> 0
bytes. Census 2026-10-24 11:02 at 32774ab033 lacks 22,646 current objects
in this container, so selection and any linked-byte improvement remain
UNKNOWN. No census rebuild or fabricated linked-byte credit is used.
