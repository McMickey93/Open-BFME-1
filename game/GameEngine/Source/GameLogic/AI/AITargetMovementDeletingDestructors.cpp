// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: scalar-deleting destructors for seven pool-backed AI target-
// movement states. Exact named constructors and their dedicated vtable slot
// zero routes establish each 30-byte wrapper independently.

class AIMoveOutOfTheWayState
{
protected:
	virtual ~AIMoveOutOfTheWayState();
private:
	friend void forceAIMoveOutOfTheWayStateDeletingDestructor();
};

class AIMoveAwayFromRepulsorsState
{
protected:
	virtual ~AIMoveAwayFromRepulsorsState();
private:
	friend void forceAIMoveAwayFromRepulsorsStateDeletingDestructor();
};

class AIAttackPursueTargetState
{
protected:
	virtual ~AIAttackPursueTargetState();
private:
	friend void forceAIAttackPursueTargetStateDeletingDestructor();
};

// These destructors are implicit: retail ~AIAttackMeleeHordeApproachTargetState at 0x001853C0 (own ILT 0x00020DBA), ~AIAttackFireDuringApproachState at 0x00185440 (own ILT 0x00027F43), ~AIAttackMeleeSquishState at 0x001854C0 (own ILT 0x00013D59) are each a bare tail
// jump to AIInternalMoveToState::~AIInternalMoveToState (ILT 0x0004AAF7)
// with no vptr reset, the shape VC7.1 gives an implicit virtual
// destructor; every ILT named here is ilt_oracle CONFIRMED exact.

class AIInternalMoveToState
{
public:
	virtual ~AIInternalMoveToState();
};

class AIAttackMeleeHordeApproachTargetState : public AIInternalMoveToState
{
private:
	friend void forceAIAttackMeleeHordeApproachTargetStateDeletingDestructor();
};

class AIAttackFireDuringApproachState : public AIInternalMoveToState
{
private:
	friend void forceAIAttackFireDuringApproachStateDeletingDestructor();
};

class AIAttackMeleeSquishState : public AIInternalMoveToState
{
private:
	friend void forceAIAttackMeleeSquishStateDeletingDestructor();
};

class AIAttackMeleeEngageState
{
public:
	virtual ~AIAttackMeleeEngageState();
private:
	friend void forceAIAttackMeleeEngageStateDeletingDestructor();
};

void forceAIMoveOutOfTheWayStateDeletingDestructor() { AIMoveOutOfTheWayState value; }
void forceAIMoveAwayFromRepulsorsStateDeletingDestructor() { AIMoveAwayFromRepulsorsState value; }
void forceAIAttackPursueTargetStateDeletingDestructor() { AIAttackPursueTargetState value; }
void forceAIAttackMeleeHordeApproachTargetStateDeletingDestructor() { AIAttackMeleeHordeApproachTargetState value; }
void forceAIAttackFireDuringApproachStateDeletingDestructor() { AIAttackFireDuringApproachState value; }
void forceAIAttackMeleeSquishStateDeletingDestructor() { AIAttackMeleeSquishState value; }
void forceAIAttackMeleeEngageStateDeletingDestructor() { AIAttackMeleeEngageState value; }
