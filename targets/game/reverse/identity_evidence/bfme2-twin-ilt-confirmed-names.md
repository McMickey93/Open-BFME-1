# Names carried over from byte-identical Open-BFME-2 twins, confirmed by BFME1's ILT

Method (2026-10-21 BFME2 -> BFME1 sweep): every matched Open-BFME-2 body with
real source was masked (REL32/DIR32 operands) and searched in BFME1 retail
.text; a body is used only when it has exactly one placement and every
unmasked byte agrees. Where the BFME1 row at that placement carried a
placeholder name, the BFME2 decorated name was checked against BFME1's own
incremental-link thunk table with `tools/ilt_oracle.py check`: the rows
below are CONFIRMED, i.e. the decorated name sorts into the narrow window of
the thunk slot that jumps to this body (false-fit probability ~1e-3 each).
Two independent witnesses therefore agree: identical code in BFME2 under
that name, and BFME1's linker ordering of the same name.

| BFME1 RVA | size | name | p_false |
|---|---|---|---|
| 0x000A22F0 | 63 | ?zeroOutStats@StatsCollector@@AAEXXZ | 9.8e-04 |
| 0x004902A0 | 23 | ??1ProgressIndicator@@UAE@XZ | 6.5e-04 |
| 0x00123780 | 27 | ??0AssistedTargetingUpdateModuleData@@QAE@XZ | 1.2e-03 |
| 0x00700240 | 20 | ??0MouseThreadClass@@QAE@XZ | 7.2e-04 |
| 0x0034F780 | 39 | ??4ObjectTypes@@QAEAAV0@ABV0@@Z | 9.8e-04 |
| 0x0040FF90 | 19 | ?removeLastChar@DisplayString@@UAEXXZ | 1.4e-03 |
| 0x007BA110 | 32 | ??0Geometry@@QAE@XZ | 4.6e-04 |
| 0x001246D0 | 16 | ??0OathbreakersFadeAwayBehaviorModuleData@@QAE@XZ | 7.2e-04 |
| 0x00516660 | 25 | ?GadgetTextEntryHasSelection@@YA_NPAVGameWindow@@@Z | 9.1e-04 |
| 0x007BBDB0 | 17 | ?Get_Key@W3DShadowGeometry@@UAEPBDXZ | 3.3e-04 |
| 0x00161220 | 50 | ??0TeamInQueue@@QAE@XZ | 3.3e-04 |
| 0x006C5310 | 21 | ?Set_Cull_Mode@ShaderClass@@QAEXW4CullModeType@1@@Z | 2.6e-04 |

Each landing still compiles the named body and byte-verifies it at the
address; field layouts come from the BFME1 TU that already models the class.
