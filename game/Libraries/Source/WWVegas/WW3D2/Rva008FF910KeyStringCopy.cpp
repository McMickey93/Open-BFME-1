// stlport
// cl: /O2 /Ob0 /MD /D_STLP_USE_STATIC_LIB
#include <string>

class Rva008FF910
{
	unsigned m_key;
	_STL::string m_value;

public:
	Rva008FF910(const Rva008FF910 &other);
	Rva008FF910(const unsigned &key, const _STL::string &value);
};

Rva008FF910::Rva008FF910(const Rva008FF910 &other)
	: m_key(other.m_key), m_value(other.m_value)
{
}

// 0x008FF940 (30 B, unreferenced gap body): the pair-style value constructor
// of the same unsigned + string shape, copying the key and copy-constructing
// the string through basic_string<char>'s copy constructor (ILT 0x0001CB11).
Rva008FF910::Rva008FF910(const unsigned &key, const _STL::string &value)
	: m_key(key), m_value(value)
{
}
