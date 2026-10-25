# Particle parent search: complete-extent trial (2026-10-25)

BFME 1 input: 3d3b0681294a0de92aae10ea1a753ae22068f091.
Home: `game/GameEngine/Source/GameClient/System/ParticleSys.cpp`.
No production source or ledger edit was retained.

## Target facts and scope

The dump at RVA 005CB600 is a 28-byte empty-name guard. Its taken nonempty
branch reaches 005CB61C, the start of the separately rowed 202-byte dump.
The latter's ret8 ends at 005CB6E6: the full candidate is 230 bytes.
The existing ILT 00048220 enters the guard, not the continuation.
This is boundary evidence, not independently sufficient proof of the method name.
The existing proper-home source and previous attempts identify the semantic lead
as `ParticleSystemManager::findParentTemplate(AsciiString const&, int) const`.
Retail reads the manager map at +9c, node value at +8 and template string at +68.
`callees.py 0x005CB600 230` supplies j_0003407c (begin, body 005C55D0) and
j_0002cdf4 (skip, body 003442B0); both already exist. No pins were added.

## Donor evidence and mapping

Reviewed read-only BFME 2 revision 16c3ea885a293dafc872dd5b67a59fa92b1d6407,
`Code/GameEngine/Source/GameClient/System/ParticleSystemManagerMappedTextureUVs.cpp`,
and recovery commit c4d504c265bee0203690545ff959e4feb0d1d976.
That source explicitly credits BFME 1 ba7ddda7 as its semantic donor.
Its complete search and established cursor providers support trying a full body
instead of reconstructing the 202-byte continuation in isolation. BFME 2 map +88
was translated to witnessed BFME 1 +9c; donor RVAs/providers were not imported.
The BFME 1 home TU's existing includes/flags/STLport selection were preserved;
no donor include paths, toolchain flags or private manager class were copied.

## Measured trials and remaining mismatches

All trials used isolated copies of the existing whole TU and `tools/probe.py`
with the exact decorated method and `0x005CB600 --size 230 --all`.
The home TU's leading cl line and normal MSVC 7.1 configuration apply.

* Aggregate-return cursor adapter: 236 bytes / 196 differing nonrelocation bytes.
  Its temporary return introduced a copy absent in retail.
* Explicit output cursor plus direct StringBase isEmpty call: 230 / 48.
  The call stayed out of line; retail inlines the guard. The loop from +40 through
  its back edge otherwise reproduces the instructions (relocations excepted).
* Inline getLength-zero guard: 230 / 42, but movzx/test replaces cmp word.
* Raw witnessed header guard, either local or repeated expression: 135 / 119;
  MSVC stops inlining AsciiString::compare. Those spellings are equivalent results.
* Explicit comparison using existing getLength/str accessors, memcmp and length
  subtraction: 238 / 30. The attached replacement block preserves this last trial. Retail
  returns early at +14; ours merges guard failure at +e6, spills the length
  difference and grows the local frame from 0c to 10. Direct length equality
  instead of subtraction gave 234 / 91 and is not an improvement.

The attached probe transcript preserves the measured instruction differences.
The replacement block is diagnostic source, not a conversion. No trial passed the byte gate.
The existing 005CB61C bank was preserved. A future attempt should address the
joint inline/early-return/frame shape, then consolidate both old dump extents
through a supported ledger operation. add_match currently retires one row and
rejects another overlapping matched span; no bypass or manual row edit was tried.
