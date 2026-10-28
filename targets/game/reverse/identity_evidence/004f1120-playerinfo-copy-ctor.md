# 0x004F1120: PlayerInfo copy constructor (identity correction)

Old claim: `??0Open2Rec4F1120@@QAE@ABV0@@Z` (address-derived placeholder class in
`game/GameEngine/Source/Common/Open2Records.cpp`, bytes already verified).
New identity: `??0PlayerInfo@@QAE@ABV0@@Z`.

BFME 1 target evidence:

1. ILT oracle: `python3 tools/ilt_oracle.py check '??0PlayerInfo@@QAE@ABV0@@Z' 0x004F1120`
   reports CONFIRMED, exact, p_false 5.22e-04. The pinned ILT at this body's
   slot carried the candidate name; no other real candidate there fits.
2. Layout: the body copies three AsciiStrings at +0x00/+0x04/+0x08 and ten
   dwords at +0x0C..+0x30 (52 bytes). The matched `PlayerInfo::isIgnored`
   at 0x006318A0 (`game/GameEngine/Source/GameNetwork/GameSpy/PlayerInfoIsIgnored.cpp`)
   uses exactly this BFME PlayerInfo: three AsciiStrings, profile ID at +0x14,
   52 bytes in all (its comment notes the third AsciiString absent in Zero Hour).
3. Zero Hour's PeerDefs.h declares `PlayerInfo` with an implicit copy
   constructor that copies every member in declaration order, which is what
   this body does; PlayerInfoMap (`std::map<AsciiString, PlayerInfo>`) needs it.

Donor/inference split: the class name and member order come from Zero Hour
source; the BFME layout and the identity at this address come from the BFME 1
evidence above. Bytes are unchanged; only the class name (and two member names
backed by the matched isIgnored view) change.
