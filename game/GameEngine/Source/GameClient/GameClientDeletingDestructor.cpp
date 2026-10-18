// cl: /DNDEBUG /MD /EHsc
// Scalar wrapper 0x00597680 calls Rva00597FC0Client::~Rva00597FC0Client through ILT 0x00025FB8.
//
// The real destructor (0x00596500) lives in GameClientDestructor.cpp.  A
// defined destructor here would also emit a short COMDAT ??1 that precedes
// retail's copy in link order, so force cl to emit the vftable group (and the
// scalar deleting destructor in it) with an unreferenced copy constructor
// instead, leaving ??1Rva00597FC0Client undefined in this object.

class Rva00597FC0Client
{
public:
	Rva00597FC0Client(const Rva00597FC0Client &);
	virtual ~Rva00597FC0Client();
};

Rva00597FC0Client::Rva00597FC0Client(const Rva00597FC0Client &)
{
}

void Force_Rva00597FC0Client_Deleting_Destructor(Rva00597FC0Client *client)
{
	delete client;
}
