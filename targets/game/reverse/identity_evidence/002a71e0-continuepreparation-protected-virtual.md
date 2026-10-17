# 0x002A71E0 is SpecialAbilityUpdate::continuePreparation as a protected virtual (MAE)

The matched 681-byte body at 0x002A71E0 was spelled
`?continuePreparation@SpecialAbilityUpdate@@IAE_NXZ` (protected, non-virtual).
Every retail caller reaches it through ILT 0x0002FE05, and the incremental-link
thunk table decides the spelling:

    py -3 tools/ilt_oracle.py check '?continuePreparation@SpecialAbilityUpdate@@MAE_NXZ' 0x2A71E0
    CONFIRMED  p_false=2.61e-04  (exact)
    py -3 tools/ilt_oracle.py check '?continuePreparation@SpecialAbilityUpdate@@IAE_NXZ' 0x2A71E0
    CONTRADICTED  p_false=2.61e-04  (outside every window of the target's slots 38400:23363-23366)

The IAE spelling was already listed in `ilt_contradicted_baseline.txt`, and
symbols.csv pins the MAE spelling at ILT 0x0002FE05. Zero Hour declares
`Bool continuePreparation()` under `protected:` (non-virtual) in
SpecialAbilityUpdate.h; BFME made it virtual, which the matched
GloriousChargeUpdate (0x0025E820) and RousingSpeechUpdate (0x00264B20)
overrides show: both tail-jump to the base through the same ILT under the MAE
spelling.

The body bytes are unchanged: the defining TU now declares the member
`protected: virtual`, which puts the vptr where the old `void *m_vtable`
placeholder sat. The two direct callers that used the IAE spelling
(BfmeConv768.cpp, S3StateTwoGuards.cpp) call it qualified, so the call stays a
direct jump.
