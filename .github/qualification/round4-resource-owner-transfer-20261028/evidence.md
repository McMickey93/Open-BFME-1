# Resource-bar binding to the LivingWorldLogic data owner

Target: `Rva0058DBC0OwnerUpdate.cpp`, existing rows 0x0058DD70/71B and 0x0058DDD0/872B.
The project link queue serves the undefined Glo012F1028 pointer in this unit (943 B at census a0940f921b). The old name has no defining provider.

## Independent BFME 1 evidence

The matched data row owns `LivingWorldLogic *TheLivingWorldLogic` at VA 0x012F1028.
`LivingWorldLogic.cpp` records the GameEngine::init literal/store, constructor vtable and class-name witnesses; its four zero-initialized bytes are verified with the consumer.
The update changes the external pointer name and type only. Each use casts to the existing local Glo012F1028Type view. Fields +0x2C/+0x2D, all calls, branch ordering and the 71B sibling are retained.
No definition, pin, DIR32 authority line, header, field, data row or function row is added.

## Donor review and limits

BFME 2 revision 3459c2524cf56b2b06cac4217e8a839e3e26984e uses one typed LivingWorldLogic owner in `Code/GameEngine/Source/GameLogic/System/LivingWorld/LivingWorldLogic.cpp` (data VA 0x00DFEF10). Client users such as `ArmyUnitSwapperSelection.cpp` and `Eva.cpp` reuse that global through local views. The owner/binding pattern is corroboration; no BFME 2 address or field offset is imported.
BFME 1's donor reference remains 73898a96342963eac2826836db10649a69e3dbb8, with its 2026-10-27 freshness receipt still within 72 hours. The target compiles against its own inputs.

## Qualification

Use paired unmodified build.cmd checks for the complete consumer and data provider. Compare every non-debug COFF section, relocation target and external definition; the only permitted undefined-symbol replacement is the old pointer to the canonical data name.
Local execution could not launch the compiler (WinError 623); no local successful byte check is claimed. Native Windows receipts follow below.
Before/after link previews keep their actual exit codes. A stale or incomplete census is UNKNOWN; no measured linked-byte gain is claimed. New C++ bytes: zero.
