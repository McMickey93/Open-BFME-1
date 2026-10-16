# 0x002F22A0: ScriptActions team-home group action keeps its address

The 266-byte body at 0x002F22A0 (ret 4 at +0x105, int3 after) was ledgered as
`?doPlaySoundEffect@ScriptActions@@IAEXABVAsciiString@@@Z`, from a naked
`__emit` lift. The bytes do not play a sound: they call ScriptEngine slot
+0x44 (getTeamNamed, by-value AsciiString plus `false`), `AI::createGroup`
(0x0014C630), `Team::getTeamAsAIGroup` (0x000F45A0), `Team::countObjects`
(0x000F2770) with two copies of the empty KindOf mask, `Team::getHomePosition`
(0x000F3500), then the AI-group helper 0x0015A190 (count > 1) or its packet
fallback 0x00159AD0.

Retail reaches the body through the incremental-link thunk at 0x00041E93
(`jmp 0x002F22A0`); `tools/callers_of.py` shows executeAction (0x00303BF0) as
its caller, so the ScriptActions receiver and `ret 4` one-reference-argument
signature stand.

`tools/ilt_oracle.py check '?doPlaySoundEffect@ScriptActions@@IAEXABVAsciiString@@@Z' 0x41e93`
reports CONTRADICTED (p_false 5.87e-04, outside every window of slot 53174,
buckets 31298-31306). The same check over all 380 `do*` ScriptActions method
names found in the Zero Hour ScriptActions.h, the repo's ScriptActions sources
and the ledgers, each with this signature, found none that fits. Zero Hour has
no action using getHomePosition or countObjects, so there is no twin. The real
name is unknown, and per AGENTS.md the row becomes
`?rva002F22A0@ScriptActions@@IAEXABVAsciiString@@@Z` (class, access and
signature unchanged).
