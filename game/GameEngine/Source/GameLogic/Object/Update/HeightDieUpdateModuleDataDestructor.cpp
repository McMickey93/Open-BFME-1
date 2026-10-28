// cl: /O2 /Ob1
// Retail 0x00295750 (7 bytes): the complete destructor of HeightDieUpdateModuleData. Only the
// store of Snapshot's table (0x01073744) survives; the derived and
// ModuleData stores die against the inlined ~Snapshot. Pinned ILT
// 0x0002DC9A routes ??1HeightDieUpdateModuleData@@UAE@XZ here, and tools/ilt_oracle.py confirms the
// decoration; the scalar deleting destructor lives in HeightDieUpdateModuleDataDeletingDestructor.cpp.
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

class HeightDieUpdateModuleData : public ModuleData
{
public:
	virtual ~HeightDieUpdateModuleData();
};

HeightDieUpdateModuleData::~HeightDieUpdateModuleData()
{
}
