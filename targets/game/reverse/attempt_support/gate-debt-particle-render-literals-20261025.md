# Particle writer RenderObjectUpdate literal references

Input BFME 1 revision: `01cfc68123`. The only source edited is
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`.
No shared headers, providers, ledger identities or ABI declarations change.

## String evidence

Retail image strings and PUSH operands establish the exact string literals used in
`RenderObjectUpdateModuleTemplate::writeINI` (RVA `0x00600E10`, size 1099 bytes):

- 0x01114A90: "StartSizeX"
- 0x01114A80: "StartSizeY"
- 0x01114A70: "StartSizeZ"
- 0x01114A64: "SizeRateX"
- 0x01114A58: "SizeRateY"
- 0x01114A4C: "SizeRateZ"
- 0x01114A3C: "SizeDampingX"
- 0x01114A2C: "SizeDampingY"
- 0x01114A1C: "SizeDampingZ"
- 0x01114930: "AngleZ"
- 0x01114920: "AngularRateZ"
- 0x0111490C: "AngularDamping"
- 0x01114900: "Rotation"

The writer at RVA `0x00600E10` pushes each literal pointer directly in sequence:
`0x600e8f: push 0x1114a90` ("StartSizeX")
`0x600ed1: push 0x1114a80` ("StartSizeY")
`0x600f13: push 0x1114a70` ("StartSizeZ")
`0x600f55: push 0x1114a64` ("SizeRateX")
`0x600f97: push 0x1114a58` ("SizeRateY")
`0x600fd9: push 0x1114a4c` ("SizeRateZ")
`0x60101b: push 0x1114a3c` ("SizeDampingX")
`0x60105d: push 0x1114a2c` ("SizeDampingY")
`0x60109f: push 0x1114a1c` ("SizeDampingZ")
`0x6010e1: push 0x1114930` ("AngleZ")
`0x601126: push 0x1114920` ("AngularRateZ")
`0x60116b: push 0x111490c` ("AngularDamping")
`0x601198: push 0x1114900` ("Rotation")

Replacing the 13 external array references with string literals preserves the native
pointer arguments and exact compiled byte match. The names, member offsets, conditional
tests, formatter calls, stream lifetimes and function boundaries remain unchanged.

## Acceptance and verification

The normal scoped build passes all 470 functions and eight data rows, 37 string
references (13 newly verified literals), 93 float references, 1,029 remaining DIR32
references (down from 1,042), and zero baselined body findings. All 13 keyed string
`repair_queue.py pass-test` commands pass the entire unit and delete their exceptions
from `targets/game/reverse/body_guard_baseline.csv` (gate debt reduced by 13).
No new alias, pin, datum, name, compiler override or escape hatch is introduced.
