# 0x001FF060: GettingBuiltBehavior member, meaning unproven

- Retail body 0x001FF060..0x001FF151 (242 B, `ret` then int3 padding).
- Only caller: GettingBuiltBehavior::update (0x001FF880, matched in
  GettingBuiltBehavior_update.cpp, vtable 0x010A4624 slot 0). It calls this body
  through ILT 0x00036449 on its own object (`ecx` = this) and sets the +0x30
  flag that this body tests and clears. The body sits between the
  GettingBuiltBehavior bodies 0x001FEC30 and ??_G 0x001FF190.
- The banked attempt's descriptive method name `killPendingCastleMember` was a
  guess: `python3 tools/ilt_oracle.py check
  '?killPendingCastleMember@GettingBuiltBehavior@@QAE_NXZ' 0x36449` reports
  CONTRADICTED (p_false 1.96e-04, outside every window of the ILT's slots).
- So the row keeps an address-derived method name,
  `?rva001FF060@GettingBuiltBehavior@@QAE_NXZ`, following the neighbouring
  `?rva001FEC30@GettingBuiltBehavior@@QAEXXZ`.
