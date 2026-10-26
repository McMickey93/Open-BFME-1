// cl: /DNDEBUG /MD /EHsc /Iinputs/reference/shims/ini /Igame/Libraries/Source/WWVegas/WWLib
// Retail 0x0013B990, 321 bytes: the sole caller 0x0013C720 fills a 0x48-byte record per
// module-info row and condition entry; ecx is that caller's this, and ret 0x14 gives five args.

#include "Common/AsciiString.h"
#include "wwstring.h"
#include "vector.h"

// Name table whose first entry is "UNSPECIFIED", indexed by the signed byte at source +0x496.
extern const char *const ThingClassNames012AC510[];

// View of the record the matched Rva0013A820::reset clears (strings at +0x00..+0x10, +0x1C).
class Rva0013A820
{
public:
	void reset();

	AsciiString m_00;
	AsciiString m_04;
	AsciiString m_08;
	AsciiString m_0C;
	AsciiString m_10;
	int m_14;
	int m_18;
	AsciiString m_1C;
};

// The caller passes one 20-byte-row table to both matched row getters.
class Rva0013B2F0StringTable
{
public:
	AsciiString getField0(int index) const;
};

class Rva0013B370StringTable
{
public:
	AsciiString getField4(int index) const;
};

// The 0x128-byte condition entry: the matched accessor reads +0x28/+0x2C, this body +0x34.
class Gen_007622C0
{
public:
	AsciiString method() const;

	unsigned char m_unreconstructed_00[0x34];
	AsciiString m_34;
};

class Rva0013B990Template
{
public:
	unsigned char m_unreconstructed_00[0x20];
	AsciiString m_20;
	unsigned char m_unreconstructed_24[0x472];
	char m_496;
};

class Rva0013C720Owner
{
public:
	bool build(Rva0013A820 *out, const Rva0013B2F0StringTable *moduleInfo,
		const Rva0013B990Template *source, const Gen_007622C0 *entry, int index);
	bool rva0013BE40(Rva0013A820 *out, int index);
};

bool Rva0013C720Owner::build(Rva0013A820 *out, const Rva0013B2F0StringTable *moduleInfo,
	const Rva0013B990Template *source, const Gen_007622C0 *entry, int index)
{
	out->m_00.set(source->m_20);
	out->m_04 = ThingClassNames012AC510[source->m_496];
	out->m_08 = moduleInfo->getField0(index);
	out->m_0C = reinterpret_cast<const Rva0013B370StringTable *>(moduleInfo)->getField4(index);
	out->m_10 = entry->method();
	out->m_1C.set(entry->m_34);
	if (out->m_10.isEmpty())
	{
		out->reset();
		return false;
	}
	return true;
}

// Retail 0x0013BE40, 152 bytes through RET 8. The same caller 0x0013C720 reaches it
// through ILT 0x00038EF1 with the ecx and record pointer it gives build(), plus that
// call's index. Neither argument is read: the body builds an empty
// DynamicVectorClass<StringClass> (ILT 0x000187AF to the matched base ctor, vtable
// 0x01091078) and an empty string, then destroys both. Retail's unwind map has three
// states, the third with no cleanup action: a destructible local in code the
// optimizer dropped. A loop over the still-empty list reproduces it, and its extra
// state store is why retail keeps zero in ebx. What that loop did is not recoverable.
bool Rva0013C720Owner::rva0013BE40(Rva0013A820 *out, int index)
{
	DynamicVectorClass<StringClass> list;
	AsciiString tmp;
	for (int i = 0; i < list.Count(); ++i)
	{
		AsciiString item;
	}
	return true;
}
