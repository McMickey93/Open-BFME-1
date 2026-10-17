// Retail 0x005C6400 and 0x005C6520..0x005C65E0 (23 B each): eight file-static setters
// that delete the owned polymorphic object in one of eight consecutive pointer fields
// (+0xA0..+0xBC) and store the replacement. None has a direct retail caller (every use is
// inlined), so the owner and the setters keep address-derived names. As file-statics they
// take retail's private convention: the owner in ESI, the replacement in EDI.
class Rva005C6400Owned
{
public:
	virtual ~Rva005C6400Owned();
};

class Rva005C6400Owner
{
public:
	char m_pad[0xA0];
	Rva005C6400Owned *m_owned[8];	// +0xA0
};

// ?rva005C6400@@YAXPAVRva005C6400Owner@@PAVRva005C6400Owned@@@Z (+0xA0)
static __declspec(noinline) void rva005C6400(Rva005C6400Owner *owner, Rva005C6400Owned *owned)
{
	delete owner->m_owned[0];
	owner->m_owned[0] = owned;
}

// ?rva005C6520@@YAXPAVRva005C6400Owner@@PAVRva005C6400Owned@@@Z (+0xA4)
static __declspec(noinline) void rva005C6520(Rva005C6400Owner *owner, Rva005C6400Owned *owned)
{
	delete owner->m_owned[1];
	owner->m_owned[1] = owned;
}

// ?rva005C6540@@YAXPAVRva005C6400Owner@@PAVRva005C6400Owned@@@Z (+0xA8)
static __declspec(noinline) void rva005C6540(Rva005C6400Owner *owner, Rva005C6400Owned *owned)
{
	delete owner->m_owned[2];
	owner->m_owned[2] = owned;
}

// ?rva005C6560@@YAXPAVRva005C6400Owner@@PAVRva005C6400Owned@@@Z (+0xAC)
static __declspec(noinline) void rva005C6560(Rva005C6400Owner *owner, Rva005C6400Owned *owned)
{
	delete owner->m_owned[3];
	owner->m_owned[3] = owned;
}

// ?rva005C6580@@YAXPAVRva005C6400Owner@@PAVRva005C6400Owned@@@Z (+0xB0)
static __declspec(noinline) void rva005C6580(Rva005C6400Owner *owner, Rva005C6400Owned *owned)
{
	delete owner->m_owned[4];
	owner->m_owned[4] = owned;
}

// ?rva005C65A0@@YAXPAVRva005C6400Owner@@PAVRva005C6400Owned@@@Z (+0xB4)
static __declspec(noinline) void rva005C65A0(Rva005C6400Owner *owner, Rva005C6400Owned *owned)
{
	delete owner->m_owned[5];
	owner->m_owned[5] = owned;
}

// ?rva005C65C0@@YAXPAVRva005C6400Owner@@PAVRva005C6400Owned@@@Z (+0xB8)
static __declspec(noinline) void rva005C65C0(Rva005C6400Owner *owner, Rva005C6400Owned *owned)
{
	delete owner->m_owned[6];
	owner->m_owned[6] = owned;
}

// ?rva005C65E0@@YAXPAVRva005C6400Owner@@PAVRva005C6400Owned@@@Z (+0xBC)
static __declspec(noinline) void rva005C65E0(Rva005C6400Owner *owner, Rva005C6400Owned *owned)
{
	delete owner->m_owned[7];
	owner->m_owned[7] = owned;
}

// ?rva005C6400Callers@@YAXPAVRva005C6400Owner@@PAVRva005C6400Owned@@@Z absent-from-retail
// TU-local caller that keeps the statics above alive.
void rva005C6400Callers(Rva005C6400Owner *owner, Rva005C6400Owned *owned)
{
	rva005C6400(owner, owned);
	rva005C6520(owner, owned);
	rva005C6540(owner, owned);
	rva005C6560(owner, owned);
	rva005C6580(owner, owned);
	rva005C65A0(owner, owned);
	rva005C65C0(owner, owned);
	rva005C65E0(owner, owned);
}
