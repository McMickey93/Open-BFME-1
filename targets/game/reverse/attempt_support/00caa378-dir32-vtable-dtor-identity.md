# dir32 gate-debt 0x010AA378 — vtable slot-0 deleting-dtor identity (blocked)

Debt line (`targets/game/reverse/body_guard_baseline.csv:168`):

    dir32,0x010AA378,??_7CrateCollideModuleData@@6B@,"??_7CrateCollideModuleData@@6B@ is a function the ledger places elsewhere, not at 0x010AA378"

The `detail` text is **stale** (it is the `Z`-ending "function placed elsewhere"
branch, build.py:3662). The name ends `@@6B@`, so the live gate routes it to the
`??_7` primary-vtable-ownership branch (build.py:3674) and the current finding is:

    nothing in the ledger owns 0x010AA378. Give the datum a data row first
    (tools/add_data_match.py), or use an address name (g_Va<VA>)

(Reproduced by `build/live_finding.py`: `build.unrecorded_dir32_problem` returns
exactly that string; the symbol is pinned in `symbols.csv` at RVA 0x00CAA378 = VA
0x010AA378, is **not** in `dir32_addresses.csv`, and `function_owner_problem`
fails.)

This is a **real** reject, not the prior seat's guessed "false-reject": the gate is
correctly reporting that no ledger identity backs the vtable's ownership.

## Structural root cause (byte-level, retail-1.03-unpacked)

Vtable VA 0x010AA378 (RVA 0x00CAA378) = `??_7CrateCollideModuleData@@6B@` (base
class), 17 slots (0–16), slot 17 = 0. Installed by the matched ctor
`??0CrateCollideModuleData@@QAE@XZ` at 0x00217870 (147 B,
`CrateCollideModuleDataConstructor.cpp`; see
`identity_evidence/0x00217870-crate-collide-module-data.md`). Sibling vtables,
byte-identical in slots 1–16 and differing **only in slot 0**:

| vtable VA | name (dir32)                    | slot-0 thunk      | slot-0 body (30 B) | body's `??1` call |
|-----------|---------------------------------|-------------------|--------------------|-------------------|
| 0x010AA378 | `??_7CrateCollideModuleData@@6B@` (none) | `?j_00023a47` | **0x00217930** | `??1ConvertToCarBombCrateCollideModuleData` @ 0x00125E40 [matched] |
| 0x0108E8E8 | `??_7UnitCrateCollideModuleData@@6B@`   | `?j_0000a81c` | 0x001270C0 | `??1UnitCrateCollideModuleData` @ 0x001270F0 [matched] |
| 0x0108E940 | `??_7ConvertToCarBombCrateCollideModuleDataVtbl@@6B@` / `??_7VeterancyCrateCollideModuleDataVtbl@@6B@` | `?j_00038bf9` | 0x00127160 | `??1Rva00127190` @ 0x00127190 [matched, opaque] |

All three slot-0 bodies are scalar deleting-destructor shape
(`push esi; mov esi,ecx; call ??1Class; test [esp+8],1; jz; push esi; call
??3@YAXPAX@Z (operator delete) @ 0x00881EB0; add esp,4; mov eax,esi; pop esi;
ret 4`). A scalar deleting dtor `??_GClass` directly calls its own class's
complete-object dtor `??1Class`, so the call target identifies the owning class.

The anomaly: the **base** class's vtable slot 0 points to 0x00217930, whose
`??1` call targets the **derived** `ConvertToCarBomb` class. Body 0x00217930 is
therefore mechanistically `??_GConvertToCarBombCrateCollideModuleData` (its
ledger name is consistent with its bytes), yet it occupies the base vtable's
slot-0 slot. The `ConvertToCarBomb` vtable's slot 0 in turn points to 0x00127160,
which calls an **opaque** `??1Rva00127190` (not the known `??1ConvertToCarBomb`
@ 0x00125E40). So the "each vtable's slot 0 = its own class's `??_G`" mapping is
**not self-consistent** across the family, and the family's
vtable→class / `??_G` / `??1` assignment is not established.

Ledger gaps that make the ownership proof fail:
- **No** `??1CrateCollideModuleData` (base complete-object dtor) row.
- **No** `??_GCrateCollideModuleData` / `??_ECrateCollideModuleData` (base
  deleting dtor) row.
- `dir32_record_guard.function_owner_problem` requires the table at the VA to
  reach a matched, non-generated `??_G`/`??_E` of **exactly** class
  `CrateCollideModuleData` (`is_dtor_of` = name starts
  `??_GCrateCollideModuleData@@`/`??_ECrateCollideModuleData@@` + U/M/E). The
  only deleting dtor the table reaches is `??_GConvertToCarBomb…` (a different
  class) → `dtors` is empty → proof fails.
