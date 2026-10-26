// cl: /DNDEBUG /MD /EHsc /Igame/Libraries/Source/WWVegas/WWLib
// Open-BFME5: BoneFXUpdateModuleData dtor.
// Triple 0x20-element arrays of 0x24-byte elems at +0x0c/+0x490/+0x914.

#include "ascii_string.h"

// The three arrays' element destructors (eh vector destructor iterator
// arguments in the 0x00288490 body) are ILTs 0x0004788E, 0x00007617 and
// 0x000271C9 (ilt_oracle CONFIRMED exact for ??1BoneFXListInfo,
// ??1BoneOCLInfo and ??1BoneParticleSystemInfo), each a five-byte jmp to
// releaseBuffer: the implicit destructor of a record whose first member is
// Zero Hour's BoneLocInfo bone name. The other 0x20 bytes are not modelled.
struct BoneFXListInfo
{
	AsciiString boneName;
	unsigned char m_rest[0x20];
};

struct BoneOCLInfo
{
	AsciiString boneName;
	unsigned char m_rest[0x20];
};

struct BoneParticleSystemInfo
{
	AsciiString boneName;
	unsigned char m_rest[0x20];
};

class BoneFXUpdateModuleDataBase
{
public:
	virtual ~BoneFXUpdateModuleDataBase() {}
private:
	unsigned char m_pad[0x8];
};

class __declspec(novtable) BoneFXUpdateModuleData
	: public BoneFXUpdateModuleDataBase
{
public:
	virtual ~BoneFXUpdateModuleData();
private:
	BoneFXListInfo m_fxList[0x20];
	unsigned char m_gap1[4];
	BoneOCLInfo m_OCL[0x20];
	unsigned char m_gap2[4];
	BoneParticleSystemInfo m_particleSystem[0x20];
};

// ??1BoneFXUpdateModuleData@@UAE@XZ
BoneFXUpdateModuleData::~BoneFXUpdateModuleData()
{
}
