# Queue 16: AsciiString map operator[]

Blocked on global COMDAT selection, not a missing caller declaration. Both
queued callers (Open2Twins003 and setCampaignDifficulty) already declare the
operator externally. Their current COFF symbols have section zero: neither
emits it. Suppressing another definition in either caller is impossible.

The canonical owner AsciiStringMapMetaDataMapOperatorThunk.cpp defines the
231-byte retail body at 0x0007DF70 and passes 1/1 with all scoped guards.
The two queued callers pass 4/4, eight string literals and all scoped guards.
The copied October 19 census contains 41 wrong copies, including a historical
wrong verdict for this now-verifying owner. It selects FirewallHelper first.
Its census-only preview reports selected-not-retail for both callers, 0/2.

A current `link_check.py --compile-limit 0` was allowed to finish (155.9s):
both callers report LINKED PREVIEW UNKNOWN, 0/2, LINKED 0 -> 0. It cannot read
21,685 new/changed ledger objects. The historical wrong verdict cannot serve
as current proof, and the current UNKNOWN cannot serve as a success.

No source, pin, shared header, generated source or baseline was changed.
Before/after are identical. Future work must handle actual competing emitters
while preserving their verified helpers and then refresh global selection.
The re_log locator is the synthetic queue key, not a retail body boundary.
