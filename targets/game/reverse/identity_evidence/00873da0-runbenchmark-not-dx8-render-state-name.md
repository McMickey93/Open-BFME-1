# 0x00873DA0: `RunBenchmark`, not `DX8Wrapper::Get_DX8_Render_State_Name`

The 673-byte body at 0x00873DA0 was an `__emit` lift named
`?Get_DX8_Render_State_Name@DX8Wrapper@@SAPBDK@Z`. It is BYTEmark's
`RunBenchmark` (C linkage), now compiled from
game/Libraries/Source/Benchmark/nbench0.c.

## Facts

- Calling convention: the only caller, W3DShaderManager's minimum-requirements
  test at 0x0071792B, pushes five arguments (`0, 0, ecx, edx, eax`) and pops
  them itself (`add esp,0x14`). That is a cdecl
  `RunBenchmark(argc, argv, float*, float*, float*)`, the Zero Hour
  benchmark.h entry point. `Get_DX8_Render_State_Name` takes one argument and
  returns a string.
- The body calls `bench_with_confidence` (0x00873CF0, matched in nbench0.cpp)
  and `_CIpow` three times, and brackets the run with
  Get/SetPriorityClass and Get/SetThreadPriority. That is BYTEmark's
  driver loop with EA's priority raise. Nothing in it touches Direct3D.
- symbols.csv already pins `_RunBenchmark` at 0x00873DA0 from that caller.
- Open-BFME-2 matched the same function as `_RunBenchmark` at BFME2 retail
  0x006B3640 (673 bytes, Code/Libraries/Source/Benchmark/nbench0.c). After
  relocation and call-target fields are explained, those bytes are identical
  to BFME1's 0x00873DA0, its only placement in BFME1 .text.
- The address lies inside the nbench0 block, between
  `bench_with_confidence` (0x00873CF0) and the nbench1 functions (0x00874050+),
  well outside the WW3D2 range.
