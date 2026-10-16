// cl: /DNDEBUG /MD /EHsc
//
// W3DShadowGeometryManagerIterator complete destructor at retail 0x007B96D0
// (7 bytes): `mov [ecx], 0x011283D4 / ret`. The iterator's own destructor is
// empty and does not re-seat its vftable; the only store is the inlined
// empty base destructor putting the base vftable back. Its ??_G (0x007BB4F0)
// calls it through ILT 0x00010B3B, where ilt_oracle CONFIRMS
// ??1W3DShadowGeometryManagerIterator@@UAE@XZ (MAE contradicted). The base
// vftable is recorded only under the address-derived ??_7Rva007AE550Base@@6B@,
// so the base keeps that name here. novtable reproduces the missing re-seat
// (as GameLogic/AI/AIDockMoveToEntryStateDestructor.cpp).

class Rva007AE550Base
{
public:
	virtual ~Rva007AE550Base() {}
};

class __declspec(novtable) W3DShadowGeometryManagerIterator : public Rva007AE550Base
{
public:
	virtual ~W3DShadowGeometryManagerIterator();
};

W3DShadowGeometryManagerIterator::~W3DShadowGeometryManagerIterator()
{
}
