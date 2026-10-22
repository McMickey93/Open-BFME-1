# 0x006D8C10 W3DBridge::load name-pairing check

The exact conversion moves `W3DBridge::load` from the naked lift in
`W3DBridgeBuffer.cpp` to `W3DBridgeLoad.cpp`. The bank's descriptive
`TerrainRoadType` and `getTexture` declarations remain present in the new
source, including all four damage-state lookups.

The name checker pairs the deleted bank with the unrelated `BfmeC998` and
`bfmeGo998C` mesh-normal helper that remains in `W3DBridgeBuffer.cpp`. Those
tokens are a positional false pairing: they describe another function in the
same host TU and were neither renamed nor removed by this conversion.

Exact checker snapshots:

- bank before: `2a776a9aea96441b2bd908c61f0d58150670fe63089ef44f51df3baade4c92c9`
- buffer after: `b985913a139eb9ab049d566d10b62b565db2c30dce1fc6f81885ce4e7c2ad5ad`

The target body is 2836/2836 bytes exact with 66 relocations and preserves the
retail x87 grouping `(Y + Z), then X, then translation` in its first product.
