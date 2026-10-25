# Blocked GameSpy callback ownership retirement

Gate-debt fallback; all attempted source comments, record retirements and
baseline removals were reverted. No callback body or pin changed.

## Independent BFME 1 evidence

| Existing matched owner | RVA / extent | Obsolete recorded identity |
| --- | --- | --- |
| `_piChangeNickCallback` | `0x0085FCD0` / 89 B | `_piChangeNickCallbackA` |
| `_piAuthenticateCDKeyCallback` | `0x00860020` / 56 B | `_piAuthenticateCDKeyCallbackA` |
| `_piUserChangedNickCallback` | `0x0086B810` / 68 B | `_piChannelUserChangedNickA` |

The first two providers are in
`game/GameEngine/Source/GameNetwork/GameSpy/peer/peerOperations.c`; the third
is `peerUserChangedNickCallback.c` in that directory. Matched operation
constructors `piNewChangeNickOperation` (RVA `0x0085FD30`, 69 B) and
`piNewAuthenticateCDKeyOperation` (`0x00860060`, 69 B), in
`peerOperationsListGroupRooms.cpp`, pass the first two addresses as Chat
completion callbacks. Matched `piSetChannelCallbacks` (`0x0086BA10`, 94 B),
in `peerGlobalCallbacksSetChannel.c`, installs the third in userChangedNick.
These established consumers carry identity evidence beyond equal bytes.

`callees.py` independently confirms the expected retail sequences:
`piAddChangeNickCallback` + `piRemoveOperation`,
`piAddAuthenticateCDKeyCallback` + `piRemoveOperation`, and
`piRoomToType` + `piPlayerChangedNick` + `piAddPlayerChangedNickCallback`.
All three old records have zero active source mentions, including bare names.
The official retirement guard accepts each replacement by its existing matched
non-generated function row. Existing extents and cdecl ABI were preserved.

## Exact refusal and restoration

Added temporary comments spelling each decorated C-linkage owner, because
`repair_queue.locate_source` cannot locate `_pi...` from the ordinary C
identifier alone. Retired the three records via `dir32_record.py retire`.
All three keyed `repair_queue.py pass-test LINE` commands passed the providers:
8/8 rows twice in peerOperations and 1/1 in peerUserChangedNickCallback,
with zero body-guard findings.

The independent consumer gate then passed 23/23 matched rows but failed DIR32
for exactly the three function pointers. For example:

```
_piNewChangeNickOperation +0x30: _piChangeNickCallback:
nothing in the ledger owns 0x00C5FCD0. Give the datum a data row first
(tools/add_data_match.py), or use an address name (g_Va<VA>)
```

The other sites were `piNewAuthenticateCDKeyOperation +0x30` at
VA `0x00C60020` and `piSetChannelCallbacks +0x35` at VA `0x00C6B810`.
Thus the retirement guard accepts the matched code identity while the byte
verifier does not accept it as an unrecorded DIR32 owner. This is a
`false-reject dir32` blocker; no data rows, pins, aliases, gate edits or other
workarounds were introduced. Restored both sources, all three records and all
three baseline exceptions to the verified parent state. Do not repeat this
retirement until the two ownership checks agree.

## Donor and build context

Read-only BFME 2 revision `16c3ea885a293dafc872dd5b67a59fa92b1d6407`
has the same provider paths and old references in
`Code/GameEngine/Source/GameNetwork/GameSpy/peer/peerOperationsListGroupRooms.c`.
Its provider files use `/alternatename` directives to bind the old spellings.
Those are forbidden in this seat and were not imported. BFME 1 consumers
already reference the matched providers directly, so no donor source, layout,
name, address or linker directive is needed or adopted.

BFME 1 parent `98463eaba5`, MSVC 7.1, existing source flags and GameSpy shim
includes unchanged. No compiler variants or body reconstruction were tried.
Useful artifacts are the exact refusal and reproduction above; no candidate
bank is necessary because all C bodies already match. t=6min.
