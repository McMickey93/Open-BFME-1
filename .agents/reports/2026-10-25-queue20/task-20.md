# Task 20: state-transition vector overflow — blocked

Queue rank 40, census e9a5ae5b4c. The dedicated provider is Common/TransitionInfoVectorInsertOverflowBody.cpp at BFME1 0x000A1DD0, 314 bytes. Competing emitters are Common/StateMachine.cpp and GameLogic/Object/Body/ActiveBodyParseDamageCreationList.cpp.

The BFME2 declaration-only technique (sibling f301d686c70c3e5fa0b51b342a2745f495b8a0b1, Code/Libraries/Source/WWVegas/WWLib/RvaHashResize00927DE0.cpp and e9d93338e0) does not transfer directly. State::TransitionInfo is private in the BFME1 StateMachine header. MSVC rejects both a specialization declaration and an extern-template declaration with C2248. Spelling arguments through vector::pointer and const_reference also fails access checking. No shared header was changed to work around it.

The independently tested damage-parser TU has a public local view, so its declaration compiles, but its existing 182-byte parser changes shape. The new call displacement extends to byte 183; this is a failed caller reconstruction, not evidence that the verified retail row should be enlarged. It is consistent with the empty-tag visibility changes reproduced in tasks 17–19.

All attempted changes were reverted. Original StateMachine, damage-parser and dedicated-provider units were rebuilt together. No source repair lands for task 20. The retained progress is a reproducible blocker record and the ruled-out declaration forms. Next work needs a supported native-helper reconciliation or a coherent header/caller change with the required full dependent gate. No conversion or aggregate linking gain is claimed.
