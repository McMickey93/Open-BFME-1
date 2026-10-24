// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: scalar-deleting destructor for CostModifierUpgrade.
// Its unique primary vtable (0x010CC5AC) is installed by the named
// constructor at 0x002D4570; slot zero routes through ILT 0x00049CD8 to
// this 30-byte wrapper.  Retail teardown evidence includes the class's
// complete destructor at 0x001F8970 and nested/base teardown at 0x002D44E0.

// ILT 0x00025293 reaches the ledger-owned nested teardown at 0x002D44E0.
class Rva002D44E0DeepDtor
{
public:
	virtual ~Rva002D44E0DeepDtor();
};

void operator delete(void *);

// Keep the scalar-deletion flags explicit without emitting another vtable
// for the nested teardown's class. The helper is named by its retail address.
class Rva002D46A0
{
public:
	void *method(unsigned flags);
};

void *Rva002D46A0::method(unsigned flags)
{
	((Rva002D44E0DeepDtor *)this)->Rva002D44E0DeepDtor::~Rva002D44E0DeepDtor();
	if (flags & 1)
		operator delete(this);
	return this;
}
