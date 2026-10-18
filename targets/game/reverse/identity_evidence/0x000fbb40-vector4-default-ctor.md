# Vector4 default constructor is at 0x000FBB40, not 0x007A62E0

## Verdict

`??0Vector4@@QAE@XZ` is the 3-byte body at RVA 0x000FBB40
(`8B C1 C3` = `mov eax, ecx; ret`), reached through the incremental-link
thunk at RVA 0x00045561 (`E9 DA 65 0B 00` -> 0x000FBB40). The empty 3-byte
body at 0x007A62E0 has the same bytes but is a different retail function and
carries a different name.

## Evidence

- `python3 tools/ilt_oracle.py check '??0Vector4@@QAE@XZ' 0x000FBB40`
  -> CONFIRMED (exact), p_false 4.57e-04.
- `python3 tools/ilt_oracle.py check '??0Vector4@@QAE@XZ' 0x00045561`
  -> CONFIRMED (exact), the thunk slot retail encodes.
- `python3 tools/ilt_oracle.py check '??0Vector4@@QAE@XZ' 0x007A62E0`
  -> CONTRADICTED (outside every window of the target's slots).
- `SortingRendererClass::Flush` at 0x0093A810 pushes VA 0x00445561 at +0x8D2
  and calls `_eh_vector_constructor_iterator_` for 4 elements x 16 bytes at
  +0x917: the callback is the `Vector4[4]` temporary of the inlined
  transpose/`Set_Transform` path.
- The four row-array TUs (`Rva00413400NestedArraysCtor.cpp`,
  `SpawnPointProductionExitUpdateInitializeBonePositions.cpp`,
  `SiegeDockingInitialize00206CB0.cpp`,
  `W3DAptRendererEnd0078B4F0.cpp`) all push VA 0x00445561 in their retail
  bodies, confirming the same 16-byte row constructor.

## Ledger action

The old `functions.csv` row took the descriptive `Vector4` name at the
ILT-refuted 0x007A62E0 body. This change moves that identity back to the
oracle-confirmed body: the row at 0x007A62E0 becomes the address-derived
`?get@Rva007A62E0@@QAEPAXXZ` placeholder for the unrelated 3-byte body, and
`??0Vector4@@QAE@XZ` lands at 0x000FBB40 in the follow-up commit. The
0x00045561 pin is renamed from the ILT-refuted `??0SpawnBoneRow@@QAE@XZ` to
`??0Vector4@@QAE@XZ` at the same address.
