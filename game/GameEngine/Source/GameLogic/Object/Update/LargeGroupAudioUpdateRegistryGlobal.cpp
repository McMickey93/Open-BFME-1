// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD
// The 12-byte tree at VA 0x012EFFA0 that the matched LargeGroupAudio module
// data constructors insert `this` into (as g_lgaGlobal), the matched
// destructor removes it from and bfmeCollectRegisteredKeyMap walks; the
// singleton forwarder 0x00C6FE10 names it TheBfmeObject_00C6FE10. Defining it
// here lets MSVC emit its namespace-scope initializer _$E1, byte-equal to
// retail 0x00C6B120: default-construct through ILT 0x0000B1F9 (body
// 0x00296E10), then atexit 0x00C6FE10, which destroys it through ILT
// 0x000390C7. Class and members stay address-derived.

class Gen_00C6FE10Target
{
public:
	Gen_00C6FE10Target();
	~Gen_00C6FE10Target();

private:
	void *m_header;
	unsigned int m_nodeCount;
	unsigned char m_compare;
};

Gen_00C6FE10Target TheBfmeObject_00C6FE10;
