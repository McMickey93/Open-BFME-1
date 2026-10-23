// cl: /DNDEBUG /MD /Igame/Libraries/Source/WWVegas/WWMath /Igame/Libraries/Source/WWVegas/WWLib /Igame/Libraries/Source/WWVegas/WW3D2 /Igame/Libraries/Source/WWVegas/WWSaveLoad /Igame/Libraries/Source/WWVegas/Wwutil /Igame/Libraries/Source/WWVegas/WWDownload /Igame/Libraries/Source/Compression /Igame/Libraries/Source/WWVegas/WWDebug /Iinputs/reference/shims/sweep
// VectorClass<BfmeHandleCX>::Resize, retail 0x009302C0 (403 bytes).
//
// The element is the four-byte texture handle whose out-of-line constructor
// (0x0044F3C0, ILT 0x000110D6) and destructor (0x0005CC00, ILT 0x00030652)
// this body pushes to the EH vector constructor iterator and the vector
// destructor iterator. Its copy assignment is inline: add a reference to the
// incoming texture (inline Add_Ref: 16-bit count at +4), release the old one,
// store. As in VectorClassResizeNothrowDelete.cpp, retail saw a throw()
// operator delete[].

void __cdecl operator delete[](void *) throw();

#include "always.h"
#include "vector.h"

class TextureClass
{
public:
	void Release_Ref();
	void Add_Ref() { ++m_bfmeRefCount; }

	void *m_bfmeVtable;
	unsigned short m_bfmeRefCount;
};

class BfmeHandleCX
{
public:
	BfmeHandleCX();
	~BfmeHandleCX();

	BfmeHandleCX &operator=(const BfmeHandleCX &other)
	{
		if (other.p)
			other.p->Add_Ref();
		if (p)
			p->Release_Ref();
		p = other.p;
		return *this;
	}
	bool operator==(const BfmeHandleCX &other) const { return p == other.p; }
	bool operator!=(const BfmeHandleCX &other) const { return p != other.p; }

	TextureClass *p;
};

template class VectorClass<BfmeHandleCX>;

// DynamicVectorClass<BfmeHandleCX>::Resize, retail 0x00930BE0 (47 bytes): its
// direct call into 0x009302C0 above makes it the same element's derived vector.
template class DynamicVectorClass<BfmeHandleCX>;
