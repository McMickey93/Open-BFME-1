class BfmeVecUE
{
public:
	BfmeVecUE(const BfmeVecUE &other) throw()
	{
		m_bfmeXUE = other.m_bfmeXUE;
		m_bfmeYUE = other.m_bfmeYUE;
		m_bfmeZUE = other.m_bfmeZUE;
	}
	~BfmeVecUE() throw() {}

	int m_bfmeXUE;
	int m_bfmeYUE;
	int m_bfmeZUE;
};

class BfmeTgtUE {};
class AsciiString;
class Matrix3D;
struct Rva00720D10Data;
#include "../../../Libraries/Include/Lib/Coord3D.h"
class W3DShrubBuffer
{
public:
    void rva00720D10(unsigned int, Coord3D, float, const Matrix3D *, float,
        const Rva00720D10Data *, int, const AsciiString &, const AsciiString &);
};

class BfmeOwnUE
{
public:
	void bfmeFwdUE(void *first, BfmeVecUE value, void *third, void *fourth,
		void *fifth, void *sixth, void *seventh, void *eighth, void *ninth);

	unsigned char m_bfmeHeadUE[0x3098];
	BfmeTgtUE *m_bfmeTgtUE;
};

void BfmeOwnUE::bfmeFwdUE(void *first, BfmeVecUE value, void *third, void *fourth,
	void *fifth, void *sixth, void *seventh, void *eighth, void *ninth)
{
    if (m_bfmeTgtUE)
    {
        // The eleven native argument words include this caller's temporary
        // coordinate copy; retain that lifetime while naming the real callee.
        union {
            void (W3DShrubBuffer::*native)(unsigned int, Coord3D, float,
                const Matrix3D *, float, const Rva00720D10Data *, int,
                const AsciiString &, const AsciiString &);
            void (BfmeTgtUE::*forward)(void *, BfmeVecUE, void *, void *,
                void *, void *, void *, void *, void *);
        } call;
        call.native = &W3DShrubBuffer::rva00720D10;
        (m_bfmeTgtUE->*call.forward)(first, value, third, fourth, fifth, sixth,
            seventh, eighth, ninth);
    }
}
