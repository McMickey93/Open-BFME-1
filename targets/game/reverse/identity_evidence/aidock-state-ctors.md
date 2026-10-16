# Six self-naming state constructors are the AIDock / AIGuard state classes

Each constructor (address-derived `??0Rva<RVA>State@@QAE@PAX@Z`) passes a
state-name literal to its base and stores a vftable. For each one:

- the vftable it stores is referenced by the class's matched scalar-deleting
  destructor row `??_G<Class>@@UAEPAXI@Z`;
- `tools/ilt_oracle.py check '??0<Class>@@QAE@PAVStateMachine@@@Z' 0x<RVA>` is
  CONFIRMED (exact);
- the literal and base equal Zero Hour's inline constructor in AIDock.h /
  AIGuard.h / AIGuardRetaliate.h.

| RVA | class | vftable | p_false | ZH literal |
|---|---|---|---|---|
| 0x0014F420 | AIDockWaitForClearanceState | 0x01095BF0 | 1.70e-03 | "AIDockWaitForClearanceState" |
| 0x0014F490 | AIDockAdvancePositionState | 0x01095C68 | 1.37e-03 | "AIDockApproachState" (ZH passes this literal too) |
| 0x0014F610 | AIDockMoveToRallyState | 0x01095DB0 | 3.26e-04 | "AIDockMoveToRallyState" |
| 0x0014F710 | AIDockProcessDockState | 0x01095EA0 | 8.48e-04 | "AIDockProcessDockState" |
| 0x0015CF50 | AIGuardReturnState | 0x010962C8 | 5.87e-04 | "AIGuardReturn" |
| 0x0015EC40 | AIGuardRetaliateReturnState | 0x01096520 | 1.30e-03 | "AIGuardRetaliateReturn" |

Negative controls: `??0AIDockApproachState` at 0x0014F490 and
`??0AIDockMoveToRallyState` at 0x0014F690 are CONTRADICTED.
