# 0x008C6AD0: canonical callback identity and inputs

## Status

The 233-byte body remains **non-exact**. Original MSVC 7.1 compiled the best
preserved whole-file candidate to 229 bytes, with 120 non-relocation byte
differences and instruction-shape score 0.893. Variant 08 emitted the same
instruction table. The additional split-guard/early-return variant 09 exactly
repeated 05's non-exact 237-byte instruction table. No recovered C++ bytes or
successful complete byte gate are claimed.

The [tracked handoff](../attempt_support/008c6ad0-tail-order-20261025/readme.md)
preserves the exact best source, useful source transformations, raw native
comparisons and immutable run inputs. The canonical `re_log.py partial --stash`
update is pending native remeasurement of both the new and retained banks.
The existing canonical bank/log are unchanged, and the unmatched addition has
been removed from `game/`; the previously matched whole-file sibling is intact.

## Independent boundary and ABI

The target is project RVA `0x008C6AD0`, size 233 (`0xE9`). Retail ends with a
return at `+0xE8`; padding begins at `+0xE9`. Its earlier returns at `+0x0D`,
`+0xAB`, `+0xC6` and `+0xDC` belong to the same callback, not separate bodies.
The second stack argument is read at `[esp+8]`, the first is unused, all exits
use plain `ret`, and the result is an object pointer in EAX. This supports
`AptValue *BooleanCoerce008C6AD0(void *, int)` with cdecl ABI. The original
callback name is unknown, so the reconstruction keeps the RVA in its name.

The registration source
`game/Libraries/Source/EA/Apt/Rva0089BBF0InitGlobals.cpp` stores the old
`d_008c6ad0` callback in a `BfmeA1029` object. That establishes registration,
not a source-level method name or a zero-argument void ABI.

The canonical home is
`game/Libraries/Source/Apt/AptActionInterpreter.cpp`. Its existing
`rva8CF1B0ProcessRecord` body at `0x008CF1B0` is 520 bytes. The complete original
5,349-byte source prefix was preserved byte for byte, and every native trial
reported that sibling exact modulo relocation slots. Reviewed base:
`3d3b0681294a0de92aae10ea1a753ae22068f091`. Later accepted upstream changes
were unrelated; detailed native payload inputs are in the handoff.

## Direct callees

| RVA | Canonical declaration | Independently supported ABI |
|---|---|---|
| `0x008983D0` | `float AptValue::toNumber()` | ECX receiver, no stack argument, x87 result; matched 170-byte body |
| `0x008996B0` | `static AptBoolean *AptBoolean::Create(bool)` | One stack argument, caller cleanup, pointer result in EAX; matched 184-byte body |
| `0x008C4A30` | `bool __cdecl Rva008C4A30Check(Rva8CD130Value *)` | One pushed pointer, caller `add esp,4`, result tested in AL; matched 873-byte body |

Provider sources are, respectively,
`game/Libraries/Source/EA/Apt/AptValue_toNumber.cpp`,
`game/Libraries/Source/EA/Apt/AptBooleanCreate.cpp`, and
`game/Libraries/Source/EA/Apt/Rva008C4A30Check.cpp`.
The predicate evidence is also recorded in
`targets/game/reverse/identity_evidence/008c4a30-numeric-predicate.md`.
The callee inventory's heuristic `thiscall` label for the predicate is
superseded by its recovered cdecl source and the actual caller's stack use.
No new pin is required; the old bank's void-function cast is removed.

## Value layout and data bindings

Retail reads the value word at `+4`, masks its low six bits for the type, and
uses bit 15 for validity. The Boolean payload is read as one byte at `+8`.
The matched numeric conversion and Boolean factory independently support
those fields. Existing Apt numeric consumers also use the raw-shift
`isUndefined` member spelling retained here. There is no canonical shared
AptValue/AptBoolean/stack header under `game/` to adopt for these views.
The private view establishes only the accessed prefix, not a complete class
size or ownership contract.

| Retail VA | Canonical binding | Evidence |
|---|---|---|
| `0x013379BC` | `g_bfmeFallbackDB` | Existing matched four-byte data row and both retail references |
| `0x01075350` | `extern const float g_rva01075350` | Existing matched four-byte zero data row; retail performs an actual memory `fld` |
| `0x01338748` | `Rva008AE770TheStack.m_count` | Existing canonical stack object, count at offset zero |
| `0x01338750` | `Rva008AE770TheStack.m_rva01338750` | Array pointer at stack-object offset eight |

`game/GameEngine/Source/Common/Rva00C6DCC0StaticInit.cpp` independently binds
`Rva008AE770TheStack` at `0x01338748`. The twelve-byte prefix follows adjacent
matched `game/Libraries/Source/EA/Apt/Rva008C6800.cpp`; the complete provider's
larger object size is not redefined. The old bank's `g_bfmeCount1233` used a
different image base, and its `BfmeZeroRange` was not a canonical binding.
A folded `0.0f` literal would also lose the actual retail memory load.

Loading the array into a local before reading count reproduces the retail
EAX/ECX roles and indexed ESI load. This is a measured correction in native
04 and later trials, independent of the unresolved branch layout.

## Semantics and physical control flow

Zero count returns the fallback object. Valid values in type range 12-19,
and valid type 27, select the true factory. The fallback identity selects
false. Valid types 6/7 enter the coercion dispatch; the other path calls the
numeric-failure predicate, returning false when it succeeds, otherwise
comparing `toNumber()` with the canonical zero. The coercion dispatch keeps
its physical type-5 payload branch, numeric type-6/type-7 branches and
separate default-false branch. These branches must not be removed merely
because the surrounding guards appear to constrain their types.

Retail shares one numeric-conversion block while retaining four factory
call blocks: common false, byte-payload, separate default false and common
true. Distinct compiler-only `_WriteBarrier` and `_ReadWriteBarrier` tags
preserve both false tails in the native trials. The established witnesses
are `stlport_narrow_string_find_char_alias.cpp` (`0x00653990`, 69 bytes) and
`LinePassableStruct_linePassableCallback.cpp` (`0x003E5950`, 203 bytes),
documented in `docs/shape_levers.md`. They support the tail-separation
mechanism, not an exactness claim for this callback.

The residual is the placement of numeric conversion after coercion and
true before default false. The handoff gives exact offsets, jump widths and
raw comparisons. No assembly, dummy runtime operation, shared-header edit,
new binding or modified matched sibling was used to hide this difference.

## Donor evidence and attribution

The BFME 2 reference remains at verified revision
`beed8a16790a6812231ac7b05e3e6893e4cb5d1b`. The earlier bounded donor scan
found no eligible exact callback transfer; that is not an exhaustive
negative claim about all donor opportunities.

Its `docs/recipes.md:646-652` and matched
`Code/GameEngineDevice/Source/MilesAudioDevice/MilesAudioManager.cpp`
`shouldPlayLocally` body at `0x00053BA1` (320 bytes) motivated the explicit
`else` test in variant 08. The referenced landing is `6f35948871`, cited in
`reverse/attempt_support/banked-landings-20261021/readme.md:42`. The donor
has counted-info cleanup and EDI shrink-wrapping absent here; its evidence
supports a bounded arm-ownership experiment, not a BFME 1 source identity.
Variant 08 was a measured null result. Its material contribution to the
investigation still requires the `[BFME 2 donor]` commit-title prefix.
