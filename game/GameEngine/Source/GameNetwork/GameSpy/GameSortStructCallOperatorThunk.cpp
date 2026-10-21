// cl: /DNDEBUG /MD /EHsc
// The incremental-link thunk at 0x000317D7: `jmp 0x0053EDD0`, the body of
// GameSortStruct::operator() (LobbyUtilsGameSortStruct.cpp). The staging-room
// tree insert calls the comparator through it. Claimed by address, as the ILT
// convention says, jumping to the address pin for the body. Under /O2 a tail
// call with no arguments is exactly `E9 rel32`.

void b_0053edd0();

void j_000317d7() { b_0053edd0(); }
