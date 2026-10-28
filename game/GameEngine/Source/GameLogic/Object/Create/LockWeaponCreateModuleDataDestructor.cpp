// cl: /O2 /Ob1
// Retail 0x0024FE50 (7 bytes): the complete destructor of LockWeaponCreateModuleData. Only the
// store of Snapshot's table (0x01073744) survives; the derived and
// ModuleData stores die against the inlined ~Snapshot. Pinned ILT
// 0x00031DEF routes ??1LockWeaponCreateModuleData@@UAE@XZ here, and tools/ilt_oracle.py confirms the
// decoration; the scalar deleting destructor lives in LockWeaponCreateModuleDataDeletingDestructor.cpp.
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/Common/Snapshot.h
class Snapshot
{
public:
	virtual ~Snapshot() {}
};

class ModuleData : public Snapshot
{
public:
	virtual void moduleDataAnchor();
};

class LockWeaponCreateModuleData : public ModuleData
{
public:
	virtual ~LockWeaponCreateModuleData();
};

LockWeaponCreateModuleData::~LockWeaponCreateModuleData()
{
}
