# textEntryGameDescriptionID storage at VA 0x012F3EFC

The existing decorated identity `?textEntryGameDescriptionID@@3W4NameKeyType@@A` owns one four-byte NameKeyType at RVA 0x00EF3EFC in the virtual zero-filled tail of retail .data. Its initial bytes are 00 00 00 00, which represent NAMEKEY_INVALID. This writable runtime key cell is not a compiler constant. The missing data row is provided by an EOF storage definition in PopupHostGameInit.cpp.

## Retail facts and contract

PopupHostGameInit body at RVA 0x004D68C0 constructs an AsciiString for "PopupHostGame.wnd:TextEntryGameDescription" and calls NameKeyGenerator::nameToKey. The enum cookie returned in EAX is stored at VA 0x012F3EFC. After temporary cleanup, the same key is loaded from VA 0x012F3EFC and passed to winGetWindowFromId.

Zero Hour GeneralsMD PopupHostGame.cpp declares static NameKeyType textEntryGameDescriptionID and uses the same widget string and parentPopup lookup. NameKeyGenerator.h defines NAMEKEY_INVALID as zero and forces 32-bit enum representation.

## Extent and all users

No retained pointer targets any of its interior bytes. Its own four bytes contain no HIGHLOW field or pointer initializer. The datum is 4 bytes at VA 0x012F3EFC.
