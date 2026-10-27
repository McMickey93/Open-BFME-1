# 0x002850A0 Rva002850A0::rva002850A0 bank (2026-10-27, a1 s465)

Source: attempt_history/0x002850a0/4b91f79b77550fd92547cd1a6783cffecc904d0357887c787b025a271099c2a9.json
(byte score 0.28 because of the 1-byte shift; kept beside the older bank).
Reached via ILT 0x0003767D from matched BannerCarrierUpdate::update; owner
and method name remain address-derived (no new identity claim).

Decode (retail): player = m_object->getControllingPlayer() (ILT 0x20824), 0 ->
return; data = m_data; iterate 0x009F2960(&result, &m_object->pos,
data+0x3C range, 0, PartitionFilterAcceptByKindOf(mask bit 108,
KINDOFMASK_NONE) [out-of-line ctor ILT 0x382FD] .link(&PartitionFilterPlayerAffiliation(player,2,true)), 1).
Loop: skip other+0x90 & 4; iface = other->unidentified_001BFE20(); limit =
iface vslot 0x14C; if vslot 0x158 < limit: made = vslot 0x15C(other+8);
made -> updateShroudNow (ILT 0x292DF) and FXList::doFXObj(data+0x34, made, 0)
when set; break unless data+0x39; else if vslot 0x148 > 1 -> vslot 0x144(1).

Result: 479/479 B, shape 0.967; loop body identical modulo a 1-byte shift.
Remaining: (1) ours pushes EBP right after EBX (+0x32) where retail delays
`push ebp` to just before the loop (+0xCF, after the filter dtors);
(2) retail reloads m_object into ESI between the KindOf ctor and link
(this dead), ours loads it into EAX after link.
Tried: no data local (484 B), Object* local (481 B: arg order then matches
retail but object->EDI, zero->EBP), data local placed late (same),
`slot14c() > slot158()` compare (481 B). Template: CombineHordeSpecialPowerDoSpecialPower
bank (0x00259910) and VeterancyCrateCollideExecute.cpp; a named mask local
hurt here (mask must follow the affiliation filter's stores).
model=claude-opus-5-5 t=25min
