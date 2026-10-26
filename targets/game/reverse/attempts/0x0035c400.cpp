// ?findOrCreateIndex@Rva00359330StringRecordTable@@AAEHPAVAsciiString@@@Z
// partial score=0.4836 date=2026-10-26
// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /D_STLP_USE_STATIC_LIB /Igame/Libraries/Source/WWVegas/WWLib
// stlport
// ?findOrCreateIndex@Rva00359330StringRecordTable@@AAEHPAVAsciiString@@@Z 0x0035C400 428 B
// 428/428 B shape 0.980 221 diffs. Real STLport: the table derives from
// vector<int> (insert/reserve take the table in ECX; capacity is computed from
// the cached begin), records are vector<_STL::Rva0035AFC0Element> whose
// inlined push_back passes the _IsPODType() tag at name's arg home exactly as
// retail. reserve is called under the ledger's placeholder vector type
// (0x00356ED0 is ILT-CONFIRMED vector<int>::reserve; tg_00067670 wrongly
// carries that object symbol). Left: count/nameIndex/recordIndex register
// rotation and `or eax,-1` vs `mov eax,-1`; sibling 0x0035C620 is byte-equal.

#include <vector>
#include "ascii_string.h"

struct Gen_t_00356ed0_p4pod
{
	int m_value;
};

namespace _STL
{
struct Rva0035AFC0Element
{
	Rva0035AFC0Element() : m_nodes(0) {}

	int m_previous;
	int m_next;
	AsciiString m_name;
	unsigned char m_released;
	unsigned char m_pad;
	unsigned short m_references;
	void *m_nodes;
};
}

class Rva00359330StringRecordTable : public _STL::vector<int>
{
private:
	int findOrCreateIndex(AsciiString *name);
	int findNameIndex(AsciiString *name);
	void setRecordName(_STL::Rva0035AFC0Element *record, int index, unsigned int position, AsciiString *name)
	{
		record->m_name = *name;
		insert(_M_start + position, index);
	}

	_STL::vector<_STL::Rva0035AFC0Element> m_records;
	int m_freeHead;
	int m_activeTail;
};

int Rva00359330StringRecordTable::findOrCreateIndex(AsciiString *name)
{
	unsigned int nameIndex = findNameIndex(name);
	int *begin = _M_start;
	int count = _M_finish - begin;
	int recordIndex;
	if (nameIndex < (unsigned int)count &&
		m_records[begin[nameIndex]].m_name.StringBase<char>::compare(*name) == 0)
	{
		recordIndex = begin[nameIndex];
		if (!m_records[recordIndex].m_released)
			return -1;
	}
	else
	{
		unsigned int required = count + 1;
		if (required > (unsigned int)(_M_end_of_storage._M_data - begin))
			reinterpret_cast<_STL::vector<Gen_t_00356ed0_p4pod> *>(this)->reserve(required + required / 2 + 8);

		if (m_freeHead == -1)
		{
			int size = m_records.size();
			m_records.push_back(_STL::Rva0035AFC0Element());
			m_records.back().m_previous = -1;
			m_freeHead = size;
		}

		recordIndex = m_freeHead;
		_STL::Rva0035AFC0Element *record = &m_records[recordIndex];
		setRecordName(record, recordIndex, nameIndex, name);
		m_freeHead = record->m_previous;
		if (m_activeTail != -1)
			m_records[m_activeTail].m_next = recordIndex;
		record->m_previous = m_activeTail;
		record->m_next = -1;
		m_activeTail = recordIndex;
		record->m_references = 0;
	}

	_STL::Rva0035AFC0Element *record = &m_records[recordIndex];
	++record->m_references;
	record->m_released = 0;
	return recordIndex;
}
