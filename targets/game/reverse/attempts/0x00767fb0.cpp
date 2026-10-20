// ?rva00767FB0@W3DModelDraw@@UAEXPAVAsciiString@@H@Z
// partial score=0.2019 date=2026-10-20
// cl: /DNDEBUG /DWIN32 /MD /EHsc /D_STLP_USE_STATIC_LIB /Igame/Libraries/Source/WWVegas/WWLib
// stlport
// Open-BFME: retail 0x00767FB0 (639 bytes, ret 8), a W3DModelDraw virtual:
// primary-vtable slot 53 of the seven W3DModelDraw-family tables (ILT
// 0x0003116A). It writes the two 24-byte permission lists at +0x58 and +0x4C
// into `out` as "+Perm:%s"/"-Perm:%s" and then "+%s"/"-%s" entries, separated
// by ", " with a newline every `perLine` entries. The method keeps the
// address.

#define _STLP_NO_EXCEPTIONS 1
#include <vector>
#include "ascii_string.h"

typedef int Int;
typedef bool Bool;

// 24-byte list entry: a name and a flag that selects the "-" form.
struct Rva00767FB0Entry
{
	AsciiString m_name;
	Bool m_removed;
	char m_pad005[0x18 - 5];
};

// Retail inlines StringBase<char>::concat(const char *) and
// concat(const StringBase<char> &) here as explicit-length calls.
static inline void inlineConcat(AsciiString *s, const char *text, int len)
{
	static_cast<StringBase<char> *>(s)->concat(text, len);
}

static inline void inlineConcat(AsciiString *s, const AsciiString &t)
{
	const char *data = *reinterpret_cast<const char *const *>(&t);
	if (data != 0)
		static_cast<StringBase<char> *>(s)->concat(data + 8, *reinterpret_cast<const unsigned short *>(data + 4));
	else
		static_cast<StringBase<char> *>(s)->concat(t.str(), 0);
}

class W3DModelDraw
{
public:
	virtual void rva00767FB0(AsciiString *out, Int perLine);

private:
	unsigned char m_unmodelled04[0x4C - 4];
	_STL::vector<Rva00767FB0Entry> m_list4C;	///< +0x4C
	_STL::vector<Rva00767FB0Entry> m_list58;	///< +0x58
};

void W3DModelDraw::rva00767FB0(AsciiString *out, Int perLine)
{
	AsciiString entry;
	if (out)
	{
		out->clear();
		Bool first = true;
		Int count = 0;
		Int i;
		Int n = m_list58.size();
		for (i = 0; i < n; ++i)
		{
			if (!first)
				inlineConcat(out, ", ", 2);
			if (count >= perLine)
			{
				inlineConcat(out, "\n", 1);
				count = 0;
			}
			if (m_list58[i].m_removed)
				entry.format("-Perm:%s", m_list58[i].m_name.str());
			else
				entry.format("+Perm:%s", m_list58[i].m_name.str());
			inlineConcat(out, entry);
			first = false;
			++count;
		}
		n = m_list4C.size();
		for (i = 0; i < n; ++i)
		{
			if (!first)
				inlineConcat(out, ", ", 2);
			if (count >= perLine)
			{
				inlineConcat(out, "\n", 1);
				count = 0;
			}
			if (m_list4C[i].m_removed)
				entry.format("-%s", m_list4C[i].m_name.str());
			else
				entry.format("+%s", m_list4C[i].m_name.str());
			inlineConcat(out, entry);
			first = false;
			++count;
		}
	}
}
