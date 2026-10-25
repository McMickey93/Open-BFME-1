# Particle writer literal references

Input BFME 1 revision: `410d59252f`. The only source edited is
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`.
No shared headers, providers, ledger identities or ABI declarations change.

## String evidence

Retail VA `0x0108EE10` contains `Radius\0`, already recorded as
`??_C@_06GJMFONGK@Radius?$AA@`. The Cylinder writer at RVA `0x005F95C0`
pushes it at `0x005F9651`; the Sphere writer at RVA `0x005FAAE0` pushes it
at `0x005FAB71`. Their existing matched extents are 470 and 340 bytes,
ending in RET 8 at `0x005F9793` and `0x005FAC31` respectively.

Retail VA `0x0109F2A4` contains `Offset\0`, already recorded as
`??_C@_06GEMKPBPA@Offset?$AA@`. The Cylinder writer pushes it at
`0x005F96D3`. Replacing the two external array references with the exact
literals preserves the native pointer arguments. The names, member
offsets, conditional tests, formatter calls and stream lifetimes remain
unchanged. The existing Sphere identity evidence cites the decorated
method and matching Point/Cylinder sibling ABI; no new identity is asserted.

## Shared zero prerequisite

The first string-only trial matched all 470 functions and eight data rows,
but the scoped gate exposed 90 unchanged references to
`?g_rva01075350@@3MB`. Its old shared exception had already been removed
by the earlier parser/Drawable repair recorded in
`20261025-readonly-float-debt.md`. The existing matched data row in
`BfmeAngleWrap0079D0.cpp` proves four readonly zero bytes at VA
`0x01075350`. This unit's 90 comparisons now spell that value as `0.0f`.

This is one comparison pattern across twelve existing writer rows:

| Module template | RVA | Existing extent |
| --- | --- | ---: |
| BoxEmissionVolume | 0x005F8CF0 | 376 |
| CylinderEmissionVolume | 0x005F95C0 | 470 |
| CylindricalEmissionVelocity | 0x005F9170 | 388 |
| LightningDraw | 0x005F5150 | 538 |
| LightningEmission | 0x005FBDB0 | 1020 |
| LineEmissionVolume | 0x005F9B80 | 459 |
| OrthoEmissionVelocity | 0x005F9EA0 | 454 |
| OutwardEmissionVelocity | 0x005FA1B0 | 388 |
| RenderObjectDraw | 0x005F7A50 | 887 |
| RenderObjectUpdate | 0x00600E10 | 1099 |
| SphereEmissionVolume | 0x005FAAE0 | 340 |
| SphericalEmissionVelocity | 0x005FA710 | 322 |

All are existing `FXParticleSystem::*ModuleTemplate::writeINI(File&,
unsigned) const` identities. Before editing, their attempt records and
callee packs were reviewed. The former formatter-ABI migration refusal is
unrelated and was not retried. Existing layouts, return boundaries and
callees are preserved by the complete scoped byte/relocation check.

## Acceptance and provenance

The normal scoped build passes all 470 functions and eight data rows,
24 string references, 93 float references, 1,042 remaining DIR32 references
and zero baselined body findings. Both keyed string `repair_queue.py
pass-test` commands pass the entire unit and delete exactly their two
exceptions: gate debt 988 -> 986. The zero prerequisite separately removes
90 unbaselined DIR32 failures; it does not delete another baseline entry.
Eight existing funclet rows are resolved past changed compiler label
numbers by the gate; no funclet pins were edited.

Compiler and includes remain the TU's existing MSVC 7.1 `/EHsc` controls
and BFME 1 Common/System, Common, WWMath and WWLib paths. No new alias,
pin, datum, name, compiler override or escape hatch is introduced.
The same-unit literal repair in BFME 1 commit `45c2f47596` was reviewed.

Read-only BFME 2 revision `e2fdc5620c5834c1c98de24aa3510d72e2cbcc69`
was searched by the existing names and Cylinder/Sphere family. Its
ParticleSystemTemplateWriteINI.cpp, related module writers and family
history provide no required implementation for these operands; no donor
body, layout, address or compiler context was imported. Values and string
addresses come from BFME 1 retail and its existing data/constant records.
No authored-C++ or newly linked-byte gain is claimed.
