// cl: /DNDEBUG /MD /EHsc
// Open-BFME: constant return reconstructed from retail RVA 0x0006063C.
// The dword is the address 0x3E3 bytes into the matched body
// ?d_000600f0@@YAXXZ (0x000600F0, 1356 B, which contains it). The plain literal
// emitted no relocation, so the linker dropped this file; naming the body it
// points into puts the address on the image.

extern "C" const char __identifier("?d_000600f0@@YAXXZ")[];

void *Rva0006063CGet()
{
	return (void *)(__identifier("?d_000600f0@@YAXXZ") + 0x3E3);
}
