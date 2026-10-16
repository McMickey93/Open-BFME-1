// cl: /DNDEBUG /MD /EHsc
//
// The constructor at retail 0x002BEFA0 installs vtable 0x010C79E0.
// Its first slot reaches the scalar deleting destructor at 0x002C1B50;
// that wrapper calls the class destructor through ILT 0x00015C8A.

// The destructor is implicit: retail ~GiantBirdFollowWaypointPathState at 0x002C1B80 (own ILT 0x00015C8A) is a
// bare tail jump to State::~State (ILT 0x00016725) with no vptr reset,
// the shape VC7.1 gives an implicit virtual destructor; both ILTs are
// ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class GiantBirdFollowWaypointPathState : public State
{
};

void Force_GiantBirdFollowWaypointPathState_Deleting_Destructor(
	GiantBirdFollowWaypointPathState *state)
{
	delete state;
}

// Constructing one emits the vtable and with it the scalar-deleting destructor.
void Force_GiantBirdFollowWaypointPathState_Vtable() { GiantBirdFollowWaypointPathState value; }
