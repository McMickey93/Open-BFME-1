// cl: /DNDEBUG /DWIN32 /MD /EHsc /D_STLP_USE_STATIC_LIB /D_STLP_NO_EXCEPTIONS
// stlport
// STLport _Rb_tree<AsciiString, AudioEventRTS>::_M_copy at retail 0x001373D0.

#define _STLP_NO_EXCEPTIONS 1
#include <map>


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
	AsciiString();
	AsciiString( const AsciiString &other );
	~AsciiString() { ((StringBase<char> *)this)->releaseBuffer(); }
	AsciiString &operator=( const AsciiString &other );
	int compare( const AsciiString &other ) const;

private:
	void *m_data;
};

inline bool operator<( const AsciiString &left, const AsciiString &right )
{
	return left.compare( right ) < 0;
}

class AudioEventRTS
{
public:
	AudioEventRTS();
	AudioEventRTS( const AudioEventRTS &other );
	virtual ~AudioEventRTS();
	AudioEventRTS &operator=( const AudioEventRTS &other );

private:
	unsigned char m_data[ 0x6C ];
};

typedef _STL::pair<const AsciiString, AudioEventRTS> Rva001373D0Pair;
typedef _STL::_Rb_tree<AsciiString, Rva001373D0Pair,
	_STL::_Select1st<Rva001373D0Pair>, _STL::less<AsciiString>,
	_STL::allocator<Rva001373D0Pair> > Rva001373D0Tree;

template class _STL::_Rb_tree<AsciiString, Rva001373D0Pair,
	_STL::_Select1st<Rva001373D0Pair>, _STL::less<AsciiString>,
	_STL::allocator<Rva001373D0Pair> >;
