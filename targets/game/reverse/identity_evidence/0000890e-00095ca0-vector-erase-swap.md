# 0x0000890E / 0x00095CA0: the two vector erases are swapped in the ledger

Retail evidence, re-derived from `inputs/baselines/bfme1/retail-1.03-unpacked/files/lotrbfme.exe`
(image base 0x400000; RVA = VA - 0x400000):

- `0x0000890E` is a 5-byte incremental-link thunk: `e9 fd 94 44 00`, `jmp 0x00451E10`.
- `0x00013656` is a 5-byte incremental-link thunk: `e9 45 26 08 00`, `jmp 0x00095CA0`.

A direct call/jmp scan of the image finds exactly one reference to each body:

- `0x00451E10` is targeted only by the jmp at `0x0000890E`. The only users of
  `0x0000890E` are the two matched `vector<ICoord2D>::resize` bodies:
  - `0x00453DF0` (90 B, `resize(size_type)`, `ret 4`), `call 0x0000890E` at +0x2D;
  - `0x004535F0` (66 B, `resize(size_type, ICoord2D)`, `ret 0xC`), `call 0x0000890E` at +0x1B.
- `0x00095CA0` is targeted only by the jmp at `0x00013656`, and `0x00013656` has
  no direct callers. It is the incremental-link thunk emitted for the
  `vector<INILine>::erase(first, last)` COMDAT that `INILineBuffer.cpp`
  instantiates from `m_lines.erase(begin(), end())`.

Both bodies are byte-identical, 59 bytes, 8-byte element stride, `ret 8`, no calls:

    +0000 8b 44 24 04              mov  eax, dword ptr [esp+4]
    +0004 56                       push esi
    +0005 8b 71 04                 mov  esi, dword ptr [ecx+4]
    +0008 57                       push edi
    +0009 8b 7c 24 10              mov  edi, dword ptr [esp+0x10]
    +000d 2b f7                    sub  esi, edi
    +000f c1 fe 03                 sar  esi, 3
    +0012 85 f6                    test esi, esi
    +0014 8b d0                    mov  edx, eax
    +0016 7e 1b                    jle  +0x33
    +0018 2b f8                    sub  edi, eax
    +001a 53                       push ebx
    +001b eb 03                    jmp  +0x20
    +001d 8d 49 00                 lea  ecx, [ecx]
    +0020 8b 1c 17                 mov  ebx, dword ptr [edi+edx]
    +0023 89 1a                    mov  dword ptr [edx], ebx
    +0025 8b 5c 17 04              mov  ebx, dword ptr [edi+edx+4]
    +0029 89 5a 04                 mov  dword ptr [edx+4], ebx
    +002c 83 c2 08                 add  edx, 8
    +002f 4e                       dec  esi
    +0030 75 ee                    jne  +0x20
    +0032 5b                       pop  ebx
    +0033 5f                       pop  edi
    +0034 89 51 04                 mov  dword ptr [ecx+4], edx
    +0037 5e                       pop  esi
    +0038 c2 08 00                 ret  8

Retail was linked without identical-COMDAT folding, so one body has exactly one
identity. The copy reached through `0x0000890E` is called only by
`vector<ICoord2D>::resize`, and `tools/ilt_oracle.py check` CONFIRMS
`?erase@?$vector@UICoord2D@@...` at `0x00451E10` (window 6135-6138, exact).
That identity is proven.

The copy at `0x00095CA0` is reached only through the thunk at `0x00013656`,
which has no callers at all. It is an 8-byte-element erase body, but its owner
is not established. `tools/ilt_oracle.py check` CONTRADICTS both names the
ledger has tried on it — `vector<ICoord2D>::erase` and
`vector<INILine>::erase` — because slot 15069 (thunk `0x00013656`) has bucket
window 10942-10946 and neither decorated name hashes into it
(p_false 3.26e-4). It therefore keeps an address-derived name,
`?dup_00095ca0@@YAXXZ`, with `object-symbol=` naming the
`vector<INILine>::erase` COMDAT that `INILineBuffer.cpp` emits: the TU is byte
verified, but that name is not claimed as the body's identity.

The ledger had the identities swapped: `0x00451E10` was named the
`vector<INILine>` erase with source `INILineBuffer.cpp`, and `0x00095CA0` was
named the `vector<ICoord2D>` erase with source `MapUtil.cpp`. It also pinned
`vector<ICoord2D>::erase` at `0x0000890E` with an ICF-alias note.

The corrected rows put the canonical `vector<ICoord2D>` body on the address its
callers reach, `0x00451E10`, and leave `0x00095CA0` opaque. Both
`WorldHeightMap.cpp` (instantiating `m_boundaries.resize`) and `MapUtil.cpp`
emit the same decorated COMDAT; the ledger verifies the row from `MapUtil.cpp`,
whose object defines the symbol and passes the 59-byte selector, while
`WorldHeightMap.cpp` passes all 127 of its rows. The `0x0000890E` pin
stays, because retail's resize relocations land on that thunk; it now carries
`route=0x00451E10` instead of an ICF claim.
