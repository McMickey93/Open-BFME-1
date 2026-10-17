// Open-BFME: constant return reconstructed from retail RVA 0x0063F8CD.
// The dword is the address 0x1E5 bytes into the matched body
// ?Thread_Function@BuddyThreadClass@@UAEXXZ (0x0063EB00, 3533 B, which contains
// it). The plain literal emitted no relocation, so the linker dropped this
// file; naming the body it points into puts the address on the image.

extern "C" const char __identifier("?Thread_Function@BuddyThreadClass@@UAEXXZ")[];

unsigned int Rva0063F8CDConstant()
{
	return (unsigned int)(__identifier("?Thread_Function@BuddyThreadClass@@UAEXXZ") + 0x1E5);
}
