# Task 16: Subtitle map resize

Queue rank 7 at census e9a5ae5b4c. The census records competing non-retail COMDAT copies for `?resize@?$hashtable@U?$pair@$$CBVAsciiString@@VUnicodeString@@@_STL@@VAsciiString@@U?$hash@VAsciiString@@@rts@@U?$_Select1st@U?$pair@$$CBVAsciiString@@VUnicodeString@@@_STL@@@2@U?$equal_to@VAsciiString@@@5@V?$allocator@U?$pair@$$CBVAsciiString@@VUnicodeString@@@_STL@@@2@@_STL@@QAEXI@Z`. Suppress the competing emitter(s) with declaration-only specializations, retaining calls to the separately verified BFME1 provider(s).

Changed sources: game/GameEngineDevice/Source/MilesAudioDevice/MilesAudioManagerRva006AF840.cpp.
Providers verified: game/Libraries/Source/WWVegas/WWLib/HashtableAsciiUnicodeResize006A7B60.cpp.

BFME2 reference evidence: ../Open-BFME-2 at f301d686c70c3e5fa0b51b342a2745f495b8a0b1, Code/Libraries/Source/WWVegas/WWLib/RvaHashResize00927DE0.cpp and commit e9d93338e0 demonstrate the same declaration-only technique for losing STL copies. BFME1's existing ledger and matched caller/provider bytes establish this specialization independently; no donor addresses or layouts are imported.

Verification: all matched rows in every changed unit and provider pass scoped byte/relocation verification. COFF confirms the selected symbol is now an undefined external in every edited emitter. Before: census has competing losing copies. After: those emitters are gone and providers still byte-verify; current global linking remains unknown pending a refreshed census. No aggregate linked-byte increase or new conversion is claimed.
