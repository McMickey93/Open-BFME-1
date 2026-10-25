# Recorded references and vtable owners, ninth batch

Shard 1/5 repair queue served this entry in `Rva012ED4F0Global.cpp` and `Rva00C6GapCallbacks.cpp`.

| Retail VA | Retired reference | Repair / Existing recorded owner | Source TU |
| --- | --- | --- | --- |
| 0x012ED4F0 | `?g_rva012ED4F0@@3VAsciiString@@A` | Reference recorded owner `_g_bfmeHostVSF` (`g_bfmeHostVSF`) | `game/GameEngine/Source/Common/StaticInit/Rva012ED4F0Global.cpp`, `game/GameEngine/Source/Common/StaticInit/Rva00C6GapCallbacks.cpp` |

The owner `_g_bfmeHostVSF` is recorded in BFME 1's `dir32_addresses.csv` and `symbols.csv`.
Only placeholder external symbol references were updated to use the recorded name;
underlying type (`AsciiString`), layout, dynamic initializer, cleanup callback and ABI are preserved.

The exact keyed `repair_queue.py pass-test` succeeded and alone removed its baseline line.
Baseline entries shrink 882 -> 881. No escape hatches, header modifications or linked byte credits claimed.
