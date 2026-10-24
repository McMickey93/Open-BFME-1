// cl: /O2 /DNDEBUG /MD
//
// Small bodies that nothing calls directly: each is reached only through an
// absolute address stored by already-matched code or tables. Names keep the
// address; no owner or semantic identity is claimed.

// 0x00651800: callback registered by BFMENetworkBackend::dispatchEvents
// (DIR32 0x0065CDEF); only its seventh argument is used, a counted object
// whose +0x54 count is released.
struct Rva00651800Counter
{
	char m_padding[0x54];
	int m_count;
};
void __cdecl Rva00651800(int, int, int, int, int, int, Rva00651800Counter *counter)
{
	if (counter)
		--counter->m_count;
}

// 0x00883210: entry of the function table at 0x00EA6070; sets a byte flag.
extern unsigned char g_Va01336CE4;
void Rva00883210()
{
	g_Va01336CE4 = 1;
}

// 0x00AFE910: lookup callback handed out by GameSpy peer's piGetRoomKeysCopy
// (DIR32 0x0085DBE1); returns one dword of the table at 0x012E6040.
extern int g_Va012E6040[];
int __cdecl Rva00AFE910(int index)
{
	return g_Va012E6040[index];
}

// 0x00C6C7D0: CRT startup-table entry at RVA 0x00EA5ADC. The complete
// body stores this dword at VA 0x0130A44C, returns at +0x0A, then reaches
// INT3 padding at +0x0B. Keep the raw value; its owning type is unproven.
extern unsigned int g_Va0130A44C;
void Rva00C6C7D0()
{
	g_Va0130A44C = 0x3E4CCCCD;
}

// 0x00C6C7E0: the next CRT startup-table entry, RVA 0x00EA5AE0.
// RET at +0x0A and INT3 at +0x0B bound the complete dword store.
extern unsigned int g_Va0130A454;
void Rva00C6C7E0()
{
	g_Va0130A454 = 0x3D088889;
}

// 0x00C6AA40: CRT startup-table entry at RVA 0x00EA565C publishes the
// static holder at VA 0x012A7A4C through the canonical map-list pointer.
// See identity_evidence/012ed5dc-object-pointer.md for the independently
// decoded writer and readers. RET+0x0A / INT3+0x0B prove the 11-byte extent.
class BfmeMapObjectListHolder;
extern BfmeMapObjectListHolder *BfmeTheMapObjectListHolder;
extern BfmeMapObjectListHolder g_Va012A7A4C;
void Rva00C6AA40()
{
	BfmeTheMapObjectListHolder = &g_Va012A7A4C;
}
