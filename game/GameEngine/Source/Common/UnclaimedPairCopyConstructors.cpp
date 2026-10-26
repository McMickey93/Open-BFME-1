// cl: /O2 /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
//
// Unclaimed pair-shaped copy constructors, each alone in a .text gap no ledger
// row covered and reached by no call, jump, ILT stub or table slot.  The body
// copies a four-byte first member and copy-constructs an AsciiString second
// through StringBase<char>'s copy constructor (0x00887B60): the shape of an
// STLport pair<const K, AsciiString> copy constructor, byte-identical to the
// matched pair<const int, AsciiString> one at 0x00851E00.  Retail was linked
// without identical-COMDAT folding, so this is another instantiation whose key
// type nothing in the image reveals.
//
// IDENTITY IS NOT RECOVERED.  Every name is derived from an address.

#include "ascii_string.h"

// 0x00851EC0 (29 B): between the UserPreferences pair rows and INI's
// parseAsciiString.
struct Rva00851EC0Pair
{
	int first;
	AsciiString second;

	Rva00851EC0Pair(const Rva00851EC0Pair &other);
};

Rva00851EC0Pair::Rva00851EC0Pair(const Rva00851EC0Pair &other)
	: first(other.first), second(other.second)
{
}
