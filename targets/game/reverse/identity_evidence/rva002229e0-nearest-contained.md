# 0x002229E0: nearest contained object, owner unproven

- Retail body 0x002229E0..0x0022244F (112 B, `ret 4`, int3 padding), reached
  only through ILT 0x0000CCA2 from eleven contain vtables (for example slot 56 of
  `??_7CaveContain@@6BCaveContainIface3@@@` and
  `??_7GarrisonContain@@6B?$OpenContainSecondaryBase@$01@@@`).
- It walks the object list at this+0x18 (node+8 = Object*), the same list the
  matched `Rva222970FilteredDispatch::findAndDispatch` (0x00222970) walks, and
  returns the object nearest a point in 2D.
- The 0.07 bank (targets/game/reverse/attempts/0x002229e0.cpp) used one-letter
  stand-ins: class `C`, node struct `N` and a `gap` pad. None is a retail name;
  they become the address-derived `Rva002229E0Contain`, `Rva002229E0Node` and
  the project's `m_unmodelled_04` padding. The method keeps the bank's `nearest`.
