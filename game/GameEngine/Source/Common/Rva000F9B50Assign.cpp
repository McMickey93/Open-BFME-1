// cl: /O2 /Ob0

#include "../../../Libraries/Source/WWVegas/WWLib/string_base.h"

typedef StringBase<char> Rva0036CA00Str;

typedef StringBase<unsigned short> Rva00630D00UStr;

struct Rva000F9B50Pod
{
	int a;
	int b;
	int c;
	int d;
	int e;
	int f;
};

// The 0x60-byte element of the vector whose erase overloads 0x000FAF90 and
// 0x000FA9A0 assign through this body (their __copy helper ILT 0x00046A6F ->
// 0x000FA0E0 calls ILT 0x0001802F -> here) and whose destructor is
// ??1BfmeVecElem_000FAFF0@@QAE@XZ (0x000D1690). One placeholder name for the
// one class, struct-keyed like its destructor and erase rows; see
// targets/game/reverse/identity_evidence/000f9b50-bfmevecelem-assign.md.
struct BfmeVecElem_000FAFF0
{
private:
	Rva0036CA00Str m_00;
	int m_04;
	int m_08;
	int m_0C;
	int m_10;
	Rva000F9B50Pod m_14;
	int m_2C;
	int m_30;
	int m_34;
	char m_38;
	int m_3C;
	int m_40;
	int m_44;
	int m_48;
	int m_4C;
	int m_50;
	char m_54;
	Rva00630D00UStr m_58;
	Rva0036CA00Str m_5C;

public:
	BfmeVecElem_000FAFF0 &operator=(const BfmeVecElem_000FAFF0 &other);
};

BfmeVecElem_000FAFF0 &BfmeVecElem_000FAFF0::operator=(const BfmeVecElem_000FAFF0 &other)
{
	m_00.set(other.m_00);
	m_04 = other.m_04;
	m_08 = other.m_08;
	m_0C = other.m_0C;
	m_10 = other.m_10;
	m_14 = other.m_14;
	m_2C = other.m_2C;
	m_30 = other.m_30;
	m_34 = other.m_34;
	m_38 = other.m_38;
	m_3C = other.m_3C;
	m_40 = other.m_40;
	m_44 = other.m_44;
	m_48 = other.m_48;
	m_4C = other.m_4C;
	m_50 = other.m_50;
	m_54 = other.m_54;
	m_58.set(other.m_58);
	m_5C.set(other.m_5C);
	return *this;
}
