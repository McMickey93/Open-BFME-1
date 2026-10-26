# 0x00288280 is ??0BoneFXListInfo, not ??0DFX@DamageFX

The 16-byte body at 0x00288280 (`mov eax,ecx; xor ecx,ecx`, four zero stores
to +0x00/+0x04/+0x08/+0x0C, `ret`) zeroes an `AsciiString` slot followed by a
12-byte `{int; float; float}` block. That is `BoneFXListInfo::{boneName,
gameClientDelay}` in the flat 0x24-byte element view (onlyOnce at +0x1c,
pointer at +0x20), not `DamageFX::DFX::{m_amountForMajorFX,
m_majorDamageFXList, m_minorDamageFXList, m_damageFXThrottleTime}`.

Caller evidence (strongest kind): the sole referencing caller is the matched
`??0BoneFXUpdateModuleData` ctor at 0x00288340, whose `??_H` array
construction for the `m_fxList` `BoneFXListInfo` members reaches this body
through ILT slot 0x1E15. No DamageFX-amount context references it; no TU
spells `??0DFX@DamageFX` as a caller. The `??0DFX@DamageFX` object-symbol on
the retired gen-alias row was a skeleton heuristic without caller support.

Family evidence: the bodies at 0x002882A0/0x002882B0/0x002882D0/0x002882E0/
0x00288300 are the matching element dtor/ctor pairs for the three
`BoneFXUpdateModuleData` arrays (fxList, OCL, particleSystem), each reached
through its own ILT slot.

Consistency (not identity proof): `ilt_oracle.py check
'??0BoneFXListInfo@@QAE@XZ' 0x00288280` reports CONFIRMED (exact).
model=muse-spark, 2026-10-26.
