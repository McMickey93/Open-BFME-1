# Task 17: Module nugget copy

Queue rank 31, census e9a5ae5b4c. Rva0013C1D0NuggetVectorBodies.cpp emitted the wrong _STL::__copy worker because its Nugget was represented as twenty opaque bytes.

Repair: include the existing ascii_string.h and adopt the exact Nugget layout already byte-proven in BFME1 ModuleInfoClearModuleDataWithTag.cpp: two AsciiStrings, a pointer, int and two bools, twenty bytes total. This retains the caller's normal STL implementation and produces the nontrivial string assignments required by retail. No new names, addresses or symbol pins are introduced.

BFME2 evidence at sibling revision f301d686c70c3e5fa0b51b342a2745f495b8a0b1: Code/GameEngine/Source/Common/Thing/ModuleInfoNuggetAssign.cpp and ModuleInfoNuggetCopyPtrs.cpp corroborate the two string fields and assignment semantics. BFME2 has different helper ABIs and some views add a third flag; neither was imported. Local includes resolve through game/Libraries/Source/WWVegas/WWLib, and existing BFME1 flags remain intact.

Verification: edited source passes 3/3 rows; ModuleInfoClearModuleDataWithTag.cpp and ThingTemplateInitForLTA.cpp pass 2/2 rows together. compile_function verifies the emitted queue-named copy helper at BFME1 RVA 0x0013EA50 for all 105 bytes with no unresolved relocations. Callees confirms two calls to StringBase<char>::set. Existing erase at 0x00142350 retains all 76 bytes. Current global linking remains unknown; no aggregate gain or new conversion is claimed.

Ruled out: early specialization and extern-template declarations preserve helper calls but shift the erase empty-tag address from esp+0x18 to esp+0x1c. A late specialization is rejected by MSVC C2908; late extern-template retains the same one-byte mismatch. All these unsuccessful changes were reverted. The actual type-layout repair passes without suppression or a rewritten erase body.
