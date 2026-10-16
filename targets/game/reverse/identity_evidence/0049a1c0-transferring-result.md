# 0x0049A1C0 transferring owning clone result

The established complete body is 99 bytes: RET 4 at +0x60 and INT3 at +0x63. The receiver is the already matched Gen_0049A070 copy-constructor class in BfmeWideCopyVY.cpp; no new native class or method identity is asserted. Its 12-byte layout and original m_bfmeVtable/m_bfmeText/m_bfmeValue spellings are retained.

The body allocates twelve bytes through operator new at 0x00881F30 and calls ILT 0x00041303, whose five-byte jump targets the matched 87-byte Gen_0049A070 copy constructor. The two inputs to that constructor are its ECX destination and one const source reference. Its complete retail body independently establishes the copied wide-string member and value; the clone introduces no new binding or pin.

Handler 0x00C27994 refers to FuncInfo 0x00E17E04. State 0 cleans the hidden return result through action 0x00C2797B, guarded by bit 0 at EBP-0x14; its tail routes through ILT 0x000224D0 to the 13-byte 0x00499F30 body. That body reads the handle's pointer and deletes a non-null pointee through vslot 0 with scalar-delete flag one. State 1's action 0x00C27970 deletes the raw new allocation if the copy constructor throws. These independently prove both owning lifetimes.

The local matched donor 0x004C1AE0 and its newly recovered two-word relative 0x004B2470 use a non-const transferring handle copy constructor and inline virtual deletion. Applying that same real ownership contract to the existing bank removes its redundant local copy/destructor and reproduces all 99 bytes with six aligned relocations. Merely changing expression syntax on its shallow-copy/external-destructor handle had emitted 119 or 125 bytes. The canonical named result still reads `temp(new Gen_0049A070(*this)); return temp;`.

The virtual pointee view only represents the independently decoded destructor slot at offset zero, without inventing an owner for that slot. No new pin, alias, header, shim, assembly or intrinsic is introduced. The clone is defined before the existing constructor so that this TU retains the independently proven out-of-line copy call while preserving the old constructor body.
