# 0x00150C90: AIGroup owner name refuted by the ILT window

The banked attempt `targets/game/reverse/attempts/0x00150c90.cpp` declared the
187-byte body as `AIGroup::groupDoSpecialPowerAtLocation`, after Zero Hour's
`AIGroup.cpp`. The body is that operation: GameLogic::logicMessageDispatcher
calls it, and it walks the member list at `this+0x04`, looks up the special
power template, asks the ActionManager and dispatches the waypoint form.

The decorated name does not fit retail's incremental-link thunk table:

```
python3 tools/ilt_oracle.py check '?groupDoSpecialPowerAtLocation@AIGroup@@QAEXIPBUCoord3D@@MPBVObject@@I@Z' 0x00150C90
CONTRADICTED  p_false=1.17e-03  (outside every window of the target's slots 6886:6520-6537)
```

The same check also contradicts the `W4CommandSourceType@@` and
`IW4CommandSourceType@@` last-argument spellings, so the owner or signature
differs from every AIGroup spelling tried. The landed source therefore keeps
the address token in the owner, `Rva00150C90AIGroup`, exactly as the sibling
special-power-at-object dispatch does at 0x00152110
(`Rva00152110AIGroup::groupDoSpecialPowerAtObject`).
