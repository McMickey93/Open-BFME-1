# 0x006F5A90 is W3DDisplayStringManager::newDisplayString; 0x005A5AE0 is not

Before this change the ledger had two wrong names:

- `?newDisplayString@W3DDisplayStringManager@@UAEPAVDisplayString@@XZ` sat on
  0x005A5AE0 (774 B, an `__emit` lift).
- `?winCreate@GameWindowManager@@UAEPAVGameWindow@@PAV2@IHHHHP6A?AW4WindowMsgHandledType@@0III@ZPAVWinInstanceData@@@Z`
  sat on 0x006F5A90 (269 B, an `__emit` lift).

## 0x006F5A90

The ILT oracle confirms the newDisplayString name here.
`tools/ilt_oracle.py check ?newDisplayString@W3DDisplayStringManager@@UAEPAVDisplayString@@XZ 0x006F5A90`
reports CONFIRMED (re_attempts row of 2026-10-16). W3DDisplayStringManager's
vtable at VA 0x0111FF40 holds that body's ILT, 0x00038A32. The body follows the
matched `??_GW3DDisplayStringManager@@UAEPAXI@Z` at 0x006F5A60.

The bytes are Zero Hour's newDisplayString:

1. `operator new(0x210)` and the W3DDisplayString constructor.
2. A test of TheGlobalLanguageData's default display-string font (+0xAC name,
   +0xB0 size, +0xB4 bold).
3. A fallback to "Times New Roman" at 12.
4. A `setFont` vcall, then `DisplayStringManager::link`, then `return newString`.

The body ends in a plain `ret`. That refutes the winCreate name, which
declares nine arguments.

## 0x005A5AE0

ILT 0x0004A8BD contradicts the newDisplayString name here; it is in
`ilt_contradicted_baseline.txt`. The body calls
`SubsystemInterface::SubsystemInterface` and installs vtable 0x0110D580, so it
is a constructor. The DirectInputMouse constructor reaches it. `??0Mouse@@QAE@XZ`
is also CONTRADICTED at that ILT. Its identity stays open, so the row becomes
`?dup_005a5ae0@@YAXXZ` and its lift defines that name.

## Retired names

The rows change as follows:

- 0x006F5A90 retires `?winCreate@GameWindowManager@@UAEPAVGameWindow@@PAV2@IHHHHP6A?AW4WindowMsgHandledType@@0III@ZPAVWinInstanceData@@@Z`
  and takes `?newDisplayString@W3DDisplayStringManager@@UAEPAVDisplayString@@XZ`.
- 0x005A5AE0 retires `?newDisplayString@W3DDisplayStringManager@@UAEPAVDisplayString@@XZ`
  and takes `?dup_005a5ae0@@YAXXZ`.
