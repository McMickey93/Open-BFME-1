# Queue 18: existing constructor has a different recorded identity

The unresolved `SurfaceClass(IDirect3DSurface9 *)` in
`Rva0090C2F0InnerLoad.cpp` already has a consistent pin to RVA `0x008FC590`.
`pin_consistency.py --symbol` confirms the only matched owner there is
`BfmeThingDC::BfmeThingDC(BfmeItemDC *)`, a 25-byte body in
`BfmeOneHundredEightySix.cpp`. Adding another definition or pin would not
resolve the one-body/one-identity problem.

The retail constructor stores the argument at this+0, null-tests it, calls
COM slot +4 (AddRef), returns this and executes `ret 4`. The matched loader
calls that address to wrap a surface, then calls `SurfaceClass::DrawPixel`.
The source-path evidence surfaced by `name_lane.py next --file` is
`Libraries/Source/WWVegas/WW3D2/surfaceclass.cpp`. Together these support a
SurfaceClass identity correction, while the old Zero Hour +8 member offset
is only a hint: `name_oracle.py --class SurfaceClass` has no BFME layout witness.

Both constructor spellings produce `UNTESTABLE` from `ilt_oracle.py check`
because this library address is not a thunk target. `ilt_repair.py` only
supports unused pin renames and access/const edits; class changes on an
existing handwritten body are explicitly nonmechanical. Its local repairs
CSV is absent. The naming lane session was opened for the provider file; it
did not serve BfmeThingDC among its rename candidates. No second vendor vote
was obtained in this task.

AGENTS.md reserves name writes to name_lane/ilt_repair and pauses bulk
renames. Therefore this task preserves evidence for the authorized naming
workflow. The consistent old provider and caller remain unchanged; the
strict unresolved constructor remains open.
