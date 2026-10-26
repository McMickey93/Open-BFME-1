# 0x0064CBD0 (628 B): the hinted insert_unique of map<string, int>, not three AsciiString maps

Found 2026-10-26 while landing a header: the full gate had been red on origin since
3ce339fbfa (2026-10-16) on the three rows at 0x0064CBD0 (INIMapCache.cpp x2, MapUtil.cpp),
and two re_attempts records (isEmpty canonical fix, InGameUI::postDraw) were refused by it.

Retail evidence (inputs/baselines/bfme1/retail-1.03-unpacked, read directly):
- The only call into 0x0064CBD0 goes through the ILT thunk 0x0003AFEE, from 0x0064E604 and
  0x0064E6F7, the map<string, int> code the ledger already attributes to the string/int map
  (symbols.csv pins the hinted basic_string/int insert_unique name at 0x0003AFEE).
- At +0xC8 the body calls the thunk 0x0001C01C -> 0x006455D0, a 21-byte comparator that calls
  the out-of-line basic_string<char> operator< at 0x006451D0 (functions.csv row,
  ??$?MDV?$char_traits@D...). less<AsciiString>::operator() is 0x00062FA0 (26 B, inlines
  operator< as compare + setl; pin 0x00043D42 -> 0x00062FA0 CONFIRMED by ilt_oracle,
  identity_evidence/pin-candidates-op1-batch4-oracle.md). A comparator calling
  basic_string's operator< is less<basic_string<char>>, so the tree is keyed by std::string.
- Retail was linked without identical-COMDAT folding: one body, one identity. Three
  AsciiString-keyed names at one address were an over-claim; the value types
  (Coord3D, MapMetaData, bool) never appear in the bytes, which is how three guesses all
  byte-matched.

Reconstruction: PingThread_mapInsertUnique.cpp already instantiates map<string, int> under
_BFME_RETAIL_TREE_INSERT_LAYOUT for the non-hinted insert_unique at 0x0064C4C0; an explicit
instantiation of the hinted overload there compiles to 628 bytes with 0 unmasked byte
differences against 0x0064CBD0, and every relocation resolves to retail's targets under
./build.sh. INIMapCache.cpp and MapUtil.cpp keep their map<AsciiString, ...> code (their
rows elsewhere still verify); only the three rows at 0x0064CBD0 move.

## 0x0064E5F0 (31 B): the map-level insert(hint, value) wrapper of the same map

Its one call, `e8 e5 c9 9e ff` at +0x14, is the ILT thunk 0x0003AFEE -> 0x0064CBD0 above, so it
is map<basic_string<char>, int>::insert(iterator, const value_type &), claimed twice under
AsciiString names (Coord3D and MapMetaData values) in INIMapCache.cpp. The explicit
instantiation in PingThread_mapInsertUnique.cpp compiles to 31 bytes with 0 unmasked byte
differences; the AsciiString rows had become unresolved once their insert_unique moved.
