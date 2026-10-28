# 0x00514A40 AptInGameChat slot 2 (628 B) — bank 0.97, 19 bytes left

Bank: `targets/game/reverse/attempts/0x00514a40.cpp` (cl `/DNDEBUG /MD /EHsc
/Iinputs/reference/shims/stringinline`), name
`?rva00514A40@AptInGameChat@@QAEHHPAX0@Z`.

Identity (BFME 1 target evidence): vtable 0x01105384 slot 2 through ILT
0x00023BE6, installed by the matched AptInGameChat constructor 0x005160E0.
Window-message handler: `BfmeMsgHandler::defaultHandler`, then
`switch(msg)`: 0x18 hover over the friends list (+0x264) counts repeats in
+0x298/+0x29C/+0x2A0 and past ten on column 2 shows the friend-status
tooltip; it falls through into 0x4030 (zero payload from the chat entry
+0x260 sends, otherwise refresh buttons); 0x4014 refreshes; default 0.
Callee spellings come from the matched sibling
`BfmeAptScreenInGameChatRefreshFriendsList.cpp`.

Lever applied (docs/shape_levers.md "identical return tails" row): retail
keeps the status-2 tooltip arm unmerged and merges status 1 into status 4.
`_WriteBarrier()` ending the status-2 arm and `_ReadWriteBarrier()` ending
the 1, 4 and APT:Null arms reproduce that layout exactly (160 -> 19 diffs).

Remaining (all register choice): in the 1/4/Null arms retail uses eax for
the GameText vtable and edx for the by-value fetch temporary (ours swaps
them, matching arm 2), and before the setCursorTooltip copy constructor
retail writes `mov ecx,esp` before the saved-esp spill.

Ruled out: switch statement (0.863); negated outer test; else-block
nesting; ternary label for 1/4 (0.746); barriers at arm starts (160) or
around the chain (27); swapped intrinsic roles (19, same); WWLib
`unicode_string.h` with body-call constructors instead of StringInline.h
(19, same).

## Session 470 re-probe (2026-10-28, claude-opus-5-5)

Bank re-probed 628/628 B, 19 diffs, unchanged. Further ruled out (diffs):
the status-2 `_WriteBarrier()` is redundant (removing it: 19, same
layout); Null arm without barrier (63); `tooltip` declared before `name`
(45); `unsigned` status (19); `Mouse *` local (453); hoisted `name.str()`
local (418); inline non-virtual `fetch` wrapper for the 1/4/Null arms (443)
or all arms (438). The eax/edx role swap therefore does not come from
declaration order, the barrier on arm 2, or an inline fetch layer.
