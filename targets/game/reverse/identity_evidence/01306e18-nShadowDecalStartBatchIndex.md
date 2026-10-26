# nShadowDecalStartBatchIndex storage at VA 0x01306E18

The decorated identity `?nShadowDecalStartBatchIndex@@3HA` owns one four-byte integer at VA 0x01306E18 in retail `.data`. Its initial value in retail `.data` is 0.

## Retail facts and contract

`nShadowDecalStartBatchIndex` is declared and defined in `game/GameEngineDevice/Source/W3DDevice/GameClient/Shadow/W3DProjectedShadow.cpp` (matching Zero Hour `W3DProjectedShadow.cpp`) as `int nShadowDecalStartBatchIndex = 0;`. It stores the starting index for drawing indexed primitives in a shadow decal batch. Retail `.data` places it at 0x01306E18 immediately following `nShadowDecalIndicesInBuf` (0x01306E14) and immediately preceding `nShadowDecalPolysInBatch` (0x01306E1C).

## Extent and all users

4 bytes at VA 0x01306E18.
