// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// Retail 0x00088140 (21 B) is Zero Hour WorldHeightMap.cpp's file-static validateName,
// returned by value into the MapObject constructor at 0x00088160, whose only call
// (0x000881CB) passes the name in EAX and the result slot in ESI. That private
// convention is what MSVC 7.1 gives a file-static; the unused flags argument drops out.
// Zero Hour takes the name by value; retail releases nothing here, so BFME takes it by
// reference.
// The constructor is still a byte lift, so this TU keeps the static alive with a local
// caller, and uses the BFME AsciiString whose copy is the StringBase<char> copy
// constructor call retail makes (0x00887B60).
// upstream: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngineDevice/Source/W3DDevice/GameClient/WorldHeightMap.cpp:68

#include "ascii_string.h"

typedef int Int;

// ?validateName@@YA?AVAsciiString@@ABV1@H@Z
static __declspec(noinline) AsciiString validateName(const AsciiString &n, Int flags)
{
	return n;
}

// ?validateNameCaller@@YA?AVAsciiString@@ABV1@H@Z absent-from-retail TU-local caller that
// keeps the static above alive.
AsciiString validateNameCaller(const AsciiString &n, Int flags)
{
	return validateName(n, flags);
}
