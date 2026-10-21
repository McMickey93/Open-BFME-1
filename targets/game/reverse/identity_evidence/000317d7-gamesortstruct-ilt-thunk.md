# ILT thunk 0x000317D7 is not the GameSortStruct::operator() body

The 5-byte row at 0x000317D7 was named `??RGameSortStruct@@QBE_NPAVGameSpyStagingRoom@@0@Z`
and forwarded, through a TU-local `GameSortStructCallOperatorShim::compare` pin, to 0x0053EDD0.
Retail at 0x000317D7 is one instruction:

    +0000 e9 f4 d5 50 00    jmp 0x0053EDD0

(`python3 tools/dis_retail.py 0x000317D7 5`). It lies in the incremental-link table and has no
body of its own. The body is 0x0053EDD0 (864 B including its 8-entry jump table), now matched
from clean C++ under the real name in
`game/GameEngine/Source/GameNetwork/GameSpy/LobbyUtilsGameSortStruct.cpp`:

- the staging-room `_Rb_tree<..., GameSortStruct, ...>` insert calls it through this thunk at
  0x0053F80B on its comparator subobject (this+8), the existing `??RGameSortStruct` route pin;
- the body is Zero Hour's `GameSortStruct::operator()` from LobbyUtils.cpp: CRC mismatches
  (`exeCRC` at +0x430 against the obfuscated GlobalData exe CRC, `iniCRC` at +0x434) sort last,
  then full rooms (`getNumNonObserverPlayers()` / `getNumPlayers() == MAX_SLOTS (8)`), then the
  configured sort columns, with `_wcsicmp` of the two game names.

The thunk keeps its bytes as the address-claimed ILT thunk `?j_000317d7@@YAXXZ`, jumping to the
address pin `?b_0053edd0@@YAXXZ` (0x0053EDD0), which replaces the retired shim pin, and the real
name moves to the body under the non-const decoration
`??RGameSortStruct@@QAE_NPAVGameSpyStagingRoom@@0@Z`: `python3 tools/ilt_oracle.py check` reports it
CONFIRMED exact for 0x0053EDD0 and contradicts the `QBE` (const) spelling the old row used.
