# MultiList pool ownership prerequisite

The existing opaque 20-byte row at 0x009DBF40 keeps its name and extent.
Retail loads the argument, guards null, loads 0x0134ECD4 into ECX, calls
0x009DBEB0 and returns at +0x13. `callees.py` identifies that call as the
already matched MultiListNodeClass `Free_Object_Memory` specialization.

BFME 1 `dir32_addresses.csv` records 0x0134ECD4 as
`AutoPoolClass<MultiListNodeClass,256>::Allocator`. `multilist.cpp` owns it
through `DEFINE_AUTO_POOL`. Calling the existing public AutoPool delete
interface emits the same wrapper while referencing that owner. The explicit
free specialization declaration prevents instantiation of the unlocked
upstream template; the matched lock-bearing provider remains in
`ObjectPoolFreeObjectMemory.cpp`. This changes no class definition or data pin.

Donor review: Open-BFME-2 8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9,
`Code/Libraries/Source/WWVegas/WWLib/multilist.cpp` and its rows at 0x00610770
and 0x00610780 also associate AutoPool new/delete with one pool. This is
corroboration of the interface pattern, not BFME 1 address or identity proof.
No donor flags, shim, layout, address or function name was imported.

Acceptance: scoped builds pass 1/1 wrapper, 9/9 free-provider and 20/20
multilist rows. The wrapper verifies its DIR32 reference without an exemption.
`repair_queue.py pass-test` removed exactly its old pool-name exemption;
`progress_v2.py` reports gate debt 1024 -> 1023.

This is a prerequisite for linking the pool family, not a new conversion.
`link_check.py` before: unresolved old pool name and wrong free COMDAT.
After: neither finding remains. Both reports say linked 0 -> 0 with selection
preview unknown: 22,656 ledger objects are unavailable against census
2026-10-24 11:02 at 32774ab033. No linked-byte gain is claimed. A refreshed
census/current dependency set is required to measure provider selection.
