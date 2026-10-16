// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: protected scalar-deleting destructor for DozerPrimaryIdleState.
// Vtable 0x00CC6F00 slots name this class (?onExit@DozerPrimaryIdleState@@UAEXW4StateExitType@@@Z); its slot zero routes
// through ILT 0x0001C562 to this 30-byte wrapper, whose complete destructor
// route ILT 0x0003E5EF reaches cleanup body 0x000A1B30.

// The destructors are implicit: retail ~DozerPrimaryIdleState at 0x002B8580 (own ILT 0x0003E5EF) is each a bare tail jump to
// State::~State (ILT 0x00016725) with no vptr reset, the shape VC7.1 gives an
// implicit virtual destructor; every ILT here is ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class DozerPrimaryIdleState : public State
{
private:
	friend void forceDozerPrimaryIdleStateDeletingDestructor();
};

void forceDozerPrimaryIdleStateDeletingDestructor()
{
	DozerPrimaryIdleState value;
}
