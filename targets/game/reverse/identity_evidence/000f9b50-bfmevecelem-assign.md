# 0x000F9B50 is BfmeVecElem_000FAFF0::operator=

BFME 1 retail evidence only; both names are address-derived placeholders.

* The vector erase overloads matched as
  `?erase@?$vector@UBfmeVecElem_000FAFF0@@...` at 0x000FAF90 (76 B) and
  0x000FA9A0 (59 B) call the shift helper through ILT 0x00046A6F, which
  jumps to 0x000FA0E0. That helper walks 0x60-byte elements and assigns
  each one with `call 0x0041802F` (ILT 0x0001802F), which jumps to
  0x000F9B50. The same erase bodies destroy the freed tail through
  ILT 0x0002C3BD -> 0x000D1690, matched as `??1BfmeVecElem_000FAFF0@@QAE@XZ`.
* So 0x000F9B50 is the assignment operator of the class whose destructor
  is 0x000D1690. It was matched as `??4Rva000F9B50@@QAEAAV0@ABV0@@Z`, a
  second placeholder for the same class, which left
  `??4BfmeVecElem_000FAFF0@@QAEAAU0@ABU0@@Z` (called by the erase TU's
  `__copy` instantiation) unresolved in the link census.
* The rename keeps the body, layout and bytes; it only gives the class the
  struct-keyed spelling its destructor and erase rows already use. No
  matched caller names the old spelling (`rg Rva000F9B50 game/`).
* ilt_oracle contradicts the placeholder at ILT slot 0x0001802F, as it
  does any address-derived name; the original class name stays unknown.
