// ?consume@Glo012F1028Sub@@QAEXPAVAsciiString@@@Z
// partial score=0.788 date=2026-10-26
// cl: /O2 /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// ?consume@Glo012F1028Sub@@QAEXPAVAsciiString@@@Z 0x003C88E0 283 B
// 283/283 B, shape 0.963, 60 non-reloc diffs (was 280 B / 191). Left: retail
// keeps m_begin in ESI across the size guard (push esi before the guard,
// key pointer in ECX); ours keeps it in ECX and pushes ebp/esi/edi later.
// Gains: compare via getLength()/str() (TheNullChr fallback); explicit size
// guard before the for (owner EBX); release helper taking Resource *& with
// its own null test and store (keeps both +0x24 stores, the duplicate null
// test and the EDI zero register). Inert: owner local, size() accessor,
// != 0 guard, while loop, query ref, member/view compare, param order,
// iterator pointer, /Ox /Ob1 /Ob2, shape_family_levers.

#include "ascii_string.h"

static inline int CompareAscii003C88E0(const AsciiString &self, const AsciiString &other)
{
	int thatLen = other.getLength();
	const char *thatData = other.str();
	int thisLen = self.getLength();
	const char *thisData = self.str();
	int c = memcmp(thisData, thatData, thisLen < thatLen ? thisLen : thatLen);
	return c ? c : thisLen - thatLen;
}

class Glo012F1028Record
{
public:
	char m_pad00[4];
	AsciiString m_name;
};
class Glo012F1028Resource
{
public:
	virtual void slot00(void) = 0;
	virtual void slot01(void) = 0;
	virtual void slot02(void) = 0;
	virtual void slot03(void) = 0;
	virtual void slot04(void) = 0;
	virtual void slot05(void) = 0;
	virtual void slot06(void) = 0;
	virtual void slot07(void) = 0;
	virtual void slot08(void) = 0;
	virtual void slot09(void) = 0;
	virtual void slot10(void) = 0;
	virtual void slot11(void) = 0;
	virtual void slot12(void) = 0;
	virtual void slot13(void) = 0;
	virtual void slot14(void) = 0;
	virtual void slot15(void) = 0;
	virtual void slot16(void) = 0;

	int m_refCount;
};

static __forceinline void releaseGlo012F1028Resource(
	Glo012F1028Resource *&ref)
{
	Glo012F1028Resource *resource = ref;
	if (resource != 0)
	{
		resource->slot16();
		if (--resource->m_refCount == 0)
			resource->slot00();
		ref = 0;
	}
}

class Glo012F1028Sub
{
public:
	void consume(AsciiString *key);

private:
	void *m_vptr;
	Glo012F1028Record *m_selected;
	char m_pad08[0x1c];
	Glo012F1028Resource *m_resource;
	Glo012F1028Record **m_begin;
	Glo012F1028Record **m_end;
};

void Glo012F1028Sub::consume(AsciiString *key)
{
	unsigned int index = 0;
	if ((unsigned int)(m_end - m_begin) > 0)
	for (; index < (unsigned int)(m_end - m_begin); ++index)
	{
		if (CompareAscii003C88E0(*key, m_begin[index]->m_name) == 0)
		{
			if (m_selected != 0 && m_selected != m_begin[index])
			{
				if (m_resource != 0)
					releaseGlo012F1028Resource(m_resource);
				m_resource = 0;
				m_resource = 0;
				m_selected = 0;
			}
			m_selected = m_begin[index];
			return;
		}
	}
}
