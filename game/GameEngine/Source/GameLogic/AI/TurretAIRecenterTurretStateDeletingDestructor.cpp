// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: protected scalar-deleting destructor for TurretAIRecenterTurretState.
// Vtable 0x00C9BDC0 slots name this class (?update@TurretAIRecenterTurretState@@UAE?AW4StateReturnType@@XZ); its slot zero routes
// through ILT 0x00030F9E to this 30-byte wrapper, whose complete destructor
// route ILT 0x000319C1 reaches cleanup body 0x000A1B30.

// The destructors are implicit: retail ~TurretAIRecenterTurretState at 0x0018E610 (own ILT 0x000319C1) is each a bare tail jump to
// State::~State (ILT 0x00016725) with no vptr reset, the shape VC7.1 gives an
// implicit virtual destructor; every ILT here is ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class TurretAIRecenterTurretState : public State
{
private:
	friend void forceTurretAIRecenterTurretStateDeletingDestructor();
};

void forceTurretAIRecenterTurretStateDeletingDestructor()
{
	TurretAIRecenterTurretState value;
}
