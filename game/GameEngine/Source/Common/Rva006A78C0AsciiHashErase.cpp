// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /D_STLP_USE_STATIC_LIB /EHsc
// stlport
//
// Open-BFME: STLport hashtable erase(const AsciiString&) at retail
// 0x006A78C0. Its one caller, 0x006AC0F0, is the AudioManager vtable slot after
// find/add/newAudioEventInfo and erases from the hash map at this+0x70 (Zero
// Hour's m_allAudioEventInfo: AudioEventInfoHash = hash_map<AsciiString,
// AudioEventInfo*, rts::hash<AsciiString>, rts::equal_to<AsciiString> >). It is
// NOT hash_map<AsciiString, BuildableStatus>, whose members sit at 0x0038xxxx
// (pair destructor via ILT 0x0000FF10). ilt_oracle confirms this spelling at
// all three thunks: erase 0x00047D1B, _M_bkt_num_key 0x0004004D, pair
// destructor 0x00036291. Evidence:
// targets/game/reverse/identity_evidence/006a78c0-ascii-hash-erase-not-buildablestatus.md

#define _STLP_NO_EXCEPTIONS 1
#include <hash_map>

#include "../../../Libraries/Source/WWVegas/WWLib/string_base.h"

extern "C" int __cdecl memcmp(const void *buf1, const void *buf2,
	unsigned int count);
#pragma intrinsic(memcmp)

// class-gate: allow AsciiString this unit is a byte-proved reconstruction of 0x006A78C0 (316/316):
// the private view inlines compare()/operator== the way the retail erase does; it predates the
// rename from Rva006A78C0BuildableStatusErase.cpp, and the canonical header is a separate reconciliation.
class AsciiString
{
public:
	AsciiString(const AsciiString &other) : m_data(other.m_data) {}

	int compare(const AsciiString &str) const
	{
		const int len = str.m_data.m_data ? str.m_data.m_data->length : 0;
		const char *data = str.m_data.m_data ?
			&str.m_data.m_data->data[0] : "";
		const int myLen = m_data.m_data ? m_data.m_data->length : 0;
		const char *myData = m_data.m_data ? &m_data.m_data->data[0] : "";
		const int result = memcmp(myData, data, myLen < len ? myLen : len);
		if (result != 0)
			return result;
		return myLen - len;
	}

	StringBase<char> m_data;
};

inline bool operator==(const AsciiString &left, const AsciiString &right)
{
	return left.compare(right) == 0;
}

class AudioEventInfo;

namespace rts
{
	template <class T> struct equal_to
	{
		bool operator()(const T &left, const T &right) const { return left == right; }
	};
	template <class T> struct hash;
	template <> struct hash<AsciiString>
	{
		unsigned int operator()(AsciiString value) const;
	};
}

typedef _STL::pair<const AsciiString, AudioEventInfo *> Rva006A78C0Pair;
typedef _STL::hashtable<Rva006A78C0Pair, AsciiString, rts::hash<AsciiString>,
	_STL::_Select1st<Rva006A78C0Pair>, rts::equal_to<AsciiString>,
	_STL::allocator<Rva006A78C0Pair> > Rva006A78C0HashTable;


template unsigned int Rva006A78C0HashTable::erase(const AsciiString &key);
