# 0x001F1370: AICommandInterface int command keeps its address

The 203-byte body at 0x001F1370 (ret 8 at +0xA6 and +0xC8, int3 after) was
ledgered as `??1OathbreakersFadeAwayBehavior@@UAE@XZ` from a naked `__emit`
lift. A destructor takes no stack argument; this body pops two.

The bytes build an `AICommandParms` on the stack through the pinned
constructor `??0AICommandParms@@QAE@W4AICommandType@@W4CommandSourceType@@@Z`
(ILT 0x00030EA4) with command 0x31 and the second argument as the command
source, store the first argument at +0x34 (`m_intValue`), call the receiver's
vtable slot 0 (`aiDoCommand`) with the parameters, then run the parameters'
inline destructor (the `std::vector<Coord3D>` at +0x20). It is the same shape
as the matched `AICommandInterface::aiEnter` (0x000D89C0, also 203 bytes) with
`m_intValue` in place of `m_obj`, so the receiver is `AICommandInterface`.

`tools/ilt_oracle.py check '??1OathbreakersFadeAwayBehavior@@UAE@XZ' 0x1336d`
reports CONTRADICTED (p_false 5.22e-04). Retail calls it through ILT
0x0001336D from 0x001F1620, 0x00201D30, 0x00203F90 and 0x00242B90, whose
matched sources pin only opaque names there. BFME renumbered AICommandType
(AICMD_ENTER is 0x17 here, 27 in Zero Hour), so 0x31 cannot be mapped to a
Zero Hour command name, and the method name is unknown. The row becomes
`?rva001F1370@AICommandInterface@@QAEXHW4CommandSourceType@@@Z` in
AICommandInterfaceMovementOrders.cpp beside aiEnter.
