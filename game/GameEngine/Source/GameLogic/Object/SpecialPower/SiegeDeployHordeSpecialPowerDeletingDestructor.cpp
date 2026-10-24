// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: scalar-deleting destructor for SiegeDeployHordeSpecialPower.
// Its unique primary vtable (0x010B71FC) is installed by the named
// constructor at 0x00265B20; slot zero routes through ILT 0x00025612 to
// this 30-byte wrapper. The wrapper calls ILT 0x0000DFB7, which reaches
// the existing flat destructor at 0x00265BF0, then conditionally frees this.

class Rva00265BF0FlatDtor
{
public:
	virtual ~Rva00265BF0FlatDtor();
};

void operator delete(void *);

class Rva00265CD0
{
public:
	void *method(unsigned int flags);
};

void *Rva00265CD0::method(unsigned int flags)
{
	reinterpret_cast<Rva00265BF0FlatDtor *>(this)->Rva00265BF0FlatDtor::~Rva00265BF0FlatDtor();
	if (flags & 1)
		operator delete(this);
	return this;
}
