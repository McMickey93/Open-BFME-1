# RenderInfoClass::~RenderInfoClass at 0x00923880

The 162-byte body at 0x00923880 was ledgered as the placeholder
`?releaseStacks@Rva00923880Owner@@QAEXXZ`
(Common/SmallGaps/Rva00923880ReleaseStacks.cpp), so the pinned
`??1RenderInfoClass@@QAE@XZ` (symbols.csv, 0x00923880) had no definition
(link queue rank 163, 157 B; rinfo.cpp).

- Callers (rel32 scan of retail .text): 0x008FE718 inside the matched
  WW3D::Render and 0x00746CA1 inside the matched
  W3DWaypointBuffer::drawWaypoints call it on their RenderInfoClass
  locals; unwind funclets 0x00C4DDB1 and 0x00C5ABC6 jump to it. Only a
  destructor is reached from both the normal path and an unwind funclet of
  a local.
- Layout: the matched constructor 0x00923690
  (RenderInfoClassConstructorBfme.cpp) sets up exactly the fields the body
  drains. The material-pass array is at +0x24 with count +0xA4 and reject
  count +0xA8 (the inlined Pop_Material_Pass of the matched 0x009237C0).
  BFME's second pass array is at +0x130 with words +0x1B0/+0x1B4.
- Open-BFME-2's matched RenderInfoClass dtor (0x00142FE0, 141 B) is also a
  loop that pops every remaining material pass with Pop_Material_Pass
  inlined, followed by BFME2's own extra teardown. Zero Hour's dtor is
  empty.
