# Complete seven existing matched-data ownership repairs

This homogeneous batch completes existing ownership prerequisites by removing
unused competing DIR32 records and keyed exemptions. Provider comments give the
existing external symbols to repair_queue.py's keyed source locator. No body,
identity, boundary, initializer, name, layout, ABI, compiler flag, data row or pin
changes. The sanctioned dir32_record.py retire command checks every deletion.

Independent BFME 1 evidence and earlier ownership commits:

* VA 0108132C, 32 bytes, Rva000C2A00Get.cpp (ba933c6da5): the matched getter
  returns the FieldParse table passed by INIWaterTextureList to initFromINI.
  Retail holds Texture, parseAsciiStringVectorAppend, zero, offset eight and
  a zero terminator. The old char-array record was already retired; its keyed
  exemption remained. No new record retirement is needed for this item.
* VA 012B9469, one byte, MainMenuUtils.cpp: the existing Bool isHttpOk has the
  retail initializer 01. HTTPThinkWrapperBFME's matched 00630450 body reads
  that byte before its ghttpThink tail jump. The previous ownership repair
  exported the existing definition; 70187250e7 retained the retail wrapper.
  The unused bfmeHttpOk reservation remained. Other active bool conflicts
  in this provider are outside this batch and remain unchanged.
* VA 012F1098, four bytes, PathfindCellInfoAcquire.cpp (917cdb01e0): a zero
  dword incremented by the acquire/hierarchical-cell/Bfme5EightyFive paths
  and decremented by MixFileInfoBuffer_releaseInto. The existing address name
  replaces three unused spellings. The adjacent pool's active conflicts are
  deliberately left intact.
* VA 012F496C, four bytes, ShowMapTransferLoadScreen.cpp (18a8ddac2d): the
  singleton pointer stored by 00510A10, deleted and cleared by 0050FE20,
  cleared by 0050FD90 and read by 0066CE50/0066CE60. Its zero initializer
  and address-derived identity are unchanged; four obsolete names remain.
* VA 012F9808, 84 bytes, Rva00C6C4F0Init.cpp (43cb525621): initializer
  00C6C4F0 calls ILT 0003CDD0 and registers shutdown 00C709C0. The matched
  W3DMouse constructor's handle at +50 fixes the existing 54-byte extent.
  No EA global name is established. Two obsolete reservations remain.
* VA 01306C6C, 16 bytes, Rva00C6C5A0Init.cpp (09c69caad6): zero-filled
  vptr-plus-three-int object; font consumers use +4/+8/+C, initializer
  00C6C5A0 registers 00C70AD0. The existing RvaSimpleDynVec view is retained;
  two obsolete names remain. No class or field identity is newly inferred.
* VA 01337864, four bytes, BfmeConv2012.cpp (9f9be34e1e): zero callback
  cell installed through slot 12 and called cdecl with two const char pointers
  by bfmeReportEAW and Rva008CE1E0StoreMember. Two unused competing spellings
  remain. No descriptive callback name is inferred.

BFME 2 read-only revision 16c3ea885a293dafc872dd5b67a59fa92b1d6407
was searched narrowly for these families and old names. Reviewed paths include
Code/GameEngine/Source/GameNetwork/GameSpy/MainMenuUtils_hasWriteAccess.cpp,
Code/GameEngineDevice/Source/W3DDevice/GameClient/W3DMouse.cpp,
Code/GameEngineDevice/Source/W3DDevice/GameClient/GUI/W3DFontCharsCache.cpp
and its history, and the WaterTextureList declarations in INITerrain.cpp and
Rva007ABBF6BlockParseInits.cpp. The donor HTTP flag is static, its mouse object
has a different exported spelling, and its font-cache name is explicitly
descriptive. These establish no BFME 1 address or ownership change. No donor
body, name, layout, global, address or include path is imported; BFME 1's own
ownership commits and target evidence carry this repair. The pinned submodule
is unchanged.

Acceptance: all seven repair_queue.py keyed pass-test calls report PASS and
remove seven exemptions (1011 -> 1004). Sanctioned retirements remove fourteen
obsolete records (17319 -> 17305). Provider builds verify 15/15 functions,
15/15 data rows and 49 DIR32 references. One normal ./build.sh invocation on
the seventeen matched consumer units verifies 206/206 functions, 23 string
literals, twelve float constants and 392 DIR32 references. Every build has
zero body exemptions. CSV integrity, declared-unmatched checks and whitespace
checks pass. MainMenuUtils' two existing unclaimed definitions are reported
by the declaration checker; no definition or exemption is added here.

Scope logs: build/owner-batch-pass-tests.log, owner-batch-consumers.log and
owner-batch-check-csv.log. Pre-change link previews are in owner-*-link-before.log
and owner-batch-link-before.log. Missing/stale census objects leave selection
unknown; MainMenuUtils additionally retains existing unresolved providers and
a duplicate AsciiString::trim. Before-change displayed linked bytes by VA:
0108132C=6, 012B9469=0, 012F1098=163, 012F496C=0, 012F9808=22,
01306C6C=24, 01337864=136. No new linked or exact C++ bytes are claimed.

The combined after-change preview (owner-batch-link-after.log) displays the
same 351 -> 351 bytes. Five providers remain UNKNOWN and MainMenuUtils retains
its blockers. Refreshing the matched consumer objects exposes an additional
known blocker for ShowMapTransferLoadScreen: the selected
??0BfmeAptScreenMapTransfer@@QAE@PAX@Z definition is not retail's. Its earlier
preview was unknown. The constructor and all executable sources are unchanged;
this batch does not reconcile that provider or claim the caller links. Consumer
byte agreement alone does not prove the selected constructor's identity.
