// cl: /O2 /Ob1
// Retail 0x0020D920 (7 bytes): the complete destructor of SupplyWarehouseCripplingBehaviorModuleData. Only the
// store of Snapshot's table (0x01073744) survives; the derived and
// ModuleData stores die against the inlined ~Snapshot. Pinned ILT
// 0x0003C4C0 routes ??1SupplyWarehouseCripplingBehaviorModuleData@@UAE@XZ here, and tools/ilt_oracle.py confirms the
// decoration; the scalar deleting destructor lives in SupplyWarehouseCripplingBehaviorModuleDataDeletingDestructor.cpp.
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

class SupplyWarehouseCripplingBehaviorModuleData : public ModuleData
{
public:
	virtual ~SupplyWarehouseCripplingBehaviorModuleData();
};

SupplyWarehouseCripplingBehaviorModuleData::~SupplyWarehouseCripplingBehaviorModuleData()
{
}
