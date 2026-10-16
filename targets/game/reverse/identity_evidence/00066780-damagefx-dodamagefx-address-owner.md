# 0x00066780 keeps its address owner: Rva00066780DamageFX::doDamageFX

- Retail ILT 0x0001F65E (slot 24901) jumps to 0x00066780. `tools/ilt_oracle.py check`
  CONTRADICTS the old row's name `?doDamageFX@DamageFX@@QBE_NW4DamageType@@MPBVObject@@1@Z`
  (p_false 7.18e-04, outside every window of slots 16155-16165), and the same for its
  QAE/void-return/non-const-Object variants. The name was listed in
  `ilt_contradicted_baseline.txt`; this commit removes that line.
- The body's behaviour (major/minor FXList by damage amount, 0x40-byte per-type stride,
  returns whether an effect exists) is Zero Hour's DamageFX::doDamageFX shape, so the class
  keeps the address: `Rva00066780DamageFX`, the spelling the matched caller
  `Rva0020F240Body::doDamageFX` (0x0020F240+0x4E, via ILT 0x0001F65E) already declares and the
  symbols.csv pin at 0x0001F65E already records.
- Before this change nothing defined that spelling, so link queue #197 reported it unresolved
  (185 B of the caller blocked). The body source is unchanged apart from the class name.
