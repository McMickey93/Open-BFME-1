# 0x003A9F60 vector constructor

The 134-byte body keeps an address-derived identity. It is called through an ILT by the matched Rva003B6680 copy constructor at 0x003ABC80 for the member at +0xA8. No native class name is claimed. The complete body returns the receiver with ret 4; its final padding is included in the established 134-byte extent.

Donor: Open BFME 2 snapshot 743ac9f66572523eaacb3abc7e2cb0430e35832b, Code/Libraries/Source/WWVegas/WWLib/StlportCapturedBoneVectorCopy.cpp, constructor at 0x00166110. Its explicit embedded-coordinate copy and source-first loop increment transfer to BFME1's different 32-byte element. The prior trivial Coord3D copy emitted 122 bytes. Explicit memberwise copying of the canonical Coord3D-derived view retains source and destination cursors at coordinate Z (+0x10), reproducing all 134 bytes with three relocation slots.

The payload is independently witnessed by the complete 0x003A84E0 constructor and 0x003B3560 copy sibling: vtable 0x010EC764; integer +4; canonical Coord3D +8; float +0x14; integer +0x18; bool +0x1C. The 003b3560-nested-payload-copy.md evidence records the field table and complete parser/destructor checks. The disputed ApplyRandomForceNugget vtable spelling is not adopted. The pre-existing R2Data010EC764 data symbol is reused; no pin or vtable identity is added.

Both direct calls were checked before writing. ILT 0x0000E47B routes to 0x003A6710, whose complete seven bytes load the sole stack word into EAX and return with ret 4. This is the empty allocator's hidden result-buffer ABI; the generated m(int) declaration is retained via a typed member-function-pointer view. ILT 0x00027750 routes to the existing 0x003A7BF0 _Vector_base specialization (count and allocator-reference stack words). Its declaration is reused without emitting a competing allocation implementation. The constructor's count is source byte extent divided by 32.

Validation: exact scratch probe; production scoped gate 2/2 including unchanged 490-byte caller; ordinary relocation/string/constant/body guards; LINKED 0 before and 0 after because of existing caller/provider blockers. No header, shim, pin or generated source was edited.
