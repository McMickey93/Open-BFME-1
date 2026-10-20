# 0x006BD6E0 W3DGhostObject::DoXfer in clean C++

Retail 0x006BD6E0..0x006BDA28 (840 bytes): the RET 4 at +0x305 and two cold
throw tails, the second ending with the noreturn `_CxxThrowException` call at
+0x343 (INT3 padding from +0x348). The extent is the one the MASM dump
`game/masm_dumps/Rva006BD6E0Xfer.asm` carried as `?Rva006BD6E0@@YAXXZ`; the
compiled body equals retail over all 840 bytes modulo its 25 relocation slots
and also reproduces the padding INT3 that follows.

## Identity

- The W3DGhostObject vftable 0x0111CFB8 reaches this body from slot 3 (the
  BFME Snapshot DoXfer slot) through ILT 0x000268D7. Slot 1 is the matched
  `?loadPostProcess@W3DGhostObject@@MAEXXZ` and slot 2 the class-name getter
  returning "W3DGhostObject" (0x0111CFCC).
- `python3 tools/ilt_oracle.py check '?DoXfer@W3DGhostObject@@MAEXAAVXfer@@@Z' 0x006BD6E0`
  prints `CONFIRMED p_false=5.22e-04 (exact)`. Both ZH `?xfer@` spellings and
  `?DoXfer@W3DGhostObjectManager@@MAEXAAVXfer@@@Z` are CONTRADICTED here.
- The body is GeneralsMD W3DGhostObject.cpp `W3DGhostObject::xfer` without the
  trailing shroudedness block: base transfer, version 1, DrawableInfo object
  ID/flags/drawable ID, the per-player snapshot lists, removeParentObject.

## Callees and data

- 0x001B3B70 via ILT 0x0003C1CD: GhostObject's own Snapshot slot 3 body
  (vtable 0x0109CE94, installed by `??0GhostObject@@QAE@XZ` 0x001B3CF0),
  thiscall reading the Xfer argument and ending `ret 4`. ilt_oracle CONFIRMS
  `?DoXfer@GhostObject@@MAEXAAVXfer@@@Z` there (p_false 1.30e-04, exact); the
  call resolves to that matched row (landed in 1be4c6ded7), so no pin is
  needed.
- 0x0010C3C0 / 0x0010C3E0 via ILTs 0x0000C9B4 / 0x00008CA1: the ledger's
  ObjectID and DrawableID transfers (`Rva0010C3C0`, `Rva0010C3E0`).
- `?getID@Drawable@@QBE?AW4DrawableID@@XZ` (0x004116B0),
  `?disableUVAnimations@@YAXPAVRenderObjClass@@@Z` (0x006BCB70),
  `?removeParentObject@W3DGhostObject@@IAEXXZ` (0x006BC750),
  `?Create_Render_Obj@@YAPAVRenderObjClass@@PBDMH@Z`,
  `?set@?$StringBase@D@@QAEXPBDH@Z` and the canonical AsciiString/StringBase
  headers, and the native `throw XferException(4, 0)` (variadic ctor
  0x009D6220, ThrowInfo `__TI1?AVXferException@@`).
- Data: `?TheGameClient@@3PAVGameClient@@A`,
  `?m_3DScene@W3DDisplay@@2PAVRTS3DScene@@A`, `?ThePlayerList@@3PAVPlayerList@@A`,
  `??_7W3DRenderObjectSnapshot@@6B@` and the StringBase<char>::str TheNullChr.
- The unwind map has three states (name string at ebp-0x30, the `new`
  pointer at ebp-0x14 freed by operator delete, then the Snapshot base dtor),
  which the build reproduces.

## The frame wall

The banked C++ (attempt_history/0x006bd6e0, score 0.989) emitted bfmeFormatText
plus an absolute ThrowInfo address and held at eight displacement bytes.
With native throws the body was exact except a 0x2C frame against retail's
0x28: the `/FAsc` table showed the two XferException temporaries in
different slots (one with `i`, one with the `new` pointer), where retail
keeps both in the `new` pointer's slot. Writing the stale-list-head throw as
the else arm of the loop body's guard (`if (count != 0 || head == NULL) {...}
else throw`) gives retail's table (j -49, name -48, drawableID -44, colour
-40, scale -36, this -32, version/cursor -28, i -24, both exceptions and the
`new` pointer -20) and every byte.
