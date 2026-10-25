# GridLink pool ownership prerequisite

The existing rows at 0x008DDEB0 (20 bytes) and 0x008DDED0 (36 bytes)
keep their names, ABI and extents. The first ends at RET +0x13; the second
ends at RET4 +0x21. Both load 0x0133D1AC into ECX before calling the matched
GridLinkClass Free_Object_Memory specialization at 0x008DDA50. The second
also calls 0x008DD8A0 and retains its original deletion-flag test and return.
This repair makes no new claim about its placeholder class or method names.

BFME 1 dir32_addresses.csv records 0x0133D1AC as
AutoPoolClass<GridLinkClass,256>::Allocator. gridcull.cpp defines that member
with DEFINE_AUTO_POOL, and gridcull.h establishes the GridLinkClass AutoPool
base. Both consumers now use the existing public AutoPool operator delete,
which supplies the same null guard and canonical allocator reference. Their
existing external free-specialization declarations retain the lock-bearing
provider in ObjectPoolFreeObjectMemory.cpp. No private allocator access,
class definition, data ownership row or pin is introduced.

BFME 2 donor review: 8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9,
Code/Libraries/Source/WWVegas/WWMath/gridcull.cpp and matched AutoPool new/delete
rows at 0x0071B440/0x0071B450 associate this interface with one GridLink pool.
That corroborates the interface pattern; BFME 1's pool address, call targets
and guards come from its own retail image and records. No donor flags,
layout, shim, address or name was imported.

Acceptance: scoped builds pass the standalone wrapper 1/1, mixed unit 3/3
and pool-owning gridcull.cpp 66/66. All DIR32 references pass, with zero
baselined body findings. The unchanged shared free-provider passed 9/9 in
the preceding MultiList repair. Both repair_queue.py pass-test commands pass
and delete exactly the two obsolete pool-name exemptions. Gate debt falls
1023 -> 1021; exact C++ coverage is unchanged.

This is the GridLink pool-family linking prerequisite, following the verified
MultiList repair. link_check.py before reports the old pool reference unresolved
in each consumer. After, neither old pool reference remains unresolved. The
standalone wrapper changes from does-not-link to LINKED PREVIEW UNKNOWN; the
mixed unit still has independent unresolved destructor, report helper and GUID
references. Both checks count linked 0 -> 0 bytes. The after check exits 1
with 22,652 unavailable current ledger objects against census 2026-10-24 11:02
at 32774ab033. A current census/dependency set is needed before claiming any
linked-byte improvement; no new linked or exact C++ bytes are claimed here.
