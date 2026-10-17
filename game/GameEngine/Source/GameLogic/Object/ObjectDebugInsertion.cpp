// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib

// Open-BFME5: Debug stream insertion for an Object pointer, retail
// 0x001C45E0, 112 bytes.  Retail materializes DescribeObject's AsciiString
// return value, streams its C string through Debug's const-char virtual slot,
// destroys the temporary, and returns the original stream reference.

class Object;

#include "ascii_string.h"

// DescribeObject is called through ILT 0x0000D08A, the ledger's 5-byte row
// ?j_0000d08a@@YAXXZ (game/gen_small/thunks_005.cpp), jmp to 0x001C4310, as
// tools/callees.py 0x1c45e0 112 prints.  Nothing defines the pinned
// ?DescribeObject@@YA?AVAsciiString@@PBVObject@@@Z, so the call names the thunk
// through a function pointer cast that keeps the cdecl by-value return shape.
void j_0000d08a();
typedef AsciiString (*DescribeObjectFn)(const Object *object);

// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/Libraries/Source/debug/debug_debug.h
class Debug
{
public:
	virtual ~Debug();
	virtual void pad01();
	virtual void pad02();
	virtual void pad03();
	virtual void pad04();
	virtual void pad05();
	virtual void pad06();
	virtual void pad07();
	virtual void pad08();
	virtual void pad09();
	virtual void pad10();
	virtual void pad11();
	virtual void pad12();
	virtual void pad13();
	virtual Debug &operator<<(const char *text);
};

// ??6@YAAAVDebug@@AAV0@PBVObject@@@Z
Debug &operator<<(Debug &debug, const Object *object)
{
	debug << ((DescribeObjectFn)&j_0000d08a)(object).str();
	return debug;
}
