// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: protected scalar-deleting destructor for AIAttackMeleeHordeWaitState.
// Vtable 0x00C97B68 slots name this class (?onEnter@AIAttackMeleeHordeWaitState@@UAE?AW4StateReturnType@@XZ); its slot zero routes
// through ILT 0x00012B1B to this 30-byte wrapper, whose complete destructor
// route ILT 0x00041C68 reaches cleanup body 0x000A1B30.

// The destructors are implicit: retail ~AIAttackMeleeHordeWaitState at 0x0017F6B0 (own ILT 0x00041C68) is each a bare tail jump to
// State::~State (ILT 0x00016725) with no vptr reset, the shape VC7.1 gives an
// implicit virtual destructor; every ILT here is ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class AIAttackMeleeHordeWaitState : public State
{
private:
	friend void forceAIAttackMeleeHordeWaitStateDeletingDestructor();
};

void forceAIAttackMeleeHordeWaitStateDeletingDestructor()
{
	AIAttackMeleeHordeWaitState value;
}
