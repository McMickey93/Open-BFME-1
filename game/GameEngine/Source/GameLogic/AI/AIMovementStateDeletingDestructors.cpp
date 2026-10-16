// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: scalar-deleting destructors for three pool-backed AI movement
// states. Exact named constructors install their dedicated vtables and each
// slot-zero ILT routes to the corresponding 30-byte wrapper below.

// These destructors are implicit: retail ~AIWanderState at 0x00185570 (own ILT 0x00016095), ~AIPanicState at 0x001855F0 (own ILT 0x0001CA08) are each a bare tail
// jump to AIInternalMoveToState::~AIInternalMoveToState (ILT 0x0004AAF7)
// with no vptr reset, the shape VC7.1 gives an implicit virtual
// destructor; every ILT named here is ilt_oracle CONFIRMED exact.

class AIInternalMoveToState
{
public:
	virtual ~AIInternalMoveToState();
};

class AIWanderState : public AIInternalMoveToState
{
private:
	friend void forceAIWanderStateDeletingDestructor();
};

class AIPanicState : public AIInternalMoveToState
{
private:
	friend void forceAIPanicStateDeletingDestructor();
};

class AIEnterState
{
protected:
	virtual ~AIEnterState();
private:
	friend void forceAIEnterStateDeletingDestructor();
};

void forceAIWanderStateDeletingDestructor() { AIWanderState value; }
void forceAIPanicStateDeletingDestructor() { AIPanicState value; }
void forceAIEnterStateDeletingDestructor() { AIEnterState value; }
