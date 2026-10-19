# 0x00873960: BYTEmark `set_request_secs`, not `syncGlobals`

The 56-byte body at 0x00873960 was matched as `?syncGlobals@@YAXXZ` from
game/GameEngine/Source/Common/SmallGaps/syncGlobals.cpp, a name made up for an
unknown "small gap leaf". It is BYTEmark's `set_request_secs` (nbench0.c), now
compiled from game/Libraries/Source/Benchmark/nbench0.cpp.

## Facts

- The body loads one DWORD at VA 0x0135654C and stores it into ten DWORDs.
  Each of the ten is at +4 of a BYTEmark benchmark struct that
  dir32_addresses.csv already records at the base: global_ideastruct
  0x01356340, global_bitopstruct 0x01356360, global_fourierstruct 0x01356380,
  global_huffstruct 0x01356460, global_assignstruct 0x01356480,
  global_strsortstruct 0x013564A0, global_numsortstruct 0x013564C0,
  global_lustruct 0x013564E0, global_nnetstruct 0x01356500 and
  global_emfloatstruct 0x01356560. +4 is `request_secs` in each.
  nbench0.c's `set_request_secs` copies `global_min_seconds` into exactly
  these ten fields.
- The compiled `set_request_secs` from nbench0.cpp is byte-equal to retail.
- The address lies inside the nbench0 block, just before `getscore`
  (0x008739A0), `output_string`, `calc_confidence`, `bench_with_confidence`
  and `RunBenchmark` (0x00873DA0), all matched from nbench0.cpp.
- Open-BFME-2 matched the same body as `?set_request_secs@@YAXXZ` at BFME2
  retail 0x006B3200, also from nbench0.cpp.

The 0x0135654C source datum is therefore `global_min_seconds`. Its data row
moves to that name, and the ten address-named int rows syncGlobals.cpp defined
inside the structs are dropped, since the struct names already cover them.
