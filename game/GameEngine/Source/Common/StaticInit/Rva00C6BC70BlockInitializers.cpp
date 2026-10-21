// cl: /O2 /MD
// Seven retail dynamic initializers no row claimed, each
// `mov ecx, block; jmp 0x00034E00` (the ILT of the matched 28-byte
// constructor ??0Rva00651840@@QAE@XZ, which zeroes eight dwords): construction
// of the 32-byte blocks 0x012F48CC/EC, 0x012F490C (defined here, .bss) and
// 0x012F4A10/30/50/70 (defined by Rva00545D00CopyBlocks.cpp).
// The blocks' real type is unknown, so the constructor runs on each in place
// and every initializer keeps an address-derived name.

struct Rva00651840
{
	Rva00651840();
};

inline void *operator new( unsigned int, void *where ) { return where; }

unsigned int g_Va012F48CC[8];
unsigned int g_Va012F48EC[8];
unsigned int g_Va012F490C[8];
extern unsigned int g_Va012F4A10[8];
extern unsigned int g_Va012F4A30[8];
extern unsigned int g_Va012F4A50[8];
extern unsigned int g_Va012F4A70[8];

void Rva00C6BBA0Initialize() { new( g_Va012F48CC ) Rva00651840; }
void Rva00C6BBB0Initialize() { new( g_Va012F48EC ) Rva00651840; }
void Rva00C6BBC0Initialize() { new( g_Va012F490C ) Rva00651840; }
void Rva00C6BC70Initialize() { new( g_Va012F4A10 ) Rva00651840; }
void Rva00C6BC80Initialize() { new( g_Va012F4A30 ) Rva00651840; }
void Rva00C6BC90Initialize() { new( g_Va012F4A50 ) Rva00651840; }
void Rva00C6BCA0Initialize() { new( g_Va012F4A70 ) Rva00651840; }
