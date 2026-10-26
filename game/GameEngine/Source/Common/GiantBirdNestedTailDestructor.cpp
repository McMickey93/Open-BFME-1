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

// The record's ten-element array is destroyed through ILT 0x0001364C, the
// matched empty ??1Coord3D@@QAE@XZ (0x0005BC40): BFME's class-keyed Coord3D.
// class-gate: allow Coord3D the array destructor needs BFME's declared Coord3D destructor, absent from the struct-keyed canonical header
class Coord3D
{
public:
	~Coord3D();

	float x;
	float y;
	float z;
};

class GiantBirdNestedRecord
{
private:
	unsigned char m_prefix[0x2c];
	Coord3D m_spots[10];
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
