# Disconnect-command allocation cleanup at RVA 00C447D0

The byte-matched sendDisconnectCommand body at 0066B9F0 pushes handler
00C447DB. That handler names FuncInfo 00E340DC. Its single unwind entry
maps state 0 to -1 through 00C447D0, proving ownership independently of
adjacency. The action loads the allocation at EBP+4 and calls the established
global operator delete at 00881EB0. POP ECX and RET at 00C447D9/DA prove
the complete 11-byte extent.

The native C++ global new-expression emits the corresponding single-state
map with action $L50505. The previous placement expression emitted an extra
enum argument and class placement delete, which the parent body alone could
not distinguish. Explicit global allocation corrects the failure path while
preserving every byte of the parent. The five existing placement-delete
providers remain as ordinary out-of-line definitions in the same file.

All 40 bodies in DisconnectManager.cpp pass the scoped gate, including
the new action, its parent, the five placement deletes and the two other
recorded unwind actions. eh_state_pins.py proves the new action's binding;
it leaves the two older unanchored rows unchanged. The scoped byte gate
recovers those existing rows at their renumbered labels and verifies them.
The cleanup retains an address-derived name; no assembly or new pin is used.
