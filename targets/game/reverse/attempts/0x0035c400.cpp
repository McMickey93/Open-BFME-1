// ?findOrCreateIndex@Rva00359330StringRecordTable@@AAEHPAVAsciiString@@@Z
// partial score=0.4766 date=2026-10-26
// cl: /O2 /DNDEBUG /DWIN32 /D_WINDOWS /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// ?findOrCreateIndex@Rva00359330StringRecordTable@@AAEHPAVAsciiString@@@Z 0x0035C400 428 B
// 428/428 B, shape 0.980, 224 non-reloc diffs: register permutation only
// (retail count EBP / nameIndex EBX / recordIndex EBP; ours count EBX /
// nameIndex EBP / recordIndex EDI) plus `or eax,-1` vs `mov eax,-1`.
// Levers that got here: __forceinline push_back; the insert copy made by an
// inline helper taking the index before the name set (gives retail's
// dedicated [esp+0x10] slot); the __false_type tag at name's arg home.
// Inert: unsigned/int index or count, cached/uncached begin, nested ifs,
// recordAt accessor, released/refs order, /Ox, shape_family_levers.

#include "ascii_string.h"

struct Gen_t_00356ed0_p4pod;
class Open2Rec355050;
void Open2Construct355050(Open2Rec355050 *destination, const Open2Rec355050 &value);

namespace _STL
{
template <class Type>
class allocator
{
};

struct __false_type
{
	__false_type() {}
};

template <class Type, class Allocator = allocator<Type> >
class vector
{
public:
	void reserve(unsigned int count);
	Type *insert(Type *position, const Type &value);

protected:
	void _M_insert_overflow(Type *position, const Type &value,
		const __false_type &, unsigned int fillLength, bool atEnd);

public:
	Type *_M_start;
	Type *_M_finish;
	Type *_M_end_of_storage;

	__forceinline void push_back(const Type &value, const __false_type &tag)
	{
		if (_M_finish != _M_end_of_storage)
		{
			Open2Construct355050(reinterpret_cast<Open2Rec355050 *>(_M_finish),
				reinterpret_cast<const Open2Rec355050 &>(value));
			++_M_finish;
		}
		else
		{
			_M_insert_overflow(_M_finish, value, tag, 1, true);
		}
	}
};

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

class Rva00359330StringRecordTable
{
private:
	int findOrCreateIndex(AsciiString *name);
	int findNameIndex(AsciiString *name);
	void setRecordName(_STL::Rva0035AFC0Element *record, int index, unsigned int position, AsciiString *name)
	{
		record->m_name = *name;
		m_nameIndexes.insert(m_nameIndexes._M_start + position, index);
	}

	_STL::vector<int> m_nameIndexes;
	_STL::vector<_STL::Rva0035AFC0Element> m_records;
	int m_freeHead;
	int m_activeTail;
};

int Rva00359330StringRecordTable::findOrCreateIndex(AsciiString *name)
{
	unsigned int nameIndex = findNameIndex(name);
	int *begin = m_nameIndexes._M_start;
	int count = m_nameIndexes._M_finish - begin;
	int recordIndex;
	if (nameIndex < (unsigned int)count &&
		m_records._M_start[begin[nameIndex]].m_name.StringBase<char>::compare(*name) == 0)
	{
		recordIndex = begin[nameIndex];
		if (!m_records._M_start[recordIndex].m_released)
			return -1;
	}
	else
	{
		unsigned int required = count + 1;
		if (required > (unsigned int)(m_nameIndexes._M_end_of_storage - begin))
			reinterpret_cast<_STL::vector<Gen_t_00356ed0_p4pod> *>(&m_nameIndexes)->reserve(required + required / 2 + 8);

		if (m_freeHead == -1)
		{
			int size = m_records._M_finish - m_records._M_start;
			m_records.push_back(_STL::Rva0035AFC0Element(), reinterpret_cast<const _STL::__false_type &>(name));
			m_records._M_finish[-1].m_previous = -1;
			m_freeHead = size;
		}

		recordIndex = m_freeHead;
		_STL::Rva0035AFC0Element *record = &m_records._M_start[recordIndex];
		setRecordName(record, recordIndex, nameIndex, name);
		m_freeHead = record->m_previous;
		if (m_activeTail != -1)
			m_records._M_start[m_activeTail].m_next = recordIndex;
		record->m_previous = m_activeTail;
		record->m_next = -1;
		m_activeTail = recordIndex;
		record->m_references = 0;
	}

	_STL::Rva0035AFC0Element *record = &m_records._M_start[recordIndex];
	++record->m_references;
	record->m_released = 0;
	return recordIndex;
}
