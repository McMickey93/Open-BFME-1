# 0x00418490 is Drawable::drawDisabled, not drawBombed

- `tools/ilt_oracle.py check '?drawDisabled@Drawable@@AAEXXZ' 0x2F6E9`:
  CONFIRMED (exact, p_false 1.96e-04); `?drawBombed@Drawable@@AAEXXZ` at the
  same thunk: CONTRADICTED. j_0002f6e9 jumps to 0x00418490.
- The body creates, draws or clears icon slot 6. Zero Hour's
  DrawableIconType puts ICON_DISABLED at index 6 (DEFAULT_HEAL,
  STRUCTURE_HEAL, VEHICLE_HEAL, DEMORALIZED, BOMB_TIMED, BOMB_REMOTE,
  DISABLED).
- Group 2 of drawIconUI then calls thunk 0x00038AAA, where
  `?drawVeterancy@Drawable@@AAEXXZ` is CONFIRMED (exact, p_false 6.52e-04)
  and drawDisabled is CONTRADICTED; it lands in the unconverted dump
  0x00420670.
See also 00420ac0-drawiconui-group-callees.md.
