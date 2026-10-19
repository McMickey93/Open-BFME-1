# BuildingBehaviorModuleData::~BuildingBehaviorModuleData at 0x001F6D40

The 90-byte body at 0x001F6D40 was ledgered as the placeholder
`??1BfmeOwnerBX@@QAE@XZ` (Common/BfmeOwnerDtorBX.cpp), so the pinned
`??1BuildingBehaviorModuleData@@UAE@XZ` (ILT 0x00016A13) had no definition
(link queue rank 165, 156 B; BuildingBehaviorModuleDataCtor.cpp).

- ILT 0x00016A13 jumps to 0x001F6D40. Its only rel32 caller is 0x001F6D13,
  inside the matched `??_GBuildingBehaviorModuleData@@UAEPAXI@Z` 0x001F6D10.
  That is slot 0 of the class's own vtable 0x00CA2C88, which the matched
  constructor 0x001F6C70 installs. A scalar deleting destructor calls the
  complete destructor of its own class.
- The body matches the ctor's layout: the vector<AsciiString> at +0x18 (the
  three words the ctor zeroes) is destroyed through ILT 0x00026AB2 (pinned
  `??1?$vector@VAsciiString@@...`). The four AsciiStrings at +0x08 go through
  the eh vector destructor iterator with the AsciiString dtor ILT 0x0000D828,
  and the Snapshot vtable 0x00C73744 is restored last.
- Open-BFME-2's matched `??1BuildingBehaviorModuleData@@UAE@XZ` 0x004564E6
  (58 B) does the same: a four-element name array via the eh vector
  destructor iterator, then a Snapshot vtable restore with no base call.

## Its unwind funclet 0x00C0AE48

`?dup_00C0AE48@@YAXXZ` (22 B, `$L889` of the placeholder TU, parent
`??1BfmeOwnerBX@@QAE@XZ`) is this destructor's state-1 cleanup. The parent's
prologue pushes handler 0x00C0AE5E, and the 22 bytes end at that handler.
The new TU emits it as `$L4917` at the same place: offset 8 of the funclet
section, 22 bytes before `__ehhandler$??1BuildingBehaviorModuleData@@UAE@XZ`.
It moves with its parent as `uw_00c0ae48`.
