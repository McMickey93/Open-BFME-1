# Retire the impossible allocateFromW3DMemPool pin

`targets/game/reverse/symbols.csv` carried one record for
`?allocateFromW3DMemPool@@YAPAXPAXH@Z`:

```csv
?allocateFromW3DMemPool@@YAPAXPAXH@Z,0x00881F30,packet 00921eba callee pin
```

Two independent facts make that pin impossible, so the record is removed.

**1. 0x00881F30 is already a matched ledger row for a different name.**
`functions.csv` homes `??2@YAPAXI@Z` at 0x00881F30, size 17, source
`game/Libraries/Source/WWVegas/WWLib/mem_ops.cpp`, notes `operator new`. Its
body (tools/dis_retail.py 881f30) reads exactly one stack argument and
tail-calls the allocator hook:

```
+0000 8b 44 24 04   mov  eax, dword ptr [esp + 4]   ; size
+0004 6a 01         push 1
+0006 50            push eax
+0007 ff 15 b4 e9 30 01  call dword ptr [0x130e9b4]   ; __gameMemAllocPtr
```

That is `void * operator new(size_t size) { return gameMemAlloc(size, 1); }`.
`?allocateFromW3DMemPool@@YAPAXPAXH@Z` takes two arguments, so the same
address cannot hold both bodies.

**2. The body the name needs is absent from the retail image.** Under NDEBUG the
source body in `game/GameEngine/Source/Common/System/GameMemory.cpp` reduces to
`return ((MemoryPool*)pool)->allocateBlock("allocateFromW3DMemPool");`, so its
only string literal is `allocateFromW3DMemPool`. That literal does not occur
anywhere in `inputs/baselines/bfme1/retail-1.03-unpacked/files/lotrbfme.exe`,
nor does the shorter `W3DMemPool`; an inlined copy would have left the literal
at each call site. Retail therefore has no out-of-line two-argument
`allocateFromW3DMemPool`, and no call site can name one. The control search
over the same image finds the real literals that must be there (`NULL`, 39
occurrences), and finds no debug-only strings (`bad w3d pool`, `pool is null`),
which is the expected NDEBUG shape.

Removal corrects pin metadata only: no function row, source implementation or
coverage changes. The definition in GameMemory.cpp stays, because the W3DMPO
glue in `game/Libraries/Source/WWVegas/WWLib/always.h` still references it; with
no retail address the census no longer judges that source-only helper against
operator new's bytes, which is what kept `nullrobj.cpp` at `wrong_selected`.

The retired record, verbatim:

```csv
?allocateFromW3DMemPool@@YAPAXPAXH@Z,0x00881F30,packet 00921eba callee pin
```
