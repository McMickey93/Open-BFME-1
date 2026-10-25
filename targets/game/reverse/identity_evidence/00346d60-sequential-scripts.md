# ScriptEngine sequential progression and erase ABI

Parent: RVA 0x00346D60, 1950 bytes; RET at +0x79D and INT3 at +0x79E.
The established ScriptEngine update caller uses ILT 0x0000FCBD to this body.
GeneralsMD ScriptEngine.cpp supplies the semantic guide. BFME 2's verified
ScriptEngineEvaluateAndProgressAllSequentialScripts.cpp (0x0020C83F), reviewed
at ce1b975697c2f20e514174e3875f8820d1dba612, supplies structural leads. Its mode
flags, layouts, cleanup signature and additional AI writes are not BFME 1 facts.

The old bank emitted 1856 bytes with 57 relocations and 1227 masked differences.
A new combination emits 1950 bytes with no non-relocation differences:
advance flag with positive waits inhibited, negative waits testing readiness,
zero advancing; retain positive-wait decrement at loop tail; force-inline
cleanup including deletion loops; keep non-null dangling erase opaque; use a
negated default-team guard around cleanup followed by one continue to share EH
cleanup tails. Include canonical AsciiString and expose the existing native
StringBase concat implementation locally; no shared header changes.

## Provider proof and narrowly scoped ledger repair

The 43-byte body at 0x00339D10 is already rowed as dup_339d10 via a ScienceInfo
vector erase copy. That byte-identical copy does not establish the original
instantiation. The old plain-text label also declares no fixed ABI. No original
template type is recovered here. Preserve one address owner and the existing
object-symbol mechanism; repoint its backing object to the exact caller-emitted
copy and name the witnessed ABI by its address. Do not add guessed template pins.

The complete body: ECX is a three-pointer vector view, the one stack argument
is a position. Compare end at receiver+4 with position+4; if unequal call IAT
memmove(position, position+4, end-position-4). Decrement end by four, return the
original position in EAX, RET4 at +0x28. No record is dereferenced.
Four decoded parent instructions, 0x00346E9E / 0x00347395 / 0x003473FA /
0x00347470, encode ILT 0x0003F99F and reach 0x00339D10. The established append
body and parent array accesses separately establish pointer-sized record entries.

Private proof in attempt_support/00346d60-20261024/private-provider-proof.json
confirms the caller and emitted erase copy reproduce their complete extents,
with all REL32 operands resolved against the existing map plus the proposed
erase association. This private map was never installed in the verifier or
ledger. DIR32/string/constant/EH checks remain required in the normal gate.
The proposed mangled member signature is __thiscall, pointer return, one pointer
argument, exactly agreeing with decoded ECX, EAX and RET4. Original element
identity remains explicitly unproven; Bfme5CtorA0 is a pre-existing compilation
view. No new recovered bytes are credited for repointing this existing provider.

The ScienceInfo source and its other matched rows are unchanged and must still
verify. The row count and object-symbol binding count do not increase for this
provider repair. Normal add_match verification is mandatory; no gate exception,
identity override, extra alias pin or baseline growth is proposed.
