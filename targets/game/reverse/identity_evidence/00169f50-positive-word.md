# Opaque positive-word query at 00169F50

Fresh carve build/sol3_r2_carved.csv proves a direct REL32 entry at
0x00169F50. MOV EDX,[ECX+1A0] / XOR EAX,EAX / TEST EDX,EDX / SETG AL / RET
occupies exactly 14 bytes; padding begins at +E. There are no callees or
incoming stack arguments. SETG after TEST witnesses a signed-positive
word test. The source views the fully defined EAX result as int 0 or 1;
no original scalar typedef or owner identity is claimed. name_oracle has
no layout witness for Rva00169F50. Its receiver and field retain addresses.

Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b supplies the
ordinary signed-word positivity expression in
Code/GameEngine/Source/Common/VtableSlotBodiesR3.cpp at 00251C08 (9 bytes),
Rva00251C08::rva00251C08. That donor returns bool from offset C. BFME1's
independent displacement 1A0 needs three more bytes; the full EAX result
needs XOR EAX,EAX (two more). Adapting those observed details gives all
14 bytes without compiler switches or helper functions. Donor identity
and offset are not transferred.

repair_queue.py dest selects TinyIndexedForwarders.cpp from the proven
00169F70 sibling 32 bytes away. All 102 source rows pass strict checks.
link_check before and after remains LINKED 0 -> 0 bytes with the same six
unresolved generic forwarder names. No pin, header, shim, assembly, or
hatch changes. Receipts are build/r2_*00169f50* in ds-9.
