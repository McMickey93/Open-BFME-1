# Character find: canonical DIR32 prerequisite

This is a blocked baseline investigation, with no production edit and no new
C++ bytes. The consumer is
game/GameEngine/Source/GameClient/MessageStream/Rva005A67E0Translator.cpp;
the candidate name is ??$find@PADD@_STL@@YAPADPAD0ABD@Z.
The existing 30-byte provider at RVA 0x00845800 is
game/stlport/NumFacetsInstantiations.cpp.

Native baseline verification passed all 42 code rows but refused seven DIR32
references to the canonical
?g_rva012F19E8WindowManager@@3PAVWindowManager@@A:
the address is already recorded under 67 older aliases.
Adding the actual WindowManager.cpp data provider to the verification scope
passed its one 4-byte data row and still refused those same seven references.

build.unrecorded_dir32_problem checks existing alternative names before the
matched-data path. This is the verifier's current deliberate ownership rule.
Do not add another alias, an address-record exception or a whitelist entry, and
do not weaken the verifier in this repair. The consumer already uses the real
canonical data owner; the BFME 2 global sweep found no unambiguous rewrite.

The proposed extern-template consumer change was not attempted because the
baseline failed. Reconcile the canonical-global alias history through the
project's admitted migration, or obtain a separate maintainer ruling first.
The claim was released. The completed local measurements preceded loss of the
Windows executor; no failed source draft remains in production.

Autonomous implementation and measurements: OpenAI Codex.
