# W3DView::setZoom / setHeightAboveGround were swapped

- `0x00742E60` (218 B) had landed as `?setZoom@W3DView@@UAEXM@Z`.
  `tools/ilt_oracle.py check '?setZoom@W3DView@@UAEXM@Z' 0x00742E60` is
  CONTRADICTED, while `?setHeightAboveGround@W3DView@@UAEXM@Z` at 0x00742E60 is
  CONFIRMED (p_false 7.8e-04).
- `0x00742F70` (185 B, the former gen_asm dump `?d_00742f70`):
  `?setZoom@W3DView@@UAEXM@Z` is CONFIRMED (p_false 2.0e-04);
  `?setHeightAboveGround@W3DView@@UAEXM@Z` is CONTRADICTED. A sweep of every
  `void (Real)`-shaped View/W3DView method name from the Zero Hour headers
  fits exactly one name at 0x00742F70: setZoom.
- The fields agree with Zero Hour's View member order (`m_maxZoom`,
  `m_minZoom`, ..., `m_zoom`, `m_heightAboveGround`): 0x00742F70 stores its
  argument at +0x3C and clamps it between +0x38 (min) and +0x34 (max), as ZH
  `W3DView::setZoom` clamps `m_zoom` between `m_minZoom` and `m_maxZoom`;
  0x00742E60 stores at +0x40, the slot after it.
- Both bodies are byte-exact under the corrected names (scoped build).
