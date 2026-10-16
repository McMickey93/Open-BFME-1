// cl: /DNDEBUG /MD /EHsc
//
// ActAsDozerState is defined in WorkerAIUpdate.cpp.  The focused declaration
// keeps its compiler-generated scalar deleting destructor available as a
// standalone byte-match candidate.

// The destructor is implicit: retail ~ActAsDozerState at 0x002C9BF0 (own ILT 0x0003C943) is a
// bare tail jump to State::~State (ILT 0x00016725) with no vptr reset,
// the shape VC7.1 gives an implicit virtual destructor; both ILTs are
// ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class ActAsDozerState : public State
{
};

void Force_ActAsDozerState_Deleting_Destructor(ActAsDozerState *state)
{
	delete state;
}

// Constructing one emits the vtable and with it the scalar-deleting destructor.
void Force_ActAsDozerState_Vtable() { ActAsDozerState value; }
