# Pathfinder readonly operands: one gate debt removed

Input BFME 1 revision: `d3020c62f3dce8c60a66e869b3471d1e88ae2a28`.

The existing matched data rows establish VA `0x010977E0` as readonly
`00 00 A0 41` (`20.0f`) and VA `0x01075350` as readonly zero (`0.0f`).
The matched `Pathfinder::getRadiusAndCenter` row establishes the 297-byte
body at RVA `0x003DEE30`; its existing visible copies in
`PathfinderRva003DF250.cpp` and `PathfinderInternalFindPath.cpp` preserve
the non-retaining helper context required by those callers. No new identity,
layout, ABI, boundary, callee, global name or data row is inferred here.

All three helper copies now express these two proven readonly values as
literals. The first normal build passed both function rows but rejected
the existing `g_rva01075350` DIR32 operand at helper+`0x9a`; changing that
comparison to the independently proven zero literal completes the repair.
The mutable `0.3f` bias remains an external load.

Normal scoped builds pass:

* `PathfindGetRadiusAndCenterE30.cpp`: 2/2 functions, 14 float constants,
  19 DIR32 references, zero baselined findings.
* `PathfinderRva003DF250.cpp`: 1/1 function, 2 float constants,
  3 DIR32 references, zero baselined findings.
* `PathfinderInternalFindPath.cpp`: 1/1 function, 27 strings,
  4 float constants, 52 DIR32 references, zero baselined findings.
* `PathfinderCellConstants.cpp`: both existing data rows pass.

The sanctioned `repair_queue.py pass-test` for
`?g_Rva010977E0@@3MB` selects the first consumer, passes its normal gate,
and removes exactly one exception: 985 -> 984 debts. The other consumers
were verified independently, so locator success alone is not the evidence.
CSV and declared-unmatched checks pass. No verifier or registry was edited.

Read-only BFME 2 `e2fdc5620c5834c1c98de24aa3510d72e2cbcc69` was searched
for the operand name and radius helper. No corresponding source or applicable
repair was found; this repair uses BFME 1 target and matched-data evidence.
The pinned donor reference remains unchanged.

Census-only `link_check.py` before the edit reports 647 linked bytes across
these files: the DF250 unit links, while the other two retain unrelated
callee/global/COMDAT blockers. This is a census preview, not a measured new
link gain. `progress.py origin/master` reports +0 exact C++ bytes and +0
linked bytes. The measured improvement is the passing keyed gate debt.

The served TeamReadyQueue link blocker was separately reassessed, recorded
blocked and released: unchanged census `32774ab033`, artifact `12560789240`,
and BFME 2 iterator evidence do not resolve its incompatible provider views
or missing current dependency evidence. No disproven compiler trial repeated.
