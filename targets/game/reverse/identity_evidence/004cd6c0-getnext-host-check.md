# 0x004CD6C0 getNextSelectablePlayer: the host check is not GameInfo::amIHost's slot

Session a1/58, 2026-10-17, model=claude-opus-5-5.

Retail 0x004CD6C0 +0x16 calls ILT 0x000329B1, which jumps to 0x0068D4A0
(18 B: `mov al,[ecx+0xc]; test al,al; jne; xor al,al; ret; add ecx,0x58;
jmp ILT 0x2DB2D`). The receiver is the LANGameInfo that TheLAN's slot 0xC0
returned. The earlier unverified source spelled this test
`((BfmeVirtualLanGameInfo *)game)->amIHost()`, a virtual call through
slot 0x10, which retail does not make here. The direct callee's ledger name
is `?bfmeGo935B@BfmeThing935B@@QAEDXZ` (the same call this file's
handlePlayerTemplateSelection already makes), so the body now calls that.
What 0x0068D4A0 really is stays unproven; it keeps its ledger name.

The converted body verifies 142/142 against retail.
