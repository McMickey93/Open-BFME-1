# Wrapper allocation failure cleanup at RVA 00C455C0

The byte-matched processWrapper body at 00676600 pushes handler 00C455CB.
That handler loads FuncInfo 00E34E98. Its sole unwind entry maps state 0
to -1 through action 00C455C0. The action loads the allocation from EBP+4,
calls global operator delete at 00881EB0, pops its argument and returns at
00C455CA. These instructions prove the complete 11-byte extent.

The native C++ new-expression in processWrapper emits the corresponding
single-state unwind map and action $L36765. Global new selects global
delete on constructor failure; the former placement expression instead
passed an extra enum argument to class placement delete. The separately
verified placement-delete definitions remain available out of line.

The full NetCommandWrapperList.cpp scoped gate verifies all 21 bodies,
including this action, the unchanged parent and both placement deletes.
The action keeps an address-derived identity; no original semantic name
is asserted. No assembly, new pin or verifier implementation is added.
