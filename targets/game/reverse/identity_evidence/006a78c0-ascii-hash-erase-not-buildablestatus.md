# 0x006A78C0 is not hash_map<AsciiString, BuildableStatus>: ILT 0x00036291 and the 0x6A hashtable family

Investigation requested by the project lead 2026-10-16 (commit 829632cac6 follow-up).

## What ILT 0x00036291 jumps to

Retail 0x00036291 is `E9 -> 0x0069DEC0`. 0x0069DEC0 is a 5-byte body,
`jmp 0x00887940` (StringBase<char> buffer release, the AsciiString
destructor's body), followed by INT3 padding. That is
`pair<const AsciiString, M>::~pair()` for a 4-byte M with a trivial
destructor: only the key is destroyed. The ledger already holds this body as
`?dup_0069DEC0@@YAXXZ` with object-symbol
`??1?$pair@$$CBVAsciiString@@W4Rva006A7AD0Mapped@@@_STL@@QAE@XZ`
(RvaHashIndexAsciiString.cpp).

`pair<const AsciiString, BuildableStatus>::~pair` is a different body.
`ilt_oracle` confirms it at ILT 0x0000FF10 -> 0x003872F0, reached from the
unwind funclet 0x00C1C0F0 of the matched
`hash_map<AsciiString,BuildableStatus>::operator[]` (0x00390660). The real
BuildableStatus family sits at 0x0038xxxx-0x0039xxxx (operator[] 0x00390660,
_M_find 0x0038BE40, _M_insert 0x0038ED80). Retail was linked without
identical-COMDAT folding, so one name cannot have both bodies: the
BuildableStatus pin at 0x00036291 is wrong.

## Which table the caller erases from

0x006A78C0 (hashtable::erase(const key&), 316 bytes) has one caller, 0x006AC0F0.
That function sits in the AudioManager vtable at VA 0x0111C1DC, the slot right
after newAudioEventInfo (0x006AE710), addAudioEventInfo (0x006AE910) and
findAudioEventInfo (0x006AEA10). Like them, it takes the manager mutex at
this+0x95C and works on the hash map at this+0x70. It erases the AsciiString
at +8 of its argument, clears the byte at +0x630 and releases the mutex.
addAudioEventInfo inserts into this+0x70 through ILT 0x00027E03 ->
0x006AC440 (operator[]), and findAudioEventInfo looks it up through ILT
0x0000691A -> 0x006A7F80 (_M_find). In Zero Hour (GameAudio.h) that member is
`AudioEventInfoHash m_allAudioEventInfo`, i.e.
`hash_map<AsciiString, AudioEventInfo*, rts::hash<AsciiString>, rts::equal_to<AsciiString>>`.
The matched AudioManagerAddAudioEventInfo.cpp already declares it that way.
So 0x006AC0F0 is very likely BFME's AudioManager::removeAudioEventInfo, and
0x006A78C0 erases from the AudioEventInfo table. The same family's bucket
helper 0x006A1060 (ILT 0x0004004D) is shared by this erase, by _M_insert
0x006A7AD0 and by _M_skip_to_next 0x006A7F00.

## The incremental-link thunk table settles the spelling

tools/ilt_oracle.py tests a decorated name against the window of the thunk
slot it is called through. The window comes from link.exe's external-symbol
hash order; a wrong name fits by chance with p ~ 1e-3.

| thunk | name | verdict |
|---|---|---|
| 0x00036291 | `??1?$pair@$$CBVAsciiString@@PAVAudioEventInfo@@@_STL@@QAE@XZ` | CONFIRMED exact |
| 0x00036291 | the same with `PAUAudioEventInfo` (struct) | CONTRADICTED |
| 0x00036291 | `...W4BuildableStatus...` | CONTRADICTED |
| 0x00047D1B | `?erase@?$hashtable@U?$pair@$$CBVAsciiString@@PAVAudioEventInfo@@...U?$equal_to@VAsciiString@@@5@...QAEIABVAsciiString@@@Z` (rts::equal_to) | CONFIRMED |
| 0x00047D1B | the same with `_STL::equal_to` (`@2@`) | CONTRADICTED |
| 0x0004004D | `?_M_bkt_num_key@...PAVAudioEventInfo...rts::equal_to...ABEIABVAsciiString@@I@Z` | CONFIRMED |
| 0x0004004D | the BuildableStatus spelling | CONTRADICTED |
| 0x0000FF10 | `??1?$pair@$$CBVAsciiString@@W4BuildableStatus@@@_STL@@QAE@XZ` | CONFIRMED exact (kept) |

Three independent thunks agree. The table is Zero Hour's
`AudioEventInfoHash = hash_map<AsciiString, AudioEventInfo*,
rts::hash<AsciiString>, rts::equal_to<AsciiString>>` with AudioEventInfo
declared as a class. No ledger row or pin carries any of the `PAV` names. The
ledger's existing `PAUAudioEventInfo` (struct) family at
0x000B8670/0x000B87C0/0x000D0AE0/0x007A5180 is a different spelling, so
nothing collides.

## Changes

- 0x006A78C0 row: `?erase@?$hashtable@U?$pair@$$CBVAsciiString@@W4BuildableStatus@@...`
  -> `?erase@?$hashtable@U?$pair@$$CBVAsciiString@@PAVAudioEventInfo@@...rts::equal_to...`.
  The source is renamed Rva006A78C0AsciiHashErase.cpp.
- Both `/alternatename` hatches in that TU are removed. Its pair destructor and
  bucket helper are now named for what they are, and the byte gate resolves
  them through new identity pins at ILT 0x00036291 and 0x0004004D (both
  ilt_oracle CONFIRMED).
- The contradicted BuildableStatus pair-destructor pin at 0x00036291 is
  retired. The confirmed 0x0000FF10 pin and the native funclet stay.
- Follow-up (not in this commit): the rest of this family still carries
  address-tagged or BuildableStatus spellings: operator[] 0x006AC440, _M_insert
  0x006A7AD0, _M_find 0x006A7F80, resize 0x006A4E70, pair-dtor row
  0x0069DEC0, _M_skip_to_next 0x006A7F00 and the BuildableStatus
  _M_bkt_num_key pins at 0x0004004D. Each can now be re-spelled and checked
  with the same oracle.
