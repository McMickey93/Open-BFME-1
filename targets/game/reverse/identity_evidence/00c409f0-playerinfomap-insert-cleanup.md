# 0x00C409F0: cleanup funclet of the PlayerInfoMap `_M_insert` (0x00633C70)

Retail 0x00C409F0 (8 B) is `mov ecx,[ebp+0xC]; jmp ~AsciiString`. Its row
`?a_00c409f0@@YAXXZ` claimed it as a "C++ alias" of `$L3421`, the funclet
that `GetStringFromRegistry` (0x00109640) owns at 0x00BFD098. Retail was
linked without COMDAT folding and cleanup funclets are not COMDATs, so the
bytes being identical does not give them a shared identity. The alias also
fails the body guard's tail check, because retail 0x00C409F8 is not
`$L3423`.

Unwind evidence:

- FuncInfo 0x01230598 (magic 0x19930520, 3 states) has 0x00C409F0 as the
  action of state 0 and 0x00C409F8 as the action of state 2.
- Its handler stub belongs to the matched
  `_Rb_tree<AsciiString, pair<const AsciiString, PlayerInfo>, ...>::_M_insert`
  at 0x00633C70, in
  `game/GameEngine/Source/GameNetwork/GameSpy/PeerDefs_PlayerInfoMap_M_insert.cpp`.
- The sibling funclets 0x00C409F8 (`$L1212`) and 0x00C40A09 (`$L1149`) are
  already claimed from that same TU.

In the object compiled from that TU, `.xdata$x` unwind state 0 relocates to
`$L1104`. The row is re-homed as `?Rva00C409F0Cleanup@@YAXXZ` with
`object-symbol=$L1104`, `parent=` set to that `_M_insert`.
