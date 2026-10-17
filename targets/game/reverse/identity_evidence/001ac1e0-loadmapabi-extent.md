# 0x001AC1E0 TerrainLogic::loadMapAbi: 381-byte extent with an inline catch funclet

Session a1/58, 2026-10-17, model=claude-opus-5-5.

Retail 0x001AC1E0..0x001AC35D is one function. MSVC 7.1 placed its catch
funclet in the middle of the body:

- 0x001AC2F7: the try body's last call, then `jmp 0x005AC311`.
- 0x001AC305: the catch funclet, `mov eax, 0x005AC30B; ret` (the catch block
  returns its continuation address to the EH runtime).
- 0x001AC30B..0x001AC35D: the continuation, ending `ret 0x10`.

The ledger had three rows over this range: the parent at 293 bytes (to the
funclet), `?Rva001AC305Get@@YAPAXXZ` (6 B, read as a function returning the
constant 0x005AC30B, which is the funclet) and `?d_001ac311@@YAXXZ` (76 B,
the continuation from 0x001AC311 as a gen dump; 0x001AC30B..0x001AC311 was
unowned). The parent's source, TerrainLogic_loadMap_Thunk.cpp, compiles to
381 bytes and `tools/probe.py --size 381` reports it EXACT against retail, so
the parent row now covers the whole range and the two rows are retired;
Rva001AC305Get.cpp is deleted (nothing references it).
