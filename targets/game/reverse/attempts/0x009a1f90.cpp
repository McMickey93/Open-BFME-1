// ?releaseContents@Rva009A2030OwnedRecord@@AAEXXZ
// partial score=0.3656 date=2026-10-17
// ?releaseContents@Rva009A2030OwnedRecord@@AAEXXZ
// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /GX /D_STLP_USE_STATIC_LIB
// stlport
//
// Retail 0x009A2030 (125 B): fuzzy twin (tools/fuzzy_twin_scan.py) of the
// Rva003691A0OwnedRecord destructor in Rva0036B6B0OwnedPointerCleanup.cpp.
// Same 8-byte-pair vector at +0 freed through the inline __node_alloc shape,
// but where the twin releases a trailing StringBase member, this body calls a
// this-relative helper (the dump at 0x009A1F90, thiscall, no arguments) from
// the destructor body first. Identity unproven; address-derived names.

#include <vector>

// The second word owns a polymorphic object: releaseContents deletes it
// through its virtual destructor (vtable slot 0, flag 1).
class Rva009A2030Owned
{
public:
	virtual ~Rva009A2030Owned();
};

struct Rva009A2030Pair
{
	Rva009A2030Pair(void *first, Rva009A2030Owned *second) : m_first(first), m_second(second) {}
	Rva009A2030Pair &operator=(const Rva009A2030Pair &that)
	{
		m_first = that.m_first;
		m_second = that.m_second;
		return *this;
	}

	void *m_first;
	Rva009A2030Owned *m_second;
};

class Rva009A2030OwnedRecord
{
public:
	~Rva009A2030OwnedRecord();

private:
	void releaseContents();	// 0x009A1F90

	std::vector<Rva009A2030Pair> m_pairs;
	int m_count;				// +0x0C
};

Rva009A2030OwnedRecord::~Rva009A2030OwnedRecord()
{
	releaseContents();
}

// Retail 0x009A1F90 (93 B, plain ret): release each pair from the back, then
// clear the vector (STLport erase(begin, end): the self-subtracted count of
// its copy loop) and reset the count.
void Rva009A2030OwnedRecord::releaseContents()
{
	for (std::vector<Rva009A2030Pair>::reverse_iterator it = m_pairs.rbegin(); it != m_pairs.rend(); ++it)
	{
		delete it->m_second;
		*it = Rva009A2030Pair(0, 0);
	}
	m_pairs.clear();
	m_count = 0;
}
