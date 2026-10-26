# Three visibility consumers of the existing 0x00410BA0 owner

Selected by `tools/link_check.py next --no-claim` at BFME 1
`179d0eb2814d08eaccab76f5c4f78bb7c4ad1467`, census `5cba370cb6`.
The queued `Drawable::isDrawableEffectivelyHidden` name is not the existing
29-byte owner: `Gen_00410BA0::isDrawableEffectivelyHidden() const` in
`Bfme5TinyTwentySeven.cpp` returns int, exactly 0 or 1. Its placeholder class
name is retained. No new pin, alias or function row is introduced.

## Target facts

The original consumers call ILT RVA `0x00012E3B`, which jumps to `0x00410BA0`:

| Consumer | Call RVA | Complete row bytes | Return use |
| --- | --- | ---: | --- |
| GameClientRva00431A60Frustum.cpp | 0x00431B33 | 357 | AL copied to CL, neg/sbb/inc |
| W3DTankTruckDrawCreateEmitters.cpp | 0x0077FE79 | 436 | test AL,AL |
| RTS3DSceneRva00713780.cpp | 0x007138B9 | 2,491 | cmp AL,1; save AL |

Existing `Rva002494D0FindClosest.cpp` and its two archived siblings already
reference the canonical int owner and consume its low byte. Apply that proven
binding to these callers. The RTS saved result is explicitly unsigned char,
retaining the original low-byte storage without an extra bool normalization.

The first direct unsigned-char cast left one raw-byte mismatch in the frustum
caller: compiled `8B C8` (mov ECX,EAX), retail `8A C8` (mov CL,AL). Both other
callers passed. A complete-class member-pointer return view referencing the
canonical int designator preserves this caller's witnessed bool-in-AL ABI and
restores all 357 bytes. This is a target-specific MSVC x86 ABI adapter: the
provider is independently verified to return only 0/1. Do not infer that an
arbitrary int-returning function can be called through a bool result view.

## Donor review and freshness

BFME 2 `RTS3DSceneRenderOneObject.cpp` uses its existing `Rva00270260` owner
behind the analogous visibility helper. Reviewed donor `3252f8ecf0` and current
`13cfa404dfe65a062e2e5effe030ff826b905adc`; that source is unchanged between
them. Its address and class view are not transplanted. The target's existing
owner, original call sites and earlier BFME 1 consumers determine this repair.
The BFME 2 donor pointer advances to that reviewed revision without recursion.
`header_dependents.py --staged` for this pointer change returns 0 with no
affected BFME 1 build inputs; these units use BFME 1's own headers/toolchain.
No BFME 2 compiler, nested reference or shim replaces a BFME 1 dependency.

## Native verification and remaining link prerequisite

Windows/MSVC 7.1 run [40355346701](https://github.com/McMickey93/Open-BFME-1/actions/runs/40355346701),
control `8e8a564fdc8e7e56644d5dcad7a14892f81ce26e`, verifies all eight rows
of the three callers plus their owner before and after the final change;
three data rows, five float references and 20 DIR32 references also pass.
All declared functions are already matched. Existing flags are unchanged.

The ordinary before-link preview in run `40353079647` uses index `5cba370cb6`
but is **UNKNOWN**: 22,663 ledger objects cannot be refreshed on the scoped
host. It proves no linked-byte gain or selected-provider clearance. Do not
repeat that unchanged broad scan; use the next current census/object set to
check the three consumers together with the canonical owner. The source-level
references and complete bytes are verified; the family remains open for this
link confirmation. No C++ coverage or census linking credit is claimed.

Final experiment artifact `12664549750`, ZIP SHA-256:
`c3ac4bed504c153702b88e5579e92185ebfdb7f8e94868b9931709a635f8973b`.
The preceding run retains the unsuccessful direct-cast diagnostic and the
UNKNOWN link preview. Normal commit and outgoing hooks qualify the exact
proposed commit separately before publication.
