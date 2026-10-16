# 0x00414E40: Drawable::drawContained takes no argument in BFME

The 833-byte body at 0x00414E40 was ledgered as
`?drawContained@Drawable@@AAEXPBUIRegion2D@@@Z`, the Zero Hour signature with
a health-bar region pointer. Retail exits with a plain `ret` and reads the
drawable's own region at +0x3C4, as the matched no-argument drawBombed,
drawHealing and drawEnthusiastic do.

Retail reaches the body through ILT 0x00012E2C, which the matched
`Drawable::drawIconUI` stage table (Drawable_drawIconUI_Dispatch.cpp,
`j_00012e2c`) uses. `tools/ilt_oracle.py check '?drawContained@Drawable@@AAEXXZ' 0x12e2c`
reports CONFIRMED (exact); the one-argument decoration is CONTRADICTED.
The body is Zero Hour's drawContained with BFME's two pip rows.
