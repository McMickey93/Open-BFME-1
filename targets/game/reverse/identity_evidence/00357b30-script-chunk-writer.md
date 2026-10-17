# 0x00357B30: BFME "Script" chunk writer, address-named Rva00357B30

Session a1/68, 2026-10-17, model=claude-opus-5-5.

## Boundary

Retail 0x00357B30..0x00357C6E (318 B): `ret` at +0x13D, int3 padding from +0x13E. The
only incremental-link thunk that reaches it is 0x000285D3 (`jmp 0x00757B30`). It is a cdecl
function with three arguments: `ebx = [esp+0x10]` after one push is the third.

## What it does

It walks a chain of script handles `{next, recordIndex, version}`. For each live handle it takes
the 20-byte record at `list+0x38`, follows `previousVersion` back to the handle's version, then:

- `openDataChunk("Script", 2)`: the literal at VA 0x010E8470 is `Script\0`
- writes the record name, then the data's three comments (+0x08/+0x0C/+0x10)
- writes six flag bytes in the reference order active, oneShot, easy, normal, hard, subroutine
  (+0x19, +0x1A, +0x1C, +0x1D, +0x1E, +0x1B) and the delay int (+0x14)
- calls OrCondition::WriteOrConditionDataChunk (ILT 0x285D8 -> 0x00355C90),
  ScriptAction::WriteActionDataChunk (0x1B4B4 -> 0x003513F0) and
  WriteActionFalseDataChunk (0x8940 -> 0x003514C0) on +0x20/+0x24/+0x28, then closeDataChunk.

So it is BFME's counterpart of the reference `Script::WriteScriptDataChunk`, with the list as
a new second argument.

## Why the old names are retired

- The row was `?WriteScriptDataChunk@Script@@SAXAAVDataChunkOutput@@PAV1@@Z`, a two-argument
  static; the body reads a third argument. tools/ilt_oracle.py CONTRADICTS it at 0x285D3.
- The pin at the ILT was `?WriteGroupDataChunk@@YAXAAVDataChunkOutput@@PAVScriptList@@PAVScriptGroup@@@Z`.
  The body writes "Script" chunks, not "ScriptGroup" ones (that literal, VA 0x010E8478, is
  0x00359EE0's), and the oracle CONTRADICTS that name at 0x285D3 too.
- Retail callers: ScriptList::WriteScriptListDataChunk (0x0035B470, on this+0x08 before the
  this+0x04 group chain, the reference order), ScriptList::WriteScriptsDataChunk's inlined
  copy (0x0035B4F4) and the "ScriptGroup" writer 0x00359EE0 (on each group's +0x0C chain).

No decorated name was proven (a brute force over plausible spellings fits too many windows by
chance to mean anything), so the body keeps its address: `Rva00357B30`.
