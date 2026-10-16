// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: protected scalar-deleting destructor for AIDockProcessDockState.
// Vtable 0x00C95EA0 slots name this class (?onEnter@AIDockProcessDockState@@UAE?AW4StateReturnType@@XZ); its slot zero routes
// through ILT 0x0003B8E5 to this 30-byte wrapper, whose complete destructor
// route ILT 0x0003E6CB reaches cleanup body 0x000A1B30.

// The destructors are implicit: retail ~AIDockProcessDockState at 0x0014FC00 (own ILT 0x0003E6CB) is each a bare tail jump to
// State::~State (ILT 0x00016725) with no vptr reset, the shape VC7.1 gives an
// implicit virtual destructor; every ILT here is ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class AIDockProcessDockState : public State
{
private:
	friend void forceAIDockProcessDockStateDeletingDestructor();
};

void forceAIDockProcessDockStateDeletingDestructor()
{
	AIDockProcessDockState value;
}
