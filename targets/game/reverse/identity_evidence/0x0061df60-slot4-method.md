# 0x0061DF60: address-derived method name

The bank `targets/game/reverse/attempts/0x0061df60.cpp` spelled this body
`Rva0061DF60::Update` with a `slot4` placeholder. Neither name is evidenced.

- `tools/vtable_lookup.py --target 0x0061DF60` places the body in slot 4 (+0x10)
  of vtable 0x01115C60 (installed by `??0BfmeNamedBG@@QAE@ABVAsciiStringBG@@@Z`,
  0x0060AAE0) and of the inheriting tables 0x01115E60 and 0x01115E90.
- `tools/callers_of.py 0x0061DF60` finds no named direct caller. No string or
  RTTI record names the slot.
- "Update" comes from the body's behaviour (it moves the holder by a scaled
  delta), not from evidence. So the landed source keeps the address:
  `?rva0061DF60@BfmeAnimationHolder@@UAEXXZ`, as the sibling
  `?rva0061D5A0@BfmeAnimationHolder@@QAEXM@Z` does.

The field names (m_mode, m_enabled, m_from, m_to, m_amount) are kept from the
bank. They describe how this body uses +0x44, +0x4C, +0x50, +0x5C and +0x68.
