# 0x0047D2B0: gogoGadgetSlider under an address-derived class

The body at 0x0047D2B0 (471 bytes) is slot 20 of GameWindowManager's vtable
(VA 0x010F8B60). It sits between the matched gadget factories at 0x0047D090
and 0x0047D500. Its behaviour is Zero Hour's `GameWindowManager::gogoGadgetSlider`:

1. It sets a status bit on the creation descriptor.
2. It creates the window through slot 29.
3. It installs the slider's user data.
4. It builds the thumb through `gogoGadgetPushButton` (slot 14) with a second
   descriptor on the stack.
5. It applies the default look through slot 25.

The decoration is not Zero Hour's. Retail ends with `ret 0x10`: four stack
arguments (BFME's creation descriptor, SliderData, font, visual), not ten.
ILT slot 11655 contradicts both spellings on `GameWindowManager`:

- the Zero Hour ten-argument
  `?gogoGadgetSlider@GameWindowManager@@UAEPAVGameWindow@@PAV2@IHHHHPAVWinInstanceData@@PAU_SliderData@@PAVGameFont@@_N@Z`
  (its pin was retired in 2584af1519);
- the descriptor spelling on `GameWindowManager` (re_attempts, 2026-10-16).

The true decoration of BFME's class is unproven. The class therefore keeps an
address token: `Rva0047D2B0GameWindowManager::gogoGadgetSlider`. The
gogoGadgetTextEntry sibling at 0x0047FCF0 is named the same way
(`Rva0047FCF0GameWindowManager`). Every call in the body is virtual, so the
class name changes no byte.
