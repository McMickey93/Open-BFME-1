# 009EFF50 refresh: reference ordering reduces 39 differences to 14

This is a compiler-matching prerequisite for recovering the complete 3186-byte
`Q1Receiver0134FAAC::refresh`, not a landed body. No game source, ledger, pin,
baseline or build input changed. The improved candidate is banked in
`targets/game/reverse/attempts/0x009eff50.cpp`.

## Independent BFME 1 facts

The existing pin and five matched callers establish the member identity; see
`targets/game/reverse/identity_evidence/009eff50-refresh-reverify-20261013.md`.
Retail RET at +0xC71 and INT3 at +0xC72 establish 3186 bytes. The existing bank
at BFME 1 revision `45452aecf2d5bf4d4bf9f010593acf3d72615c54` emitted 3186 bytes,
39 relocations and 39 differing non-relocation bytes. Its normalized instruction
shape was 1.000. This session read the prior attempt log before experimenting.

The new bank emits 3186 bytes with 39 relocations and **14** non-relocation
differences, shape 1.000, measured by `tools/probe.py`. First differing byte is
+0xB2A, inside the instruction at +0xB28. Only deque-size operand displacements
differ. The node sum and pass-0 start terms now match; pass 0 still exchanges
the deque-0/deque-1 finish terms, and pass 1 retains a finish/start permutation.
This masked comparison does not verify unresolved relocations.

## Donor contribution and limits

Reviewed pinned donor `beed8a16790a6812231ac7b05e3e6893e4cb5d1b` and read-only
current donor `8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9`:

- `Code/Libraries/Source/assetmanager/AssetManagerImplRefresh.cpp`
- `reverse/attempt_support/0x006227e0-reduction-mechanism-20261021.md`
- `reverse/attempt_support/0x006227e0-per-arm-addressing-20261020.md`
- `docs/recipes.md`, the c2 flattened-sum sorting discussion
- donor recovery `ae782dbf28` and later linking revisions `22febfd829`,
  `3c6a1bd5fb`, `fc64722c74`

The donor's measured mechanism is that c2 FactCanonSort keys depend on local
reference declaration numbers and on member/pointer/reference addressing.
That was a new hypothesis beyond BFME 1's exhausted addend permutations.
The donor's winning `r1,r0,r2` order did not transfer directly. The BFME 1
improvement is independently measured below; no donor layout or callee address
was imported. BFME 2 has an eight-byte layout shift and a signed 64-bit budget;
BFME 1's existing 32-bit fields and offsets were preserved.

The required private donor compile was attempted with
`bfme2_sweep.py compile Code/Libraries/Source/assetmanager/AssetManagerImplRefresh.cpp`.
Receipt `build/bfme2_sweep/trials/3fe4a10872ee4e0cb911bc9978cb6532/trial.json`
is failed. Its include trace combines BFME 1's STLport container headers with
the donor allocator shim, and line 320's const `allocator::allocate`
specialization fails C2244/C1506. This is an unresolved build-context failure,
not evidence against the donor body. No match command was run on that failed
receipt. The donor trees and pinned pointer were not changed.

## Minimal successful transformation

Immediately after `Q1ReceiverPending pending;`, before `known`, declare:

```cpp
Q1ReceiverQueue *queues = m_deques78;
Q1ReceiverQueue &r0 = m_deques78[0];
Q1ReceiverQueue &r2 = m_deques78[2];
Q1ReceiverQueue &r1 = m_deques78[1];
```

Keep the existing control flow and use these count expressions:

```cpp
if (pass == 0)
    m_field1e0 = r0.size() + r1.size() + r2.size();
else
    m_field1e4 = queues[0].size() + queues[1].size() +
        queues[2].size() - m_field1e0;
```

All four locals are used. Moving the same declarations just before the pass
loop gives 18 differences instead of 14. The 14 differing byte offsets are
`B2A B32 B38 B43 B91 B97 B9D BA5 BB0 BB8 BC3 BCB BD6 BDE`.

## Trials and compiler context

`20261025-refresh-reference-order-trials.csv` preserves 730 experiment rows.
`masked_diff_bytes` also includes the absolute size delta for unequal extents;
only equal-size masked comparisons are near-match evidence. Case names encode
the exact declaration order and per-arm addressing (`r` reference, `p` queue
pointer, `m` receiver member). Phases:

- `pass`: old bank and six reference orders, then all 6 x 8 x 8 reference/
  pointer arm combinations with declarations just before the pass loop.
- `declarations`: all 24 orders of pointer `q` plus references 0/1/2, using
  `rrr/ppp` and donor `rrp/rrr` addressing; no improvement below 18.
- `placement`: six reference orders before lock, pending, known, q loop or
  eviction loop; best 14 before known/q or before eviction with order 102.
- `known-grid`: order 021 before known, all r/p/m arm pairs using every
  declared reference and the pointer; best 14, member form does not improve it.
- `qualifiers-flags`: all 16 const qualifications of pointer/references,
  plus /G6, /G6 /arch:SSE and /G7 /arch:SSE. Const and the first two flag
  forms retain 14; /G7 /arch:SSE changes the body to 3142 bytes.
- `per-arm`: separate first/second reference sets in every pair of orders,
  grouped or interleaved; all break the shared shape (best 881 differences).
- `final-refs`: six orders before the known flag, keys construction, key
  iteration or count sums, plus all eight member/pointer reference-initializer
  combinations; best remains 14.

Three additional native `deque<int>` variants emitted 3124/3233/3170 bytes
with 850/898/859 differences, first +0x836. Changing the queue template type
also changes inlining; it is not a direct callee-binding fix.

MSVC 7.1 from `inputs/toolchains/vs2003`, Wine, normal BFME 1 compiler helper.
Observed default command: `-O2 -GR- -EHsc- -DNDEBUG -DWIN32 -D_WINDOWS -MD
-EHsc -D_STLP_USE_STATIC_LIB -D_STLP_NO_EXCEPTIONS`; no explicit /G switch.
Compiler binary-set fingerprint:
`e287f350c5c53dc919dde6a140209899c33bf61e495ad5668f4d1ca049d60477`.
Diagnostics used private `build/experiments/<hash>/object-<uuid>.obj` outputs.
No diagnostic object is an acceptance receipt.

## Remaining prerequisites

Do not add the old logs' proposed ICF aliases: retail has one identity per
body. `callees.py` identifies `_Deque_iterator_base<int>::_M_advance` at
009ED4A0, whereas the bank emits a pointer-deque specialization. Its pending
tree destructor also has an unresolved specialization against the currently
generated 009EE070 identity. Reconcile the actual storage types, inlining and
callee ABI before landing; byte masking alone cannot settle those identities.

Official home is `game/Libraries/Source/assetmanager/assetmanager_impl.cpp`.
Its existing receiver/tree/hash views must be reconciled when porting; do not
append another definition of the same class. There are no other served
reloc-named siblings in that file in this queue snapshot.

`link_check.py` reports this home's preview **unknown**: 22,641 changed or
missing ledger objects since census `32774ab033` (2026-10-24 11:02), including
unreadable `game_gen_small_thunks_000.obj`. No linked-byte improvement is
claimed. No full build or census rebuild was started.
