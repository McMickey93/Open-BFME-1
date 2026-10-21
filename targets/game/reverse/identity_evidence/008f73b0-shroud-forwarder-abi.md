# RVA 0x008F73B0: two-provider ShroudManager forwarder

The old `?m@Gen_008f73b0@@QAEXXZ` is a generated delegate-d8 skeleton,
not an independently established zero-argument member identity. The body is
exactly eight bytes: `8b 49 0c e9 b8 18 00 00`, loading the implementation
from this+0x0c and tail-jumping to RVA 0x008F8C70. The next body starts at
0x008F73C0, after padding; this agrees with the existing eight-byte row.

Independent caller evidence: byte-matched W3DGhostObjectManager::DoXfer
(RVA 0x006BDC10, 395 bytes) loads TheShroudManager, passes Object+0x64
and the ghost object's CDEProvider secondary base (or null), and calls
RVA 0x008F73B0 at body offset 0x184. The signature already pinned by this
caller is `?rva008F73B0@ShroudManager@@QAEXPAVCDEProvider@@0@Z`.

Independent callee evidence: the matched implementation
`?rva008F8C70@ShroudManagerImpl@@QAEXPAVCDEProvider@@0@Z` at RVA
0x008F8C70 reads two stack arguments, adjusts both provider virtual bases,
calls their virtual methods, and ends `ret 8` at +0x85. A zero-argument
signature cannot describe this forwarder's caller-visible ABI. The exact
semantic method name remains unknown, so the replacement retains its RVA.

BFME-2's Code/GameEngine/Source/GameLogic/Object/PartitionManagerShroudThunks.cpp
contains the analogous two-provider forwarder at RVA 0x00739760; its
implementation pointer sits at +0x10, while BFME-1 independently uses +0x0c.
This is a structural cross-check, not the source of BFME-1's offsets.

The explicit name-correction entry follows docs/naming_evidence.md:
`m` is being paired with an address-derived member because the ledger row
is replaced, not because an established semantic identity is being erased.
The guard reports this as a ledger-row pairing, so before_sha256 and
after_sha256 bind the exact removed/added ledger row text, as implemented
by name_regression.ledger_symbol_regressions. The additional old_source_sha256
and new_source_sha256 fields record the generated and native source snapshots. No generated
source is edited. Both the eight-byte forwarder and the 395-byte caller
are independently byte-verified by add_match/build.sh.
