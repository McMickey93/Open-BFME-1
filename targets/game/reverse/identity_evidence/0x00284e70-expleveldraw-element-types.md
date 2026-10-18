# 0x00284E70 BannerCarrierUpdateModuleData::parseExpLevelDraw element types

- Body: retail 0x00284E70, 443 B, the `ExpLevelDraw` FieldParse callback (row VA
  0x010BBD88, store offset 0x24). `ilt_oracle.py check` CONFIRMS (exact)
  `?parseExpLevelDraw@BannerCarrierUpdateModuleData@@SAXPAVINI@@PAX1PBX@Z` at
  its ILT 0x00049D50.
- Store vector: the out-of-line push_back behind ILT 0x0004B2C2 -> 0x00284A60.
  `ilt_oracle.py check` CONFIRMS (exact)
  `vector<BannerCarrierUpdateModuleData::ExpLevelDraw *>::push_back`
  (60 candidate spellings tried; expected false hits about 0.03).
- Sub-object vector: the inline push_back calls `_M_insert_overflow` through
  ILT 0x0003918A -> 0x00284100, a pointer-vector `__true_type` body (byte-equal
  to the matched `vector<Rva002D8C10Record *>` overflow 0x002D8820 except its
  four call operands). The bank's element names are refuted there:
  `ilt_oracle.py check` returns CONTRADICTED for
  `vector<BannerCarrierSubObject *>` and `vector<BannerCarrierString *>`, as
  struct and as class. No oracle-consistent name was found, so the element
  type is `Rva00284E70SubObject` (address-derived).
