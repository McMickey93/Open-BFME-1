# Task 2: AsciiString::compare

Queue rank 4, claim 0xFDAA8FED; two emitters cover seven map operator[] rows (1,205 source bytes). No source repair landed.

`callees.py 0x000C0D00 191` confirms the comparison reaches 0x0005FEB0 through ILT 0x000220C5. That address is the ledger alias of StringBase<char>::compare. Replacing both comparators with direct StringBase<char>::compare calls removes the AsciiString wrapper dependency but fails all seven byte checks: the waypoint body changes ESI/EDI allocation and the conditional branch displacement 0x6c -> 0x55; the other six show the same allocation/lifetime change. The experiment was reverted. The unchanged waypoint source passes 1/1.

BFME2 evidence: `/home/yannick/projects/Open-BFME-2/reference/shims/asciistring_downloadmanager/ascii_string.h` contains the same AsciiString wrapper plus inline memcmp implementation; it supplies context, not BFME1 byte proof.

Before `link_check.py game/GameEngine/Source/GameClient/Rva000C0D00WaypointMapIndex.cpp`: LINKED PREVIEW UNKNOWN, 0 -> 0 bytes. The Oct 19 census lacks 22,655 current ledger objects, so it cannot prove selected definitions. After reverting the source there is no claimed link improvement. A future repair must retain the current inlining-cost/register shape while suppressing the unwanted wrapper emitter.
