# 0x00477B30: not Object::getAI; address-derived name

- Retail 0x00477B30 (7 B): `mov eax,[ecx+0x19C]; ret`. Its only ILT jmp
  (0x00002784) has no rel32 callers, so no matched caller names it.
- The old row `?getAI@Object@@QAEPAVAIUpdateInterface@@XZ` came from
  Weapon.cpp's Zero Hour Object.h layout (m_ai at +0x19C). It sat in
  ilt_contradicted_baseline.txt, and `tools/ilt_oracle.py check` contradicts
  the name at 0x00477B30 (p_false=1.50e-03, outside every window of slots
  1257-1279).
- The same check CONFIRMS the name exactly at 0x000E59A0
  (`mov eax,[ecx+0x204]; ret`, ILT 0x0001D6E7, also uncalled), the offset
  BFME's own Object views use (AITNGuardIdleStateOnEnter.cpp, AIDockState.cpp,
  PathfinderDestinationWork.cpp and six more emit that body). The const
  spellings `QBEPAV`/`QBEPBV` are contradicted at 0x000E59A0.
- Nothing proves the class or method of 0x00477B30, so it lands as
  `Rva00477B30::get` in game/GameEngine/Source/GameLogic/Object/Rva00477B30.cpp,
  and 0x000E59A0 takes the real name (link queue #20).
