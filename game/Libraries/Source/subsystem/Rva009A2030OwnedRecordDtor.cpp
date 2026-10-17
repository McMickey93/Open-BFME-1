// cl: /DNDEBUG /DWIN32 /D_WINDOWS /MD /GX /D_STLP_USE_STATIC_LIB
// stlport
//
// Retail 0x009A2030 (125 B): fuzzy twin (tools/fuzzy_twin_scan.py) of the
// Rva003691A0OwnedRecord destructor in Rva0036B6B0OwnedPointerCleanup.cpp.
// Same 8-byte-pair vector at +0 freed through the inline __node_alloc shape,
// but where the twin releases a trailing StringBase member, this body calls a
// this-relative helper (the dump at 0x009A1F90, thiscall, no arguments) from
// the destructor body first. Identity unproven; address-derived names.

#include <vector>

struct Rva009A2030Pair
{
	void *m_first;
	void *m_second;
};

class Rva009A2030OwnedRecord
{
public:
	~Rva009A2030OwnedRecord();

private:
	std::vector<Rva009A2030Pair> m_pairs;
};

// The helper at 0x009A1F90 is linked as the gen-dump ?d_009a1f90@@YAXXZ, so the
// thiscall is reached through a member-pointer call (the pattern the Apt
// callers of ?d_008cc940 use).
extern void d_009a1f90();
typedef void (Rva009A2030OwnedRecord::*Rva009A1F90Release)();

Rva009A2030OwnedRecord::~Rva009A2030OwnedRecord()
{
	union { void (*fn)(); Rva009A1F90Release call; } releaseContents = { d_009a1f90 };
	(this->*releaseContents.call)();
}
