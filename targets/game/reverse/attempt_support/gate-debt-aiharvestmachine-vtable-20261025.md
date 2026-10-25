# AIHarvestMachine vtable reference gate-debt retirement

Shard 2/4 ranked repair queue served:
`dir32,0x010967E8,_bfmeVftRva0015FE20State,"retail 0x010967E8 is already recorded as ??_7Rva0015FE20State@@6B@; reference that name, not a new one"`

In `game/GameEngine/Source/GameLogic/AI/AIHarvestMachine.cpp`:
Replaced stand-in `extern "C" void *bfmeVftRva0015FE20State[];` and its `/alternatename`
binding with direct reference to `__identifier("??_7Rva0015FE20State@@6B@")`.
The retail VA 0x010967E8 is already recorded as `??_7Rva0015FE20State@@6B@` in
`dir32_addresses.csv`.

Exact keyed `repair_queue.py pass-test` passed: all 4 bodies, 4 literals and
4 DIR32 references verify with zero baselined findings.
Exception retired from `body_guard_baseline.csv`.
No escape hatches, pins or new identities added.
