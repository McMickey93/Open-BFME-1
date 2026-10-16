// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: protected scalar-deleting destructor for AIDockWaitForClearanceState.
// Vtable 0x00C95BF0 slots name this class (?onEnter@AIDockWaitForClearanceState@@UAE?AW4StateReturnType@@XZ); its slot zero routes
// through ILT 0x0002B8B9 to this 30-byte wrapper, whose complete destructor
// route ILT 0x0001AD66 reaches cleanup body 0x000A1B30.

// The destructors are implicit: retail ~AIDockWaitForClearanceState at 0x0014F7B0 (own ILT 0x0001AD66) is each a bare tail jump to
// State::~State (ILT 0x00016725) with no vptr reset, the shape VC7.1 gives an
// implicit virtual destructor; every ILT here is ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class AIDockWaitForClearanceState : public State
{
private:
	friend void forceAIDockWaitForClearanceStateDeletingDestructor();
};

void forceAIDockWaitForClearanceStateDeletingDestructor()
{
	AIDockWaitForClearanceState value;
}
