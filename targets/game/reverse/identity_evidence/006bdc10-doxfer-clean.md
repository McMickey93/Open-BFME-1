# 0x006BDC10 W3DGhostObjectManager::DoXfer in clean C++

Retail 0x006BDC10..0x006BDD9B (395 bytes): two `ret 4` exits at +0xBF and
+0x156, then the hash-hit block whose backward JMP at +0x189 ends the body
(INT3 from +0x18B). The extent is the one the MASM dump
`game/masm_dumps/Rva006BDC10GhostXfer.asm` carried as `?Rva006BDC10@@YAXXZ`.

## Identity

- The matched constructor `??0W3DGhostObjectManager@@QAE@XZ` (0x006BC8C0)
  installs vftable 0x0111CFE0. Slot 2 reaches the 6-byte
  "W3DGhostObjectManager" name getter 0x006BC8E0 (ILT 0x000367A0), slot 3 (the
  BFME Snapshot DoXfer slot, as for TeamFactory and LivingWorldEyeTower)
  reaches this body through ILT 0x0000D12A, and slot 7 reaches the matched
  `?addGhostObject@W3DGhostObjectManager@@UAEPAVGhostObject@@PAVObject@@@Z`
  (0x006BD280, ILT 0x000461EB), which this body calls through `[vtbl+0x1C]`.
- `python3 tools/ilt_oracle.py check '?DoXfer@W3DGhostObjectManager@@MAEXAAVXfer@@@Z' 0x006BDC10`
  prints `CONFIRMED p_false=1.96e-04 (exact)`. The ZH spelling
  `?xfer@W3DGhostObjectManager@@MAEXPAVXfer@@@Z` and
  `?DoXfer@W3DGhostObject@@MAEXAAVXfer@@@Z` are CONTRADICTED at this address.
- The body is GeneralsMD W3DGhostObject.cpp `W3DGhostObjectManager::xfer`:
  base transfer (0x001B3B00 through ILT 0x00024230), version 1, the count of
  the used-module list linked at +0x110, then ObjectID + ghost snapshot per
  module on save, or ObjectID, inline GameLogic hash lookup (+0xB0),
  addGhostObject and the shroud-manager provider bind on load.

## Callees

- 0x0010C3C0 via ILT 0x0000C9B4: the ledger's
  `?Rva0010C3C0@@YAAAVXfer@@PAVMidVirtualSlot90Receiver@@PAX@Z` (cdecl, two
  arguments, `add esp,8` at both call sites), as TunnelTracker_xfer.cpp calls it.
- 0x008F73B0: an 8-byte forwarder `mov ecx,[ecx+0Ch]; jmp 0x008F8C70`, the
  matched `?rva008F8C70@ShroudManagerImpl@@QAEXPAVCDEProvider@@0@Z` (RET 8).
  The caller loads TheShroudManager (0x012ED5BC) into ECX and pushes the
  nullable ghost provider and Object+0x64. It is pinned under the
  address-derived `?rva008F73B0@ShroudManager@@QAEXPAVCDEProvider@@0@Z`, like
  its sibling forwarders 0x008F7370 and 0x008F7390;
  `pin_consistency.py --symbol` reports it consistent.
- Data: `?TheGameLogic@@3PAVGameLogic@@A` (0x012F0898),
  `?TheShroudManager@@3PAVShroudManager@@A` (0x012ED5BC) and
  `?TheGhostObjectManager@@3PAVGhostObjectManager@@A` (0x012EF4FC), the
  data_rows.csv names.

## The frame wall

The banked C++ (attempt_history/0x006bdc10) held at three bytes for several
sessions: the `Xfer::Version` aggregate took the dead `xfer` argument slot,
where retail keeps `count` and puts the version pair in the frame beside the
loader's loop counter. The `/FAsc` tables show the rule: VC7.1 hands the dead
argument slot to an aggregate `Xfer::Version` (or a char array, or a union)
ahead of `count` whenever the two overlap. Declaring `count` first in one
enclosing block and building the version as the constructed `XferVersion`
record in its own block gives retail's table (`objectID` -8, `i` and
`version` -4, `count` +8), and the body compiles byte-identical modulo its
relocation slots.
