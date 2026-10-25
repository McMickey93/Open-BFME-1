# Complete the existing NaN ownership repair

BFME 1 commit cc6ad0fecc558948251588149ffb9fde5d1178a7 established
the existing matched four-byte union at VA 0112E8AC in
game/GameEngine/Source/Common/FloatConstantGetters.cpp. Retail .rdata is
0000A07F, the binary32 signaling-NaN payload 7FA00000. The union's integer
initializer preserves those bits; its float-member read reproduces the
seven-byte fld/ret getter at RVA 000B4A70. The existing data row and scoped
byte verification establish size, bits and operand identity independently
of any semantic name. No class or semantic identity is newly inferred.

The old integer spelling g_bfmeDefaultQA no longer occurs in tracked game/
or inputs/reference/shims/. Its remaining DIR32 reservation conflicts with
the existing matched owner. tools/dir32_record.py retire accepts its deletion
for that owner. No data row, pin or mapping is added; the payload, union,
function bodies, boundaries, ABI and compiler flags remain unchanged. The
provider comment documents its exact external symbol for the repair queue's
existing keyed source locator.

BFME 2 read-only revision 16c3ea885a293dafc872dd5b67a59fa92b1d6407
was searched for the old spelling, target cell and payload. Its
Code/GameEngineDevice/Source/MilesAudioDevice/MicrophoneSettingsConstructor.cpp
reads another already-owned 7FA00000 datum. Equal NaN bits do not establish
shared identity or ownership: no donor source, name, address or provider is
imported. The pinned BFME 1 donor reference remains unchanged.

Acceptance: repair_queue.py pass-test reports PASS and removes one keyed
exemption (1012 -> 1011). The provider verifies 17/17 functions, 5/5 data,
ten floating constants and 15 DIR32 references. Normal builds of
BfmeOneHundredEight.cpp and AudioSettingsCtorThunk.cpp verify 8/8 functions
and 49 DIR32 references. Every build has zero body exemptions. CSV integrity,
declared-unmatched and whitespace checks pass.

link_check.py FloatConstantGetters.cpp --compile-limit 0 is run before and
after; both display 119 -> 119 linked bytes with LINKED PREVIEW UNKNOWN.
Stale/missing census objects prevent a known linked-byte improvement.
Exact C++ coverage grows by zero bytes. The measured improvement is one fewer
gate exemption and one fewer obsolete address record, completing the existing
NaN ownership prerequisite.
