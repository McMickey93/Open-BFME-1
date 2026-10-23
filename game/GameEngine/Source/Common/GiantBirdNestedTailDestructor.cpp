// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport
// Open-BFME5: GiantBirdNestedTail owns a vector of 0xb8-byte records.

#include <vector>

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/AsciiString.h

// Retail inlines this wrapper into StringBase<char> directly; declare just the
// StringBase<char> members it reaches (see build/whatif/wrapfix.py).
template <class T> class StringBase
{
	friend class AsciiString;
	friend class UnicodeString;
public:
	void set(const StringBase<T> &other);
private:
	void releaseBuffer();
};
class AsciiString
{
public:
	~AsciiString() { ((StringBase<char> *)this)->releaseBuffer(); }

private:
	void *m_data;
};

class GiantBirdNestedCoord3D
{
public:
	~GiantBirdNestedCoord3D();

private:
	float m_x;
	float m_y;
	float m_z;
};

class GiantBirdNestedRecord
{
private:
	unsigned char m_prefix[0x2c];
	GiantBirdNestedCoord3D m_spots[10];
	unsigned char m_between[0x0c];
	AsciiString m_name;
	unsigned char m_tail[4];
};

class GiantBirdNestedTail
{
public:
	~GiantBirdNestedTail();

private:
	_STL::vector<GiantBirdNestedRecord> m_records;
};

template class _STL::vector<GiantBirdNestedRecord>;

GiantBirdNestedTail::~GiantBirdNestedTail()
{
}
