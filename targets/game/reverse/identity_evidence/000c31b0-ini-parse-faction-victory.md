# 0x000C31B0 is iniParseFactionVictoryDefinition, not SidesList::removeSide

The 363-byte body at 0x000C31B0 (plain `ret`) was ledgered as
`?removeSide@SidesList@@QAEXH@Z` from a naked `__emit` lift. A thiscall method
with one int argument would end `ret 4`; this body is cdecl and reads its
`INI *` from the stack.

- INI block table 0x012A88AC binds the FactionVictoryData block to ILT
  0x00011FAE, which jumps to this body (symbols.csv pin).
- The body's own assert text, at VA 0x010839F8, reads "Could not find/create
  FactionVictoryParameters in iniParseFactionVictoryDefinition!".
- It calls `INI::getNextToken`, maps the block name "neutral" to the empty
  name, calls `VictorySystem::_bfme_findOrCreateFactionVictoryParameters` and
  `INI::initFromINI` with the FactionVictoryData field table at VA 0x0109FBC8:
  the shape of its matched sibling `iniParseVictorySystemDefinition`
  (0x000C3060).
- `tools/ilt_oracle.py check '?iniParseFactionVictoryDefinition@@YAXPAVINI@@@Z' 0x11fae`
  reports CONFIRMED (exact); `?removeSide@SidesList@@QAEXH@Z` is CONTRADICTED.
