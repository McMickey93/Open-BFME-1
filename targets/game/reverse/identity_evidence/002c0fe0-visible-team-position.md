# GiantBirdGuardIdleState::update, RVA 002C0FE0

The matched self-naming state constructor at 002C0470 passes the literal
GiantBirdGuardIdleState at VA010C7C0C, then installs table VA010C7BB8.
Its slot6 contains ILT0003A55D, whose five-byte JMP reaches 002C0FE0.
The constructor also initializes the next scan frame at +24. This proves
the state's identity independently of matching its update body. The body
has complete RET paths through 002C1101; its end is 002C1102 (290 bytes).
Retail source-file evidence identifies GiantBirdAIUpdate.cpp. The guard
portion is kept beside the existing split GiantBird state implementations
in GameLogic/Object/Update/AIUpdate/GiantBirdGuardIdleState.cpp.

The update follows the ZH guard-idle behavior with BFME's crate-state check:
wait for the scan frame, schedule the next scan, switch the machine to
0x138C for a crate owner, ask the GiantBird inner-target scan, and otherwise
compare the guarded object or team's current position to the saved position.
An up-front both-null check retains retail's team/object branch layout.
The four direct call routes are 0001F253->0009A510 (object lookup),
000241FE->000EDCD0 (team average), 0002F527->002C07E0 (GiantBird target scan),
and 00044C2E->000EF060 (team lookup). No new pins are needed.

The preferred bank emitted290 bytes but had14 differing bytes in the object
position copy. Retail loads x/y/z before storing x/y to the local; the bank
interleaved those loads and stores. Native coordinates, the Object layout,
the authentic visible GameLogic lookup, by-value copy/return helpers and an
empty coordinate constructor did not change this residue. The actual
186-byte Team::getEstimateTeamPosition_000EDCD0 body fixes all14 bytes when
visible with inline __declspec(noinline). It writes the position without
retaining that output pointer. Its body is independently exact, including
the native DLINK pointer-to-member traversal. The shared ObjectDlinkPmf.h
supplies that established virtual-inheritance representation.

The Team implementation's authoritative ledger row remains in
Common/RTS/Rva000EDCD0TeamEstimatePosition.cpp. The inline COMDAT here only
exposes its effects; it is not another claimed identity or new progress.
GameLogic uses the existing GameLogicObjectLookup.h declaration, and Coord3D
uses the existing native coord.h. TU-local position and AI readers use only the
retail-witnessed Object position +38 and AI pointer +204 offsets.

Validation: add_match and the scoped build verify all290 bytes, both float
constants and all four DIR32 references without baselined findings. A second
strict build verification of the Team row against this TU verifies its186
bytes, its float constant and its function-pointer binding. Probe-only equality is
not the landing proof. No assembly, volatile access, header change, new pin
or gate exception is added.
