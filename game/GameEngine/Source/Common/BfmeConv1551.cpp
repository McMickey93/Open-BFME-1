// cl: /DNDEBUG /MD /EHsc /D_STLP_USE_STATIC_LIB
// stlport

#include "../../../Libraries/Source/WWVegas/WWLib/ascii_string.h"
#include <vector>

extern void j_00007a63();

namespace _STL
{
template <> vector<AsciiString> &vector<AsciiString>::operator=(
	const vector<AsciiString> &);
}

struct BfmeElemVOW
{
	StringBase<char> m_bfme00;
	_STL::vector<AsciiString> m_bfme04;
};

BfmeElemVOW *bfmeCopyBackVOW(const BfmeElemVOW *first, const BfmeElemVOW *last, BfmeElemVOW *dest)
{
    // Preserve the observed vector-assignment ABI through its retail ILT.
    union {
        void (*raw)();
        _STL::vector<AsciiString> &(_STL::vector<AsciiString>::*assign)(const _STL::vector<AsciiString> &);
    } target;
    target.raw = j_00007a63;
	int n = last - first;

	if (n > 0)
	{
		int i = n;

		do
		{
			--last;
			--dest;
			dest->m_bfme00.set(last->m_bfme00);
			(dest->m_bfme04.*target.assign)(last->m_bfme04);
		} while (--i);
	}
	return dest;
}
