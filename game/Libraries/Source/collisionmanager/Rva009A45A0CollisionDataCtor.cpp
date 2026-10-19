// cl: /O2 /arch:SSE /DNDEBUG /MD /EHsc
// Retail 0x009A45A0 (117 B): constructor of the 0xC070-byte object that
// CollisionManager::CollisionManager (0x009A25B0) allocates; its destructor
// call site is 0x009A4620. Three leading words and three more, two embedded
// tables at +0x18 (0x2B7B cells) and +0xAE10 (0x493 cells), each cells[] +
// count + two words, then a word set to 3 (the axis count UpdateSort reads at
// +0xC068) and two flag bytes. Each table constructor clears its two trailing
// words, memsets the cells and zeroes the count; the tail is its own member
// object, whose constructor fixes retail's store schedule. Byte-identical to
// Open-BFME-2's matched 0x0075A000, ported from there. Member names are
// structural.
#include <string.h>

template <int N>
struct Rva009A45A0Table
{
	int m_cells[N];
	int m_count;
	int m_a;
	int m_b;

	Rva009A45A0Table()
	{
		m_a = 0;
		m_b = 0;
		memset(m_cells, 0, sizeof(m_cells));
		m_count = 0;
	}
};

struct Rva009A45A0Tail
{
	int m_axisCount;
	unsigned char m_flagA;
	unsigned char m_flagB;

	Rva009A45A0Tail()
	{
		m_flagA = 0;
		m_flagB = 0;
		m_axisCount = 3;
	}
};

class Rva009A45A0CollisionData
{
public:
	Rva009A45A0CollisionData();

private:
	int m_00;
	int m_04;
	int m_08;
	int m_0c;
	int m_10;
	int m_14;
	Rva009A45A0Table<0x2B7B> m_pairTable;
	Rva009A45A0Table<0x493> m_queueTable;
	Rva009A45A0Tail m_tail;
};

Rva009A45A0CollisionData::Rva009A45A0CollisionData() : m_00(0), m_04(0), m_08(0)
{
	m_0c = 0;
	m_10 = 0;
	m_14 = 0;
}
