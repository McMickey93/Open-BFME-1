# Team refresh callback link task

BFME 1 b406ac3bb7: ILT RVA 0x29CD jumps to 0x37D180 (21 bytes, RET then INT3). The body reads its sole used argument at ESP+4, loads Object+0x210, calls ILT 0xF15F, and returns integer 1. Existing `bfmeGoBHE(BfmeOwnerBHE*)` in `game/GameEngine/Source/Common/BfmeConv464.cpp` exactly owns this body. The opaque visitor slot accepts two dwords; the body ignores the second.

Trial: declare the existing int-returning provider and reinterpret_cast it to the visitor type in ScriptActionsExperience.cpp. All four function rows match, but DIR32 refuses both callback words: VA 0x004029CD is already recorded under the obsolete void/two-argument name. Per sole-writer/refusal instructions, restored the source; did not change the DIR32 ledger or introduce an alias. The callback identity and signature are now independently established, but updating the address-taken identity needs sanctioned verifier work.

BFME 2 donor revision 47da7755f1: bounded searches of ScriptEngine action units found no corresponding refresh callback; no donor code imported. Main trial diagnostics are summarized above; native boundaries and ABI decide this finding. MSVC 7.1, existing /DNDEBUG /MD /EHsc and local ASCII include settings.
