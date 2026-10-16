// cl: /DNDEBUG /MD /EHsc
//
// The constructor at retail 0x002C04D0 installs vtable 0x010C7C28, and its
// adjacent exact name getter identifies GiantBirdGuardOuterState.  Slot zero
// reaches the scalar deleting destructor at 0x002C1CC0, which calls the
// complete destructor through ILT 0x00038118.

// The destructor is implicit: retail ~GiantBirdGuardOuterState at 0x002C1CF0 (own ILT 0x00038118) is a
// bare tail jump to State::~State (ILT 0x00016725) with no vptr reset,
// the shape VC7.1 gives an implicit virtual destructor; both ILTs are
// ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class GiantBirdGuardOuterState : public State
{
};

void Force_GiantBirdGuardOuterState_Deleting_Destructor(
	GiantBirdGuardOuterState *state)
{
	delete state;
}

// Constructing one emits the vtable and with it the scalar-deleting destructor.
void Force_GiantBirdGuardOuterState_Vtable() { GiantBirdGuardOuterState value; }
