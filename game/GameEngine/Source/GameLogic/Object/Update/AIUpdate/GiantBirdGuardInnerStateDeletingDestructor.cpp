// cl: /DNDEBUG /MD /EHsc
//
// The constructor at retail 0x002C03F0 installs vtable 0x010C7B28;
// the adjacent name getter identifies GiantBirdGuardInnerState.  Vtable slot
// zero reaches the scalar deleting destructor at 0x002C1C40, which calls the
// complete destructor through ILT 0x000317DC.

// The destructor is implicit: retail ~GiantBirdGuardInnerState at 0x002C1C70 (own ILT 0x000317DC) is a
// bare tail jump to State::~State (ILT 0x00016725) with no vptr reset,
// the shape VC7.1 gives an implicit virtual destructor; both ILTs are
// ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class GiantBirdGuardInnerState : public State
{
};

void Force_GiantBirdGuardInnerState_Deleting_Destructor(
	GiantBirdGuardInnerState *state)
{
	delete state;
}

// Constructing one emits the vtable and with it the scalar-deleting destructor.
void Force_GiantBirdGuardInnerState_Vtable() { GiantBirdGuardInnerState value; }
