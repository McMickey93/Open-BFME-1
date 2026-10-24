// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: scalar-deleting destructor for SpecialPowerCompletionDie.
// Its unique primary vtable (0x010B3414) is installed by the named
// constructor at 0x00255E30; slot zero routes through ILT 0x00023FF1 to
// this 30-byte wrapper.  Retail teardown evidence includes the class's
// complete destructor at 0x00255FD0 and nested/base teardown at 0x00255DD0.

// ILT 0x00033866 reaches the ledger-owned nested teardown at 0x00255DD0.
class Rva00255DD0NestedDtor
{
public:
	virtual ~Rva00255DD0NestedDtor();
};

void operator delete(void *);

// An explicit scalar-deletion wrapper avoids emitting a second vtable for
// the nested teardown's class. The public destructor identity remains in
// the ledger; this source-level helper is named by its address.
class Rva00255F30
{
public:
	void *method(unsigned flags);
};

void *Rva00255F30::method(unsigned flags)
{
	((Rva00255DD0NestedDtor *)this)->Rva00255DD0NestedDtor::~Rva00255DD0NestedDtor();
	if (flags & 1)
		operator delete(this);
	return this;
}
