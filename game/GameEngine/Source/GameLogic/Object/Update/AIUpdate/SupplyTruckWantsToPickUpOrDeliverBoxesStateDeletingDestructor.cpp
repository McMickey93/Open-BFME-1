// cl: /DNDEBUG /MD /EHsc
//
// SupplyTruckWantsToPickUpOrDeliverBoxesState (Zero Hour SupplyTruckAIUpdate.h)
// is defined with the supply truck state machine; this focused declaration emits
// its compiler-generated scalar deleting destructor.
//
// Retail vtable 0x010C9308 (installed by the matched SupplyTruckStateMachine
// constructor 0x002C6430 and by the out-of-line constructor 0x002C6100) has slot
// zero ILT 0x000253AB -> 0x002C69E0, this 30-byte ??_G. It calls the complete
// destructor through ILT 0x00008355 -> 0x002C6A10, a bare tail jump to
// State::~State (ILT 0x00016725) with no vptr reset: the shape VC7.1 gives an
// empty virtual destructor (Zero Hour: EMPTY_DTOR), and it frees with the global
// operator delete. See identity_evidence/002c6100-supplytruck-wants-to-pickup-state.md.

class State
{
public:
	virtual ~State();
};

class SupplyTruckWantsToPickUpOrDeliverBoxesState : public State
{
};

void Force_SupplyTruckWantsToPickUpOrDeliverBoxesState_Deleting_Destructor(
	SupplyTruckWantsToPickUpOrDeliverBoxesState *state)
{
	delete state;
}

// Constructing one emits the vtable and with it the scalar-deleting destructor.
void Force_SupplyTruckWantsToPickUpOrDeliverBoxesState_Vtable()
{
	SupplyTruckWantsToPickUpOrDeliverBoxesState value;
}
