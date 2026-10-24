// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: scalar-deleting destructor for BroadcastStealthUpdate.
// Its unique primary vtable (0x010BCC0C) is installed by the named
// constructor at 0x00289880; slot zero routes through ILT 0x00018156 to
// this 30-byte wrapper.  Retail teardown evidence includes the class's
// complete destructor at 0x00289E50 and nested/base teardown at 0x00289B00.

// ILT 0x00018156 reaches the rowed BfmeOwnerZX complete destructor.
class BfmeOwnerZX
{
public:
	virtual ~BfmeOwnerZX();
};

// Spell out the scalar wrapper to avoid emitting another owner's vtable.
class Rva00289BB0
{
public:
	void *method(unsigned int flags);
};

void *Rva00289BB0::method(unsigned int flags)
{
	reinterpret_cast<BfmeOwnerZX *>(this)->BfmeOwnerZX::~BfmeOwnerZX();
	if (flags & 1)
		::operator delete(this);
	return this;
}
