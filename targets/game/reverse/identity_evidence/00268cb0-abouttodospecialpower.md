# 0x00268CB0 is SpecialPowerModule::aboutToDoSpecialPower, not a module-data destructor

The row claimed `??1PlayerHealSpecialPowerModuleData@@UAE@XZ` for a 379-byte
naked lift. Retail refutes a destructor: the body ends `ret 4` (one stack
argument) and installs no vtable.

- Body (tools/dis_retail.py 0x00268CB0 379): `[this+4]` module data,
  `[this+8]` Object. It calls `SpecialPowerTemplate::getName` (0x00098F80) on
  module data +8, `Object::getControllingPlayer` (0x001BE3F0) and reads
  Player +0x24, then calls TheScriptEngine (0x012F076C) vtable +0x8C with
  (playerIndex, name, Object +0x74 id): Zero Hour's
  `notifyOfTriggeredSpecialPower` call. It copy-constructs the template's
  final-override +0x24 sound (`AudioEventRTS` copy ctor 0x000B2FB0), calls
  `setObjectID` (0x000B2250) and TheAudio (0x012ED668) vtable +0x44; when the
  argument is non-null it does the same for +0x94 with `setPosition`
  (0x000B2210) and `setPlayerIndex` (0x000B23C0). This is ZH
  `SpecialPowerModule::aboutToDoSpecialPower(const Coord3D*)` with the EVA
  block removed. +0x24/+0x94 are the getInitiateSound/getInitiateAtTargetSound
  offsets the matched accessors 0x00268890/0x002688C0 pin.
- Neighbours: it sits between `SpecialPowerModule::startPowerRecharge`
  (0x00268BA0) and `SpecialPowerModule::~SpecialPowerModule` (0x00268F30).
- Caller: the matched `PlayerHealSpecialPower` body 0x00263CA0 calls ILT
  0x00046C13 (-> 0x00268CB0) at +0x46 with ECX = interface - 0x10 (module
  base) and its location argument.
- ILT: `tools/ilt_oracle.py check '?aboutToDoSpecialPower@SpecialPowerModule@@IAEXPBVCoord3D@@@Z' 0x00268CB0`
  reports CONFIRMED (exact); the `PBUCoord3D` spelling, the old destructor
  name and `triggerSpecialPower` are CONTRADICTED.
