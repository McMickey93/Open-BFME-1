// cl: /DNDEBUG /DWIN32 /MD /D_STLP_USE_STATIC_LIB
// stlport
//
// Open-BFME: AudioManager::m_allAudioEventInfo, Zero Hour's
//
//     typedef std::hash_map<AsciiString, AudioEventInfo*, rts::hash<AsciiString>,
//         rts::equal_to<AsciiString> > AudioEventInfoHash;
//
// (GameAudio.h). Retail's add/find/newAudioEventInfo (0x006AE910, 0x006AEA10,
// 0x006AE710) work on it at AudioManager+0x70, and tools/ilt_oracle.py confirms
// this exact spelling at every thunk the family is reached through: operator[]
// 0x00027E03, _M_find 0x0000691A, _M_insert 0x0003E6C1, _M_skip_to_next
// 0x0000BA69, both _Ht_iterator::operator++ (0x0000162C, 0x000314A8),
// _M_bkt_num 0x00020275, both _M_bkt_num_key (0x0000F137, 0x0004004D) and the
// pair destructor 0x00036291. The bodies were previously ledgered under
// address-tagged or BuildableStatus spellings:
// targets/game/reverse/identity_evidence/006a78c0-ascii-hash-erase-not-buildablestatus.md
// and targets/game/reverse/identity_evidence/006ac440-audioeventinfo-hash-family.md
//
// class-gate: allow AsciiString the private view is the byte-proved codegen view of
// these STLport bodies (same view as RvaHashIndexAsciiString.cpp); the canonical
// header is a separate reconciliation.

#define _STLP_NO_EXCEPTIONS 1
#include <hash_map>

#include "../../../../Libraries/Source/WWVegas/WWLib/string_base.h"

typedef int Int;
typedef bool Bool;

extern "C" int __cdecl memcmp(const void *buf1, const void *buf2, unsigned int count);
#pragma intrinsic(memcmp)

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/AsciiString.h
class AsciiString
{
public:
	AsciiString(const AsciiString &other) : m_data(other.m_data) {}

	int compare(const AsciiString &str) const
	{
		const int len = str.m_data.m_data ? str.m_data.m_data->length : 0;
		const char *data = str.m_data.m_data ? &str.m_data.m_data->data[0] : "";
		const int myLen = m_data.m_data ? m_data.m_data->length : 0;
		const char *myData = m_data.m_data ? &m_data.m_data->data[0] : "";
		const int result = memcmp(myData, data, myLen < len ? myLen : len);
		if (result != 0) {
			return result;
		}
		return myLen - len;
	}

	StringBase<char> m_data;
};

inline bool operator==(const AsciiString &left, const AsciiString &right)
{
	return left.compare(right) == 0;
}

namespace rts
{
template <class T>
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/STLTypedefs.h
struct hash
{
	unsigned int operator()(T value) const;
};

template <class T>
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/STLTypedefs.h
struct equal_to
{
	bool operator()(const T &left, const T &right) const { return left == right; }
};
}


class AudioEventInfo;

typedef _STL::hash_map<AsciiString, AudioEventInfo *, rts::hash<AsciiString>,
	rts::equal_to<AsciiString> > AudioEventInfoHash;

typedef _STL::hashtable<_STL::pair<const AsciiString, AudioEventInfo *>, AsciiString, rts::hash<AsciiString>,
	_STL::_Select1st<_STL::pair<const AsciiString, AudioEventInfo *> >, rts::equal_to<AsciiString>,
	_STL::allocator<_STL::pair<const AsciiString, AudioEventInfo *> > > AudioEventInfoHashTable;

// retail 0x006AC440; it finds through 0x006A7F80 and inserts through 0x006A7AD0,
// and its key temporary dies through the pair destructor 0x0069DEC0
template AudioEventInfo *&AudioEventInfoHash::operator[](const AsciiString &);

// retail 0x006A4D30, 0x006A4D10, 0x006A1060
template AudioEventInfoHashTable::size_type AudioEventInfoHashTable::_M_bkt_num(
	const _STL::pair<const AsciiString, AudioEventInfo *> &) const;
template AudioEventInfoHashTable::size_type AudioEventInfoHashTable::_M_bkt_num_key(
	const AsciiString &) const;
template AudioEventInfoHashTable::size_type AudioEventInfoHashTable::_M_bkt_num_key(
	const AsciiString &, size_t) const;

// retail 0x006AAEF0 (const) and 0x006AAED0, both stepping through 0x006A7F00
template struct _STL::_Ht_iterator<_STL::pair<const AsciiString, AudioEventInfo *>, _STL::_Const_traits<_STL::pair<const AsciiString, AudioEventInfo *> >, AsciiString,
	rts::hash<AsciiString>, _STL::_Select1st<_STL::pair<const AsciiString, AudioEventInfo *> >, rts::equal_to<AsciiString>,
	_STL::allocator<_STL::pair<const AsciiString, AudioEventInfo *> > >;
template struct _STL::_Ht_iterator<_STL::pair<const AsciiString, AudioEventInfo *>, _STL::_Nonconst_traits<_STL::pair<const AsciiString, AudioEventInfo *> >, AsciiString,
	rts::hash<AsciiString>, _STL::_Select1st<_STL::pair<const AsciiString, AudioEventInfo *> >, rts::equal_to<AsciiString>,
	_STL::allocator<_STL::pair<const AsciiString, AudioEventInfo *> > >;
