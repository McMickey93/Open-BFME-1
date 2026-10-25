# 0x009A2750 axis-list merge sort

## Result

BFME 1 RVA `0x009A2750` (460 bytes) is `CollisionManagerImpl::rva009A2750`,
the bottom-up merge sort of each axis endpoint list. `UpdateSort`
(`0x009A3AD0`, already matched in
`game/Libraries/Source/collisionmanager/collisionmanager_impl.cpp`) calls it on
its rebuild path. The converted body is in the same TU and the previous
`/alternatename` alias to the gen-dump row is removed.

## Target evidence

- The gen-dump row `?d_009a2750@@YAXXZ` has a 460-byte extent in
  `game/gen_asm/d_0099d0c0.asm`.
- The matched `UpdateSort` body calls the address after the reinsertion pass,
  and the class fields it walks (`m_axisHeads`, `m_axisCount`) are the same
  ones this function writes.
- Thiscall void(void) and cdecl void(void) share the same machine interface
  here (this in ECX, plain return, no stack arguments), so the dump's
  address-derived name changes to the class member name without an ABI
  difference.

## Donor evidence

BFME 2 reference checkout `inputs/reference/open-bfme-2` at revision
`ce1b975697c2f20e514174e3875f8820d1dba612`:

- `Code/Libraries/Source/collisionmanager/collisionmanager_impl.cpp`,
  `CollisionManagerImpl::rva007586F0`, donor RVA `0x007586F0`, 460 bytes.
- The donor body is exact against BFME 1 outside relocation fields (here:
  no relocations at all).
- The donor header records that its UpdateSort caller and the identical
  WorldBuilder body at `0x01802EC0` establish the purpose and layout, while
  the original method name stays unknown; `rva007586F0` is address-derived.
  The BFME 1 name therefore stays address-derived too.

## Verification

`tools/probe.py game/Libraries/Source/collisionmanager/collisionmanager_impl.cpp
'?rva009A2750@CollisionManagerImpl@@QAEXXZ' 0x009A2750 --size 460` reports:

```
size     ours=460 retail=460  relocs=0
result   EXACT (modulo relocation slots)
```

The donor's two left-run count reads go through a volatile-qualified accessor
(`SortList::getCount`). That is a codegen choice reproducing VC7.1's register
cost, not evidence that the original field was declared volatile; the same
reads and merge operations are preserved.

## Prior attempts

The bank `targets/game/reverse/attempts/0x009a2750.cpp` (score 0.9304) stopped
at 32 differing bytes because every spelling that placed the second queue's
`lea` where retail puts it also permuted the callee-saved colouring. The donor
accessor shape resolves exactly that interference: it emits the intended `lea`
and keeps the retail register assignment.
