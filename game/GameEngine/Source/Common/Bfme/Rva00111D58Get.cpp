// cl: /DNDEBUG /MD /EHsc
// Open-BFME: constant return reconstructed from retail RVA 0x00111D58.
// The dword is the address 0xF8 bytes into the matched body
// ?addGameToAvailableList@@YAXVAsciiString@@PAX@Z (0x00111C40, 280 B, which
// contains it, and which dir32_addresses.csv already records at 0x00511C40).
// The plain literal emitted no relocation, so the linker dropped this file;
// naming the body it points into puts the address on the image.

extern "C" const char __identifier("?addGameToAvailableList@@YAXVAsciiString@@PAX@Z")[];

void *Rva00111D58Get()
{
	return (void *)(__identifier("?addGameToAvailableList@@YAXVAsciiString@@PAX@Z") + 0xF8);
}
