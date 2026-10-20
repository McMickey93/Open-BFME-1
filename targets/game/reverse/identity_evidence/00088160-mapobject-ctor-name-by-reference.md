# 0x00088160: BFME's MapObject constructor takes the name by reference

The ledger row named the 386-byte body at `0x00088160` with Zero Hour's
signature, `MapObject(Coord3D, AsciiString, Real, Int, const Dict *, const ThingTemplate *)`
(`??0MapObject@@QAE@UCoord3D@@VAsciiString@@MHPBVDict@@PBVThingTemplate@@@Z`).
The class and member identity are unchanged (the body installs vtable
`0x0107C7E0`, which the matched destructor `0x00088350` also installs, and
the matched `MapObject::duplicate` at `0x00089390` allocates `0x60` bytes and
calls it). Only the second parameter's type is corrected.

Retail evidence (`inputs/baselines/bfme1/retail-1.03-unpacked`, RVA = VA - 0x400000):

- The matched caller `MapObject::duplicate` (`0x00089390`) builds the argument
  list as `push tt; push &m_properties; push flags; push angle;
  lea ecx, [esi+0x14]; push ecx; sub esp, 0xC (Coord3D by value)` and then
  calls the constructor through ILT `0x0001230A`. The name argument is the
  ADDRESS of the source object's `m_objectName` (`+0x14`), not a copy-constructed
  `AsciiString`: a by-value class argument would be built in place with the
  `StringBase<char>` copy constructor, and there is none.
- The constructor itself never releases a by-value name parameter. It loads the
  parameter slot (`mov eax, [esp+0x30]`, the address) into EAX for the
  file-static `validateName` (`0x00088140`, landed with a
  `const AsciiString &` parameter received in EAX) and reuses the now-dead
  parameter slot as `validateName`'s return slot (`lea esi, [esp+0x30]`).
- `symbols.csv` already pins the same ILT under a view spelling with the
  by-reference parameter:
  `??0Rva0041230aMapObject@@QAE@VVector3@@ABVAsciiString@@MHPBVDict@@PBVThingTemplate@@@Z`.

The clean C++ with `const AsciiString &name`
(`game/GameEngineDevice/Source/W3DDevice/GameClient/WorldHeightMapValidateName.cpp`)
compiles to all 386 bytes, exact modulo relocations, so the corrected symbol is
`??0MapObject@@QAE@UCoord3D@@ABVAsciiString@@MHPBVDict@@PBVThingTemplate@@@Z`.
