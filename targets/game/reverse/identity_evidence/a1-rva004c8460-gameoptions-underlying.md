# 0x004C8460: dup_004c8460 inline asm -> EstablishConnectionsWindow.cpp static

Zero Hour EstablishConnectionsWindow.cpp defines, in order,
`static void showGameSpyGameOptionsUnderlyingGUIElements( Bool show )` and
`static void showGameSpyQMUnderlyingGUIElements( Bool show )`, each one call of
ShowUnderlyingGUIElements( show, layout, parent, gadgets, perPlayerGadgets ).
Retail 0x004C8490 is already matched as the QM helper in the BFME
EstablishConnectionsWindow.cpp; 0x004C8460 (33 B) immediately precedes it with
the identical shape (show in EDX, two loaded string pointers 0x012B6A34/38 and
two arrays 0x012B6A3C/68, cdecl call through ILT 0x00047D52, add esp 14h), and
the TU's existing GameOptions statics (layoutFilename, parentName,
gadgetsToHide, perPlayerGadgetsToHide) compile to exactly those bytes.

The prior row `?dup_004c8460@@YAXXZ` (Rva004C8460.cpp) reproduced the bytes
with an `__asm` block reading EDX implicitly. ZH also defines a second static of
the same name in WOLMapSelectMenu.cpp, already matched at 0x00503E80 under the
plain decoration, so this copy takes the address twin namespace
`Rva004C8460Twin` (the ScriptActions findCave 0x002EFDE0 precedent). probe.py:
EXACT, 5 relocations.
