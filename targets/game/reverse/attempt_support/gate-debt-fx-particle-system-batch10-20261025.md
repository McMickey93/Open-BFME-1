# FX Particle System DIR32 gate debt retirement batch 10

Input BFME 1 revision: `2fe0335613`.
The only source file edited is:
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`.
No shared headers, providers, ledger identities or ABI declarations changed.

## Retired DIR32 exceptions

Seven DIR32 gate debts retired via machine `repair_queue.py pass-test`:

1. `dir32,0x0109C33C,?g_0109C33C@FXParticleSystem@@3QBDB`
   Retail VA `0x0109C33C` holds string literal `"Normal"`, recorded as `??_C@_06EFAGIKOH@Normal?$AA@`. Used in `CylindricalEmissionVelocityModuleTemplate::writeINI`.
2. `dir32,0x010A6938,?g_010A6938@FXParticleSystem@@3QBDB`
   Retail VA `0x010A6938` holds string literal `"SinkRate"`. Used in `RenderObjectDrawModuleTemplate::writeINI`.
3. `dir32,0x011142CC,?g_011142CC@FXParticleSystem@@3QBDB`
   Retail VA `0x011142CC` holds string literal `"Phase2"`. Used in `LightningEmissionModuleTemplate::writeINI`.
4. `dir32,0x0110FA14,?g_vtbl_0110FA14@@3PAPAXA`
   Retail VA `0x0110FA14` is recorded as `??_7?$CategoryModuleInfo@$06@FXParticleSystem@@6B@`. Used in `ConcreteModuleTemplate<DefaultModuleTag<7>>::~ConcreteModuleTemplate`.
5. `dir32,0x0110F980,?g_vtbl_0110F980@@3PAPAXA`
   Retail VA `0x0110F980` is recorded as `??_7EmissionVolumeInfo@FXParticleSystem@@6B@`. Used in `ConcreteModuleTemplate<PointEmissionVolumeModuleTag>::ConcreteModuleTemplate`.
6. `dir32,0x01110EB8,?g_vtbl_01110EB8@@3PAPAXA`
   Retail VA `0x01110EB8` is recorded as `??_7?$DefaultParticleModuleTemplate@$05@FXParticleSystem@@6B?$CategoryModuleInfo@$05@1@@`. Used in `ConcreteModuleTemplate<ModuleTag<6, ...>>` constructors. Also removed obsolete linker `/alternatename` pragma.
7. `dir32,0x01111254,?g_vtbl_01111254@@3PAPAXA`
   Retail VA `0x01111254` is recorded as `??_7?$ConcreteModuleTemplate@V?$ModuleTag@$04$E?LIGHTNING_EMISSION_MODULE_KEY@FXParticleSystem@@3QBDB$E?LIGHTNING_EMISSION_MODULE_NAME@2@3QBDBVLightningEmissionModule@2@VLightningEmissionModuleTemplate@2@V?$DefaultParticleModule@$04@2@V?$DefaultParticleModuleTemplate@$04@2@@FXParticleSystem@@@FXParticleSystem@@6BLEMCT_VtblBaseB@@@`. Used in `ConcreteModuleTemplate<ModuleTag<5, ...>>` constructors.

## Verification

- All 7 pass tests passed via `python3 tools/repair_queue.py pass-test`, automatically removing the 7 lines from `targets/game/reverse/body_guard_baseline.csv`.
- Scoped build: 470/470 functions, 21 data rows, 44 literals, 93 float constants, 1022 DIR32 references verified with zero baselined findings.
- Baseline shrank by 7 lines.
