// cl: /O2 /MD
// Address-derived data owner: dir32_addresses.csv records
// ?TheBfmeObject_00C6FE50@@3VGen_00C6FE50Target@@A at VA 0x012F0770 and
// retail .data holds zero bytes there. The next recorded datum
// (g_rva00339a80Sink, 0x012F0778) bounds this unowned cell to 8 B; matched
// ScriptEngine code also addresses +4/+8 of the same storage as an overlay,
// and the separately owned sink cell covers the +8 dword.

class Gen_00C6FE50Target
{
public:
	unsigned char m_storage[8];
};

Gen_00C6FE50Target TheBfmeObject_00C6FE50;
