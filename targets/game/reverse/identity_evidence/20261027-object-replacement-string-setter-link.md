# Object replacement: bind the existing by-value name setter

Selected with tools/link_check.py near. Initially reviewed BFME 1 revision:
cd722f434deae81f44ed564a9b51d3eb200f996d.
Caller: game/GameEngine/Source/GameLogic/Object/Object_bfmeTransferReplacementState.cpp,
RVA 0x001C5620, 211-byte matched extent (210 nonpadding bytes).
Provider: game/GameEngine/Source/Common/P7ByValueStringSetters.cpp,
Gen001C4240::bfmeSet, RVA 0x001C4240, 78 bytes; unchanged.

## Target evidence and bounded contract

Retail calls ILT 0x00027BBA -> body 0x001C4240. The existing provider takes
AsciiString by value on the same thiscall receiver and writes its field at
+0x240. The caller already reads its name at +0x240. The provider owns its
parameter destruction and existing EH frame. Its address-derived Gen owner
is retained; this repair establishes no new original EA class name.

Remove the unused Object::setName declaration and call the existing row's
Gen001C4240::bfmeSet through a declaration-only receiver view. No instance,
member access, sizeof or copy is formed through that view. Control flow,
receiver address, argument representation and Object fields are unchanged.
No new function body, header, layout, pin, alias, ledger row or gate exception
is introduced.

## Donor evidence and excluded adaptations

Reviewed canonical BFME 2 reference 73898a96342963eac2826836db10649a69e3dbb8,
Code/GameEngine/Source/GameLogic/Object/ObjectTransferReplacementState.cpp.
Its 180-byte caller at RVA 0x002928B5 already uses an address-derived
Rva0029173EAsciiField receiver for the rowed setter. That binding pattern
is adapted here; no donor body or layout is imported. BFME 2 uses name
offset +0x308 rather than BFME 1's +0x240. Its addresses, /O1 /GX settings,
GameLogic view and defection helper ownership are not copied.

Donor history reviewed: 6e5805b1ebaf564a72300716a8f9136d7d6b250f explicitly
calls the setter name inferred; beded658276d8880dc95e348e12cbca680b81d69
records module string/WorldBuilder evidence; bd9a812fd3aa1824522dfbe8f1932569dd0d223d
retains address-derived owners. The donor itself cites BFME 1 for its initial
reconstruction, so it is not an independent EA-name vote. The verified
reference pointer and its 2026-10-27 freshness receipt remain unchanged.

## Measurements and scope

Native Windows MSVC 7.1 checks pass 20/20 before and 20/20 after, covering
the caller and all nineteen existing setters in the complete provider.
The literal verifies with zero skipped string references; both DIR32
references pass. Body guards report 20 rows, zero baselined findings and
five existing static_skip cases. The declared-body check passes after edit.

Local COFF inspection preserves all four executable sections, all ten
non-debug sections (including EH/static-initialization data), their relocation
offsets/types/targets and all external definitions. Internal targets are
resolved by actual section and value: the compiler merely renumbers
FuncInfo labels $T943/$T947 to $T951/$T955 at section 12 offsets 8/0.
The only external undefined-name change is
?setName@Object@@QAEXVAsciiString@@@Z ->
?bfmeSet@Gen001C4240@@QAEXVAsciiString@@@Z.
Windows qualification repeats the paired builds and structural COFF check
from the reviewed source preimage, then commits through the normal hooks.

The local Windows connection became unavailable before the commit. The exact
source change was preserved from its reviewed Git preimage and is rechecked
in Windows GitHub Actions. No unavailable local binary or log is represented
as a completed later check.

The original ordinary local link preview used census a0940f921b,
2026-10-27 11:50, and reported 22,660 unreadable new/changed ledger objects.
The caller had unresolved Object::setName; both units' selection facts were
UNKNOWN. No new whole-image linking or census bytes can be inferred from that
preview. Windows before/after preview output and actual exit codes are appended
below; cold-runner previews use the supported --compile-limit 0 and remain
separate from the mandatory byte/commit/push gates.

A related authored-source scan found no other Object declaration of this
by-value interface. Other setName(AsciiString) occurrences belong to Image,
SubsystemInterface, display managers or map objects and are outside this
provider identity. Existing unused candidate pins remain unchanged.

The earlier TerrainLogic candidate was left unchanged: its paired rows match
3/3, but the DIR32 guard refuses the existing data-row owner g_Rva00F36E5C
because retained legacy aliases are tested first. That prerequisite is recorded
through re_log.py; no registry, source, pin or verifier workaround is applied.

This repair adds +0 C++ bytes. No new census-linked gain is claimed.
Autonomous implementation and measurements: OpenAI Codex.

## Windows qualification receipts

The paired before/after build.cmd checks and structural COFF comparison pass.
All runtime sections, EH targets and external definitions are preserved.
Before preview: exit 1, unknown-or-unresolved. After preview: exit 1, unknown-or-unresolved.
These diagnostic exits are retained, not counted as passing mandatory gates.
No new census or whole-game link clearance is claimed.
Windows evidence: https://github.com/McMickey93/Open-BFME-1/actions/runs/40572193037
