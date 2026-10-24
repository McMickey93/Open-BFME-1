# Task 1: hash resize used by 0x000D6C60

Queue rank 9 (census e9a5ae5b4c). The census selects the wrong resize COMDAT from RvaHashInsertAsciiString.cpp over the dedicated provider. The insertion unit declares the hash out of line; the provider inlines the string hash. Declare the resize specialization without a definition in the insertion unit so its existing external call uses the dedicated provider.

BFME2 reference: ../Open-BFME-2 at f301d686c70c3e5fa0b51b342a2745f495b8a0b1, Code/Libraries/Source/WWVegas/WWLib/RvaHashResize00927DE0.cpp and commit e9d93338e0 use declaration-only suppression for losing STL COMDATs. This is a technique transfer, not a donor identity or address transfer. BFME1 retains its own types, ABI, flags and provider.

Verification: scoped build of insertion unit passes 23/23 functions; dedicated provider passes 1/1 (418 bytes), including relocations. COFF confirms the resize symbol is now undefined in the insertion object. Before link_check --census-only reports selected wrong; current global linking preview remains unknown because census inputs moved. No aggregate linked-byte gain or new conversion is claimed.
