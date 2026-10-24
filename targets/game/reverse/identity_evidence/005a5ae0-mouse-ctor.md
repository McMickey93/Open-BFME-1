# 0x005A5AE0 is Mouse::Mouse (`??0Mouse@@QAE@XZ`)

The row was `?dup_005a5ae0@@YAXXZ` (774 B `__emit` lift) after
`006f5a90-w3d-new-display-string.md` retired the newDisplayString name here.

## Evidence

1. Vtable. The body stores VA 0x0110D580 into `[this]`. Slot 0 of that table
   reaches `??_GMouse@@UAEPAXI@Z` (0x005A5EB0), slot 1 `?init@Mouse@@UAEXXZ`
   (0x005A4A40), slot 5 `?update@Mouse@@UAEXXZ` (0x005A44E0), all matched.
   Slots 2 and 3 are SubsystemInterface's, and the body calls
   `SubsystemInterface::SubsystemInterface` first, as Zero Hour's
   `Mouse::Mouse()` does.
2. Callers. Both matched Mouse-derived constructors call it as their base
   constructor through ILT 0x0004A8BD, which jumps to 0x005A5AE0:
   `??0DirectInputMouse@@QAE@XZ` (0x006BB7F0) and the ctor at 0x006BC010.
   Each then stores fields from +0x4E14, so sizeof(Mouse) is 0x4E14.
   `symbols.csv` already pins `??0Mouse@@QAE@XZ` at 0x0004A8BD.
3. Bytes. Zero Hour's `Mouse::Mouse()` source, extended with BFME's new
   members, compiles to retail's 774 bytes exactly (tools/probe.py EXACT).

`tools/ilt_oracle.py check` reports CONTRADICTED, p=5.9e-4, from ILT slot
ordering alone. That statistical check is weaker than the vtable and the two
direct base-constructor calls above.
