# 0x001BD400: not Object::getDisabledFlags; address-derived name

- Retail 0x001BD400 (15 B): `mov ecx,[ecx+0x1A4]; mov eax,[esp+4];
  mov [eax],ecx; ret 4`: a const getter returning a 4-byte non-POD value from
  this+0x1A4 through a hidden return slot. Its only ILT jmp (0x00023907) has
  no callers, so no matched caller names it.
- The old row `?getDisabledFlags@Object@@QBE?AV?$BitFlags@$0N@@@XZ` was only
  emitted by Object.cpp's non-retail ZH copy of Object::clearDisabled (link
  queue #15), which is removed. Its name was already in
  ilt_contradicted_baseline.txt, and `tools/ilt_oracle.py check` contradicts
  every `BitFlags<1..15>` decoration of getDisabledFlags@Object, and every
  const by-value getter of ZH Object.h with BitFlags<1..129>.
- Nothing else proves the class or method, so the body lands as
  `Rva001BD400::get` in game/GameEngine/Source/GameLogic/Object/Rva001BD400.cpp.
