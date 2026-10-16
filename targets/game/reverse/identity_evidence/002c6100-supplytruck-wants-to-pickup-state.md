# 0x002C6100 is SupplyTruckWantsToPickUpOrDeliverBoxesState's constructor; vtable 0x010C9308 is its vftable

Ledgered as `??0Rva002C6100State@@QAE@PAX@Z` (StateSelfNamingCtors.cpp) and
recorded in dir32_addresses.csv as `??_7Rva002C6100State@@6B@` at 0x010C9308,
address-derived because a self-naming literal alone does not prove a class name.
Here a matched caller witnesses it.

## The constructor (`tools/dis_retail.py 0x002C6100 46`)

- +0x0B `push 0x010C935C`: the retail string at VA 0x010C935C is
  `SupplyTruckWantsToPickUpOrDeliverBoxesState`, built into the by-value
  `AsciiString` name (`call 0x00888BC0`).
- +0x1C calls the State base constructor through ILT 0x000035B2 with
  (machine, name).
- +0x21 `mov dword ptr [esi], 0x010C9308`: installs vftable 0x010C9308.

## The matched caller names the class

`??0SupplyTruckStateMachine@@QAE@PAVObject@@@Z` (0x002C6430, 1153 B, matched,
SupplyTruckStateMachineConstructor.cpp) is Zero Hour's
`SupplyTruckStateMachine::SupplyTruckStateMachine` (SupplyTruckAIUpdate.cpp).
Its third `defineState` (`ST_WANTING`) builds
`newInstance(SupplyTruckWantsToPickUpOrDeliverBoxesState)(this)`, and the retail
body at +0x33F..+0x351 does exactly that inline: it pushes the same literal
0x010C935C, calls the same base constructor through ILT 0x000035B2 and stores
the same vftable 0x010C9308 (`mov dword ptr [edi], 0x010C9308`). The matched
source spells that class `SupplyTruckWantsToPickUpOrDeliverBoxesState`, and Zero
Hour's SupplyTruckAIUpdate.h declares it with
`SupplyTruckWantsToPickUpOrDeliverBoxesState( StateMachine *machine ) :
State( machine, "SupplyTruckWantsToPickUpOrDeliverBoxesState" ) {}`. So the
literal is the class name here, and 0x002C6100 is the out-of-line copy of that
constructor (same literal, same base, same vftable).

## Correction

- 0x002C6100 -> `??0SupplyTruckWantsToPickUpOrDeliverBoxesState@@QAE@PAVStateMachine@@@Z`
  (Zero Hour's signature), retiring `??0Rva002C6100State@@QAE@PAX@Z`.
- dir32 record 0x010C9308: `??_7Rva002C6100State@@6B@` retired for
  `??_7SupplyTruckWantsToPickUpOrDeliverBoxesState@@6B@`, the name the matched
  0x002C6430 body already reads there.
