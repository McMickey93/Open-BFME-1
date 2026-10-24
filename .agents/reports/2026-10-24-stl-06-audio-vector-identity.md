# Audio vector insert-overflow identity blocker

Queue 35 names `vector<Pair006AA940>::_M_insert_overflow`, emitted by `ResolveAudioPointers006AA940.cpp`. The source models an eight-byte pointer/float pair.

`callees.py 0x006AA940 439` proves that the verified resolve caller reaches ILT `0x0001CD6E` -> retail `0x006A3F90` with a five-slot thiscall ABI. That address already has one matched identity (`?dup_006a3f90@@YAXXZ`, object symbol `vector<OCLSpecialPowerModuleData::Upgrades>::_M_insert_overflow`) from `OCLUpgradesVectorInsert.cpp`.

Direct COFF facts using `link_census.object_facts` with current RetailTruth distinguish the local audio copy (306 bytes, digest df2cfed4f1c6, wrong) from the Upgrades provider (305 bytes, digest 6d0250921964, retail). Deleting the local body leaves its unrelated Pair symbol unresolved; pinning it to the Upgrades address would add a second semantic identity. Equal eight-byte stride alone does not prove the types are the same.

BFME2 was consulted read-only: its `Code/GameEngineDevice/Source/MilesAudioDevice` sources include audio manager and sample reconstruction, but no corresponding proven pointer-resolution implementation was found. There is no independent evidence allowing the audio pair to be renamed to Upgrades.

Outcome: blocked on the callee/type identity. No source or pin change retained, no linked-byte gain claimed. Retail boundary is the existing 305-byte Upgrades row; the current 439-byte resolve body passes its scoped build (1/1 functions, three DIR32 references). The older census lists 438 own bytes; its 0 -> 0 link verdict is not a current gain measurement.
