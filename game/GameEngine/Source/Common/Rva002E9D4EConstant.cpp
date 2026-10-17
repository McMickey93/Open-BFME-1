// Open-BFME: constant return reconstructed from retail RVA 0x002E9D4E.
// The dword is the address 0x261 bytes into the matched body ?d_002e9aa0@@YAXXZ
// (0x002E9AA0, 686 B, which contains it). The plain literal emitted no
// relocation, so the linker dropped this file; naming the body it points into
// puts the address on the image.

extern "C" const char __identifier("?d_002e9aa0@@YAXXZ")[];

unsigned int Rva002E9D4EConstant()
{
	return (unsigned int)(__identifier("?d_002e9aa0@@YAXXZ") + 0x261);
}
