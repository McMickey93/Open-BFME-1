// Open-BFME: constant return reconstructed from retail RVA 0x00660E21.
// The dword is the address 0x9E bytes into the matched body
// ?Thread_Function@PingThreadClass@@UAEXXZ (0x00660C00, 545 B, which contains
// it). The plain literal emitted no relocation, so the linker dropped this
// file; naming the body it points into puts the address on the image.

extern "C" const char __identifier("?Thread_Function@PingThreadClass@@UAEXXZ")[];

unsigned int Rva00660E21Constant()
{
	return (unsigned int)(__identifier("?Thread_Function@PingThreadClass@@UAEXXZ") + 0x9E);
}
