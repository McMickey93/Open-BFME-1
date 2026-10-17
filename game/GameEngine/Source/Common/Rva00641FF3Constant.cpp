// Open-BFME: constant return reconstructed from retail RVA 0x00641FF3.
// The dword is the address 0x99 bytes into the matched body
// ?Thread_Function@GameResultsThreadClass@@UAEXXZ (0x00641E70, 387 B, which
// contains it). The plain literal emitted no relocation, so the linker dropped
// this file; naming the body it points into puts the address on the image.

extern "C" const char __identifier("?Thread_Function@GameResultsThreadClass@@UAEXXZ")[];

unsigned int Rva00641FF3Constant()
{
	return (unsigned int)(__identifier("?Thread_Function@GameResultsThreadClass@@UAEXXZ") + 0x99);
}
