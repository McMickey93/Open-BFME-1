// cl: /O2 /Ob1
// Retail 0x001B3AF0 (7 bytes): the complete destructor of GhostObjectManager.
// Only the store of Snapshot's table (0x01073744) survives; the derived store
// dies against the inlined ~Snapshot. Pinned ILT 0x000231A5 routes
// ??1GhostObjectManager@@UAE@XZ here, and tools/ilt_oracle.py confirms the
// decoration; the scalar deleting destructor lives in
// GhostObjectManagerDeletingDestructor.cpp.
// upstream layout: inputs/reference/CnC_Generals_Zero_Hour/GeneralsMD/Code/GameEngine/Include/GameLogic/GhostObject.h
class Snapshot
{
public:
	virtual ~Snapshot() {}
};

class GhostObjectManager : public Snapshot
{
public:
	virtual ~GhostObjectManager();
};

GhostObjectManager::~GhostObjectManager()
{
}
