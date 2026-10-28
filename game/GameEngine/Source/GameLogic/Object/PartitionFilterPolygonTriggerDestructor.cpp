// cl: /O2 /Ob1
// Retail 0x00149FE0 (7 bytes): the complete destructor of PartitionFilterPolygonTrigger. Only the
// store of PartitionFilter's table (??_7PartitionFilter@@6B@) survives; the
// derived store dies against the inlined ~PartitionFilter. Pinned ILT
// 0x0000C5F9 routes ??1PartitionFilterPolygonTrigger@@UAE@XZ here, and tools/ilt_oracle.py confirms the
// decoration; the scalar deleting destructor lives in PartitionFilterPolygonTriggerDeletingDestructor.cpp.
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/PartitionManager.h
class Object;

class PartitionFilter
{
public:
	virtual bool allow(Object *other) = 0;
	virtual ~PartitionFilter() {}
};

class PartitionFilterPolygonTrigger : public PartitionFilter
{
public:
	virtual ~PartitionFilterPolygonTrigger();
};

PartitionFilterPolygonTrigger::~PartitionFilterPolygonTrigger()
{
}
