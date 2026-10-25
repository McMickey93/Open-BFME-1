# FX particle-system recorded references

Gate-debt shard `1/4`, BFME 1 input revision
`66f7faefebb2f470a234ca76838cf680527daad8`. This repair changes references in
`game/GameEngine/Source/GameClient/System/FXParticleSystem/fx_particle_system_bulk.cpp`.

Five existing DIR32 baseline keys are retired by their exact
`tools/repair_queue.py pass-test` commands:

| Retail VA | Old reference | Recorded owner |
| --- | --- | --- |
| 0x00C51050 | `_bfmeINIParseIndexList` | `?parseIndexList@INI@@SAXPAV1@PAX1PBX@Z` |
| 0x00C52E00 | `_bfmeINIParseBool` | `?parseBool@INI@@SAXPAV1@PAX1PBX@Z` |
| 0x01110EBC | `?g_vtbl_01110EBC@@3PAPAXA` | `??_7?$DefaultParticleModuleTemplate@$05@FXParticleSystem@@6BModuleTemplate@1@@` |
| 0x01111D9C | `?g_vtbl_01111D9C@@3PAPAXA` | `??_7TailX005EB6B0@@6B@` |
| 0x01111EC8 | `?g_vtbl_01111EC8@@3PAPAXA` | `??_7Rva005EBCC0Object@@6BV3Slot2@@@` |

BFME 1 evidence: `dir32_addresses.csv` already records each chosen owner at
the corresponding VA. The parser bodies are matched rows at RVAs 0x00851050
(91 bytes) and 0x00852E00 (86 bytes) in `Common/INI/ini_parsers.cpp`.
The existing aliases already specified exactly these owners. Replace the
alias declarations and their uses with direct `__identifier` references;
retain the existing callback signatures, vptr-store offsets, and array types.
This repairs references without introducing a new identity or layout claim.

Every successful pass test verifies all 470 matched bodies, eight data rows,
24 literals, 93 float constants, and 1,042 DIR32 references in this TU.
The initial Boolean-parser test failed compilation because four more table
entries still used the removed alias; replacing those uses made the second
test pass. No other pass test failed in this batch. The tools alone removed
the five baseline lines (982 debts to 977). No gate, pin, header, generated
source, or baseline was edited by hand.

The compiler reports eight existing funclet labels renumbered, but verifies
their bodies through the normal resolver. No funclet identity is changed.
The source's existing compiler flags and BFME 1 toolchain are retained.

Donor review: read-only BFME 2 revision
`cf5c96c944521da6bd8bfe7274c725d876df1f69`, narrow FXParticleSystem parser
search and path history. `Code/GameEngine/Source/GameClient/System/FXParticleSystem/Rva003A547EXfer.cpp`
uses `INI::parseIndexList` for a different table. It supplies no additional
BFME 1 identity or layout proof and no source was imported; the repair is
established entirely by BFME 1's recorded owners and normal gates.

The optional link preview remains unknown: 22,656 census objects cannot be
read locally, and the TU still has other unresolved alias references. Its
reported linked-byte preview is 0 to 0. This is five retired gate debts,
with zero added exact C++ bytes and no claimed linking gain.

Six unrelated skipped items are recorded in `re_attempts.log`: implicit
vtable source-resolution failures, an external-vtable constructor mechanism,
the private-message callback identity, a static string's class mismatch,
and an unowned secondary vtable requiring ABI/extent evidence. Their claims
were released. Further mechanical aliases in this same TU remain in shard
1/4; other shards' entries must stay untouched.
