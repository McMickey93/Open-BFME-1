# Collision sorter linking task — 2026-10-20

Queue entry #4: `?rva009A2750@CollisionManagerImpl@@QAEXXZ`, blocking
`game/Libraries/Source/collisionmanager/collisionmanager_impl.cpp`.

The matched `CollisionManagerImpl::UpdateSort` calls the sorter with its receiver
in ECX and no stack arguments. Retail RVA `0x009A2750` has a 460-byte body ending
in `ret` at `0x009A291B` (exclusive end `0x009A291C`). `callees.py` finds no direct
calls. The ledger still points to the generated assembly dump, so this is a
missing readable body rather than a name-only repair. No alias or thunk
substitution was attempted.

The existing bank `targets/game/reverse/attempts/0x009a2750.cpp` implements the
four-run bottom-up endpoint merge. A fresh probe reproduces its previous result:
460 bytes, 263 differing bytes, instruction-shape similarity 0.937. Its stack
frame is `0x50` bytes; retail allocates `0x4C`. The generated code also retains
an input-stride spill that retail recomputes.

Twelve bounded variants were compiled against the same baseline and MSVC 7.1
flags. Differences below count unequal positional bytes plus a length penalty;
there are no relocation slots in this function.

| Change from the existing bank | Compiled bytes | Differences |
| --- | ---: | ---: |
| Share tail/count append after the empty/nonempty branches | 470 | 354 |
| Increment the known-zero destination count | 460 | 263 |
| Reset counts through the output index | 460 | 263 |
| Declare the run array before the outer axis loop | 460 | 263 |
| Declare destination before the two merge counters | 460 | 266 |
| Declare right input before left input | 460 | 263 |
| Walk an explicit axis-head pointer | 460 | 280 |
| Store runs as a two-by-two array | 457 | 342 |
| Use signed input/output indices | 460 | 263 |
| Declare merge width before input index | 460 | 269 |
| Use a signed run count | 460 | 263 |
| Reverse the output-count reset order | 460 | 263 |

None improves the bank. The explicit-axis-pointer trial initially failed to
compile because its generated pointer expression needed parentheses; the table
records the corrected, successfully compiled version.

Before the attempt, `link_check.py collisionmanager_impl.cpp` reports the sorter
unresolved and LINKED 0 -> 0 bytes. It also reports PREVIEW UNKNOWN because the
local census cannot prove current selection. The attempt leaves game source and
the preferred bank unchanged. No matched or linked code bytes are claimed.

Reproduction entrypoint:

```sh
python3 tools/callees.py 0x009A2750 460
python3 tools/dis_retail.py 0x009A2750 460
python3 tools/probe.py targets/game/reverse/attempts/0x009a2750.cpp '?merge@Rva009A2750Owner@@QAEXXZ' 0x009A2750 --size 460 --all
```

Outcome: blocked on stack-slot/stride code generation after these twelve shapes.
