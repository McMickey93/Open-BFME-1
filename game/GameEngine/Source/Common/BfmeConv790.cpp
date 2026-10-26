// cl: /O1
struct BfmeCsDWD
{
	unsigned char m_bfmeHead[0x18];
};

extern "C" __declspec(dllimport) void __stdcall EnterCriticalSection(BfmeCsDWD *cs);
extern "C" __declspec(dllimport) void __stdcall LeaveCriticalSection(BfmeCsDWD *cs);

namespace ATL
{
	__declspec(noreturn) void __stdcall AtlThrow(long result);
}

struct BfmeThingDWD
{
	BfmeThingDWD(BfmeCsDWD &cs, bool initialLock);
	int bfmeLockDWD();
	void bfmeUnlockDWD();
	void bfmeReleaseDWD();
	BfmeCsDWD *m_bfmeCs;
	char m_bfmeHeld;
};

int BfmeThingDWD::bfmeLockDWD()
{
	EnterCriticalSection(m_bfmeCs);
	m_bfmeHeld = 1;
	return 0;
}

void BfmeThingDWD::bfmeUnlockDWD()
{
	LeaveCriticalSection(m_bfmeCs);
	m_bfmeHeld = 0;
}

void BfmeThingDWD::bfmeReleaseDWD()
{
	if (m_bfmeHeld)
	{
		LeaveCriticalSection(m_bfmeCs);
		m_bfmeHeld = 0;
	}
}


// 0x009F68E3..0x009F6908: four more bodies packed (no int3 padding, like the
// rest of this /O1 run) directly before bfmeLockDWD. Unreferenced in retail;
// address-derived names.

// 0x009F68E3: copies the dword the argument points at into +0, returns this
class Rva009F68E3
{
public:
	Rva009F68E3(const Rva009F68E3 &other);
	int m_0;
};

Rva009F68E3::Rva009F68E3(const Rva009F68E3 &other) : m_0(other.m_0)
{
}

// 0x009F68F0: cdecl, returns its second argument
int Rva009F68F0Second(int, int value)
{
	return value;
}

// 0x009F68F5 / 0x009F68FF: enter / leave the critical section the receiver
// itself is, returning 0
struct Rva009F68F5Section
{
	int enter();
	int leave();
	BfmeCsDWD m_section;
};

int Rva009F68F5Section::enter()
{
	EnterCriticalSection(&m_section);
	return 0;
}

int Rva009F68F5Section::leave()
{
	LeaveCriticalSection(&m_section);
	return 0;
}

// 0x009F6971: binds the section, clears the held flag and, when asked, takes
// the lock at once, throwing through the ATL helper on a failing result.
BfmeThingDWD::BfmeThingDWD(BfmeCsDWD &cs, bool initialLock)
{
	m_bfmeCs = &cs;
	m_bfmeHeld = 0;
	if (initialLock)
	{
		int result = bfmeLockDWD();
		if (result < 0)
			ATL::AtlThrow(result);
	}
}
