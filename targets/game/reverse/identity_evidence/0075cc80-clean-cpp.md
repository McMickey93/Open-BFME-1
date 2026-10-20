# 0x0075CC80 render-kind update in clean C++

Retail 0x0075CC80..0x0075CDD4 (340 bytes; plain `ret` exits at +0x134 and
+0x153). The extent is the one the MASM dump
`game/masm_dumps/Rva0075CC80RenderKindUpdate.asm` carried as the placeholder
`?Rva0075CC80@@YAXXZ` (see `0075cc80-masm-codegen-blocker.md`).

## Identity and ABI

- No caller, vtable or string names the body, so the name stays
  address-derived. The placeholder's free `void()` decoration was never ABI
  evidence: retail opens with `mov esi,ecx` and reads this+0xDC, +0xF8, +0x08,
  +0x34, +0xA0 and +0xA4, and both exits are a plain `ret`, so the body is a
  `__thiscall` member with no stack arguments. It lands as
  `?rva0075CC80@Rva0075CC80Owner@@QAEXXZ` (address-derived class and method;
  `ilt_oracle` classifies it as a placeholder, as it did the old name).
- The body is unchanged from the evidence file: early-outs on +0xDC/+0xF8,
  drawable (+0x08) and render object (+0x34) guards, render kind from the
  render object's slot +0x140, the pending arm through 0x0075B4A0 and the
  pending drawable update, and the main arm's camera-vector (tactical view slot
  +0x118) minus drawable position (ILT 0x0004B12D) distance classification
  against data+0x100/+0x104, ending in the slot +0x138 call for kind 3.

## The two register bytes

The MASM dump existed because VC7.1 emitted EAX as the vtable temporary of the
slot +0x138 call where retail has `mov edx,[ecx]; call [edx+0x138]`. The
documented typed vtable-slot lever (docs/shape_levers.md, "Vtable
register-temp call shape") closes it once the slot pointer is a three-argument
`__fastcall` view: ECX = the render object, EDX = the table (register only),
and the level as the one stack argument (`push edi`), matching the slot's
`__thiscall` contract of one stack argument. The earlier two-argument trial
moved the level into EDX; the three-argument form keeps it on the stack.
`tools/probe.py` reports EXACT (modulo relocation slots), 340/340, 6
relocations.

## Callee binding

The drawable position call (ILT 0x0004B12D, body 0x0041D090, ledger
`?get@BFMERopeDrawableGetPositionShim@@QBEPBUCoord3D@@XZ`) is spelled through
that shim; because WWMath `coord3d.h` declares Coord3D with the class key, the
TU emits the `VCoord3D` decoration, bound by one `abi-view=` pin
(`?get@BFMERopeDrawableGetPositionShim@@QBEPBVCoord3D@@XZ`, same thiscall and
`ret`). `tools/abi_view.py --check` and `tools/pin_consistency.py --check` pass.
