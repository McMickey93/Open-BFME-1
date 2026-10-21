# Queue 20: use the existing empty Snapshot destructor body

The two queued constructor TUs declared Snapshot's virtual destructor without
its existing empty definition. Their emitted scalar deleting destructor called
an out-of-line destructor, producing a different COMDAT from
`SubsystemSnapshotStateOwnerConstructor.cpp`, whose local Snapshot class already
has an empty inline destructor.

Define that same empty destructor in `DefaultPhysicsModuleInfoCtorThunk.cpp`
and `LocomotorConstructor.cpp`. No shared header, pin or ledger identity changes.
The scoped build passes both claimed constructor bodies (2/2), including string,
constant, DIR32 and body guards.

Direct COFF inspection of all three objects proves identical 31-byte
`??_GSnapshot@@UAEPAXI@Z` sections, digest `fcdb50f4cd27`. The relocations are
DIR32 at +10 to `??_7Snapshot@@6B@` and REL32 at +18 to `??3@YAXPAX@Z`.
The comparison includes relocation identities, not just masked bytes.
This repairs these two differing emitters; it does not claim a new matched
Snapshot destructor or resolve the separate 83-byte vector destructor identity.

`link_check.py --compile-limit 0` after the change exits 1 with LINKED PREVIEW
UNKNOWN for both files: 21,681 current ledger objects cannot be read locally,
and selection census data is stale, including for Snapshot. Therefore the
whole-link result and global queue closure remain unproven. The concrete result
is the identical COMDAT copies plus unchanged, byte-verified caller bodies.
