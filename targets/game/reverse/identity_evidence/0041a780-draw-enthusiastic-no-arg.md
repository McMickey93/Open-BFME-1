# 0x0041A780: Drawable::drawEnthusiastic takes no argument in BFME

The 511-byte body at 0x0041A780 was ledgered as
`?drawEnthusiastic@Drawable@@AAEXPBUIRegion2D@@@Z`, the Zero Hour signature
with a health-bar region pointer. Retail exits with plain `ret` (no stack
argument) and reads the drawable's own region at +0x3C4/+0x3CC/+0x3D0, as the
matched no-argument drawBombed (0x00418490) and drawHealing (0x0041A530) do.

Retail reaches the body through ILT 0x0003D514, which the matched
`Drawable::drawIconUI` (0x00420AC0) calls in its icon group 1 between
drawBombed and drawDemoralized, declaring `void drawEnthusiastic();`.
`tools/ilt_oracle.py check '?drawEnthusiastic@Drawable@@AAEXXZ' 0x3d514`
reports CONFIRMED (exact); the old one-argument decoration and the
`QAE`/`IAE` access variants are CONTRADICTED. The row takes the confirmed
decoration.
