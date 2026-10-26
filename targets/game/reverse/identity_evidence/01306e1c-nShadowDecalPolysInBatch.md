# nShadowDecalPolysInBatch storage at VA 0x01306E1C

The decorated identity `?nShadowDecalPolysInBatch@@3HA` owns one four-byte integer at VA 0x01306E1C in retail `.data`. Its initial value in retail `.data` is 0.

## Retail facts and contract

`nShadowDecalPolysInBatch` is declared and defined in `game/GameEngineDevice/Source/W3DDevice/GameClient/Shadow/W3DProjectedShadow.cpp` (matching Zero Hour `W3DProjectedShadow.cpp`) as `int nShadowDecalPolysInBatch = 0;`. It tracks the count of shadow decal polygons in the active batch. Retail `.data` places it at 0x01306E1C following `nShadowDecalStartBatchIndex` (0x01306E18) and preceding `nShadowDecalVertsInBatch` (0x01306E20).

## Extent and all users

4 bytes at VA 0x01306E1C.
