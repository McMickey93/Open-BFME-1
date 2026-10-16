# ILT 0x00048C61: Overridable::friend_getFinalOverride, the non-const twin

j_00048c61 jumps to 0x00097880, the matched 26-byte row
`?friend_getFinalOverride@Overridable@@QAEPAV1@XZ` (non-const). The const
twin `?friend_getFinalOverride@Overridable@@QBEPBV1@XZ` is the different
24-byte row at 0x000978A0.

`tools/ilt_oracle.py check` at 0x00048C61 (2026-10-16):
- `?friend_getFinalOverride@Overridable@@QAEPAV1@XZ`: CONFIRMED (exact,
  p_false 2.80e-03);
- `?friend_getFinalOverride@Overridable@@QBEPBV1@XZ`: CONTRADICTED.

A const pin at the thunk let two matched callers spell the call const:
LightPointSystem::rva0039CB60 and BFMEActionManager::rva000C6820. Removing
that pin fails exactly those two (and no other of the 25 objects that name
the const symbol). Zero Hour's Overridable.h declares friend_getFinalOverride
non-const; with the callers recursing through the non-const member both
bodies stay byte-identical and link_check drops their "not retail's body"
findings.
