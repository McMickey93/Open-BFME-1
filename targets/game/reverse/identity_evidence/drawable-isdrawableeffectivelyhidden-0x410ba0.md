# Drawable::isDrawableEffectivelyHidden at 0x00410BA0 (29 B)

BFME 1 target evidence:
- Retail ILT thunk 0x00012E3B jumps to 0x00410BA0.
  `tools/ilt_oracle.py check '?isDrawableEffectivelyHidden@Drawable@@QBE_NXZ' 0x410BA0`
  reports CONFIRMED (exact, p_false 5.87e-04); the old placeholder
  `?isDrawableEffectivelyHidden@Gen_00410BA0@@QBEHXZ` is CONTRADICTED.
- symbols.csv already pins the Drawable name at the ILT (CanSelectDrawable
  retail ILT); matched callers (SelectionXlatCanSelectDrawable, W3DModelDraw,
  W3DTankTruckDraw, RTS3DScene, GameClient frustum) reference that name.
- Every caller tests only `al` after the call (callers cast the int view to
  char), consistent with a bool return.
- Body: two byte flags at +0x3AD/+0x3AE, return 1 if either is set.

Donor (Zero Hour, not BFME 1 proof): GeneralsMD Drawable.h:329
`inline Bool isDrawableEffectivelyHidden() const { return m_hidden || m_hiddenByStealth; }`.

Linking: link_queue row #2 (census 179d0eb281) lists three files whose only
blocker is this name: they call the Drawable name that no object defined.
