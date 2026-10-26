// cl: /DNDEBUG /MD
// Retail 0x00887000 (14 B narrow tolower) and 0x00887010 (11 B wide
// towlower): file-static single-character case wrappers. File-static
// scope is what keeps the narrow argument as (movsx eax,al / push
// eax) instead of loading it from the stack. The wide one returns
// towlower's unsigned short unchanged (no movzx), so it is declared
// that way.

extern "C" __declspec(dllimport) int __cdecl tolower(int value);
extern "C" __declspec(dllimport) unsigned short __cdecl towlower(unsigned short value);

static int Rva00887000Narrow(char value)
{
	return tolower(value);
}

static unsigned short Rva00887010Wide(unsigned short value)
{
	return towlower(value);
}

// Visible call sites so both statics are emitted; not claimed.
void Rva00887000Keep(char value, unsigned short wide)
{
	Rva00887000Narrow(value);
	Rva00887010Wide(wide);
}
