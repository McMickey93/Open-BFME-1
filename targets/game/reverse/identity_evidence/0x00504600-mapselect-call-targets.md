# 0x00504600 WOLMapSelectMenuSystem: map-list call targets and the dropped view class

The bank `targets/game/reverse/attempts/0x00504600.cpp` (retail 0x00504600,
1372 bytes, `?WOLMapSelectMenuSystem@@YA?AW4WindowMsgHandledType@@PAVGameWindow@@III@Z`)
changed two names when its body was re-probed on 2026-10-21:

- `populateMapListbox` at the two menu-driven call sites became a local
  `populateMapListboxByRef` wrapper over the import stub `j_00029cee`
  (ILT 0x00029CEE -> 0x00457090). Retail's menu path passes a pointer to a
  caller-owned `AsciiString` temporary that the caller destroys after return,
  which is not the ZH by-value `populateMapListbox` API used by the init path at
  the same bank (that call site is unchanged). The matched sibling
  `game/GameEngine/Source/GameClient/GUI/GUICallbacks/Menus/WOLMapSelectInitialize00503FA0.cpp`
  already spells the same ILT contract.
- The `Rva00098E70GameInfoView` view class and its
  `#pragma comment(linker, "/alternatename:...getMap@GameInfo@@...")` bridge are
  gone; the body now calls `reinterpret_cast<GameInfo *>(TheGameSpyGame)->getMap()`
  directly, which is the spelling every matched sibling uses
  (`WOLMapSelectInitialize00503FA0.cpp:55`, `SkirmishScreenStateBfmeFlush11.cpp:16`,
  `PositionStartSpotsGameInfo.cpp:56`, `Rva004C8B40RefreshGameInfoWindow.cpp:95`).
  Those siblings all declare `AsciiString getMap() const;` with no `throw()`
  specification, so the bank's old `AsciiString getMap() const throw();` was an
  invention of the workaround class, not an established name. Removing the class
  is what drops the `throw` token; no other spelling of the call is accepted by
  the four retail vtable-slot bytes this pass fixed.
