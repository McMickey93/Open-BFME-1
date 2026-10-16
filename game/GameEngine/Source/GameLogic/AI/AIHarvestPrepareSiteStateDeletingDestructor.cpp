// cl: /DNDEBUG /MD /EHsc
//
// Open-BFME: protected scalar-deleting destructor for AIHarvestPrepareSiteState.
// Vtable 0x00C96770 slots name this class (?update@AIHarvestPrepareSiteState@@UAE?AW4StateReturnType@@XZ); its slot zero routes
// through ILT 0x00003E6D to this 30-byte wrapper, whose complete destructor
// route ILT 0x0002DECF reaches cleanup body 0x000A1B30.

// The destructors are implicit: retail ~AIHarvestPrepareSiteState at 0x001603D0 (own ILT 0x0002DECF) is each a bare tail jump to
// State::~State (ILT 0x00016725) with no vptr reset, the shape VC7.1 gives an
// implicit virtual destructor; every ILT here is ilt_oracle CONFIRMED exact.

class State
{
public:
	virtual ~State();
};

class AIHarvestPrepareSiteState : public State
{
private:
	friend void forceAIHarvestPrepareSiteStateDeletingDestructor();
};

void forceAIHarvestPrepareSiteStateDeletingDestructor()
{
	AIHarvestPrepareSiteState value;
}
