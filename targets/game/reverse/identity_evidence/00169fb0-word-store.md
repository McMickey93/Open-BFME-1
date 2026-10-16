# Opaque word store at 00169FB0

Fresh carve build/sol3_r2_carved.csv proves the direct REL32 target at
0x00169FB0. Its complete 13-byte body loads the dword at [ESP+4] into EAX,
stores it at [ECX+3A4], and ends with RET 4 at +A..+C. INT3 padding starts
at +D. There is no outgoing call or other side effect. The source uses an
unsigned-word view without claiming an original enum or pointer identity.
name_oracle has no witness for Rva00169FB0; the owner and field stay opaque.

Open BFME 2 revision 743ac9f66572523eaacb3abc7e2cb0430e35832b supplies the
ordinary member assignment at 0041FDEE (10 bytes) in
Code/GameEngine/Source/Common/Audio/AudioEventInfoPriority.cpp. BFME1's
larger independently observed offset 3A4 requires a disp32 store and accounts
for the additional three bytes. Neither AudioEventInfo nor AudioPriority
identity is transferred. The native source_donors lookup also serves matching
13-byte word-assignment bodies, independently of semantic identity.

repair_queue.py dest selects TinyIndexedForwarders.cpp between the proven
00169F70 and 00169FF0 entries. All 101 source rows pass strict byte checks.
link_check stays LINKED 0 -> 0 bytes with the same six pre-existing generic
forwarder providers unresolved. No pin, header, shim, assembly, or hatch is
changed. Receipts are build/r2_*00169fb0* in ds-9.
