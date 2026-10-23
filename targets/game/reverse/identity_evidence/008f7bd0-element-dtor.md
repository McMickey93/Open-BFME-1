# 0x008F7BD0 is the CDE array element destructor

The matched `BfmeThingCDE::initializeArray` (0x008F7E20, BfmeThingCDEInitializeArray.cpp)
builds its array with the EH vector constructor iterator (`??_L` 0x009F6EE4), pushing
the element destructor 0x00CF7BD0 (VA) and constructor 0x00CF7BC0 (VA) at +0x22/+0x27.
dir32_addresses.csv records those two operands as `??1Element@@QAE@XZ` and
`??0Element@@QAE@XZ`, the TU's own element class. The one-byte `ret` at 0x008F7BD0
had been landed as the opaque free function `?Rva008F7BD0Empty@@YAXXZ`
(Rva004C5480EmptyBodies.cpp); the caller proves it is that element's empty
destructor, so the row moves to `??1Element@@QAE@XZ` in the caller's TU.
