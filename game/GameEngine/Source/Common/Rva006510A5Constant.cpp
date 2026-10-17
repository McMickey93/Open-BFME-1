// Open-BFME: constant return reconstructed from retail RVA 0x006510A5.
// The dword is the address 0x150F bytes into the emitted body of the matched
// ?Thread_Function@PeerThreadClass@@UAEXXZ (0x0064FB90, 5316-byte row whose
// 5508-byte emitted extent carries the catch funclets at 0x00651054 and
// 0x006510A5), so it is inside that body. The plain literal emitted no
// relocation, so the linker dropped this file; naming the body puts the address
// on the image.

extern "C" const char __identifier("?Thread_Function@PeerThreadClass@@UAEXXZ")[];

unsigned int Rva006510A5Constant()
{
	return (unsigned int)(__identifier("?Thread_Function@PeerThreadClass@@UAEXXZ") + 0x150F);
}
