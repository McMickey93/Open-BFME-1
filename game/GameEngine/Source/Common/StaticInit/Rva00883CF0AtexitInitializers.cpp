// cl: /O2 /MD
// Thirteen retail dynamic initializers no row claimed, each only
// `push teardown; call _atexit; pop ecx; ret`: the registration of a static
// object's teardown. The objects' owning TUs are unknown, so each keeps an
// address-derived name; every teardown is an existing matched body, reached by
// its own free-function name or, for members, a ?b_ address pin.
//
//   0x00883CF0 registers 0x00883CC0  ?rva00883c0@Rva008838F0Owner@@SAXXZ
//   0x00C6AA30 registers 0x00C6FCC0  ?rva00C6FCC0@@YAXXZ
//   0x00C6B710 registers 0x00C6FFE0  ?m@Gen_00c6ffe0@@QAEXXZ
//   0x00C6BE10 registers 0x00C70400  ?Rva00C70400Shutdown@@YAXXZ
//   0x00C6C510 registers 0x00C709F0  ?bfmeDropLockZS@@YAXXZ
//   0x00C6C550 registers 0x00C70A50  ?Rva00C70A50@@YAXXZ
//   0x00C6C560 registers 0x00C70A60  ?Rva00C70A60@@YAXXZ
//   0x00C6C700 registers 0x00C70B80  (empty teardown)
//   0x00C6C7F0 registers 0x00C70BF0  ?m@Gen_00c70bf0@@QAEXXZ
//   0x00C6D8A0 registers 0x00C70C90  ?bfmeForward@Gen_00C70C90@@QAEXXZ
//   0x00C6DBA0 registers 0x00C70E70  ?m@Gen_00c70e70@@QAEXXZ
//   0x00C6DBE0 registers 0x00C70E80  ?bfmeForward_00C70E80@@YAXXZ
//   0x00C6E140 registers 0x00C714B0  ?bfmeGoECF@@YAXXZ

extern "C" int __cdecl atexit(void (__cdecl *)(void));

void Rva00C70B80Empty();   // empty teardown, Rva004C5480EmptyBodies.cpp

void b_00883cc0();
void rva00C6FCC0();
void b_00c6ffe0();
void Rva00C70400Shutdown();
void bfmeDropLockZS();
void Rva00C70A50();
void Rva00C70A60();
void b_00c70bf0();
void b_00c70c90();
void b_00c70e70();
void bfmeForward_00C70E80();
void bfmeGoECF();

void Rva00883CF0Initialize() { atexit(b_00883cc0); }
void Rva00C6AA30Initialize() { atexit(rva00C6FCC0); }
void Rva00C6B710Initialize() { atexit(b_00c6ffe0); }
void Rva00C6BE10Initialize() { atexit(Rva00C70400Shutdown); }
void Rva00C6C510Initialize() { atexit(bfmeDropLockZS); }
void Rva00C6C550Initialize() { atexit(Rva00C70A50); }
void Rva00C6C560Initialize() { atexit(Rva00C70A60); }
void Rva00C6C700Initialize() { atexit(Rva00C70B80Empty); }
void Rva00C6C7F0Initialize() { atexit(b_00c70bf0); }
void Rva00C6D8A0Initialize() { atexit(b_00c70c90); }
void Rva00C6DBA0Initialize() { atexit(b_00c70e70); }
void Rva00C6DBE0Initialize() { atexit(bfmeForward_00C70E80); }
void Rva00C6E140Initialize() { atexit(bfmeGoECF); }
