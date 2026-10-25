# DX8TextureCategoryClass::Render: matrix-storage trials

Target: `?Render@DX8TextureCategoryClass@@QAEXXZ`, RVA `0x00948BD0`,
4397 bytes. BFME 1 input revision: `d6c4b40659`.

BFME 1 evidence remains the matched `DX8RigidFVFCategoryContainer::Render`
caller at `0x00949EA0`, the task-loop relationships recorded in the preferred
bank, and the retail RET at `0x00949CFC` followed by INT3 at `0x00949CFD`.
The picker still reports the obsolete 4389-byte extent. No identity, layout,
global-name or boundary change is proposed.

Reviewed the bank `targets/game/reverse/attempts/0x00948bd0.cpp` and prior
argument-order, flag, helper, sphere-type and allocator experiments before
testing a new lead. The read-only BFME 2 donor revision was
`8db6f7ddafdedb73b6e90d081d21bf7a70d89aa9`:
`Code/Libraries/Source/WWVegas/WW3D2/dx8renderer.cpp`. Its native Render uses
a twelve-float storage object viewed as a Matrix3D reference. This is a
compiler-context lead, not BFME 1 layout proof.

The required donor compile used the pinned submodule revision
`beed8a16790a6812231ac7b05e3e6893e4cb5d1b`:

```
python3 tools/bfme2_sweep.py compile Code/Libraries/Source/WWVegas/WW3D2/dx8renderer.cpp
```

It stopped with `unsupported donor compiler control: /FIshader.h`, before
producing a trial receipt or include trace. The intended source mapping is
`Code/Libraries/Source/WWVegas/WW3D2/dx8renderer.cpp` to
`game/Libraries/Source/WWVegas/WW3D2/dx8renderer.cpp`; no include mapping was
accepted or verified. This is a setup refusal, not a negative result for the
donor body. No tool override or fallback headers were used.

Private BFME 1 trials used `tools/probe.py SOURCE SYMBOL 0x00948BD0 --size
4397`, preserving the bank's MSVC 7.1 compiler controls and declarations.
Each produced 4397 bytes, 291 relocations and the same 36 non-relocation
differences, first at `+0x685`:

| Source change | Result |
| --- | --- |
| Unmodified preferred bank | 36 differences |
| `tmp_world` as twelve-float storage plus Matrix3D reference | 36 differences |
| Inverse matrix as twelve-float storage plus Matrix3D reference | 36 differences |
| Both matrix-storage changes | 36 differences |
| Donor-style named sorted base-vertex-offset local | 36 differences |

The first divergent instruction still loads the index offset into EDX
instead of retail's ECX; the sphere result then occupies ECX instead of EBP.
The renderer register, argument scheduling and sorted-path join follow that
choice. These trials provide no new explanation for the allocator decision.
Do not repeat them without a changed compiler context or other new evidence.

The best bank is unchanged. Sources and probe logs remain in the ignored
`build/banked-dx8-20261025/` directory; the minimal transformations and measured
results above are sufficient to recreate them. No production source, pin,
datum, header or ledger row changed.

`link_check.py game/Libraries/Source/WWVegas/WW3D2/dx8renderer.cpp` also reported
an **unknown** preview: 22,639 new/changed ledger objects could not be read
against the published census. Its listed unresolved names and duplicate
providers are leads only; no linked-byte improvement is claimed. The body
claim was released. Resume only with a supported allocator hypothesis or a
maintainer repair of the donor compiler-control refusal.
