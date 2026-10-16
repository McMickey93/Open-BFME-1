# AudioManager::m_allAudioEventInfo: the 0x006A AsciiString hash_map family

Approved by the project lead 2026-10-16 (follow-up to
006a78c0-ascii-hash-erase-not-buildablestatus.md).

AudioManager's find/add/newAudioEventInfo (0x006AEA10, 0x006AE910, 0x006AE710,
consecutive vtable slots in Zero Hour's GameAudio.h order) all work on the hash
map at AudioManager+0x70: Zero Hour's

    typedef std::hash_map<AsciiString, AudioEventInfo*, rts::hash<AsciiString>,
        rts::equal_to<AsciiString> > AudioEventInfoHash;

Every member of that table's STLport instantiation in this family was ledgered
under an address-tagged mapped type (Rva006A7AD0Mapped / Rva006A7AD0Value /
Rva006A7F80Value), a BuildableStatus spelling, or as a ?dup_ alias. The real
spelling is checked independently at each thunk the bodies are reached
through with tools/ilt_oracle.py. That test uses link.exe's external-symbol
hash order, so a wrong name fits by chance with p ~ 1e-3. All twelve are
CONFIRMED exact:

| body | size | thunk | member |
|---|---|---|---|
| 0x006AC440 | 142 | 0x00027E03 | hash_map::operator[] |
| 0x006A7F80 | 159 | 0x0000691A | hashtable::_M_find<AsciiString> |
| 0x006A7AD0 | 114 | 0x0003E6C1 | hashtable::_M_insert |
| 0x006A4E70 | 418 | 0x0001CBED | hashtable::resize |
| 0x006A7F00 | 65 | 0x0000BA69 | _Hashtable_iterator::_M_skip_to_next |
| 0x0069DEC0 | 5 | 0x00036291 | pair<const AsciiString, AudioEventInfo*>::~pair |
| 0x006A1060 | 41 | 0x0004004D | hashtable::_M_bkt_num_key(key, n) |
| 0x006A4D10 | 25 | 0x0000F137 | hashtable::_M_bkt_num_key(key) |
| 0x006A4D30 | 25 | 0x00020275 | hashtable::_M_bkt_num(value) |
| 0x006AAEF0 | 22 | 0x0000162C | _Ht_iterator<_Const_traits>::operator++ |
| 0x006AAED0 | 22 | 0x000314A8 | _Ht_iterator<_Nonconst_traits>::operator++ |
| 0x006A1550 | 79 | 0x0001910F | _Construct<pair> (was a tgrid_121 gen-tgrid row) |

The two operator++ bodies and the two 25-byte bucket helpers are byte-twins.
The oracle is what assigns each name to its address. The BuildableStatus,
struct-AudioEventInfo (`PAU`) and `_STL::equal_to` spellings are CONTRADICTED.
The genuine BuildableStatus hash_map is a separate family at 0x0038xxxx
(operator[] 0x00390660, pair destructor via ILT 0x0000FF10) and is untouched.

Bodies come from game/GameEngine/Source/Common/Audio/AudioEventInfoHash.cpp
(resize stays in RvaHashResizeAsciiString0045FDC0.cpp, whose inline-hash view it
needs). Each is byte-exact at the full extent. The operator[] unwind funclet
0x00C48210 follows its parent to the new TU.
