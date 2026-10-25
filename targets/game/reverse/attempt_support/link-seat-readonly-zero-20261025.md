# Readonly-zero gate debt

Input: `ccd94e5a8e`; census artifact `12560789240`, revision `32774ab033`.
This is a gate-debt repair, with no new authored C++ coverage or claimed
linked-byte gain. No identity, layout, ABI, pin or ownership changes.

## Target evidence and scope

Existing matched data row `?g_rva01075350@@3MB` establishes four readonly
zero bytes at VA `0x01075350`, owned by `BfmeAngleWrap0079D0.cpp`.
GettingBuiltBehavior's existing 178-byte body at RVA `0x001FE7C0` compares
module data field `+0x20` with that zero. Its secondary-vtable slot 7 at
VA `0x010A45E0`, routed through ILT RVA `0x00022C19`, remains its identity
evidence; the method retains its address-derived name. The direct callees
and their declarations are unchanged. Replacing its external-zero macro
with `0.0f` preserves the complete retail body and relocation checks.

A tracked-source sweep found only three other BfmeZeroRange mentions:
unused declarations in SubtitleLineTable and getHeightMapHeight, and an
unused literal macro in classifyCells. Remove those. SubtitleLineTable
retains a comment with both historical COFF spellings so the sanctioned
keyed pass-test can find and verify this repaired consumer; the other
consumers are independently verified, not inferred from that test.

The provider's data row passes, but its two helpers initially fail DIR32
checks on references to their own canonical zero name, whose former
exemption is already absent. Their two comparisons also become `0.0f`.
Both complete bodies (57 bytes at `0x0079D0A0`, 68 at `0x0079D0F0`) and
the existing data definition then pass together. The `_CIfmod` intrinsic,
atan2 expression, arithmetic and compiler controls remain unchanged.

Existing identity evidence for the untouched larger bodies remains
`identity_evidence/0x0081d600-donor-port.md` and
`identity_evidence/006cbb50-height-normal.md`; classifyCells retains its
established matched identity and 1405-byte extent. No donor body or name
is imported. The read-only BFME 2 revision
`e2fdc5620c5834c1c98de24aa3510d72e2cbcc69` was searched for corresponding
GettingBuiltBehavior and zero references; it supplies no additional target
proof and no material adaptation for this repair.

## Acceptance

Normal scoped builds pass six matched function rows totaling 3006 bytes,
the existing zero data row, 46 float-constant checks, and 52 DIR32 checks,
with zero baselined body findings. Logs: `build/codex8-zero-*.log`.
The keyed `repair_queue.py pass-test` passes both BfmeZeroRange variants
(`3MA` and `3MB`), removing exactly two existing debts (984 to 982).
No exemption is added. CSV, unmatched-definition and whitespace checks pass.

Census-only preview for the four consumer files is 1135 -> 1135 linked
bytes: GettingBuiltBehavior and getHeightMapHeight link; SubtitleLineTable
still has INI getter ownership/dependency blockers, and classifyCells has
PathfindCell/Pathfinder private-view COMDAT conflicts. These remain outside
this readonly-zero repair. Fresh dependency evidence is required before
claiming any new linked bytes; the census preview is not a live link proof.

Live `link_check.py --refresh` first refused a changed include-search
snapshot; the retry reports 591 stale or missing ledger objects (limit 50).
The live linking verdict is therefore UNKNOWN. A whole-tree rebuild is
outside this seat's scope; no linked-byte improvement is asserted.