- Note: the `??_GConvertToCarBombCrateCollideModuleData` row at 0x00217930 is
  sourced from `game/GameEngine/Source/Common/Thing/ModuleFactory.cpp`, whereas
  the sibling deleting dtors (`??_GMoney…` 0x00126F90, `??_GUnit…` 0x001270C0)
  live under `game/GameEngine/Source/GameLogic/Object/Collide/CrateCollide/` —
  a placement red flag worth re-checking during the identity pass.

## Why the tool's two suggested paths are not clean

- **Data row** (`add_data_match.py`): needs a `game/` source that *defines* the
  COFF symbol and verifies its bytes. A compiler-emitted COMDAT vtable has no
  such single-TU source; the vtable bytes are not an EXTERNAL data global a
  normal TU can define and land. Not achievable without inventing a source.
- **Address name** (`g_Va010AA378`): a forced rename of a vtable that is in fact
  `??_7CrateCollideModuleData@@6B@`, with no identity evidence for the new name.
  AGENTS.md forbids shipping a plausible-guessed name; a wrong name compiles to
  the same bytes and no gate can see it.

The minimal gate-passing edit would be to rename 0x00217930 to
`??_GCrateCollideModuleData@@UAEPAXI@Z`, but that **contradicts** the
mechanistic evidence (0x00217930 calls `??1ConvertToCarBomb`), so it is not an
honest rename. The debt cannot be retired without first resolving the family's
identity.

## Donor method (lead, not proof)

BFME 2 submodule (gitlink 73898a96) resolves the same identity class for this
family. `Code/GameEngine/Source/GameLogic/Object/Collide/CollideModuleDeletingDtors.cpp`
emits the scalar deleting-dtor wrappers (28 B there vs 30 B here) and cites
`docs/reconstruction/deleting-destructor-identity-audit.md` (2026-09-26). That
audit's evidence standard:
- Every wrapper is independently decoded (this → recorded `??1` callee; bit-0
  flag test; conditional `operator delete`; `ret 4`).
- A named wrapper's **owner** is established by one of: (a) a retail name-string
  in another slot of the same vtable, (b) the **registry** path (retail module
  registration → data factory → ctor → primary vptr store), or (c) corroborated
  donor attribution.
- "A named slot alone does not establish the complete owner." A harvested pin /
  call destination "proves a call destination, not a class" (the retracted
  `DamageModuleBase` case).
- Donor resolved the sibling `SalvageCrateCollideModuleData` via the registry
  path (registration → data factory 0x00255BD2 → ctor 0x00255B7E; vptr store
  0x00255BA3; vtable VA 0x00BF3A40, wrapper @ slot 0 0x002563D3 calling `??1`
  @ 0x002563EF).

Per AGENTS.md, the donor's names/placements/registrations are **leads, not BFME 1
proof**; BFME 1's own registration/RTTI/string evidence must establish the
identity independently.

## Prerequisite to retire this debt (next concrete work)

1. Establish the true class hierarchy and vtable→class mapping for the
   CrateCollideModuleData family (base / Unit / ConvertToCarBomb / Veterancy /
   Money, including the `…Base` and `…Vtbl` multiple-inheritance variants and
   secondary vtables).
2. Identify each class's `??1` (complete-object) and `??_G`/`??_E` (deleting)
   dtors as distinct retail bodies; reconcile 0x00217930 (in ModuleFactory.cpp,
   calling `??1ConvertToCarBomb`) and the opaque `??1Rva00127190` (0x00127190).
3. Apply the donor's registry/name-string audit method with BFME 1 evidence to
   fix any misnamed/misplaced rows; add matched rows for the base class's
   `??_G`/`??_E` (and `??1`) where they are distinct bodies.
4. Only once the base vtable is proven to reach the base's own matched deleting
   dtor: record `??_7CrateCollideModuleData@@6B@` at 0x010AA378 via
   `tools/dir32_record.py record` and retire the debt line with
   `tools/repair_queue.py pass-test` (the gate must then report the finding gone).

This is a substantive class-family identity reconstruction, not a small dir32
repair; it is a separate work item. Banked and switched.

## Scratch drivers (untracked, under build/)

- `build/vtable_010AA378.py`, `build/vtable_compare.py` — dump + compare the
  three vtables' slots against functions.csv.
- `build/dtor_decode.py`, `build/dtor_capstone.py`, `build/dtor_thunks.py` —
  decode the three slot-0 deleting-dtor bodies and resolve their `??1` call
  targets through the ILT thunks; identify 0x00881EB0 = `??3@YAXPAX@Z`.
- `build/ctor_vtable_store.py` — list the family's dtor rows and the ctor's
  stored addresses.
- `build/live_finding.py` — reproduce the live gate finding for the name.

No source, ledger, baseline or identity edit was attempted; no rename forced;
no data row added.
