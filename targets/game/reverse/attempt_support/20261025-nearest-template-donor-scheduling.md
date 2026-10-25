# 0x0036FE10: donor scheduling trial, 2026-10-25

BFME 1 revision: ad617ed1dc. Preferred bank remains
`targets/game/reverse/attempts/0x0036fe10.cpp`, unchanged: 279 bytes, six
relocations, four non-relocation differences at A1/A8/AE/B9. This trial did
not recover authored C++ or establish a linking improvement.

## Independent target facts

Retail RET4 at 0036FF24 and INT3 at 0036FF27 establish 279 bytes. The matched
CastleBuild caller passes a const AsciiString reference and consumes an Object
pointer. The receiver comes from the CastleBehavior module lookup, but the
original method spelling is unproven. Retail uses template +4, override +4,
name +20, position +38, next-object +88 and receiver object +8.
`callees.py 0x0036FE10 279` confirms ILTs 000358BE -> 00383090 (thiscall,
zero stack arguments, EAX return), 000022BB -> 00087A80 and 00036AA2 ->
0015B830. No new pin, name, global, alias or production definition was added.
The inherited bank's three alternatename directives still need removal and
independent canonical binding checks before any promotion.

## Donor evidence and applicability

Reviewed read-only BFME 2 revision 8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9,
pinned revision beed8a16790a6812231ac7b05e3e6893e4cb5d1b, and donor commit
81e4dfc9ac310ad8e7c06fced9b917e088699640. The corresponding matched source is
`Code/GameEngine/Source/GameLogic/Object/Behavior/CastleBehaviorNearestTemplate.cpp`,
rva00397429, 165 bytes. It uses volatile XYZ reads and a standalone
_WriteBarrier after subtraction to obtain its SSE schedule. This is a new
mechanism for the bank, not BFME 1 identity or layout proof. BFME 1 has extra
inline name comparison/override handling, next +88 rather than donor +8C,
and x87 rather than the donor's SSE context; those target facts were retained.

The required `bfme2_sweep.py compile Code/GameEngine/Source/GameLogic/Object/Behavior/CastleBehaviorNearestTemplate.cpp`
stopped with `header dependency set changed during trial`. Diagnostics are in
ignored `build/bfme2_sweep/trials/ca5e71bd9ca441259770fdc346e509d8/compile.log`.
The trace contains a lowercase z:/work7/open-bfme-1/.../string_base.h path,
whereas the initial dependency collector only retains existing case-sensitive
host files and the second collector does not apply that filter. This explains
the refusal from inspection; it is not a successful trial receipt. No matching
command was run on the unreceipted object and no gate/tool workaround was made.

## Isolated BFME 1 trials

Private sources and object receipts live under ignored
`build/banked-nearest-20261025/` and `build/experiments/`. The baseline removes
all three linker directives without changing instructions. All sources use
BFME 1's normal O2 compiler context and original bank include paths; no shared
verification object was reused. Probe comparison masks relocation fields only;
these diagnostic measurements do not establish relocation correctness.

Donor-style scalar subtraction was tested with/without volatile reads,
with/without _WriteBarrier, full visible noinline estimate helper versus
canonical declaration only, and src/pos declaration order. None beats the bank:
nonvolatile gives 268-270 bytes; volatile gives 278-279 with at least 15
non-relocation differences. Then _WriteBarrier, _ReadBarrier and
_ReadWriteBarrier were tested before copy, between copy/subtract and after
subtract, with saved coordinate pointers and direct operand expressions. None
improves it. The 35 measurements are preserved in the paired CSV. The donor's
write barrier changes instruction scheduling, not merely ECX/EDX assignment.

## Resume only with new evidence

Keep the better four-byte bank. The remaining permutation loads `this` in ECX
and source Z in EDX, whereas retail uses EDX and ECX respectively. Previous
inline-position experiments obtain those registers but move the owner load past
FLD Y. Do not repeat volatile/barrier, local ordering or register rotation
families without a new explanation. C2 expression identity/visibility remains
a possible area, but this pass establishes no successful lever. Identity and
canonical callee/global ownership must be reviewed separately even if a future
masked match is exact. Claim released; no production file or ledger changed.
