// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: protected scalar-deleting destructor for AITNGuardOuterState.
// Vtable 0x00C9B650 slots name this class (?update@AITNGuardOuterState@@UAE?AW4StateReturnType@@XZ); its slot zero routes
// through ILT 0x00048540 to this 30-byte wrapper, whose complete destructor
// route ILT 0x000321A0 reaches cleanup body 0x000A1B30.

// The destructors are implicit: retail ~AITNGuardOuterState at 0x0018AFA0 (own ILT 0x000321A0) is each a bare tail jump to
// State::~State (ILT 0x00016725) with no vptr reset, the shape VC7.1 gives an
// implicit virtual destructor; every ILT here is ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class AITNGuardOuterState : public State
{
private:
	friend void forceAITNGuardOuterStateDeletingDestructor();
};

void forceAITNGuardOuterStateDeletingDestructor()
{
	AITNGuardOuterState value;
}
