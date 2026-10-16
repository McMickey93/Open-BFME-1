# 0x009305D0 is VectorClass<ShaderClass>::VectorClass(int, const ShaderClass *)

Retail was linked without identical-COMDAT folding, so 0x009305D0 (175 B) has one
identity. The ledger gave it to `VectorClass<PointerRemapClass::PtrRemapStruct>`
(pointerremap.cpp) and marked the `VectorClass<ShaderClass>` row (matinfo.cpp)
`icf-owner=`, so RetailTruth skipped the ShaderClass name and judged every caller
that builds a `DynamicVectorClass<ShaderClass>` wrong (link queue #18,
`??0MeshLoadContextClass@@AAE@XZ` 0x00970180).

## The body names its element type

`python3 tools/dis_retail.py 0x009305D0 175`:

- +0x20 stores vtable 0x0113C5E4; +0x5E `lea eax,[edi*4]` / +0x66 `call ??_U`:
  the element is 4 bytes.
- +0x46 and +0x80 push `?j_0001c6fc` (ILT 0x0001C6FC -> 0x006CA410) as the element
  constructor for `` `vector constructor iterator' `` (4 args, no destructor): the
  element has a non-trivial default constructor and no destructor.
- 0x006CA410 is `mov eax,ecx; mov dword ptr [eax],0x0010441B; ret`. 0x0010441B is
  the BFME default ShaderClass bits (shader.h SHIFT_CULLMODE note; `ShaderClass(void)
  { Reset(); }`), and the matched `ShareBufferClass<ShaderClass>` copy ctor row
  (0x0092B810) already names 0x006CA410 the ShaderClass default constructor.

`PtrRemapStruct` (pointerremap.h) has an empty `PtrRemapStruct(void) {}`; its
element constructor cannot store 0x0010441B.

## Every retail caller is a ShaderClass vector

`python3 tools/callers_of.py 0x009305D0`:

- 0x00970180 `MeshLoadContextClass::MeshLoadContextClass` calls it directly and stores
  0x0113C644 at member +0xAC, the `Shaders` member (`DynamicVectorClass<ShaderClass>`
  in Zero Hour meshmdlio.cpp; see 0093d780-dynamic-vector-pointer-ctors.md, which
  already reads the +0xAC table this way).
- 0x00931070 `MaterialCollectorClass::MaterialCollectorClass` calls it and stores
  0x0113C644 (Zero Hour matinfo.cpp: `DynamicVectorClass<ShaderClass> Shaders`).
- 0x00930C50 (ledgered as `DynamicVectorClass<PtrRemapStruct>` ctor) calls it and
  stores the same 0x0113C644, so it is the out-of-line
  `DynamicVectorClass<ShaderClass>` constructor.

dir32_addresses.csv already names 0x0113C644 `_bfmeVftDynamicVectorClassShaderClass`.

## Destructor side

0x00930040 (the `DynamicVectorClass<...>` complete dtor reached from ??_G 0x00930D30)
stores 0x0113C5E4 and frees with `??_V` directly, no element destructor: again an
element type with no destructor, consistent with ShaderClass.

## The 0x000187AF pin is not this body

symbols.csv pinned `??0?$VectorClass@VShaderClass@@@@QAE@HPBVShaderClass@@@Z` to ILT
0x000187AF (pinharvest x1). 0x000187AF is `jmp 0x0013A580`, a 191-byte SEH body that
uses `` `eh vector constructor iterator' `` with constructor ILT 0x35AB7 and destructor
ILT 0x1A41F (an element with a destructor), the matched
`VectorClass<StringClass>` constructor (W3DDisplay.cpp). The ShaderClass pin there is
wrong.

## Correction

- 0x009305D0 -> `??0?$VectorClass@VShaderClass@@@@QAE@HPBVShaderClass@@@Z` (sole
  name); the `VectorClass<PtrRemapStruct>` claim at this address is retired.
- symbols.csv `??0?$VectorClass@VShaderClass@@...` 0x000187AF pinharvest pin retired.
- funclets 0x00C5CE00 / 0x00C5CE11 (retail unwind states 0 and 1 of 0x009305D0's
  FuncInfo) re-homed to matinfo.cpp's labels for the ShaderClass constructor.
- 0x00930C50 ->
  `??0?$DynamicVectorClass@VShaderClass@@@@QAE@IPBVShaderClass@@@Z` (matinfo.cpp);
  the `??0?$DynamicVectorClass@UPtrRemapStruct@PointerRemapClass@@@@QAE@IPBUPtrRemapStruct@PointerRemapClass@@@Z`
  claim at 0x00930C50 is retired. 0x00930C50 calls 0x009305D0 at +0x0F and stores
  0x0113C644 at +0x14, the `DynamicVectorClass<ShaderClass>` table that
  MeshLoadContextClass (+0xAC, `Shaders`) and MaterialCollectorClass also store.

Not changed here (same family, left for a follow-up): `??_G` 0x00930D30 and the
`??1` pin 0x00930040 are still spelled `DynamicVectorClass<PtrRemapStruct>`; by the
same table evidence (0x00930040 stores 0x0113C5E4) they are the ShaderClass
instantiation too.
