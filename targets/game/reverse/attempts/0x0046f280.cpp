// ?getMode@Rva0046F3D0ModeSource@@QAEHXZ
// partial score=0.9922 date=2026-10-17
// ?getMode@Rva0046F3D0ModeSource@@QAEHXZ
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// Retail 0x0046F280 (257 B, thiscall, no stack args): the draw-mode lookup the
// matched Rva0046F3D0DrawImageAt.cpp calls through the pinned
// ?getMode@Rva0046F3D0ModeSource@@QAEHXZ. `this` is the query string handed to
// bfmeGetParamVMZ (0x0046EFA0 via ILT 0x0003C1B4) for key "_mode"; the value is
// matched case-insensitively (_stricmp import, IAT 0x0135933C hoisted to EDI)
// against the six-entry {mode, name} table at VA 0x010F738C
// (SOLID GRAYSCALE ALPHA ADDITIVE SOLID_GRAYSCALE SOLID_TEXTURE = 0..5);
// no match or no value returns 2.
// Status: 257/257 B, 2 differing bytes: at +0x73/+0x7B retail loads the table
// name into EDX, ours ECX (one scratch-rotation step). Landing also needs a data
// row for the table (tools/add_data_match.py) and the key literal "_mode".

#include "string_base.h"
template<> inline bool StringBase<char>::isEmpty() const { return !m_data || m_data->length == 0; }
#include "ascii_string.h"

extern "C" __declspec(dllimport) int __cdecl _stricmp(const char *, const char *);

class BfmeStrVMZ;
char bfmeGetParamVMZ(const char *hay, const char *key, BfmeStrVMZ *out);

typedef int Int;

struct Rva0046F280ModeName
{
	Int mode;
	const char *name;
};

extern const Rva0046F280ModeName g_rva0046F280ModeNames[6] = {
	{ 0, "SOLID" },
	{ 1, "GRAYSCALE" },
	{ 2, "ALPHA" },
	{ 3, "ADDITIVE" },
	{ 4, "SOLID_GRAYSCALE" },
	{ 5, "SOLID_TEXTURE" },
};

class Rva0046F3D0ModeSource
{
public:
	Int getMode(void);
};

Int Rva0046F3D0ModeSource::getMode(void)
{
	AsciiString value;
	if (!bfmeGetParamVMZ((const char *)this, "_mode", (BfmeStrVMZ *)&value) || value.isEmpty())
		return 2;
	for (unsigned int i = 0; i < 6; ++i)
	{
		if (_stricmp(g_rva0046F280ModeNames[i].name, value.str()) == 0)
			return g_rva0046F280ModeNames[i].mode;
	}
	return 2;
}
