# RVA 0x000D1690: 96-byte element destructor, not WorkerAIUpdateModuleData

Baseline: BFME 1 retail 1.03 unpacked, SHA256 `1fbdc0ced8f283732c094c4f0804ce8dc1e3e3675b720bcab066c94fed964e75`.

The native body at 0x000D1690 is 76 bytes (`ret` at 0x000D169C, then INT3
padding). It is non-polymorphic: it has no vptr store. It first destroys the
28-byte record at receiver+0x44 through the five-byte ILT at 0x0002671F, whose
native jump reaches 0x000CFA40, the independently matched
`??1Gen_000F9C60@@QAE@XZ`. It then releases the AsciiString at receiver+0x00
through `?releaseBuffer@BFMERetailAsciiString@@AAEXXZ` at 0x00887940.

That field layout is the one already proven by the matched 96-byte
`Rva000FB210Element` vector bodies: `Common/Rva000FB2E0Insert.cpp` places an
AsciiString at +0x00 and the 28-byte `Gen_000F9C60` at +0x44, and its matched
copy at 0x000F9FF0 destroys that same +0x44 member. The element is also walked
with a 0x60-byte stride by the matched `vector<BfmeVecElem_000FAFF0>::erase`
body at 0x000FAF90 and by `?bfmeDestroy@Gen_000FAFF0@@QAEXXZ` at 0x000FAFF0;
the latter calls this body through the 0x0002C3BD ILT, and the existing
`??1BfmeVecElem_000FAFF0@@QAE@XZ` pin names that thunk. The body at 0x000D1690
is therefore the element's non-virtual destructor.

WorkerAIUpdateModuleData's true destructor is elsewhere. The 79-byte native
body at 0x00124510 destroys an AudioEventRTS at receiver+0x90 through ILT
0x00026F35 (0x000B31F0), then its base at receiver+0x00 through ILT 0x00029D02.
The Worker constructor at 0x0011BF80 initializes the AudioEventRTS at +0x90,
matching that layout. The existing matched row at 0x00124510 already names the
address-derived `??1Rva00124510@@QAE@XZ`.

The Zero Hour `WorkerAIUpdateModuleData` header used by
`Common/Thing/ModuleFactory.cpp` compiles a same-size COMDAT whose +0x29
relocation names `??1AudioEventRTS@@UAE@XZ` (ledger address 0x000B31F0) and
whose +0x38 relocation names `??1AIUpdateModuleData@@UAE@XZ`, not the
0x0002671F/0x000CFA40 and 0x00887940 targets retail encodes. It is not this
body. This correction retires the false
`??1WorkerAIUpdateModuleData@@UAE@XZ` claim at 0x000D1690 and names the body
with the address-derived element name already used by its callers.

The same class's scalar deleting destructor is the 30-byte body at 0x000D3E80.
It calls the 0x0002C3BD ILT (which jumps to 0x000D1690) and then
`operator delete` at 0x00881EB0, exactly the MSVC 7.1 shape for a non-virtual
class: `push esi; mov esi,ecx; call dtor; test [esp+8],1; jz; push esi;
call operator delete; add esp,4; mov eax,esi; pop esi; ret 4`. A scratch TU
compiled with the retail toolchain (`class X { public: ~X(); ... };
void f(X *p) { delete p; }`) emits `??_GX@@QAEPAXI@Z` with that identical
body, so the element's helper is `??_GBfmeVecElem_000FAFF0@@QAEPAXI@Z`.
ModuleFactory.cpp's ZH stand-in emits the same instruction shape but its call
relocation names `??1WorkerAIUpdateModuleData@@UAE@XZ`; that name's only
candidate pin is 0x000D1690, which is why the false row matched. The real
WorkerAIUpdateModuleData deleting destructor must call the true 0x00124510
destructor instead, so 0x000D3E80 is not the Worker helper.
