# Gate debt repair: stdio_istreambuf vtable

Retired baseline finding for `??_7stdio_istreambuf@_SgI@@6B@` at 0x0112F27C.

| Retail VA | Retired baseline finding | Fix / Evidence |
| --- | --- | --- |
| 0x0112F27C | `??_7stdio_istreambuf@_SgI@@6B@` | Retail vtable verified via primary destructor in `game/stlport/StdioIstreambufDestructor.cpp` |

Keyed `repair_queue.py pass-test` passed and removed the baseline line from `body_guard_baseline.csv`.
Zero baselined findings.
1 exception retired; no escape hatches added.
