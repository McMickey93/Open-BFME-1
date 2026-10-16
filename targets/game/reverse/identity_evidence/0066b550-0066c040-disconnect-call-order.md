# 0x0066B550 / 0x0066C040: which DisconnectManager callee each call site reaches

Rows: `sendPlayerDestruct` 0x0066B550 (thunk 0x000201F3) and
`disconnectPlayer` 0x0066C040 (thunk 0x0004B0B0). The 0x0066C040 body calls
`ConnectionManager::disconnectPlayer`, as Zero Hour's `disconnectPlayer` does.

`tools/ilt_oracle.py check` (2026-10-16):
- `?sendPlayerDestruct@DisconnectManager@@IAEXHPAVConnectionManager@@@Z` at
  0x000201F3: CONFIRMED (exact); at 0x0004B0B0: CONTRADICTED.
- `?disconnectPlayer@DisconnectManager@@IAEXHPAVConnectionManager@@@Z` at
  0x0004B0B0: CONFIRMED (exact); at 0x000201F3: CONTRADICTED.

The symbols.csv pins had the two names on the opposite thunks, so the
matched callers spelled them the wrong way round:
- `updateDisconnectStatus` (0x0066C3B0) calls 0x000201F3 then 0x0004B0B0:
  BFME sends the player destruct before it disconnects the player (Zero
  Hour has the opposite order).
- `processDisconnectPlayer` (0x0066C760) calls 0x0004B0B0, i.e.
  `disconnectPlayer`, as in Zero Hour (DisconnectManager.cpp line 301).

With the callers corrected and the pins swapped, link_check drops the
"not retail's body" comdat/selected findings for both callers.
