// cl: /O2 /MD /Igame/Libraries/Source/WWVegas/WWLib
// Retail 0x00C6BAD0 constructs the UnicodeString at VA 0x012F3DC4 and
// registers 0x00C70160 to destroy it. Both use the verified UnicodeString
// default constructor and destructor. Its original global name is unknown.
#include "unicode_string.h"
UnicodeString g_rva012F3DC4;
