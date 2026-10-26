# textEntryLadderPassword storage at VA 0x012F3F2C

The existing decorated identity `?textEntryLadderPassword@@3PAVGameWindow@@A` owns one four-byte GameWindow pointer at RVA 0x00EF3F2C in the virtual zero-filled tail of retail .data. Its initial bytes are 00 00 00 00, which represent a NULL pointer. This writable runtime window pointer cell is not a compiler constant. The missing data row is provided by a storage definition in PopupHostGameInit.cpp.

## Retail facts and contract

PopupHostGameInit body at RVA 0x004D68C0 looks up the window pointer via `TheWindowManager->winGetWindowFromId(parentPopup, textEntryLadderPasswordID)` and stores the result at VA 0x012F3F2C. It then passes the pointer to `GadgetTextEntrySetText`.

Zero Hour GeneralsMD PopupHostGame.cpp declares static GameWindow *textEntryLadderPassword and performs the same initialization.

## Extent and all users

No retained pointer targets any of its interior bytes. Its own four bytes contain no HIGHLOW field or pointer initializer. The datum is 4 bytes at VA 0x012F3F2C.
