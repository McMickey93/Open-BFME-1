# 0x009A30B0 BfmeThingCGD::bfmeTwoCGD

## Result

BFME 1 RVA `0x009A30B0` (333 bytes) is `BfmeThingCGD::bfmeTwoCGD`, the contact
pass of the collision manager. The gen-dump row `?d_009a30b0@@YAXXZ` is retired
and the body lives in
`game/Libraries/Source/collisionmanager/BfmeThingCGDBfmeTwoCGD.cpp`.

## BFME 1 target evidence

- The matched `BfmeThingCGD::bfmeGoCGD` at `0x009A4A30` (41 bytes,
  `BfmeConv597.cpp`) calls `bfmeTwoCGD()` between `bfmeGlobalCGD` and clearing
  `m_bfmeBusy`. The call is a direct `call` to this address through the pinned
  symbol `?bfmeTwoCGD@BfmeThingCGD@@QAEXXZ` in `symbols.csv`.
- The BFME 1 class view has the contact bucket array at `+0xAE10` (0x493
  entries), the active cursor at `+0xC05C`, the index at `+0xC060` and the
  current cursor at `+0xC064`. The dumped body reads and writes exactly those
  offsets: `m_index` 0, `m_cur = m_buckets[0]`, the 0x493 scan, and the
  node-at-+0x30 cursor advance.
- The gen dump records the 333-byte extent; the body ends in `ret` before the
  next dump function at `0x009A3200`. No size change is claimed.

The method name is the existing BFME 1 pinned identity and is retained; this
body proves the same class/layout role. Contact-node field and virtual-slot
spellings describe observed roles, not recovered original identifiers.

## Donor evidence

BFME 2 reference checkout `inputs/reference/open-bfme-2` at revision
`ce1b975697c2f20e514174e3875f8820d1dba612`:

- `Code/Libraries/Source/collisionmanager/collisionmanager_impl.cpp`,
  `CollisionManagerImpl::bfmeTwoCGD`, native `0x00758DE0` (333 bytes), called by
  `Update` at `0x0075A4AB`.
- Donor evidence record
  `reverse/attempt_support/cgd-abi-758de0-20261023/README.md`: the 333 bytes
  match with zero relocations, and the interface ABI is independently
  established from Object's slot table. Slot `0x0C` is the zero-argument
  primary-Object getter (`lea eax,[ecx-70h]; ret`); slots `0x20` and `0x24` are
  three-argument callbacks (RET 12) whose point/normal arguments stay on the
  stack from the outer expression. The donor's old bank had assigned those
  arguments to the inner getter; that was the wrong ABI.
- The donor body copied into this TU is exact against the BFME 1 retail body:
  333/333 bytes and zero relocations under both the donor's
  `/O2 /G6 /DNDEBUG /MD` and this file's default BFME 1 flags.

## Prior BFME 1 attempt

The bank `targets/game/reverse/attempts/0x009a30b0.cpp` (score 0.8769) modeled
slot `0x0C` as a two-vector getter and slots `0x20`/`0x24` as one-argument
callbacks, and used a `next()` helper to walk the cursor. The donor's ABI
correction (getter with no arguments; test/response with the object, location
and normal as three arguments; save the contact before advancing the shared
cursor) resolves the scheduling and register residue. The bank is replaced by
this landing.

## Codegen note

The canonical `Coord3D` is a plain 3-float POD. The donor's
`Coord3DCtorView.h` supplies a user copy constructor, and the exact retail
sequence (`fld`/`fstp` copies of x and y, integer move of z, then in-place
negation) depends on that copy shape. Copying the three fields explicitly and
then negating them reproduces the same sequence with the canonical POD type, so
this TU needs no donor header and no second `Coord3D` definition.

## Verification

```text
python3 tools/probe.py game/Libraries/Source/collisionmanager/BfmeThingCGDBfmeTwoCGD.cpp \
  '?bfmeTwoCGD@BfmeThingCGD@@QAEXXZ' 0x009A30B0 --size 333
size     ours=333 retail=333  relocs=0
result   EXACT (modulo relocation slots)
```
