// cl: /DNDEBUG /MD /EHsc /O2 /Ob2 /D_STLP_USE_STATIC_LIB /Igame/Libraries/Source/WWVegas/WWLib
// stlport
//
// BuildingBehaviorModuleData::~BuildingBehaviorModuleData at retail
// 0x001F6D40, 90 bytes. Its only caller is the class's scalar deleting
// destructor 0x001F6D10 (vtable 0x00CA2C88 slot 0), through ILT 0x00016A13.
// It destroys the vector<AsciiString> at +0x18 (ILT 0x00026AB2), then the
// four-name array at +0x08 through the eh vector destructor iterator (element
// dtor ILT 0x0000D828), then restores the Snapshot vtable 0x00C73744 without
// a base call. Open-BFME-2's 0x004564E6 dtor has the same array-then-Snapshot
// teardown. The layout follows the matched ctor 0x001F6C70.
#include <vector>

#include "ascii_string.h"

class Snapshot
{
public:
	virtual ~Snapshot() {}
};

class __declspec(novtable) BuildingBehaviorModuleData : public Snapshot
{
public:
	virtual ~BuildingBehaviorModuleData();

private:
	unsigned int m_unused04;
	AsciiString m_names[4];
	_STL::vector<AsciiString> m_list;
};

// ??1BuildingBehaviorModuleData@@UAE@XZ
BuildingBehaviorModuleData::~BuildingBehaviorModuleData()
{
}
