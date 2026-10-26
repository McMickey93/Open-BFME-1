# 0x0074D2D0: NamedCameras chunk parse slot (Rva0074A590ParserRegistration)

All facts below are from BFME 1 retail (`lotrbfme.exe` 1.03 unpacked); no
donor source was used.

## Boundary

- 0x0074D2B6..0x0074D2CF is int3 padding after the matched
  `getEdgeTerrainTexture` (0x0074D270, 70 B).
- 0x0074D2D0 opens a full SEH frame (`push ebp; mov ebp,esp; push -1;
  push 0x0104E08B` handler) and the body ends with `ret 8` at +0x1D7
  (0x0074D4A7); int3 padding follows to the 16-aligned 0x0074D4B0... start
  of the next code.
- The old ledger row `?d_0074d461@@YAXXZ` (0x0074D461, 52 B, Ghidra
  `Catch@00b4d461`) is this function's inline `catch(...)` block: it reads the
  parent's `[ebp-0x18]` `this`, frees the list at `this+0x0C` and rethrows
  through `_CxxThrowException(0,0)`; it has no prologue of its own. It lies
  wholly inside [0x0074D2D0, 0x0074D4AA).

## Identity

- The only reference to the body is ILT 0x0004B4CF (`jmp 0x0074D2D0`).
- That ILT address is stored at VA 0x01121B28, slot 1 of the two-slot
  vtable 0x01121B24 (data row `?g_01121B24@@3PAPAXA`); slot 0 is ILT
  0x00042F3C -> 0x0074A650, a 30-byte scalar deleting destructor.
- The matched constructor 0x0074A590
  (`game/GameEngine/Source/Common/Rva0074A590ParserRegistrationCtor.cpp`)
  installs vtable 0x01121B24 at 0x0074A60D after registering the chunk
  label "NamedCameras", so this is that registration's parse callback.
- Its sibling registration 0x0074A680 installs vtable 0x01121B30 whose
  slot 1 is the matched `ParseLightingDataChunk` (0x00747FF0), the same
  `bool (DataChunkInput &, DataChunkInfo *)` thiscall shape (`ret 8`).
- Callees are pinned ILTs: `DataChunkInput::readInt` (0x0003A805),
  `readReal` (0x0002E5E1), `readAsciiString` (0x000041C9).

## Not established

- The EA method name and the meaning of the nine reals in the 0x30-byte
  node; the source keeps `rva0074D2D0` and offset field names.
