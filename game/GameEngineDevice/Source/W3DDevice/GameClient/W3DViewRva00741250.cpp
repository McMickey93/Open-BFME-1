// ?rva00741250@W3DView@@UAEXPAVRva00741250Source@@HHHHM_N@Z
// cl: /DNDEBUG /MD
// stlport
//
// W3DView primary vftable 0x011217A0 slot 25 (+0x64) reaches this body through
// ILT 0x0002D5C9; the table is installed by the W3DView constructor 0x00745B10.
// The method name is not recovered, so it keeps its address.  The two path
// records at +0x22F4 and +0x2358 are 0x60-byte records of the goal class whose configure
// slot and finalizer 0x003A2700 (ILT 0x00049AE9) the matched goal setup
// 0x002BC260 drives the same way; their point list is a vector of 184-byte
// records (retail divides the byte span by 0xB8).

#include <vector>

class Rva00741250Source
{
	char m_unreconstructed000[0x60];
public:
	int m_kind;
};

struct Rva00741250Point
{
	char m_unreconstructed000[0xb4];
	int m_value;
};

// The finalizer goes through ILT 0x00049AE9, the ledger's 5-byte row
// ?j_00049ae9@@YAXXZ (game/gen_small/thunks_035.cpp), as tools/callees.py
// 0x741250 215 prints.  Nothing defines the pinned
// ?finalize@Rva002BC260Goal@@QAEXXZ, so the calls name the thunk through a raw
// pointer bridge that keeps the thiscall shape.
void j_00049ae9();
class Rva002BC260Goal
{
public:
	virtual void unused000();
	virtual void setSource(Rva00741250Source *source);
	virtual void configure(int a, int b, int c, int d, int e, int f);

private:
	char m_unreconstructed004[0x2c - 4];
public:
	std::vector<Rva00741250Point> m_points;
private:
	char m_unreconstructed038[0x60 - 0x38];
};

class W3DView
{
public:
	virtual void slot000();
	virtual void slot001();
	virtual void slot002();
	virtual void slot003();
	virtual void slot004();
	virtual void slot005();
	virtual void slot006();
	virtual void slot007();
	virtual void slot008();
	virtual void slot009();
	virtual void slot010();
	virtual void slot011();
	virtual void slot012();
	virtual void slot013();
	virtual void slot014();
	virtual void slot015();
	virtual void slot016();
	virtual void slot017();
	virtual void slot018();
	virtual void slot019();
	virtual void slot020();
	virtual void slot021();
	virtual void slot022();
	virtual void slot023();
	virtual void slot024();
	virtual void rva00741250(Rva00741250Source *source, int a2, int a3, int a4,
		int a5, float a6, bool alternate);
	virtual void slot026();
	virtual void slot027(int value);

private:
	char m_unreconstructed0004[0x22f4 - 4];
	Rva002BC260Goal m_path22F4;
	int m_int2354;
	Rva002BC260Goal m_path2358;
	bool m_bool23B8;
	char m_unreconstructed23b9[0x23c4 - 0x23b9];
	int m_int23C4;
};

// ?rva00741250@W3DView@@UAEXPAVRva00741250Source@@HHHHM_N@Z
void W3DView::rva00741250(Rva00741250Source *source, int a2, int a3, int a4,
	int a5, float a6, bool alternate)
{
	if (source == 0 || source->m_kind != 6)
		return;
	Rva002BC260Goal *path = alternate ? &m_path2358 : &m_path22F4;
	path->setSource(source);
	path->configure(m_int23C4, a2, a4, a5, (int)a6, 1);
	union
	{
		void (*raw)(void);
		void (Rva002BC260Goal::*typed)();
	} finalize;
	finalize.raw = &j_00049ae9;
	if (alternate) {
		m_bool23B8 = true;
		(path->*finalize.typed)();
		return;
	}
	m_int2354 = 2;
	if (path->m_points.size() > 3)
		slot027(path->m_points[1].m_value);
	else
		slot027(0);
	(path->*finalize.typed)();
}
