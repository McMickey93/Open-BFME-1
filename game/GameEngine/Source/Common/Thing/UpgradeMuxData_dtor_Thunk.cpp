// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// Rva0058BE30FourString::~Rva0058BE30FourString, retail 0x0058C4C0 (102 B).
//
// Formerly filed as ??1UpgradeMuxData@@QAE@XZ (zh_sweep packet 0058c4c0); see
// targets/game/reverse/identity_evidence/0058c4c0-four-string-dtor.md. The body
// destroys four four-byte UnicodeString members at +0x0C, +0x08, +0x04, +0x00 (EH
// states 2, 1, 0, -1), the record whose copy constructor is 0x0058BE30 and whose
// owners (0x00593E60, 0x00592640, 0x005929E0) delete it through ILT 0x0003FA7B.
// The file keeps its old path; the identity is address-derived.

#include "unicode_string.h"

// Retail inlines ~UnicodeString: temporaries are released by a direct call to
// StringBase<unsigned short>::releaseBuffer (0x008881D0), not the ??1UnicodeString stub.
inline UnicodeString::~UnicodeString() { ((StringBase<unsigned short> *)this)->releaseBuffer(); }

class Rva0058BE30FourString
{
public:
	~Rva0058BE30FourString();

	UnicodeString m_string0;					///< +0x00
	UnicodeString m_string4;					///< +0x04
	UnicodeString m_string8;				///< +0x08
	UnicodeString m_stringC;					///< +0x0C
};

// ??1Rva0058BE30FourString@@QAE@XZ
Rva0058BE30FourString::~Rva0058BE30FourString()
{
}
