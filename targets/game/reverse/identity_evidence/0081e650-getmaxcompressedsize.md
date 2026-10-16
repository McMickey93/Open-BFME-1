# CompressionManager::getMaxCompressedSize at RVA 0x0081E650

New name: `?getMaxCompressedSize@CompressionManager@@SAHHW4CompressionType@@@Z`.
Retired interior claim: `?dup_0081e679@@YAXXZ` at 0x0081E679 (8 bytes).

## Extent

Retail disassembly (`tools/dis_retail.py 0x0081E648 0x90`): getCompressionType
ends with `ret` at 0x0081E648 and int3 padding follows. The body starts at
0x0081E650 with `mov eax,[esp+8]; dec eax; cmp eax,0xc; ja +0x55`. It then
indexes the byte map at VA 0x00C1E6B4 and jumps through the three-entry table at
VA 0x00C1E6A8. The code ends at +0x57 (`xor eax,eax; ret` at +0x55). The jump
table covers +0x58..+0x63 and the byte map +0x64..+0x70. Int3 padding starts at
+0x71. The full extent is 113 bytes, ending at 0x0081E6C1, and getUncompressedSize
(0x0081E6D0) follows the padding.

The table entries are VA 0x00C1E679, 0x00C1E668 and 0x00C1E681, the switch arms
at +0x29, +0x18 and +0x31. The byte map sends compType-1 = 0 (REFPACK) and
11..12 (BTREE, HUFF) to entry 0, 1 (NOXLZH) to entry 1 and 2..10 (ZLIB1..9) to
entry 2. So 0x0081E679 is the BTREE/HUFF/REFPACK arm
(`mov eax,[esp+4]; add eax,8; ret`) inside this body, not a separate
function. Its `?dup_0081e679@@YAXXZ` row was a gen-alias. It was keyed on
byte equality with `rva_a02c0_pointer_offset`, which `value + 8` also produces,
and nothing else reaches that address. A scan of the retail image finds no rel32
call or jump to it, and its only DIR32 reference is this body's own jump table at
0x0081E6A8. The
ea_evidence row for 0x0081E679 already assigns it to
`Libraries/Source/Compression/CompressionManager.cpp`.

## Identity

- The address lies between the matched getCompressionType (0x0081E560) and
  getUncompressedSize (0x0081E6D0), followed by compressData (0x0081E710). That is
  the reference CompressionManager.cpp order
  (`inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/Compression/CompressionManager.cpp`
  line 139).
- The switch matches the reference body arm for arm. Cases are compType-1 in
  0..12 (REFPACK=1 .. HUFF=13). NOXLZH (2) calls 0x0081EB70 and adds 8. That
  callee is a five-byte tail jump to the matched LZHLCompressorCalcMaxBuf
  (0x00823200), which is the reference's CalcNewSize in NoxCompress.cpp, placed
  directly before DecompressMemory (0x0081EB80). REFPACK/BTREE/HUFF return
  len + 8. ZLIB1..9 compute ceil(len * 1.1 + 20) through MSVCR71!ceil and
  __ftol2. Every other value returns 0.
- Retail has no rel32 or DIR32 reference to 0x0081E650. As in the reference, only
  the DEBUG compression test calls it, so the signature comes from the reference
  header. `compression.h` already declares
  `static Int getMaxCompressedSize( Int uncompressedLen, CompressionType compType );`.

## Byte check

`tools/probe.py` reports the reference body in
`game/Libraries/Source/Compression/CompressionManager_decompressData.cpp` as
113/113 bytes, EXACT modulo 10 relocation slots.
