// cl: /O2 /Ob1
// Retail 0x001EFE80 (7 bytes): the complete destructor of BezierProjectileBehaviorModuleData. Only the
// store of Snapshot's table (0x01073744) survives; the derived and
// ModuleData stores die against the inlined ~Snapshot. Pinned ILT
// 0x0004A14C routes ??1BezierProjectileBehaviorModuleData@@MAE@XZ here, and tools/ilt_oracle.py confirms the
// decoration; the scalar deleting destructor lives in BezierProjectileBehaviorModuleDataDeletingDestructor.cpp.
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

class BezierProjectileBehaviorModuleData : public ModuleData
{
protected:
	virtual ~BezierProjectileBehaviorModuleData();
};

BezierProjectileBehaviorModuleData::~BezierProjectileBehaviorModuleData()
{
}
