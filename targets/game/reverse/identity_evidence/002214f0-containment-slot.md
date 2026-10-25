# RVA 002214F0: shared containment interface method

## BFME 1 identity and boundary

Target: retail 1.03 unpacked, RVA `0x002214F0`, 62 bytes, replacing
`?d_002214f0@@YAXXZ`. The bounds-high dump is in
`game/gen_asm/d_00218ee0.asm`. Independent retail decoding ends with
`pop ecx` at 0022152A and `ret 0xC` at 0022152B; the next byte,
0022152E, begins INT3 padding through 0022153F. There are no calls,
relocations, string references, globals or jumps outside this extent.

The existing ILT thunk at 0003B7C8 jumps to this body. `vtable_lookup.py
--target 0x002214F0 --slots 44` finds it at slot +0x98 in multiple
containment interface tables. For example, the table at VA 010AAD80 is
installed by the independently matched CaveContain constructor 00219B90
and destructor 00219290. This establishes subsystem placement, not a
unique defining class or an EA member name. The reconstruction therefore
keeps `Rva002214F0::method` and does not adopt the old bank's guessed `set`
name or its claim that ContestableContain uniquely owns this method.
The existing containment TU houses the opaque receiver view; its named
ContestableContain class is unchanged.

## ABI, layout and behavior

ECX is the receiver. `ret 0xC` and the three stack inputs establish a
thiscall member with two pointers and a middle 32-bit integer. Retail
performs a signed comparison against 1, selects the address of either
that argument or a local 1, then reads the selected integer. It reads a
32-bit value at argument 1 +0x74 before storing the clamp at receiver
+0xA4, stores that first value at receiver +0x9C, and reads argument 3
+0x74 into receiver +0xA0. These offsets and this access order come from
the target instructions. Signedness of the copied fields and the actual
source/receiver class identities remain unproven; the layout names stay
opaque and address-derived. No canonical class is redeclared.

## Compiler recovery

The existing 0.79 bank already gave the correct 62-byte length but 13
non-relocation bytes differed: VC7.1 scheduled the first +0x74 load after
the +0xA4 store and rotated scratch registers. Loading the selected clamp
through `const volatile int *`, then materializing its value and the
first source value before the stores, reproduces the target instruction
order and all 62 bytes. Only that local access is volatile; the receiver
and source fields remain ordinary integers. This reads a stack argument
or stack local once and introduces no new externally accessed storage.

Private probes: build/seat-convert-20261025-resume/setter/maxload.cpp and
home.probe. Both the /O2 /Ob0 isolated trial and the unchanged home-TU
/O2 /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB context are exact with zero
relocations. Reordered ordinary-local, const-source and /Oa trials kept
the old 13-byte residue. Making just the source field volatile produced
17 differences. The successful lever is narrowly evidenced for this
method, not an inferred original source spelling or a general rule.

BFME 2 reference sources and recipes were searched for the containment
family; no donor implementation establishes this method's identity or
supplies this recovery. This landing uses BFME 1 target evidence and the
existing BFME 1 bank.
