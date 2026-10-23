# Task 20: call the canonical token parser

Queue rank 25, claim 0xF9620A8E. Changed both wide openFile tokenization calls to StringBase<char>::nextToken and removed the unused AsciiString declaration. This uses the independently verified bool __thiscall signature with two stack arguments printed by `callees.py 0x009CDF50 571`; retail calls the base implementation at 0x008880E0 twice. No pin or shared header changes.

`./build.sh` passes the complete 571-byte openFile row, with five string references. The compiled object references the canonical base symbol and no AsciiString nextToken symbol.

Before `link_check.py --census-only <file>`: wrong selected AsciiString nextToken definition. After the same check: source LINKS, 0 -> 570 bytes, with the nextToken selected-definition blocker gone. This is a changed-object preview against the Oct 19 census, not a fresh census.

BFME2 supporting source: `reference/shims/asciistring_downloadmanager/string_base.h` declares the base parser and `ascii_string.h` forwards the wrapper with casts to that same two-pointer API.
