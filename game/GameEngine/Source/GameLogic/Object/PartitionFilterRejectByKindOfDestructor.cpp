// cl: /O2 /Ob1
// Retail 0x00160C60 (7 bytes): the complete destructor of PartitionFilterRejectByKindOf. Only the
// store of PartitionFilter's table (??_7PartitionFilter@@6B@) survives; the
// derived store dies against the inlined ~PartitionFilter. Pinned ILT
// 0x00034F04 routes ??1PartitionFilterRejectByKindOf@@UAE@XZ here, and tools/ilt_oracle.py confirms the
// decoration; the scalar deleting destructor lives in PartitionFilterRejectByKindOfDeletingDestructor.cpp.
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/PartitionManager.h
class Object;

class PartitionFilter
{
public:
	virtual bool allow(Object *other) = 0;
	virtual ~PartitionFilter() {}
};

class PartitionFilterRejectByKindOf : public PartitionFilter
{
public:
	virtual ~PartitionFilterRejectByKindOf();
};

PartitionFilterRejectByKindOf::~PartitionFilterRejectByKindOf()
{
}
