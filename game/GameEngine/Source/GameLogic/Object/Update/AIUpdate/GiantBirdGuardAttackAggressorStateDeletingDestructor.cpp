// cl: /DNDEBUG /MD /EHsc
//
// The constructor at retail 0x002C11E0 names
// GiantBirdGuardAttackAggressorState and installs vtable 0x010C7D88.
// Its first slot reaches the scalar deleting destructor at 0x002C1D40;
// that wrapper calls the complete destructor through ILT 0x0000FDC1.

// The destructor is implicit: retail ~GiantBirdGuardAttackAggressorState at 0x002C1D70 (own ILT 0x0000FDC1) is a
// bare tail jump to State::~State (ILT 0x00016725) with no vptr reset,
// the shape VC7.1 gives an implicit virtual destructor; both ILTs are
// ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class GiantBirdGuardAttackAggressorState : public State
{
};

void Force_GiantBirdGuardAttackAggressorState_Deleting_Destructor(
	GiantBirdGuardAttackAggressorState *state)
{
	delete state;
}

// Constructing one emits the vtable and with it the scalar-deleting destructor.
void Force_GiantBirdGuardAttackAggressorState_Vtable() { GiantBirdGuardAttackAggressorState value; }
