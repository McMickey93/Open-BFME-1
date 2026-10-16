# 0x00420AC0 Drawable::drawIconUI: which member each icon-group thunk reaches

drawIconUI calls one incremental-link thunk per stage (drawIconUI2/3 in the
same TU spell the same thunks as j_XXXXXXXX). `tools/ilt_oracle.py check`
over the drawIconUI member names (2026-10-16):

| group | thunk      | lands      | CONFIRMED (exact)  | was spelled      |
|-------|------------|------------|--------------------|------------------|
| 1     | 0x0003D514 | 0x0041A780 | drawEnthusiastic   | drawHealing      |
| 1     | 0x0002F6E9 | 0x00418490 | drawDisabled       | drawBombed       |
| 1     | 0x00038BAE | 0x00414BE0 | drawAmmo           | drawEnthusiastic |
| 1     | 0x00012E2C | 0x00414E40 | drawContained      | drawDemoralized  |
| 2     | 0x00038AAA | 0x00420670 | drawVeterancy      | drawDisabled     |
| 3     | 0x00022782 | 0x00410F90 | (none)             | drawAmmo         |

The rows at 0x0041A780 (drawEnthusiastic), 0x00414BE0 (drawAmmo) and
0x00414E40 (drawContained) already carry the confirmed names, so the caller
now spells those three. drawAmmo has one body, so the group-3 thunk (no
confirmed name) calls the address-named Rva00410F90::method.

Left for a name correction (not changed here): row 0x00418490 is named
drawBombed but its thunk confirms drawDisabled; the group-2 thunk lands in
the unconverted dump 0x00420670 and confirms drawVeterancy.

With the three callers respelled, link_check drops drawIconUI's comdat and
selected "not retail's body" findings.
