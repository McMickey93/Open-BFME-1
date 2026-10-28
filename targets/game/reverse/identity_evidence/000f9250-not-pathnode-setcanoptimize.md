# 0x000F9250: not PathNode::setCanOptimize; address-derived name

- Retail 0x000F9250 (10 B): `mov al,[esp+4]; mov [ecx+0x24],al; ret 4`, a
  bool setter at this+0x24. Its only ILT jmp (0x0001764D) has no rel32
  callers, and neither 0x0041764D nor 0x004F9250 appears anywhere in the
  image, so no matched caller names it.
- The old row `?setCanOptimize@PathNode@@QAEX_N@Z` came from AIPathfind.cpp's
  Zero Hour PathNode layout (MemoryPoolObject vptr + m_id ahead of the
  links, m_canOptimize at +0x24). `tools/ilt_oracle.py check` contradicts the
  name at 0x000F9250 (p_false=1.96e-04, outside every window of slots
  12708-12710); it sat in ilt_contradicted_baseline.txt.
- BFME's own PathNode puts m_canOptimize at +0x1C: the matched
  Path::xfer00401C70 (0x00401C70) allocates the node with `push 0x24; call
  new` and stores the xfered canOptimize at [node+0x1C], and the matched
  Pathfinder::prependCells (0x003DD930) inlines setCanOptimize(false) as
  `mov byte [reg+0x1C],0` five times. A +0x24 store would sit past that node.
- Those two TUs emit the +0x1C `?setCanOptimize@PathNode@@QAEX_N@Z` COMDAT,
  which lost against the +0x24 ledger row (link queue #18). With no retail
  out-of-line copy of PathNode::setCanOptimize, the row stops claiming it.
- Nothing proves the class or method, so the body lands as
  `Rva000F9250::set` in game/GameEngine/Source/GameLogic/AI/Rva000F9250.cpp.
