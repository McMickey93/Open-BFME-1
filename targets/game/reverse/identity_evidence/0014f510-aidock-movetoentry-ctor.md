# 0x0014F510 is AIDockMoveToEntryState's constructor

- The 46-byte self-naming state constructor at `0x0014F510` (landed as the
  address-derived `??0Rva0014F510State@@QAE@PAX@Z`) stores vftable
  `0x01095CC0` after calling `AIInternalMoveToState(machine, "AIDockMoveToEntryState")`.
- `0x01095CC0`'s slots are the matched `?onEnter@AIDockMoveToEntryState`
  (0x0014EAE0), `?update@AIDockMoveToEntryState` (0x0014EBA0) and
  `?onExit@AIDockMoveToEntryState` (0x0014EBF0) in AIDock.cpp, and its
  deleting destructor is the matched `??_GAIDockMoveToEntryState@@UAEPAXI@Z`
  (0x0014F550). The constructor of the class owning that vftable is
  `AIDockMoveToEntryState::AIDockMoveToEntryState`.
- `tools/ilt_oracle.py check '??0AIDockMoveToEntryState@@QAE@PAVStateMachine@@@Z' 0x0014F510`
  is CONFIRMED (p_false 3.26e-04, exact); the old placeholder
  `??0Rva0014F510State@@QAE@PAX@Z` is CONTRADICTED.
- The Zero Hour signature is `AIDockMoveToEntryState( StateMachine *machine )`.
