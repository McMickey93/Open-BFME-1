# buttonCancel pointer cell at VA 0x012F3F24

The unowned interval [0x012F3F24, 0x012F3F28) is one writable four-byte GameWindow pointer cell, initially null. It is in the virtual zero-filled tail of retail .data.

Retail initialization at VA 0x008D68C0 constructs the string "PopupHostGame.wnd:ButtonCancel", calls nameToKey, and stores the result in buttonCancelID. It passes that key and parentPopup to TheWindowManager::winGetWindowFromId and stores the returned GameWindow pointer in VA 0x012F3F24.

Zero Hour PopupHostGame.cpp declares static GameWindow *buttonCancel = NULL and performs the identical lookup. The datum is 4 bytes at VA 0x012F3F24.
