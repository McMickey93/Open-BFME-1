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
