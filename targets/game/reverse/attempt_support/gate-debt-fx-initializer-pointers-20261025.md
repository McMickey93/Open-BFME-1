# FX initializer recorded-pointer debt repairs

Source: `game/GameEngine/Source/Common/Rva00C6BEA0Initializers.cpp`.
Shard: 1/4. Parent: 13ad3fc5d2.

Eight initializer destinations already have exact names in BFME 1
`dir32_addresses.csv`. Declare and reference those recorded FXParticleSystem
`void **` objects rather than the old unscoped `void *` references.
Preserve every initializer function, pointer value and absolute store.
The pointer type/cast follows the recorded declaration and existing consumers;
no class layout, calling convention, function identity or new data owner changes.
Comments retain the retired decorated key as provenance and allow the keyed
pass test to locate the repaired source. No donor input or name inference used.

| Retail VA | Retired key | Recorded owner |
| --- | --- | --- |
| 0x012F6CA0 | `?Rva00EF6CA0@@3PAXA` | `?streakDrawSourceAt8@FXParticleSystem@@3PAPAXA` |
| 0x012F6CBC | `?Rva00EF6CBC@@3PAXA` | `?renderObjectDrawSourceAt4@FXParticleSystem@@3PAPAXA` |
| 0x012F6D14 | `?Rva00EF6D14@@3PAXA` | `?defaultModuleTag7SourceAt8@FXParticleSystem@@3PAPAXA` |
| 0x012F6D1C | `?Rva00EF6D1C@@3PAXA` | `?lifeEventSourceAt4@FXParticleSystem@@3PAPAXA` |
| 0x012F6D4C | `?Rva00EF6D4C@@3PAXA` | `?cylindricalEmissionVelocitySourceAt4@FXParticleSystem@@3PAPAXA` |
| 0x012F6D50 | `?Rva00EF6D50@@3PAXA` | `?outwardEmissionVelocitySourceAt8@FXParticleSystem@@3PAPAXA` |
| 0x012F6D6C | `?Rva00EF6D6C@@3PAXA` | `?boxEmissionVolumeSourceAt4@FXParticleSystem@@3PAPAXA` |
| 0x012F6D80 | `?Rva00EF6D80@@3PAXA` | `?lightningEmissionSourceAt8@FXParticleSystem@@3PAPAXA` |

Every printed keyed pass-test passes on its first attempt. Each test verifies
67/67 bodies and 119 DIR32 references, then removes only its own exception.
Baseline entries shrink from 940 to 932. Source bytes remain unchanged:
+0 B exact C++; eight stricter gate checks are the credited improvement.
Normal scoped build and commit hooks also verify the combined batch.

Skipped display00487F80: recorded TheDisplay has a different private virtual
class type; requires class-contract/header reconciliation beyond mechanical
debt scope. Claim released. Existing Rva0086B360Dispatch false-reject and naming
blocker already recorded; unchanged evidence was not retried, claim released.
