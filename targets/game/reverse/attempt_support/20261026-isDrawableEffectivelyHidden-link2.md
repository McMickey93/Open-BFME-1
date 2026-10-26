# Link queue #2: ?isDrawableEffectivelyHidden@Drawable@@QBE_NXZ (census 5cba370cb6)

Session 458 (a1, claude-opus-5-5), BFME 1 target evidence only (no BFME 2 donor:
the submodule clone stalls on this host).

## Facts

- Retail body 0x00410BA0, 29 B: `mov al,[ecx+0x3AD]; test; jne; mov al,[ecx+0x3AE];
  test; jne; xor eax,eax; ret; mov eax,1; ret`. Ledgered today as
  `?isDrawableEffectivelyHidden@Gen_00410BA0@@QBEHXZ` (int return) in
  `game/GameEngine/Source/Common/Bfme5TinyTwentySeven.cpp`.
- `tools/ilt_oracle.py check '?isDrawableEffectivelyHidden@Drawable@@QBE_NXZ' 0x00012E3B`
  -> CONFIRMED exact; the `QBEHXZ` (int) spelling -> CONTRADICTED. symbols.csv already
  pins the Drawable name at that ILT.
- The ZH spelling compiles byte-exact (29/29, no diffs) against 0x00410BA0:
  `Bool Drawable::isDrawableEffectivelyHidden() const { return m_hidden || m_hiddenByStealth; }`
  with `Bool` = bool, m_hidden at +0x3AD, m_hiddenByStealth at +0x3AE.
- The wrong COMDAT copies come from TUs that include the ZH `GameClient/Drawable.h`
  (inline body, ZH offsets 0x145/0x146) and call it out of line: objects of
  W3DModelDraw.cpp, W3DTankDraw.cpp, W3DTankTruckDraw.cpp, W3DTruckDraw.cpp,
  W3DScene.cpp, W3DView.cpp and Common/System/Radar.cpp each define
  `?isDrawableEffectivelyHidden@Drawable@@QBE_NXZ` reading [ecx+0x145]/[ecx+0x146]
  (checked with objdump on scoped builds of those 14 includers).

## Repair plan (not done: spreads past one session)

1. Correct the 0x00410BA0 identity to the Drawable name (add_match --replace-rva
   --correct-identity with this note) using the exact spelling above.
2. Repoint the consumers that call the int `Gen_00410BA0` view (W3DViewDrawablePostDraw.cpp,
   Rva00755170RenderSynchronization.cpp, W3DModelDraw_updateSubObjectsFromShroud.cpp,
   Rva0024BA00.cpp, Rva00249250HordeGarrisonHook.cpp and the rest that `rg Gen_00410BA0`
   lists) and re-verify each: their retail call sites test AL, so check that a bool
   return keeps their bytes.
3. The ZH-header copies stay wrong until those includers see BFME's layout (a
   Drawable.h layout adoption: full gate) or a TU-scoped out-of-line declaration.
   Linking preview is unknown here: no census index on this host.

## Resolved (session 461)

Landed in f50a955121: the 0x00410BA0 row is now ?isDrawableEffectivelyHidden@Drawable@@QBE_NXZ
(ilt_oracle CONFIRMED), and the nine Gen_00410BA0 consumers call the Drawable name.
