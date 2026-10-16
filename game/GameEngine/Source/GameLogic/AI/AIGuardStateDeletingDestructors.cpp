// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: scalar-deleting destructors for two AIGuard states whose empty
// complete destructors tail-call State. Exact named constructors install the
// dedicated vtables and their slot-zero ILTs route to these wrappers.

class AIGuardOuterState
{
protected:
	virtual ~AIGuardOuterState();
private:
	friend void forceAIGuardOuterStateDeletingDestructor();
};

// The destructors are implicit: retail ~AIGuardAttackAggressorState at 0x0015E6B0 (own ILT 0x00016900) is each a bare tail jump to
// State::~State (ILT 0x00016725) with no vptr reset, the shape VC7.1 gives an
// implicit virtual destructor; every ILT here is ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class AIGuardAttackAggressorState : public State
{
private:
	friend void forceAIGuardAttackAggressorStateDeletingDestructor();
};

void forceAIGuardOuterStateDeletingDestructor()
{
	AIGuardOuterState value;
}

void forceAIGuardAttackAggressorStateDeletingDestructor()
{
	AIGuardAttackAggressorState value;
}
