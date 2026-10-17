# 0x0058C4C0 is the four-UnicodeString record's destructor, not UpgradeMuxData's

The 102-byte body at 0x0058C4C0 was matched as `??1UpgradeMuxData@@QAE@XZ`
(zh_sweep packet). Its own source already conceded the bytes do not support
that name: it destroys four four-byte members at +0x0C/+0x08/+0x04/+0x00, each
through the UnicodeString release body 0x008881D0, whereas Zero Hour's
UpgradeMuxData holds four 12-byte `std::vector<AsciiString>` lists plus FX data.

Evidence for the four-string record instead:

- the matched copy constructor `??0Rva0058BE30FourString@@QAE@ABV0@@Z`
  (0x0058BE30, Rva0058BE30FourStringCopy.cpp) copies exactly four
  UnicodeStrings and a trailing word of the same record; it sits 0x690 bytes
  before this body, in the GUI/Palantir block (0x0058xxxx-0x0059xxxx);
- every caller is in that block and deletes a held pointer of this record
  through ILT 0x0003FA7B (`jmp 0x0058C4C0`): 0x00593E60 (HelpBox record
  update, `delete m_ptrC` of the 0x0058BE30-copied record), 0x00592640,
  0x005929E0 and BfmeConv596; symbols.csv already pins
  `??1Rva0058BE30FourString@@QAE@XZ` at 0x0003FA7B;
- the real UpgradeMuxData methods (performUpgradeFX 0x002D9B30,
  muxDataProcessUpgradeRemoval 0x002D9C40, getUpgradeActivationMasks
  0x002D9FF0) live in the Thing module block, nowhere near this body.

The name is address-derived (the record's semantic identity is unproven);
bytes are unchanged.
