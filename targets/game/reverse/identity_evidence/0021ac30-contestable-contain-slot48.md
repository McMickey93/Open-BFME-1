# 0x0021AC30: ContestableContain primary-vtable slot +0x48

The 0.83 bank called this body `Owner::invoke`, a generic placeholder with no
identity behind it. Retail evidence (BFME 1.03 unpacked):

- The matched `??0ContestableContain@@QAE@PAVThing@@PBVModuleData@@@Z`
  (0x0021BEE0) and `??1ContestableContain@@MAE@XZ` (0x0021B6F0) both store vptr
  0x010AB3C0; its slot +0x48 holds an ILT that jumps to 0x0021AC30.
- OpenContain's primary vtable 0x010AC2B8 holds ILT 0x00005943 -> 0x00228050 in
  the same slot, and 0x0021AC30 calls ILT 0x00005943 on its own `this` as its
  fallback: the usual derived override calling its base.
- Both bodies are thiscall with one Object* argument (ret 4) and return a bool
  in AL.

The method name is not proven (no caller, string or Zero Hour twin names it),
so the owner is address-derived: `Rva0021AC30ContestableContain::method`
overriding `Rva00228050OpenContain::method`.
