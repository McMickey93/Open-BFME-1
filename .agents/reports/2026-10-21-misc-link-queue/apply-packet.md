# Queue 8: applyPacket needs a real provider

The unresolved name is `Rva0015A190Owner::applyPacket(Rva0015A190Packet *, int)`.
The existing pin points at ILT RVA `0x00048C43`, which routes to the
`?d_00159ad0@@YAXXZ` dump at RVA `0x00159AD0`, 1101 bytes. No clean C++
provider defines the requested member. The pin alone cannot resolve a strict link.

`tools/dis_retail.py 0x00159ED0 90` proves the final `ret 8` at body offset
`0x44A`, followed immediately by INT3 padding at offset `0x44D`. The entry
preserves ECX in EDI and installs an EH frame, consistent with a two-slot
thiscall member. The first explicit argument is read at `[esp+0x64]` after
the entry frame allocation; its object supplies virtual slots +0, +8.
This is richer than a trivially copied 16-byte packet and should not be replaced
with a fabricated forwarding function.

`tools/callees.py 0x00159AD0 1101` reports 23 distinct direct call targets,
including pathfinding, pooled allocation, virtual-object work and `__ftol2`.
The target still needs full reconstruction and independent ABI work for those
helpers. The three affected caller files in the queue require the same member.
The initial scoped link check confirms this exact unresolved symbol; its wider
selection verdict is UNKNOWN because 22,632 census objects were unavailable.

No source or pin was changed. Existing dump bytes remain evidence, not progress.
