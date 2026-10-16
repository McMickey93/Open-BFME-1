// cl: /DNDEBUG /MD /EHsc
//
// The constructor at retail 0x002BE000 installs vtable 0x010C77F0.
// Its first slot reaches the scalar deleting destructor at 0x002C1A60;
// that wrapper calls the class destructor through ILT 0x00022CE6.

// The destructor is implicit: retail ~GiantBirdNormalFlightState at 0x002BE220 (own ILT 0x00022CE6) is a
// bare tail jump to State::~State (ILT 0x00016725) with no vptr reset,
// the shape VC7.1 gives an implicit virtual destructor; both ILTs are
// ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class GiantBirdNormalFlightState : public State
{
};

void Force_GiantBirdNormalFlightState_Deleting_Destructor(
	GiantBirdNormalFlightState *state)
{
	delete state;
}

// Constructing one emits the vtable and with it the scalar-deleting destructor.
void Force_GiantBirdNormalFlightState_Vtable() { GiantBirdNormalFlightState value; }
