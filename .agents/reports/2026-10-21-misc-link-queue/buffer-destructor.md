# Queue 58: forceinline does not remove the duplicate Buffer destructor

The census identifies a strong retail destructor in `buff.cpp` plus wrong
COMDAT copies in `ini.cpp` and `INIClassGetWideString.cpp`. Retail destructor
RVA `0x009E1E30` is 40 bytes; Reset at `0x009E1E60` is a separate identical
40-byte body. They are separate retail identities, not ICF aliases.

Two reversible TU-local experiments used the header's existing
`BFME_BUFFER_DTOR_OUT_OF_LINE` switch without changing a shared header:

1. Declaration only: six of 208 claimed bodies fail. Calls that must target
   Reset instead target the destructor, including BufferPipe and BufferStraw.
2. Declaration plus `__forceinline Buffer::~Buffer() { Reset(); }`: caller
   bytes recover. Eighteen unwind labels shift; sanctioned
   `eh_state_pins.py --source ini.cpp --fix` proves and repins their retail
   unwind-state identities. The complete scoped gate then passes 208/208;
   a separate EH audit proves all eighteen labels.

However direct COFF symbol inspection still finds defined destructor symbols
in both objects. The current `link_check.py` confirms the duplicate,
non-retail COMDAT and wrong-selected destructor remain. Its wider verdict
also lists unrelated unresolved CRT imports, Get_String duplication and
21,680 unavailable census objects; it cannot certify a whole link.

Both source changes and dependent unwind-pin changes were reverted. The
experiment establishes that a forceinline annotation is insufficient even
when all claimed caller bytes match. A solution must suppress or correctly
identify the emitted destructor copies while retaining caller Reset routes.
