# Task 5: hash resize used by 0x00469D20

Queue rank 13, census e9a5ae5b4c. The frozen census records a wrong resize COMDAT in RvaHashInsertAsciiString.cpp competing with `game/Libraries/Source/WWVegas/WWLib/RvaHashResizeAsciiString004691A0.cpp`. The insertion unit only declares rts::hash<AsciiString>::operator() while the dedicated provider inlines the string hash. Declare the resize specialization without defining it in the insertion unit; retain the existing retail provider, its types, ABI and flags.

BFME2 evidence: sibling ../Open-BFME-2 revision f301d686c70c3e5fa0b51b342a2745f495b8a0b1; Code/Libraries/Source/WWVegas/WWLib/RvaHashResize00927DE0.cpp and commit e9d93338e0 demonstrate declaration-only suppression of losing STL members. This transfers a supported linking repair technique, not BFME2 identities or addresses. The BFME1 provider and matched insertion caller establish this specialization's target independently.

Verification: all 23 insertion rows and the dedicated provider pass scoped byte/relocation checks. Current insertion COFF has an undefined external reference for this resize, with no competing definition. Before: census-selected wrong copy. After: emitter removed and provider verified; global link preview unknown while census inputs are stale. No new function conversion or aggregate linked-byte gain is claimed.
