// cl: /DNDEBUG /MD /EHsc
//
// ActAsSupplyTruckState is defined in WorkerAIUpdate.cpp.  This focused
// declaration emits its compiler-generated scalar deleting destructor without
// pulling the full update module into the byte-match translation unit.

// The destructor is implicit: retail ~ActAsSupplyTruckState at 0x002C9C30 (own ILT 0x0003CCB8) is a
// bare tail jump to State::~State (ILT 0x00016725) with no vptr reset,
// the shape VC7.1 gives an implicit virtual destructor; both ILTs are
// ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class ActAsSupplyTruckState : public State
{
};

void Force_ActAsSupplyTruckState_Deleting_Destructor(ActAsSupplyTruckState *state)
{
	delete state;
}

// Constructing one emits the vtable and with it the scalar-deleting destructor.
void Force_ActAsSupplyTruckState_Vtable() { ActAsSupplyTruckState value; }
