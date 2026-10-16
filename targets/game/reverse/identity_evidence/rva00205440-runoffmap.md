# 0x00205440: RunOffMapBehavior Iface2 slot 0, meaning unproven

- Retail body 0x00205440..0x002055A1 (354 B, `ret`, int3 padding).
- `??_7RunOffMapBehavior@@6BRunOffMapBehaviorIface2@@@` (VA 0x010A5E0C) holds
  ILT 0x00038D25 -> 0x00205440 in slot 0; there are no direct callers. The body
  reads the object at this-8 and the module data at this-0xC, which is the
  RunOffMapBehavior +0x10 interface view (ObjectModule is 0x0C bytes; see
  RunOffMapBehaviorCtorThunk.cpp).
- The 0.20 bank (targets/game/reverse/attempts/0x00205440.cpp) used invented
  names on an anonymous `Rva00205440::method`. None is retail evidence:
  - `method` -> `rva00205440`: the bank's own placeholder; the owner class is
    now proven by the vtable, the meaning is not, so the name keeps the address.
  - `ReportView::report` -> `BFMEReportDamageSource::report`: the existing pin
    at body 0x001C9490 (symbols.csv) names that class; the bank's class was a
    local stand-in.
  - `IDView::getID` was a misreading: retail calls body-module slot 15 (+0x3C)
    twice and reads +8 of the result, i.e. a last-damage-info record; it is now
    `BodyModuleInterface::getLastDamageInfo`. The checker paired the removed
    `getID` with the unrelated new `bfmeSetModelConditionState`.
  - `pad` -> `m_unmodelled_00`: padding members only.
