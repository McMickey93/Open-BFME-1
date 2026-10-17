# 0x00211D40 is ActiveBody::attemptDamage

The ledger held this 1803-byte body as `?dup_00211d40@@YAXXZ`, an `__emit`
lift whose object symbol was `??1RespawnBodyModuleData@@UAE@XZ`. The ILT
oracle contradicts that destructor name here; `pin-candidates-op1-batch4-oracle.md`
already records it as CONTRADICTED and confirms the destructor at 0x00212BB0.

`python3 tools/ilt_oracle.py check "?attemptDamage@ActiveBody@@UAEXPAVDamageInfo@@@Z" 0x00211D40`
prints `CONFIRMED p_false=6.52e-04 (exact)`.

The bytes read as Zero Hour's `ActiveBody::attemptDamage(DamageInfo *)`, compiled
as a virtual of the body interface at +0x10 inside the module:

- It calls `validateArmorAndDamageFX` through primary slot +0x38 on entry and
  `doDamageFX` through primary slot +0x3C on exit, and it returns `ret 4`.
- It makes the armor adjust call (`HealingArmor001B0200::adjust`, shared with
  the matched `ActiveBody::attemptHealing` at 0x0020FBC0).
- `DAMAGE_HEALING` (7) hands off to `attemptHealing` through interface slot 1,
  and `DAMAGE_UNRESISTABLE` (8) skips the damage scalar at this+4.
- It calls `internalChangeHealth` through interface slot +0x80, then the
  `m_lastDamageInfo` copy (`DamageInfo::operator=`) at this+0x30 with the
  timestamp at this+0x8C.
- It sends `onDamage`/`onBodyDamageStateChange` to every behavior module's
  damage interface, plays the damaged/really-damaged sounds, and calls
  `Object::onDie` when health reaches zero.

DetachableRiderBody::attemptDamage and PorcupineFormationBodyModule::attemptDamage
reach this body as their base call.

The new source, `game/GameEngine/Source/GameLogic/Object/Body/ActiveBody_attemptDamage.cpp`,
reproduces all 1803 bytes. It replaces `?dup_00211d40@@YAXXZ` with
`?attemptDamage@ActiveBody@@UAEXPAVDamageInfo@@@Z`.
