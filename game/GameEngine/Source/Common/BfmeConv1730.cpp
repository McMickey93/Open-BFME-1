class BfmeVecUD
{
public:
	BfmeVecUD(const BfmeVecUD &other) throw()
	{
		m_bfmeXUD = other.m_bfmeXUD;
		m_bfmeYUD = other.m_bfmeYUD;
		m_bfmeZUD = other.m_bfmeZUD;
	}
	~BfmeVecUD() throw() {}

	int m_bfmeXUD;
	int m_bfmeYUD;
	int m_bfmeZUD;
};

class BfmeTgtUD {};
class AsciiString;
class Matrix3D;
struct Rva00736B60Data;
struct Rva00736B60Coord { float x, y, z; };
class W3DTreeBuffer
{
public:
    void rva00736b60(unsigned int, Rva00736B60Coord, float, const Matrix3D *,
        float, const Rva00736B60Data *, int, const AsciiString &, const AsciiString &);
};

class BfmeOwnUD
{
public:
	void bfmeFwdUD(void *first, BfmeVecUD value, void *third, void *fourth,
		void *fifth, void *sixth, void *seventh, void *eighth, void *ninth);

	unsigned char m_bfmeHeadUD[0x3094];
	BfmeTgtUD *m_bfmeTgtUD;
};

void BfmeOwnUD::bfmeFwdUD(void *first, BfmeVecUD value, void *third, void *fourth,
	void *fifth, void *sixth, void *seventh, void *eighth, void *ninth)
{
    if (m_bfmeTgtUD)
    {
        // Both signatures pass eleven words and clean 44 bytes. Keep the
        // caller's native copy/destruction lifetime for its three-word value.
        union {
            void (W3DTreeBuffer::*native)(unsigned int, Rva00736B60Coord, float,
                const Matrix3D *, float, const Rva00736B60Data *, int,
                const AsciiString &, const AsciiString &);
            void (BfmeTgtUD::*forward)(void *, BfmeVecUD, void *, void *,
                void *, void *, void *, void *, void *);
        } call;
        call.native = &W3DTreeBuffer::rva00736b60;
        (m_bfmeTgtUD->*call.forward)(first, value, third, fourth, fifth, sixth,
            seventh, eighth, ninth);
    }
}
