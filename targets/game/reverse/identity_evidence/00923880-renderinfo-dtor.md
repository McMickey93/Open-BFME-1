# 0x00923880 is RenderInfoClass::~RenderInfoClass

- The WW3D::Render unwind funclet 0x00C5ABC0 (`lea ecx,[ebp-0x1d4]; jmp
  0x00923880`) destroys the function's RenderInfoClass local; compiled from
  WW3DRenderScene.cpp it is `$L12392`, whose jmp names
  `??1RenderInfoClass@@QAE@XZ`.
- Matched WW3D::Render (call at 0x008FE718) and matched
  W3DWaypointBuffer::drawWaypoints (call at 0x00746CA1) call 0x00923880 on
  their RenderInfoClass locals at normal scope exit.
- The body's first loop is Pop_Material_Pass (0x009237C0) inlined
  (`RejectedMaterialPasses` +0xA8, `AdditionalMaterialPassCount` +0xA4,
  array +0x24); the second drains BFME's second 32-entry stack at +0x130.
  It sits in the rinfo.cpp cluster (0x00923690 ctor .. 0x009237C0).

The ledger row keeps its opaque alias `releaseStacks@Rva00923880Owner`; only
the pin names the real destructor.

pin-identity-override: ??1RenderInfoClass@@QAE@XZ 0x00923880 caller=0x00746A30 matched W3DWaypointBuffer::drawWaypoints destroys its RenderInfoClass local by calling 0x00923880 (site 0x00746CA1); matched WW3D::Render does the same at 0x008FE718 and its unwind funclet 0x00C5ABC0 jumps there
